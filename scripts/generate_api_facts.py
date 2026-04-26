#!/usr/bin/env python3
"""Generate ``docs/api-facts.yaml`` — the machine-readable index of every
generated API endpoint.

This file is the load-bearing knowledge source for AI agents working in this
repo (vertical-planner, domain-advisor, /new-vertical). It pre-computes the
facts agents would otherwise rediscover by walking the generated tree:

    - module name (with quirks like ``_a_`` infix and ``removes_`` prefix
      flagged in a top-level summary)
    - HTTP method and URL path
    - Response model class name
    - Response shape: ``field_results`` (most lists), ``raw_array`` (some
      lists), ``single`` (gets), or ``mutation`` (POST/PATCH/PUT/DELETE)
    - Per-tag wiring status: is there a hand-written helper class
      (``helpers/<resource>.py``) or domain projection
      (``domain/<resource>.py``)?

The generator imports each module dynamically and inspects:

    - ``_get_kwargs()`` for ``method`` and ``url``
    - ``_parse_response`` annotations for the parsed response type
    - The response model class for a ``field_results`` attribute

Run ``uv run poe facts`` to regenerate. Run ``uv run poe facts-check`` in CI
to fail the build if the file has drifted from the generated tree.

Usage:

    uv run python scripts/generate_api_facts.py            # write
    uv run python scripts/generate_api_facts.py --check    # CI gate
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import re
import subprocess
import sys
import typing as t
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
API_PACKAGE = "frontapp_public_api_client.api"
HELPERS_DIR = REPO_ROOT / "frontapp_public_api_client" / "helpers"
DOMAIN_DIR = REPO_ROOT / "frontapp_public_api_client" / "domain"
OUTPUT_PATH = REPO_ROOT / "docs" / "api-facts.yaml"

# Module-name quirks to flag for agent attention.
QUIRK_PATTERNS = {
    "_a_infix": re.compile(r"_a_"),  # update_a_contact, update_a_tag
    "removes_prefix": re.compile(r"^removes_"),  # removes_inbox_access
}


@dataclass
class Endpoint:
    module: str
    method: str
    path: str
    response_type: str | None
    list_shape: str  # "field_results" | "raw_array" | "single" | "mutation"
    category: str  # "list" | "get" | "create" | "update" | "delete" | "other"
    quirks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, t.Any]:
        d: dict[str, t.Any] = {
            "module": self.module,
            "method": self.method,
            "path": self.path,
            "response_type": self.response_type,
            "list_shape": self.list_shape,
            "category": self.category,
        }
        if self.quirks:
            d["quirks"] = self.quirks
        return d


@dataclass
class TagFacts:
    spec_tag: str
    api_dir: str
    helper: dict[str, t.Any]
    domain: dict[str, t.Any]
    endpoints: list[Endpoint]

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "spec_tag": self.spec_tag,
            "api_dir": self.api_dir,
            "helper": self.helper,
            "domain": self.domain,
            "endpoints": [e.to_dict() for e in self.endpoints],
        }


def _categorize(module_name: str, method: str) -> str:
    if module_name.startswith("list_"):
        return "list"
    if module_name.startswith("get_"):
        return "get"
    if method == "delete":
        return "delete"
    if method == "post":
        return "create"
    if method in {"patch", "put"}:
        return "update"
    return "other"


def _detect_list_shape(
    module_name: str, response_cls: type | None, category: str
) -> str:
    if category in {"create", "update", "delete"}:
        return "mutation"
    if category == "get":
        return "single"
    if category == "list":
        if response_cls is None:
            return "single"
        annotations = getattr(response_cls, "__annotations__", {})
        if "field_results" in annotations:
            return "field_results"
        # Some list endpoints return the response as a top-level list[Foo].
        # In that case openapi-python-client doesn't make a wrapper class —
        # the parsed type is ``list[...]`` directly. Detect via response type
        # name starting with "list[" or being a builtin list.
        return "raw_array"
    return "single"


def _detect_quirks(module_name: str) -> list[str]:
    return [
        name for name, pattern in QUIRK_PATTERNS.items() if pattern.search(module_name)
    ]


def _resolve_response_type(
    parse_response_fn: t.Callable[..., t.Any],
) -> tuple[str | None, type | None]:
    """Return ``(type_name, type_object)`` for the parsed response.

    Reads ``_parse_response``'s return annotation, which is something like
    ``ConversationResponse | None`` or ``list[TeammateResponse] | None``.
    Strips the ``| None`` / ``Optional`` and returns the meaningful side.
    """
    try:
        sig = inspect.signature(parse_response_fn)
    except (TypeError, ValueError):
        return None, None
    return_anno = sig.return_annotation
    if return_anno is inspect.Signature.empty:
        return None, None

    # The annotation is a string (PEP 563) or a real type. Resolve via __module__'s globals.
    module = inspect.getmodule(parse_response_fn)
    if module is None:
        return None, None
    if isinstance(return_anno, str):
        try:
            return_anno = eval(return_anno, module.__dict__)
        except Exception:
            return None, None

    args = t.get_args(return_anno)
    candidate = None
    for arg in args:
        if arg is type(None):
            continue
        candidate = arg
        break
    if candidate is None:
        candidate = return_anno

    # If the candidate is list[X], try to keep the wrapper info.
    origin = t.get_origin(candidate)
    if origin in (list, t.List):  # noqa: UP006 — keep both for older typings
        inner = t.get_args(candidate)
        inner_name = getattr(inner[0], "__name__", str(inner[0])) if inner else "Any"
        return f"list[{inner_name}]", None
    name = getattr(candidate, "__name__", str(candidate))
    return name, candidate if isinstance(candidate, type) else None


def _read_endpoint(tag: str, module_stem: str) -> Endpoint | None:
    full_module = f"{API_PACKAGE}.{tag}.{module_stem}"
    try:
        mod = importlib.import_module(full_module)
    except Exception as exc:  # pragma: no cover - surface import failures
        print(f"warn: failed to import {full_module}: {exc}", file=sys.stderr)
        return None

    get_kwargs = getattr(mod, "_get_kwargs", None)
    parse_response = getattr(mod, "_parse_response", None)
    if get_kwargs is None or parse_response is None:
        return None

    # _get_kwargs may take required path-param args — we only need method/url, which
    # come from the literal dict at the bottom regardless of inputs. Try with no
    # args first; if that fails, fall back to AST scanning.
    method, url = _extract_method_and_path(mod, get_kwargs)
    if method is None or url is None:
        return None

    response_type, response_cls = _resolve_response_type(parse_response)
    category = _categorize(module_stem, method)
    list_shape = _detect_list_shape(module_stem, response_cls, category)
    quirks = _detect_quirks(module_stem)

    return Endpoint(
        module=module_stem,
        method=method.upper(),
        path=url,
        response_type=response_type,
        list_shape=list_shape,
        category=category,
        quirks=quirks,
    )


def _extract_method_and_path(
    mod: t.Any, get_kwargs: t.Callable[..., t.Any]
) -> tuple[str | None, str | None]:
    """Pull method and url from ``_get_kwargs``.

    Source-extract the URL template (e.g. ``/conversations/{conversation_id}``)
    so path-param placeholders survive — calling ``_get_kwargs`` would
    interpolate any spec-example default like ``cnv_123`` into the URL,
    producing useless data.
    """
    src = inspect.getsource(mod)
    method_m = re.search(r'"method"\s*:\s*"([a-z]+)"', src)
    method = method_m.group(1) if method_m else None

    # The url is one of:
    #   "url": "/conversations"
    #   "url": "/conversations/{conversation_id}/followers".format(...)
    # Capture the template literal in either form.
    url_m = re.search(
        r'"url"\s*:\s*"([^"]+)"',  # plain literal
        src,
    )
    if not url_m:
        url_m = re.search(
            r'"url"\s*:\s*"([^"]+)"\.format',  # template before .format(...)
            src,
        )
    url = url_m.group(1) if url_m else None
    return method, url


def _wiring_status(kind: str, tag: str) -> dict[str, t.Any]:
    """Detect helper or domain wiring for a tag.

    Returns ``{"built": bool, "path": str?, "class": str?}``.
    """
    base = HELPERS_DIR if kind == "helper" else DOMAIN_DIR
    # Helpers use plural file names ("conversations.py" → ``Conversations``);
    # domains use singular ("conversation.py" → ``Conversation``). Try both.
    candidates: list[tuple[Path, str]] = []
    if kind == "helper":
        candidates.append((base / f"{tag}.py", _camel(tag)))
        candidates.append((base / f"{_singular(tag)}.py", _camel(_singular(tag))))
    else:
        candidates.append((base / f"{_singular(tag)}.py", _camel(_singular(tag))))
        candidates.append((base / f"{tag}.py", _camel(tag)))
    for path, expected_class in candidates:
        if not path.exists():
            continue
        rel = path.relative_to(REPO_ROOT)
        cls = _find_class(path, prefer=expected_class)
        return {"built": True, "path": str(rel), "class": cls}
    return {"built": False, "path": None, "class": None}


def _camel(snake: str) -> str:
    return "".join(part.capitalize() for part in snake.split("_"))


def _singular(word: str) -> str:
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _find_class(path: Path, prefer: str | None = None) -> str | None:
    """Find a public class in a module.

    If ``prefer`` is given and a class by that name exists, return it.
    Otherwise return the first public class (skipping ``_``-prefixed bases).
    """
    src = path.read_text()
    classes = [m.group(1) for m in re.finditer(r"^class\s+(\w+)\b", src, re.MULTILINE)]
    public = [c for c in classes if not c.startswith("_")]
    if prefer and prefer in public:
        return prefer
    return public[0] if public else None


def _spec_tag_label(tag_dir: str) -> str:
    """Convert ``contact_handles`` → ``Contact Handles`` (close enough)."""
    return " ".join(part.capitalize() for part in tag_dir.split("_"))


def collect_facts() -> dict[str, t.Any]:
    api_root = importlib.import_module(API_PACKAGE)
    api_path = Path(api_root.__file__).parent

    tags: dict[str, dict[str, t.Any]] = {}
    summary = {
        "list_endpoints_with_field_results": [],
        "list_endpoints_returning_raw_array": [],
        "mutations": [],
        "module_name_quirks": [],
        "tags_with_helper": [],
        "tags_with_domain": [],
    }

    for tag_dir in sorted(p for p in api_path.iterdir() if p.is_dir()):
        if tag_dir.name.startswith("_"):
            continue
        tag = tag_dir.name
        endpoints: list[Endpoint] = []
        for module_path in sorted(tag_dir.iterdir()):
            if module_path.suffix != ".py" or module_path.name == "__init__.py":
                continue
            ep = _read_endpoint(tag, module_path.stem)
            if ep is not None:
                endpoints.append(ep)
                ref = f"{tag}.{ep.module}"
                if ep.list_shape == "field_results":
                    summary["list_endpoints_with_field_results"].append(ref)
                elif ep.list_shape == "raw_array":
                    summary["list_endpoints_returning_raw_array"].append(ref)
                if ep.list_shape == "mutation":
                    summary["mutations"].append(ref)
                if ep.quirks:
                    summary["module_name_quirks"].append(ref)

        helper = _wiring_status("helper", tag)
        domain = _wiring_status("domain", tag)
        if helper["built"]:
            summary["tags_with_helper"].append(tag)
        if domain["built"]:
            summary["tags_with_domain"].append(tag)

        tags[tag] = TagFacts(
            spec_tag=_spec_tag_label(tag),
            api_dir=f"frontapp_public_api_client/api/{tag}",
            helper=helper,
            domain=domain,
            endpoints=endpoints,
        ).to_dict()

    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "generated_from_commit": _git_head_sha(),
        "summary": summary,
        "tags": tags,
    }


def _git_head_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


_HEADER = """\
# docs/api-facts.yaml — Generated by scripts/generate_api_facts.py
#
# Machine-readable index of every generated API endpoint. Used by AI agents
# (vertical-planner, domain-advisor, /new-vertical) to avoid re-grepping the
# api/ tree for routine questions like "does list_X use field_results?",
# "what's the module name for updating a contact?", or "is there a helper for
# resource Z yet?".
#
# DO NOT EDIT THIS FILE. It is regenerated by `uv run poe facts` and validated
# in CI by `uv run poe facts-check`. Edits here will be overwritten.
#
# To consult this file from an agent prompt:
#   1. Read the `summary` block first — it pre-computes the most common queries
#      (every list_* with field_results, every mutation, every quirky module
#      name) so a single grep returns the answer.
#   2. Drop into `tags.<resource>` for per-tag detail (endpoints, helper /
#      domain wiring status, full path/method/response info).
#
"""


class _IndentedDumper(yaml.SafeDumper):
    """PyYAML dumper that indents block sequences — matches this project's
    yamllint config which expects sequence items at +2 from their parent."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:  # type: ignore[override]
        return super().increase_indent(flow, False)


def write_facts(facts: dict[str, t.Any]) -> str:
    body = yaml.dump(
        facts,
        Dumper=_IndentedDumper,
        sort_keys=False,
        default_flow_style=False,
        width=100,
    )
    return _HEADER + body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if regenerating would produce a diff (CI gate).",
    )
    args = parser.parse_args()

    facts = collect_facts()
    new_content = write_facts(facts)

    if args.check:
        if not OUTPUT_PATH.exists():
            print(
                f"error: {OUTPUT_PATH.relative_to(REPO_ROOT)} does not exist; "
                f"run `uv run poe facts`",
                file=sys.stderr,
            )
            return 1
        existing = OUTPUT_PATH.read_text()
        # The generated_at + generated_from_commit fields are expected to drift
        # on every run; strip them before comparison so CI doesn't fail just
        # because the SHA changed.
        if _strip_volatile(existing) != _strip_volatile(new_content):
            print(
                f"error: {OUTPUT_PATH.relative_to(REPO_ROOT)} is out of date; "
                f"run `uv run poe facts` and commit the result",
                file=sys.stderr,
            )
            return 1
        print(f"ok: {OUTPUT_PATH.relative_to(REPO_ROOT)} is up to date")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(new_content)
    print(f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


def _strip_volatile(content: str) -> str:
    return re.sub(
        r"^(generated_at|generated_from_commit):.*$",
        "",
        content,
        flags=re.MULTILINE,
    )


if __name__ == "__main__":
    sys.exit(main())

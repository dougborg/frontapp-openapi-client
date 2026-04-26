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

The generator reads each module file with ``ast.parse`` (no import) and
extracts:

    - the ``"method"`` and ``"url"`` keys from ``_get_kwargs``'s ``_kwargs``
      dict literal
    - ``_parse_response``'s return annotation, walked as an AST union
    - the ``field_results`` attribute on the response model class — looked up
      by snake-casing the class name and AST-scanning ``models/<name>.py``

Imports were ~75% of total runtime in the previous import-based design (~233
endpoint modules, plus ``models/__init__.py``'s 480 re-exports building 420
attrs classes); AST parsing is ~50x faster on the hot loop and runs every
``agent-check`` / ``check`` / ``full-check`` invocation, so the saved time
compounds during agent development.

Run ``uv run poe facts`` to regenerate. Run ``uv run poe facts-check`` in CI
to fail the build if the file has drifted from the generated tree.

Usage:

    uv run python scripts/generate_api_facts.py            # write
    uv run python scripts/generate_api_facts.py --check    # CI gate
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
import typing as t
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import cache
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CLIENT_DIR = REPO_ROOT / "frontapp_public_api_client"
API_DIR = CLIENT_DIR / "api"
MODELS_DIR = CLIENT_DIR / "models"
HELPERS_DIR = CLIENT_DIR / "helpers"
DOMAIN_DIR = CLIENT_DIR / "domain"
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


def _detect_quirks(module_name: str) -> list[str]:
    return [
        name for name, pattern in QUIRK_PATTERNS.items() if pattern.search(module_name)
    ]


# ---------------------------------------------------------------------------
# AST extraction (replaces the previous import + inspect-based design)
# ---------------------------------------------------------------------------


def _find_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _extract_method_and_path(
    get_kwargs: ast.FunctionDef,
) -> tuple[str | None, str | None]:
    """Pull method and url from the ``_kwargs`` dict literal in ``_get_kwargs``.

    The function looks like:

        def _get_kwargs(...) -> dict[str, Any]:
            ...
            _kwargs: dict[str, Any] = {
                "method": "post",
                "url": "/conversations",            # plain literal
                # or "url": "/foo/{id}".format(id=...) for path-param URLs
            }
            ...
            return _kwargs

    We walk for ``Dict`` literals carrying both ``"method"`` and ``"url"`` and
    ignore the empty ``params``/``headers`` dicts that some endpoints set up
    earlier in the body.
    """
    for node in ast.walk(get_kwargs):
        if not isinstance(node, ast.Dict):
            continue
        method: str | None = None
        url: str | None = None
        for key, value in zip(node.keys, node.values, strict=False):
            if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                continue
            if key.value == "method":
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    method = value.value
            elif key.value == "url":
                url = _extract_url_value(value)
        if method is not None and url is not None:
            return method, url
    return None, None


def _extract_url_value(value: ast.expr) -> str | None:
    """Return the URL template string from a Dict ``"url"`` value node.

    Two forms appear in generated code:

    - ``"/conversations"`` — ast.Constant
    - ``"/conversations/{id}".format(id=...)`` —
      ast.Call(func=Attribute(value=Constant, attr='format'))

    Returning the template literal preserves ``{id}`` placeholders; calling the
    function would interpolate any spec-example default like ``cnv_123`` into
    the URL.
    """
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value.value
    if isinstance(value, ast.Call):
        func = value.func
        if isinstance(func, ast.Attribute) and func.attr == "format":
            base = func.value
            if isinstance(base, ast.Constant) and isinstance(base.value, str):
                return base.value
    return None


def _resolve_response_type(
    parse_response: ast.FunctionDef,
) -> tuple[str | None, str | None]:
    """Extract ``(display_type, model_class_name)`` from ``_parse_response``'s
    return annotation.

    The annotation is one of:

    - ``ConversationResponse | None``                  → ``("ConversationResponse", "ConversationResponse")``
    - ``Optional[ConversationResponse]``               → same
    - ``Union[Any, ConversationResponse, None]``       → ``("Any", "Any")`` (model lookup will miss → raw_array)
    - ``Any | ConversationResponse | None``            → ``("Any", "Any")``
    - ``list[TeammateResponse] | None``                → ``("list[TeammateResponse]", None)``
    - missing / unparseable                            → ``(None, None)``

    The "first non-None arm wins" rule mirrors the previous import-based
    behavior. When openapi-python-client emits ``Any | RealResponse | None``
    for endpoints with non-200 fallback bodies, the ``Any`` short-circuits the
    ``field_results`` lookup — the model_class_name comes back as ``"Any"``,
    no ``models/any.py`` exists, so the endpoint correctly classifies as
    ``raw_array``. Callers should not need to special-case ``Any``.
    """
    if parse_response.returns is None:
        return None, None

    arms = [
        a
        for a in _flatten_union_arms(parse_response.returns)
        if not (isinstance(a, ast.Constant) and a.value is None)
    ]
    if not arms:
        return None, None

    first = arms[0]

    # list[X] / List[X] — wrapper-less raw arrays.
    if isinstance(first, ast.Subscript):
        base = first.value
        if isinstance(base, ast.Name) and base.id in {"list", "List"}:
            inner = ast.unparse(first.slice)
            return f"list[{inner}]", None
        if isinstance(base, ast.Name):
            return base.id, None
        return ast.unparse(first), None

    # Bare class name — most endpoints.
    if isinstance(first, ast.Name):
        return first.id, first.id

    return ast.unparse(first), None


def _flatten_union_arms(node: ast.expr) -> Iterator[ast.expr]:
    """Yield arms of a union annotation in source order.

    Handles ``X | Y | Z`` (BinOp), ``Optional[X]``, and ``Union[X, Y]`` —
    everything openapi-python-client emits as a return annotation in this
    project. Non-union annotations yield themselves once.
    """
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        yield from _flatten_union_arms(node.left)
        yield from _flatten_union_arms(node.right)
        return
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        if node.value.id == "Optional":
            yield from _flatten_union_arms(node.slice)
            yield ast.Constant(value=None)
            return
        if node.value.id == "Union":
            slice_ = node.slice
            if isinstance(slice_, ast.Tuple):
                for elt in slice_.elts:
                    yield from _flatten_union_arms(elt)
                return
    yield node


def _detect_list_shape(model_class_name: str | None, category: str) -> str:
    if category in {"create", "update", "delete"}:
        return "mutation"
    if category == "get":
        return "single"
    if category == "list":
        # ``model_class_name is None`` covers list[X] returns and unparseable
        # annotations — the previous import-based code returned "single" in
        # both cases. Preserve that to keep the YAML byte-identical.
        if model_class_name is None:
            return "single"
        if _model_has_field_results(model_class_name):
            return "field_results"
        return "raw_array"
    return "single"


def _camel_to_snake(name: str) -> str:
    """``ConversationResponse`` → ``conversation_response``.

    Matches openapi-python-client's filename convention:
    insert ``_`` before any uppercase that isn't at position 0, and before
    any digit run that follows a letter.
    """
    out: list[str] = []
    for i, ch in enumerate(name):
        if i > 0:
            prev = name[i - 1]
            if ch.isupper() or (ch.isdigit() and prev.isalpha()):
                out.append("_")
        out.append(ch.lower())
    return "".join(out)


@cache
def _model_has_field_results(model_name: str) -> bool:
    """Check whether ``models/<snake_case_model>.py`` declares a
    ``field_results`` class attribute.

    openapi-python-client renames spec fields starting with ``_`` to
    ``field_*`` (so ``_results`` becomes ``field_results``). The attribute
    appears as a class-level ``AnnAssign`` on the attrs ``@_attrs_define``
    response wrapper. Caching matters: 14 conversation endpoints all reference
    ``ConversationResponse`` (and other resources have similar fan-out).
    """
    model_path = MODELS_DIR / f"{_camel_to_snake(model_name)}.py"
    if not model_path.exists():
        return False
    try:
        tree = ast.parse(model_path.read_text(), filename=str(model_path))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "field_results"
        ):
            return True
    return False


def _read_endpoint(tag: str, module_stem: str) -> Endpoint:
    """Parse ``api/<tag>/<module_stem>.py`` and extract endpoint facts.

    The hot loop of this script — runs ~233 times per regen. Failures are
    raised loudly: a generated module without ``_get_kwargs`` /
    ``_parse_response`` would mean the codegen contract changed, and silently
    dropping the endpoint would leave gaps in the agent-facing index.
    """
    module_path = API_DIR / tag / f"{module_stem}.py"
    tree = ast.parse(module_path.read_text(), filename=str(module_path))

    get_kwargs = _find_function(tree, "_get_kwargs")
    parse_response = _find_function(tree, "_parse_response")
    if get_kwargs is None or parse_response is None:
        raise RuntimeError(f"{module_path} is missing _get_kwargs or _parse_response")

    method, url = _extract_method_and_path(get_kwargs)
    if method is None or url is None:
        raise RuntimeError(
            f"could not extract method/url from {module_path}._get_kwargs"
        )

    response_type, model_class_name = _resolve_response_type(parse_response)
    category = _categorize(module_stem, method)
    list_shape = _detect_list_shape(model_class_name, category)
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
    tags: dict[str, dict[str, t.Any]] = {}
    summary = {
        "list_endpoints_with_field_results": [],
        "list_endpoints_returning_raw_array": [],
        "mutations": [],
        "module_name_quirks": [],
        "tags_with_helper": [],
        "tags_with_domain": [],
    }

    for tag_dir in sorted(p for p in API_DIR.iterdir() if p.is_dir()):
        if tag_dir.name.startswith("_"):
            continue
        tag = tag_dir.name
        endpoints: list[Endpoint] = []
        for module_path in sorted(tag_dir.iterdir()):
            if module_path.suffix != ".py" or module_path.name == "__init__.py":
                continue
            ep = _read_endpoint(tag, module_path.stem)
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
        # generated_at + generated_from_commit drift on every run; compare via
        # YAML round-trip so the comparison is robust against formatting,
        # comment-block, and dumper changes.
        existing_data = yaml.safe_load(OUTPUT_PATH.read_text()) or {}
        new_data = yaml.safe_load(new_content) or {}
        for key in ("generated_at", "generated_from_commit"):
            existing_data.pop(key, None)
            new_data.pop(key, None)
        if existing_data != new_data:
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


if __name__ == "__main__":
    sys.exit(main())

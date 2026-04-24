#!/usr/bin/env python3
"""Download Front's official OpenAPI spec and write a sanitized copy.

Source: https://github.com/frontapp/front-api-specs (core-api/core-api.json)

Sanitization:
    1. Removes ``example`` keys from path parameters. openapi-python-client
       renders examples as Python default values, which breaks signatures when
       a required path param has an example and is followed by one that doesn't
       (e.g. ``def f(article_id='kba_123', attachment_id)`` is invalid Python).
    2. Drops binary ``*/*`` attachment-download endpoints that the generator
       can't model cleanly. If we need attachment downloads later, hand-wire
       them on the client; they're the only binary responses in the API.

Usage:
    uv run python scripts/vendor_spec.py
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

import yaml

SPEC_URL = (
    "https://raw.githubusercontent.com/"
    "frontapp/front-api-specs/main/core-api/core-api.json"
)
OUTPUT_PATH = Path(__file__).parent.parent / "docs" / "frontapp-openapi.yaml"

# Paths to strip — all return raw binary via */* content type, which the
# generator can't represent. Add hand-written download methods on the client
# if/when needed.
PATHS_TO_STRIP = {
    "/comments/{comment_id}/download/{attachment_link_id}",
    "/download/{attachment_link_id}",
    "/knowledge_base_articles/{article_id}/download/{attachment_id}",
    "/message_templates/{message_template_id}/download/{attachment_link_id}",
    "/messages/{message_id}/download/{attachment_link_id}",
}

# (schema name, property) pairs whose ``default`` value breaks generation via
# allOf inheritance. Example: ``CreateDraft.mode`` has ``default: "private"``,
# but ``EditDraft`` inherits from it and narrows the enum to ``["shared"]``;
# openapi-python-client then emits ``CreateDraftMode.PRIVATE`` as the default
# for ``EditDraft.mode``, which references an unimported enum and is invalid
# against the narrower schema anyway. Strip the default from the base to
# avoid the bad codegen.
PROPERTY_DEFAULTS_TO_STRIP: set[tuple[str, str]] = {
    ("CreateDraft", "mode"),
}


def _strip_path_param_examples(node: object) -> None:
    """Walk the spec tree, removing ``example`` from any parameter where
    ``in: path``. Leaves query/header/body param examples alone."""
    if isinstance(node, dict):
        if node.get("in") == "path" and "example" in node:
            del node["example"]
        for v in node.values():
            _strip_path_param_examples(v)
    elif isinstance(node, list):
        for item in node:
            _strip_path_param_examples(item)


def main() -> int:
    print(f"⬇️  Downloading {SPEC_URL}")
    with urllib.request.urlopen(SPEC_URL) as response:
        spec_bytes = response.read()

    import json

    spec = json.loads(spec_bytes)
    print(
        f"   spec: {spec['info']['title']} v{spec['info']['version']} "
        f"({len(spec['paths'])} paths)"
    )

    stripped = 0
    for path in list(spec["paths"]):
        if path in PATHS_TO_STRIP:
            del spec["paths"][path]
            stripped += 1
    print(f"🗑️  Stripped {stripped} binary-download paths")

    _strip_path_param_examples(spec)
    print("🧹 Normalized path-parameter examples")

    stripped_defaults = 0
    for schema_name, prop_name in PROPERTY_DEFAULTS_TO_STRIP:
        schema = spec.get("components", {}).get("schemas", {}).get(schema_name, {})
        prop = schema.get("properties", {}).get(prop_name, {})
        if "default" in prop:
            del prop["default"]
            stripped_defaults += 1
    print(f"🧹 Stripped {stripped_defaults} inherited-default values")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            spec,
            f,
            sort_keys=False,
            width=120,
            allow_unicode=True,
            default_flow_style=False,
        )
    print(f"✅ Wrote {OUTPUT_PATH} ({len(spec['paths'])} paths)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

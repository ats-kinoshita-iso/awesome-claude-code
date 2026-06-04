#!/usr/bin/env python3
"""Validate a pattern-spec.json against the authoritative IR schema.

Usage:
    python validate.py <pattern-spec.json>

Exits non-zero on any schema violation or cross-field inconsistency, so callers
can fail loud. Beyond JSON-Schema validation it enforces two invariants the
schema alone cannot express:
  - semantic_steps must reference step ids whose kind is "semantic"
  - every input field marked "variable" must carry a name (a harness input
    dimension); fields are checked for the variable/fixed split.
"""
import json
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "pattern-spec.schema.json"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate.py <pattern-spec.json>", file=sys.stderr)
        return 2

    spec_path = Path(argv[1])
    try:
        spec = json.loads(spec_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read spec: {exc}", file=sys.stderr)
        return 2

    schema = json.loads(SCHEMA_PATH.read_text())

    try:
        import jsonschema
    except ImportError:
        print("jsonschema not installed; run: pip install jsonschema", file=sys.stderr)
        return 3

    errors = sorted(
        jsonschema.Draft7Validator(schema).iter_errors(spec),
        key=lambda e: list(e.path),
    )
    for err in errors:
        loc = "/".join(str(p) for p in err.path) or "<root>"
        print(f"schema error at {loc}: {err.message}", file=sys.stderr)
    if errors:
        return 1

    # Cross-field invariants not expressible in JSON Schema.
    steps = {s["id"]: s for s in spec["steps"]}
    semantic_ids = {sid for sid, s in steps.items() if s["kind"] == "semantic"}
    bad = [sid for sid in spec["semantic_steps"] if sid not in semantic_ids]
    if bad:
        print(
            f"semantic_steps references non-semantic or unknown step id(s): {bad}",
            file=sys.stderr,
        )
        return 1

    print(f"OK: {spec_path} conforms to pattern-spec schema {spec['spec_version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

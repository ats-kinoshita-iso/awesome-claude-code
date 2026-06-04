#!/usr/bin/env python3
"""Select a backend for a spec and emit a concrete harness scaffold.

Usage:
    python scaffold.py --spec <pattern-spec.json> --out <dir>

Validates the spec, picks the backend whose ``supports(spec)`` scores highest,
then calls ``emit`` + ``emit_tests``. Every emitted harness honors the uniform
CLI contract:

    run.py --input <path|-> --out <path|->

reading the variable inputs, validating output against the task's
``output.schema.json``, and exiting non-zero on any schema violation.

The scaffold is deterministic plumbing; the deterministic step bodies and the
structural test assertions are then filled in from the spec (look for the
``TODO(spec-learner)`` markers).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make the plugin root importable so ``backends`` resolves regardless of cwd.
_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from backends.registry import select  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", required=True, help="path to pattern-spec.json")
    ap.add_argument("--out", required=True, help="output directory for the harness")
    args = ap.parse_args(argv)

    spec_path = Path(args.spec).resolve()
    try:
        spec = json.loads(spec_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read spec: {exc}", file=sys.stderr)
        return 2

    # Reuse the validator so scaffolding fails loud on a malformed spec.
    from validate import main as validate_main  # noqa: E402

    if validate_main(["validate.py", str(spec_path)]) != 0:
        print("spec failed validation; not scaffolding.", file=sys.stderr)
        return 1

    backend = select(spec)
    out_dir = Path(args.out).resolve()
    backend.emit(spec, out_dir, spec_path=spec_path)
    backend.emit_tests(spec, out_dir, spec_path=spec_path)

    variable = [f["name"] for f in spec["input_contract"]["fields"] if f["variability"] == "variable"]
    fixed = [f["name"] for f in spec["input_contract"]["fields"] if f["variability"] == "fixed"]
    print(f"backend: {backend.name}  (score {backend.supports(spec)})")
    print(f"emitted harness -> {out_dir}")
    print(f"  variable inputs (harness dimensions): {', '.join(variable) or '(none)'}")
    print(f"  fixed inputs (constants):             {', '.join(fixed) or '(none)'}")
    print("Next: fill the TODO(spec-learner) step bodies and test assertions, then run verify.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run a harness's golden + perturbed tests and the uniform CLI contract.

Usage:
    python verify.py --harness <dir>

Reads the harness manifest (``.spec-learner.json``) to find the backend that
produced it, then runs ``backend.verify(out_dir)``:

  - structural criteria  -> the harness's pytest suite (golden + perturbed) and
    the CLI's non-zero-exit-on-schema-violation contract
  - qualitative criteria -> reported for the judge subagent (``../agents/judge.md``);
    routed to the judge only when a model is available (in-session), otherwise
    reported as ``skipped (needs judge)``

A perturbed failure means fix the harness or the spec -- never loosen the test.
Exits non-zero if verification fails, so callers can gate on it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from backends.registry import BACKENDS  # noqa: E402

_BY_NAME = {b.name: b for b in BACKENDS}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--harness", required=True, help="path to an emitted harness directory")
    args = ap.parse_args(argv)

    out_dir = Path(args.harness).resolve()
    manifest_path = out_dir / ".spec-learner.json"
    if not manifest_path.is_file():
        print(f"no manifest at {manifest_path}; is this a spec-learner harness?", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text())
    backend = _BY_NAME.get(manifest.get("backend"))
    if backend is None:
        print(f"unknown backend in manifest: {manifest.get('backend')!r}", file=sys.stderr)
        return 2

    result = backend.verify(out_dir)
    print(json.dumps(result.report, indent=2))
    print(f"\nVERIFY: {'PASS' if result.passed else 'FAIL'}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

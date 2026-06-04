#!/usr/bin/env python3
"""Select a backend for a spec and emit a concrete harness.

Picks the backend whose supports(spec) scores highest, then calls
emit(spec, out_dir) and emit_tests(spec, out_dir). Every emitted harness honors
the uniform CLI contract:

    run --input <path|-> --out <path|->

reading the variable inputs, validating output against the task's
output.schema.json, and exiting non-zero on any schema violation.

Backends (see ../references/backends/): hybrid-python, deterministic-typescript,
agentic-claude-code.

Status: Milestone-1 stub. The backend interface and the two simplest backends
land in Milestone 2.
"""
import sys

print("scaffold.py is a Milestone-1 stub; backends arrive in M2.", file=sys.stderr)
sys.exit(64)

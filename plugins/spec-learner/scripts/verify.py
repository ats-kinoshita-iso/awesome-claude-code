#!/usr/bin/env python3
"""Run a harness's golden + perturbed tests and route acceptance criteria.

  - structural criteria -> deterministic asserts (must hold on perturbed inputs)
  - qualitative criteria -> the judge subagent (../agents/judge.md), which
    returns {text, passed, evidence}

Golden test runs on the original approved input; perturbed test(s) run on
different inputs to prove generalization. A perturbed failure means fix the
harness or the spec -- never loosen the test.

Status: Milestone-1 stub. Wired up alongside the backends in Milestone 2.
"""
import sys

print("verify.py is a Milestone-1 stub; verification wiring arrives in M2.", file=sys.stderr)
sys.exit(64)

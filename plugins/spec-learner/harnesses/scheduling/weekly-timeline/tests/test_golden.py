"""Golden test: the pattern on the original approved input.

Asserts the spec's structural acceptance_criteria, schema conformance, and the
exact expected output (the regression anchor). The same invariants are checked on
a different input in test_perturbed.py.
"""
import json
from pathlib import Path

import jsonschema
import pipeline

_HERE = Path(__file__).resolve().parent
_SCHEMA = json.loads((_HERE.parent / "output.schema.json").read_text())
_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

EXPECTED = {
    "days": [
        {"day": "Monday", "date": "2026-06-08", "assignments": ["Carol"]},
        {"day": "Tuesday", "date": "2026-06-09", "assignments": ["Dan"]},
        {"day": "Wednesday", "date": "2026-06-10", "assignments": ["Erin"]},
        {"day": "Thursday", "date": "2026-06-11", "assignments": ["Carol"]},
        {"day": "Friday", "date": "2026-06-12", "assignments": ["Dan"]},
        {"day": "Saturday", "date": "2026-06-13", "assignments": ["Erin"]},
        {"day": "Sunday", "date": "2026-06-14", "assignments": ["Carol"]},
    ]
}


def test_golden():
    data = json.loads((_HERE / "inputs" / "golden.json").read_text())
    result = pipeline.run(data)

    # Schema conformance (the harness's output contract).
    jsonschema.Draft7Validator(_SCHEMA).validate(result)

    # Structural: exactly seven days, ordered Monday -> Sunday.
    assert [d["day"] for d in result["days"]] == _ORDER

    # Structural: no unavailable resource appears on any day.
    unavailable = set(data["unavailable_resources"])
    assigned = {name for d in result["days"] for name in d["assignments"]}
    assert unavailable.isdisjoint(assigned)

    # Regression: exact approved output.
    assert result == EXPECTED

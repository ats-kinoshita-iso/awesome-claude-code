"""Perturbed test: the same pattern on a DIFFERENT input.

Asserts the structural invariants (NOT equality to the golden output) -- this is
the generalization proof. A failure here means fix the harness or the spec --
never loosen the test.
"""

import datetime
import json
from pathlib import Path

import jsonschema
import pipeline

_HERE = Path(__file__).resolve().parent
_SCHEMA = json.loads((_HERE.parent / "output.schema.json").read_text())
_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def test_perturbed():
    data = json.loads((_HERE / "inputs" / "perturbed.json").read_text())
    result = pipeline.run(data)

    # Schema conformance.
    jsonschema.Draft7Validator(_SCHEMA).validate(result)

    # Structural: exactly seven days, ordered Monday -> Sunday.
    assert [d["day"] for d in result["days"]] == _ORDER

    # Structural: the week is the one containing target_date, starting Monday.
    target = datetime.date.fromisoformat(data["target_date"])
    monday = target - datetime.timedelta(days=target.weekday())
    expected_dates = [(monday + datetime.timedelta(days=i)).isoformat() for i in range(7)]
    assert [d["date"] for d in result["days"]] == expected_dates
    assert any(d["date"] == data["target_date"] for d in result["days"])

    # Structural: no unavailable resource appears on any day.
    unavailable = set(data["unavailable_resources"])
    assigned = {name for d in result["days"] for name in d["assignments"]}
    assert unavailable.isdisjoint(assigned)

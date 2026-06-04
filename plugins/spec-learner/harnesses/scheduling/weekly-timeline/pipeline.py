"""Pipeline for this harness. Filled from examples/scheduling/pattern-spec.json.

One function per spec step, run in order by ``run``. Variable inputs are read
from ``state['input']``; fixed inputs (week starts Monday; the standing roster)
are constants below. No value the spec marks 'variable' is hardcoded here.

Variable inputs (harness dimensions): target_date, unavailable_resources
Fixed inputs (constants): week_start, roster
"""
from __future__ import annotations

import datetime

# Fixed dimensions (input_contract marks these 'fixed').
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ROSTER = ["Alice", "Bob", "Carol", "Dan", "Erin"]


def parse_temporal(state: dict) -> None:
    """[deterministic] Resolve target_date to its containing week (Mon-Sun)."""
    target = datetime.date.fromisoformat(state["input"]["target_date"])
    monday = target - datetime.timedelta(days=target.weekday())
    state["week"] = [monday + datetime.timedelta(days=i) for i in range(7)]


def apply_availability(state: dict) -> None:
    """[deterministic] Remove unavailable_resources from the assignable pool for that week."""
    unavailable = set(state["input"].get("unavailable_resources", []))
    state["available"] = [r for r in ROSTER if r not in unavailable]


def render_timeline(state: dict) -> None:
    """[deterministic] Render assignments as a weekly timeline keyed by day."""
    available = state["available"]
    days = []
    for i, day_date in enumerate(state["week"]):
        # Round-robin one available resource per day for a balanced rotation.
        assignments = [available[i % len(available)]] if available else []
        days.append({"day": DAYS[i], "date": day_date.isoformat(), "assignments": assignments})
    state["output"] = {"days": days}


def run(data: dict) -> dict:
    """Run the ordered steps and return the validated output."""
    state: dict = {"input": data}
    for step in (parse_temporal, apply_availability, render_timeline):
        step(state)
    return state["output"]

"""The backend interface every backend implements.

A backend turns a validated ``pattern-spec`` (the backend-neutral IR) into a
concrete harness on disk and can verify that harness. The four methods mirror the
brief:

    supports(spec)        -> float   how well this backend fits the spec (0..1)
    emit(spec, out_dir)              write the runnable harness scaffold
    emit_tests(spec, out_dir)        write golden + perturbed test scaffolds
    verify(out_dir)       -> VerifyResult   run the tests + CLI contract

Keeping this interface stable is what lets new backends (TypeScript, the M3
agentic-claude-code recipe) slot in without touching existing code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass
class VerifyResult:
    """Outcome of verifying a harness.

    ``passed`` is the overall gate (structural checks + CLI contract). ``report``
    carries the run records and per-criterion results in the shapes documented in
    ``references/eval-and-grading.md`` so any viewer can read them.
    """

    passed: bool
    report: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Backend(Protocol):
    """Structural contract for a backend (duck-typed; no inheritance required)."""

    name: str

    def supports(self, spec: dict) -> float:
        """Score in 0..1 for how well this backend fits ``spec`` (0 = cannot)."""

    def emit(self, spec: dict, out_dir: Path, spec_path: Path | None = None) -> None:
        """Write the runnable harness scaffold into ``out_dir``."""

    def emit_tests(self, spec: dict, out_dir: Path, spec_path: Path | None = None) -> None:
        """Write golden + perturbed test scaffolds into ``out_dir``."""

    def verify(self, out_dir: Path) -> VerifyResult:
        """Run the harness's tests and the uniform CLI contract."""

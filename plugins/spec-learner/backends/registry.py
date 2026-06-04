"""Backend registry: list available backends and pick the best fit for a spec.

Selection is by highest ``supports(spec)`` score. Add a backend by appending it
to ``BACKENDS`` -- nothing else changes.
"""

from __future__ import annotations

from .base import Backend
from .hybrid_python.backend import HybridPythonBackend

# Ordered by registration; ties broken by order (first wins).
BACKENDS: list[Backend] = [HybridPythonBackend()]


def select(spec: dict) -> Backend:
    """Return the backend with the highest ``supports`` score for ``spec``.

    Raises ``LookupError`` if no backend scores above zero, so the caller fails
    loud rather than emitting an inappropriate harness.
    """
    ranked = sorted(BACKENDS, key=lambda b: b.supports(spec), reverse=True)
    best = ranked[0]
    score = best.supports(spec)
    if score <= 0:
        raise LookupError(
            "no backend supports this spec "
            f"(harness_type={spec.get('harness_type')!r}, "
            f"target_runtime={spec.get('target_runtime')!r}); "
            "available: " + ", ".join(b.name for b in BACKENDS)
        )
    return best

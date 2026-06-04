"""hybrid-python backend: emit produces the expected scaffold + scoring."""

import json
from pathlib import Path

from backends.hybrid_python.backend import HybridPythonBackend
from backends.registry import select

_ROOT = Path(__file__).resolve().parent.parent
_EXAMPLE = _ROOT / "examples" / "scheduling" / "pattern-spec.json"


def _spec():
    return json.loads(_EXAMPLE.read_text())


def test_emit_writes_scaffold(tmp_path):
    backend = HybridPythonBackend()
    spec = _spec()
    backend.emit(spec, tmp_path, spec_path=_EXAMPLE)
    backend.emit_tests(spec, tmp_path, spec_path=_EXAMPLE)

    expected = [
        "run.py",
        "pipeline.py",
        "output.schema.json",
        "pattern-spec.json",
        ".spec-learner.json",
        "README.md",
        "tests/conftest.py",
        "tests/test_golden.py",
        "tests/test_perturbed.py",
        "tests/inputs/golden.json",
    ]
    for rel in expected:
        assert (tmp_path / rel).is_file(), f"missing {rel}"

    # Deterministic spec -> no semantic machinery emitted.
    assert not (tmp_path / "semantic.py").exists()
    assert not (tmp_path / "prompts").exists()

    # Step stubs are present but unimplemented (Claude fills these).
    pipe = (tmp_path / "pipeline.py").read_text()
    assert "def parse_temporal(state: dict)" in pipe
    assert "def apply_availability(state: dict)" in pipe
    assert "TODO(spec-learner)" in pipe
    assert "NotImplementedError" in pipe

    # Manifest records the backend so verify.py can re-load it.
    manifest = json.loads((tmp_path / ".spec-learner.json").read_text())
    assert manifest["backend"] == "hybrid-python"

    # Seeded golden input contains only the variable fields.
    golden = json.loads((tmp_path / "tests" / "inputs" / "golden.json").read_text())
    assert set(golden) == {"target_date", "unavailable_resources"}


def test_generated_pipeline_is_importable_python(tmp_path):
    backend = HybridPythonBackend()
    backend.emit(_spec(), tmp_path, spec_path=_EXAMPLE)
    # Compiles as valid Python even though bodies are stubs.
    compile((tmp_path / "pipeline.py").read_text(), "pipeline.py", "exec")
    compile((tmp_path / "run.py").read_text(), "run.py", "exec")


def test_supports_scoring():
    backend = HybridPythonBackend()
    spec = _spec()
    assert backend.supports(spec) == 0.8  # deterministic + python
    assert backend.supports({**spec, "harness_type": "hybrid"}) == 1.0
    assert backend.supports({**spec, "target_runtime": "typescript"}) == 0.0
    assert backend.supports({**spec, "harness_type": "agentic"}) == 0.0


def test_registry_selects_hybrid_python():
    assert select(_spec()).name == "hybrid-python"

"""validate.py: the example spec passes; a cross-field violation fails loud."""
import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_VALIDATE = _ROOT / "scripts" / "validate.py"
_EXAMPLE = _ROOT / "examples" / "scheduling" / "pattern-spec.json"


def _run(path: Path):
    return subprocess.run(
        [sys.executable, str(_VALIDATE), str(path)], capture_output=True, text=True
    )


def test_valid_spec_passes():
    result = _run(_EXAMPLE)
    assert result.returncode == 0, result.stderr


def test_semantic_steps_must_reference_semantic_steps(tmp_path):
    spec = json.loads(_EXAMPLE.read_text())
    spec["semantic_steps"] = ["parse-temporal"]  # a deterministic step -> invalid
    bad = tmp_path / "bad-spec.json"
    bad.write_text(json.dumps(spec))

    result = _run(bad)
    assert result.returncode == 1
    assert "semantic_steps" in result.stderr

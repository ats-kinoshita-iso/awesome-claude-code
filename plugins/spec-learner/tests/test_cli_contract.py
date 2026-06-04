"""The uniform CLI contract: valid input -> schema-valid output (exit 0); a
schema-violating output -> non-zero exit (fail loud, never emit malformed output).
"""

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

_ROOT = Path(__file__).resolve().parent.parent
_HARNESS = _ROOT / "harnesses" / "scheduling" / "weekly-timeline"


def test_valid_input_emits_schema_valid_output():
    result = subprocess.run(
        [
            sys.executable,
            str(_HARNESS / "run.py"),
            "--input",
            str(_HARNESS / "tests" / "inputs" / "golden.json"),
            "--out",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    schema = json.loads((_HARNESS / "output.schema.json").read_text())
    jsonschema.Draft7Validator(schema).validate(output)


def test_fails_loud_on_schema_violation(tmp_path):
    # Reuse the generated CLI + schema, but force the pipeline to emit bad output.
    (tmp_path / "run.py").write_text((_HARNESS / "run.py").read_text())
    (tmp_path / "output.schema.json").write_text((_HARNESS / "output.schema.json").read_text())
    (tmp_path / "pipeline.py").write_text("def run(data):\n    return {'days': []}\n")  # < 7 days
    (tmp_path / "in.json").write_text(
        json.dumps({"target_date": "2026-06-14", "unavailable_resources": []})
    )

    result = subprocess.run(
        [
            sys.executable,
            str(tmp_path / "run.py"),
            "--input",
            str(tmp_path / "in.json"),
            "--out",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "schema violation" in result.stderr

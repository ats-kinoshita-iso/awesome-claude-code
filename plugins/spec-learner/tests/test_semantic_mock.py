"""semantic.call: the hybrid model-call path, proven offline with a mock client.

No API key is needed -- a fake client injects the model response, so we can prove
the schema gate (valid -> dict; invalid/non-JSON -> raise) without the SDK.
"""

import json

import jsonschema
import pytest
from backends.hybrid_python import semantic

_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["label"],
    "properties": {"label": {"type": "string"}},
}


class _Block:
    type = "text"

    def __init__(self, text):
        self.text = text


class _Message:
    def __init__(self, text):
        self.content = [_Block(text)]


class _Messages:
    def __init__(self, text):
        self._text = text

    def create(self, **_kwargs):
        return _Message(self._text)


class _FakeClient:
    def __init__(self, text):
        self.messages = _Messages(text)


def test_valid_output_returns_dict():
    client = _FakeClient(json.dumps({"label": "ok"}))
    result = semantic.call("prompt", {"x": 1}, _SCHEMA, client=client)
    assert result == {"label": "ok"}


def test_schema_violation_raises():
    client = _FakeClient(json.dumps({"label": 123}))  # wrong type
    with pytest.raises(jsonschema.ValidationError):
        semantic.call("prompt", {}, _SCHEMA, client=client)


def test_non_json_raises_value_error():
    client = _FakeClient("not json at all")
    with pytest.raises(ValueError):
        semantic.call("prompt", {}, _SCHEMA, client=client)

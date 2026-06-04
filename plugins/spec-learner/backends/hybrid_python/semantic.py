"""Schema-validated model-call wrapper for hybrid harness ``semantic`` steps.

One tightly-scoped, schema-validated Anthropic call per semantic step. The model
output MUST validate against ``out_schema`` or this raises -- an unvalidated
semantic result must never flow downstream (fail loud, like the harness CLI).

This module is both the canonical implementation and the file the backend copies
into a harness that has semantic steps. ``client`` is injectable so the call can
be unit-tested offline with a mock (no API key required); the real Anthropic SDK
is imported lazily only when no client is supplied.
"""

from __future__ import annotations

import json
from typing import Any

DEFAULT_MODEL = "claude-opus-4-8"


def _default_client():  # pragma: no cover - exercised only with a real API key
    from anthropic import Anthropic

    return Anthropic()


def _extract_text(message: Any) -> str:
    """Concatenate the text blocks of an Anthropic message."""
    parts = [block.text for block in message.content if getattr(block, "type", None) == "text"]
    return "".join(parts)


def call(
    prompt: str,
    payload: dict,
    out_schema: dict,
    *,
    client: Any | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
) -> dict:
    """Run one semantic step and return its schema-validated JSON result.

    Raises ``jsonschema.ValidationError`` if the model output does not conform to
    ``out_schema``, and ``ValueError`` if it is not valid JSON.
    """
    import jsonschema

    client = client or _default_client()
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {
                "role": "user",
                "content": prompt + "\n\nINPUT:\n" + json.dumps(payload, sort_keys=True),
            }
        ],
    )
    text = _extract_text(message).strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"semantic step returned non-JSON output: {exc}") from exc

    jsonschema.Draft7Validator(out_schema).validate(result)
    return result

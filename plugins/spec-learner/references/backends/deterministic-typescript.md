# Backend: deterministic-typescript

**When it scores high:** `harness_type` is `deterministic` and the ecosystem is
TypeScript/Node.

**Shape:** a Node pipeline — load → transform → validate → format — with no
model call. If the spec lists any irreducibly-semantic step, this backend should
score low; prefer `hybrid-python` or `agentic-claude-code` instead. Do not
reduce a genuinely semantic step to regex just to fit here.

**Dependencies (minimal):** `zod` (or `ajv`) for schema validation, `vitest` for
tests.

**Interface:** implements `supports(spec)→score`, `emit(spec, out_dir)`,
`emit_tests(spec, out_dir)`, `verify(out_dir)`.

**Uniform CLI:** the emitted harness exposes
`run --input <path|-> --out <path|->`. It reads the variable inputs, runs the
pipeline, validates output against the task's `output.schema.json`, and exits
non-zero on any schema violation.

**Variable dimensions:** exactly the `input_contract` fields marked `variable`.

> Status: reference stub. **Deferred** past Milestone 2 (which shipped
> `hybrid-python` only). The backend interface in `backends/base.py` is stable, so
> this slots in later without changing existing code. There is no technical
> blocker to a future `hybrid-typescript` either — the model-call wrapper just has
> a TypeScript counterpart — it was scoped out, not ruled out.

# Backend: hybrid-python

**When it scores high:** `harness_type` is `hybrid` (or `deterministic`) and the
ecosystem is Python.

**Shape:** deterministic loader / parser / validator / formatter, plus **one**
tightly-scoped, schema-validated Anthropic API call per `semantic` step. The
prompt for each semantic step is stored under the task's `prompts/`. If the spec
has no semantic step, this backend degrades to pure code.

**Dependencies (minimal):** `jsonschema` for validation, `pytest` for tests, and
the Anthropic SDK only if there is a semantic step.

**Interface:** implements `supports(spec)→score`, `emit(spec, out_dir)`,
`emit_tests(spec, out_dir)`, `verify(out_dir)`.

**Uniform CLI:** the emitted harness exposes
`run --input <path|-> --out <path|->`. It reads the variable inputs, runs the
ordered steps, validates output against the task's `output.schema.json`, and
exits non-zero on any schema violation. Never emit malformed output.

**Variable dimensions:** exactly the `input_contract` fields marked `variable`.
No instance value from the original session may appear in the code.

**Codegen model:** `emit` generates a deterministic *scaffold* (CLI, IO + schema
validation, one function stub per step, golden/perturbed test scaffolds); Claude
fills the deterministic step bodies and structural assertions from the spec. Step
functions share a `state` dict seeded with `state["input"]`; the final step sets
`state["output"]`, which `run.py` validates.

> Status: implemented (Milestone 2). Worked end-to-end example:
> `harnesses/scheduling/weekly-timeline/`. Package dir is `backends/hybrid_python/`
> (underscore) for importability.

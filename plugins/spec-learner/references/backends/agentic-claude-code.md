# Backend: agentic-claude-code

**When it scores high:** `harness_type` is `agentic` — the value of the original
output came from an open-ended agent loop that cannot be reduced to a script
without losing what made it good.

**Shape:** reproduce the pattern as an **agent recipe**, not a script:
- a distilled system prompt / skill capturing the invariant approach,
- the input contract (the `variable` fields),
- a tool allowlist,
- the same `run --input <path|-> --out <path|->` CLI wrapper (Claude Agent SDK).

The agent's final output is parsed and validated against the task's
`output.schema.json` exactly like any other backend, and the harness exits
non-zero on violation. This keeps the verifier backend-agnostic.

**Dependencies (minimal):** Claude Agent SDK; `jsonschema`/`zod` for the final
output validation.

**Interface:** implements `supports(spec)→score`, `emit(spec, out_dir)`,
`emit_tests(spec, out_dir)`, `verify(out_dir)`.

**Recipe layer is shared:** keep the prompt/input-contract/tool-allowlist
"recipe" separable from the runtime wrapper, so a future non-Claude runtime
adapter could reuse it. (agentic-pi is out of scope for this plugin.)

> Status: reference stub. Backend code lands in Milestone 3.

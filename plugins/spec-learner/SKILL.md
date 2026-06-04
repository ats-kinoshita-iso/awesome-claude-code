---
name: spec-learner
description: Turns an already-approved Claude output into a repeatable, tested pipeline by extracting a backend-neutral spec and generating a parametric harness verified with golden and perturbed tests. Use after the user approves an output and wants the underlying pattern (not the one-off result) reproduced on new, different inputs.
version: 0.1.0
---

# Spec Learner

Run this **after** a Claude session has produced an output the user explicitly
approved, when they want that success made repeatable. Do **not** redo the
original task. Capture *what made the output good* as a backend-neutral
specification, compile that spec into a small parametric harness, and prove the
harness generalizes with golden + perturbed tests.

Central discipline: separate the **invariant pattern** from **instance-specific
values**. "The schedule for the 14th" is an instance; "extract temporal fields,
apply resource-availability constraints, render a weekly timeline" is the
pattern. The harness's variable dimensions must equal exactly what the spec
marks variable — no more, no less. No hardcoded instance values anywhere. See
`${CLAUDE_PLUGIN_ROOT}/references/pattern-vs-instance.md`.

## When to use

- The user just approved an output and says some variant of "make this
  repeatable", "do this every week/month", "automate this for new inputs".
- A prior result was good and they want the *pattern* applied to different
  dates / resources / records / structure.

Do **not** use when: the user wants the same task re-run as a one-off, or when
no output has been approved yet (there is nothing to generalize).

## Phase 1 — Capture & spec extraction

Input is a **successful session**, not just one output file.
- Primary mode: invoked in-session immediately after approval (live
  conversation + artifacts available).
- Secondary mode: ingest an exported transcript (markdown/JSONL) for offline
  use. Guard: if neither a live session nor a transcript is available, stop and
  ask the user to provide one — there is nothing to learn from otherwise.

Steps:
1. Gather the input files/sources used, the user's stated requirements, the
   approved output, and the relevant session steps/tool calls. Ignore dead ends
   and retries — they are not part of the pattern.
   Helper: `${CLAUDE_PLUGIN_ROOT}/scripts/capture.py` (in-session capture /
   transcript ingest).
2. Ask the user **one** focused question: *what specifically made this output
   good?* Their answer is the acceptance criteria. Ask only this one thing.
3. Write the spec as a narrative `pattern-spec.md` and the authoritative machine
   IR `pattern-spec.json`. The IR — not the prose — is what backends compile.
   It must conform to `${CLAUDE_PLUGIN_ROOT}/schemas/pattern-spec.schema.json`
   and contain: intent; input contract with **variable vs fixed parts
   explicitly marked**; ordered processing steps each tagged `deterministic` or
   `semantic`; rules/constraints; output contract (a concrete
   `output.schema.json` for this task); acceptance criteria; and the explicit
   list of irreducibly-semantic steps.
   Validate it: `${CLAUDE_PLUGIN_ROOT}/scripts/validate.py <pattern-spec.json>`.
4. **Decide harness type:**
   - `deterministic` — no real semantic step; pure code reproduces it.
   - `hybrid` — mechanical scaffold + 1–2 schema-validated model calls.
   - `agentic` — the value is an open-ended agent loop; reproduce as an agent
     recipe, not a script.
   Guard: do not force a genuinely semantic step into rules/regex just to reach
   `deterministic`. Keep it as a constrained model call or agentic step.
5. **Decide target runtime** (`python` | `typescript` | `claude-code`) from the
   harness type plus the user's ecosystem. Ask only if ambiguous.

Gate before Phase 2: the user confirms the spec captures the pattern.

## Phase 2 — Harness generation (backend-pluggable)

The spec/IR layer is backend-neutral; a **backend** compiles the IR into a
concrete harness. Pick the backend that scores highest for this spec
(`hybrid-python`, `deterministic-typescript`, or `agentic-claude-code`). Each
backend implements the same interface: `supports(spec)→score`,
`emit(spec, out_dir)`, `emit_tests(spec, out_dir)`, `verify(out_dir)`. Helper:
`${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py`.

**Uniform harness CLI contract** (every backend, every language):
`run --input <path|-> --out <path|->` reads the variable inputs (JSON/files),
produces output **validated against `output.schema.json`**, and exits non-zero
on any schema violation. Fail loud; never emit malformed output. This
uniformity lets the verifier treat all backends identically.

Backend references (read the one you chose; one level deep):
- `${CLAUDE_PLUGIN_ROOT}/references/backends/hybrid-python.md`
- `${CLAUDE_PLUGIN_ROOT}/references/backends/deterministic-typescript.md`
- `${CLAUDE_PLUGIN_ROOT}/references/backends/agentic-claude-code.md`

Keep dependencies minimal in every backend. Store any prompt for a
semantic/agentic step under the task's `prompts/`.

## Phase 3 — Verification

Map the brief's tests onto evaluation-driven development. See
`${CLAUDE_PLUGIN_ROOT}/references/eval-and-grading.md`.
- **Golden test:** run on the *original approved input*; assert every acceptance
  criterion holds.
- **Perturbed test (≥1):** run on different dates/resources/structure to prove
  generalization. Guard: if it fails, fix the harness or the spec — **never
  loosen the test**.
- **Check types:** structural/contract criteria (field equality, ordering,
  length, schema conformance) are deterministic asserts and must hold on
  perturbed inputs. Genuinely qualitative criteria go to the bundled judge
  subagent (`${CLAUDE_PLUGIN_ROOT}/agents/judge.md`), which returns a
  schema-validated `{text, passed, evidence}`. Do not route structural criteria
  to the judge.
  Helper: `${CLAUDE_PLUGIN_ROOT}/scripts/verify.py`.

When a perturbed failure forces a spec/harness change, append a brief,
**user-reviewed** entry to `${CLAUDE_PLUGIN_ROOT}/learnings.md` describing the
recurring fix, so future spec extraction is primed. Surface every append for
approval; never modify the skill itself autonomously.

## Output artifacts (per task)

Write under `harnesses/<domain>/<task>/`: `pattern-spec.md`,
`pattern-spec.json`, `output.schema.json`, the harness code, golden + perturbed
tests in the backend's native runner, `prompts/` for any semantic/agentic step,
and a `README.md` stating how to run it and what is variable vs fixed.

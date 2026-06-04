# spec-learner

A standalone Claude Code plugin containing one Agent Skill, `spec-learner`. It
runs **after** a Claude session produces an output the user explicitly approved
and turns that one-off success into a repeatable, tested pipeline.

It does **not** redo the original task. Instead it:

1. **Extracts** a backend-neutral specification of *what made the output good*.
2. **Generates** a small parametric harness — in a runtime that fits the task —
   that reproduces the *pattern* on new, different inputs without hardcoding the
   specific instance.
3. **Verifies** the harness with golden + perturbed tests.

The discipline throughout: separate the **invariant pattern** from
**instance-specific values**. The harness's variable dimensions equal exactly
what the spec marked variable — no more, no less. No hardcoded instance values.

## What's here

```
.claude-plugin/plugin.json   standalone manifest (no external deps)
SKILL.md                     the skill: 3 guarded phases + decision rules
agents/judge.md              LLM-as-judge subagent for qualitative criteria only
schemas/
  pattern-spec.schema.json   backend-neutral IR — AUTHORITATIVE for codegen
  output-contract.schema.json meta-schema notes for per-task output schemas
references/
  pattern-vs-instance.md     the central discipline, with a worked example
  eval-and-grading.md        golden+perturbed <-> evals/grading mapping
  backends/*.md              one note per backend
backends/                    pluggable codegen behind one interface (M2)
  base.py                    the Backend contract: supports/emit/emit_tests/verify
  registry.py                pick the highest-scoring backend for a spec
  hybrid_python/             the hybrid-python backend + semantic-call wrapper
scripts/
  validate.py                validates a pattern-spec against the IR
  scaffold.py                spec -> emitted harness scaffold (M2)
  verify.py                  run a harness's golden + perturbed tests + CLI (M2)
  capture.py                 documented stub (transcript ingest; later)
examples/scheduling/
  pattern-spec.json          a valid IR instance
  output.schema.json         the task's concrete output schema
harnesses/scheduling/weekly-timeline/   worked end-to-end example (M2)
tests/                       plugin test suite (validate, emit, semantic, CLI)
learnings.md                 gated, human-reviewed fix log
```

## Design notes

Built to Anthropic's skill-authoring playbook: a single-line third-person
`description` that states what + when (the dominant triggering lever);
progressive disclosure (lean `SKILL.md`, detail pushed to `references/` one
level deep); deterministic scripts for mechanical steps and instructions for
judgment; evaluation-driven verification reusing Anthropic's
`{text, passed, evidence}` grading shape.

Improvement is **human-in-the-loop**: a gated `learnings.md` accumulates
recurring fixes; there is no autonomous self-evolution (the weakest-evidence,
highest-risk pattern in the research).

## Roadmap

- **M1:** skill skeleton + authoritative schema. ✅
- **M2 (this):** backend interface + `hybrid-python`; validated end-to-end on the
  scheduling example (spec → emit → golden + perturbed). ✅ TypeScript
  (`deterministic-typescript` / a future `hybrid-typescript`) is deferred — the
  interface is stable so it slots in later without rework.
- **M3:** `agentic-claude-code` backend (agent recipe behind the same `run` CLI).

`agentic-pi` is intentionally out of scope.

## Variable vs fixed (how to read a harness)

Each task's `README.md` states which inputs are variable and which are fixed.
For the bundled scheduling example: `target_date` and `unavailable_resources`
are variable; `week_start = Monday` is fixed.

## Try it locally

```
pip install jsonschema pytest

# 1. validate a spec against the IR
python scripts/validate.py examples/scheduling/pattern-spec.json

# 2. emit a harness scaffold from a spec (step bodies + assertions are TODO stubs)
python scripts/scaffold.py --spec examples/scheduling/pattern-spec.json --out /tmp/sched

# 3. verify an emitted harness (golden + perturbed tests + the CLI contract)
python scripts/verify.py --harness harnesses/scheduling/weekly-timeline

# 4. run the whole plugin test suite
python -m pytest plugins/spec-learner
```

The committed `harnesses/scheduling/weekly-timeline/` is what step 2 produces
*after* the deterministic step bodies and structural assertions are filled in.

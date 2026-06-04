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

## What's here (Milestone 1)

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
  backends/*.md              one stub per backend
scripts/
  validate.py                functional: validates a pattern-spec against the IR
  capture.py | scaffold.py | verify.py   documented stubs (land in M2/M3)
examples/scheduling/
  pattern-spec.json          a valid IR instance proving the schema works
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

- **M1 (this):** skill skeleton + authoritative schema. ← gate for approval.
- **M2:** backend interface + `hybrid-python` and `deterministic-typescript`;
  validate end-to-end on the scheduling example (capture → spec → emit →
  golden + perturbed).
- **M3:** `agentic-claude-code` backend (agent recipe behind the same `run` CLI).

`agentic-pi` is intentionally out of scope.

## Variable vs fixed (how to read a harness)

Each task's `README.md` states which inputs are variable and which are fixed.
For the bundled scheduling example: `target_date` and `unavailable_resources`
are variable; `week_start = Monday` is fixed.

## Validate the schema locally

```
pip install jsonschema
python scripts/validate.py examples/scheduling/pattern-spec.json
```

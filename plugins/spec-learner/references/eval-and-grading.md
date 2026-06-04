# Verification: golden + perturbed, as evaluation-driven development

The brief's Phase 3 maps onto Anthropic's evaluation-driven skill development.
Reuse their JSON field names so outputs are tool-compatible.

## The two tests

- **Golden** = the with-skill eval on the *original approved input*. Every
  acceptance criterion must hold. This is the regression anchor.
- **Perturbed** (≥1) = a held-out eval on different dates / resources /
  structure. This is the generalization proof. If it fails, fix the harness or
  the spec — **never loosen the test**.

## Check routing

Each acceptance criterion in the IR is tagged `check_type`:

- `structural` → deterministic assert (field equality, ordering, length, schema
  conformance). Must hold on **both** golden and perturbed inputs. Lives in the
  backend's native runner (pytest / vitest) and in the harness's own
  non-zero-exit-on-schema-violation contract.
- `qualitative` → the judge subagent (`../agents/judge.md`), which returns a
  schema-validated `{text, passed, evidence}`.

## Grading shapes (reuse verbatim)

Per-criterion result:

```json
{ "text": "<criterion>", "passed": true, "evidence": "<=125 chars" }
```

Run record for benchmarking — use the exact configuration strings so any viewer
can read them:

```json
{ "configuration": "with_skill", "eval_id": 1, "passed": true, "duration_ms": 0, "tokens_used": 0 }
```

(`with_skill` = harness applied; `without_skill` = baseline. The golden test is
the `with_skill` run on the original input.)

## Assertion quality

A passing grade on a weak assertion is worse than useless. Verify content, not
filename existence; data accuracy, not mere presence. If an assertion would pass
for a clearly wrong output, it is not discriminating — rewrite it.

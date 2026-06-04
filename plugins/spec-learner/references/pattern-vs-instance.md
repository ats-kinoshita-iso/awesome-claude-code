# The pattern-vs-instance discipline

The whole skill rests on one separation: the **invariant pattern** vs the
**instance-specific values**. Get this wrong and the harness either hardcodes
the original result (useless on new inputs) or invents variability the user
never asked for (wrong, and untestable).

## The rule

> The harness's variable dimensions MUST equal exactly what the spec marked
> variable — no more, no less. No hardcoded instance values anywhere.

In the IR (`pattern-spec.json`), every `input_contract.fields[]` entry carries
`variability: variable | fixed`:

- **variable** → a harness input dimension. Its `example` is one sample only and
  must never be baked into the code.
- **fixed** → a constant the pattern always assumes. Its `example` *is* the
  constant and may appear in the harness.

## Worked example (scheduling)

Approved one-off: *"the schedule for the 14th, given Alice and Bob are off."*

| Phrase in the request | Pattern or instance? | In the IR |
| --- | --- | --- |
| "the 14th" | instance | input field `target_date`, `variable` |
| "Alice and Bob are off" | instance | input field `unavailable_resources`, `variable` |
| "extract temporal fields" | pattern (step) | step, `deterministic` |
| "apply resource-availability constraints" | pattern (rule) | rule + step, `deterministic` |
| "render as a weekly timeline" | pattern (output shape) | output_contract |
| "weeks start on Monday" | fixed assumption | input field `week_start`, `fixed` |

The harness therefore takes `{target_date, unavailable_resources}` as input,
treats `week_start=Monday` as a constant, and renders a weekly timeline. It must
produce a correct schedule for *any* date and *any* unavailable set — proven by
the perturbed test — without the strings "14th", "Alice", or "Bob" appearing
anywhere in the code.

## Testing the separation with a fresh instance

The strongest check (Anthropic's iterative method): have a *different* Claude
instance run the emitted harness on a perturbed input with no memory of the
original session. If it succeeds, the pattern — not the instance — was captured.
If it leaks the original instance, the spec marked too little as variable.

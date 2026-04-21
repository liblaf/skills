# Coverage Checklist

Use this checklist when deciding whether a new test set is comprehensive enough.

## Cover the Behavior Surface

- Exercise the primary success path.
- Exercise boundaries such as empty, singleton, zero, min/max, or one-off sizes when they matter.
- Exercise invalid inputs and expected exceptions.
- Exercise invariants such as round-trips, idempotence, ordering, stability, or shape preservation when relevant.
- Exercise the integration seam that is most likely to regress if the behavior depends on dispatch, serialization, filesystem I/O, environment variables, warnings, or third-party adapters.

## Choose Representative Cases

- Partition the input space into meaningful equivalence classes.
- Use one or two cases per class instead of enumerating every trivial permutation.
- Use parametrization when the assertion logic is shared.
- Add an explicit regression case for every bug fix.

## Strengthen Assertions

- Assert the observable result, not just that the call did not crash.
- Assert full structured outputs when order, keys, or field values matter.
- Assert both exception type and message fragment when the error text is contractual.
- Prefer exact assertions over loose truthiness checks.
- Justify tolerances for numeric code instead of defaulting to wide `approx` bounds.

## Common Gaps

- Covering only the happy path.
- Mirroring implementation branches without testing user-visible behavior.
- Using mocks where a lightweight real input would verify more.
- Asserting too little after a complex operation.
- Repeating near-identical tests instead of capturing the dimension with parametrization.

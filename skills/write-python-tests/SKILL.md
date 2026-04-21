---
name: write-python-tests
description: Write or refresh high-value tests for Python projects from source code truth. Use when Codex needs to add missing behavioral coverage, replace stale or misleading tests, add regression tests for bug fixes, reorganize tests under `tests/`, or lock down public Python behavior in repos that use `pytest`, `nox`, and `mise`.
---

# Write Python Tests

Use source code as the source of truth. Treat existing docs, docstrings, tests, and examples only as weak hints.

## Workflow

- Inspect the target behavior before editing tests.
- Read the relevant source files plus nearby `tests/`, `conftest.py`, `pyproject.toml`, `noxfile.py`, and `mise` tasks to learn fixtures, markers, and runner conventions.
- Prefer public entry points and observable behavior over private helpers unless the helper is itself the stable contract.
- Build a coverage plan before writing tests.
- Cover the main success path, important boundaries, invalid inputs, expected failures, and the invariants that matter for the feature.
- Add a regression test for each bug fix or previously broken behavior.
- Choose representative cases instead of brute-force enumeration.
- Use parametrization to cover equivalence classes compactly.
- Prefer one strong test per meaningful behavior family over many shallow smoke tests.
- Avoid Cartesian explosions unless the interaction itself is the behavior under test.
- Write focused tests under `tests/`.
- Group files by behavior or module and keep them small enough to scan quickly.
- Use descriptive test names that state the behavior.
- Keep fixtures local unless they are reused across multiple files.
- Assert concrete outcomes instead of only asserting that execution succeeds.
- Assert exception type and the important part of the message when the error text is part of the contract.
- Assert structure, order, and values for collections or rich result objects when those details matter.

## Comprehensiveness Heuristics

- Treat a test set as incomplete if it only covers the happy path while the source normalizes input, branches on flags or types, raises domain errors, caches state, or preserves non-trivial invariants.
- For each changed public behavior, try to cover `nominal`, `boundary`, `invalid/error`, and `regression/invariant` cases when they exist.
- Prefer behavior assertions over implementation assertions.
- Read [coverage-checklist.md](./references/coverage-checklist.md) when deciding whether a new test set is broad enough.

## Boundaries

- Files to update: `tests/`
- Prefer extensive rewrites over incremental edits when the current tests are misleading or structurally weak.
- Use `pytest` for test authoring and `nox` as the primary compatibility surface.

## Validation

- Start with the narrowest relevant `pytest` target.
- Prefer `nox` as the primary test runner for the affected environment or version matrix.
- Run `mise run lint`.
- Treat unrelated lint or environment failures as separate from the change and call them out instead of silently working around them.

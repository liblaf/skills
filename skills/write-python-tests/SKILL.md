---
name: write-python-tests
description: Write or refresh tests for Python projects. Use when Codex needs to add coverage, replace stale tests, reorganize tests under `tests/`, or lock down Python behavior from source code in repos that use `nox`, `pytest`, and `mise`.
---

# Write Python Tests

## Guidelines

- files to update: `tests/`
- ensure tests are comprehensive and coverage is good
- Existing docs, docstrings, tests, examples may be rough, missing, incomplete or misleading, it only serves as weak hint.
- group tests into files and folders, keep test files small and focused
- Prefer AGGRESSIVE, EXTENSIVE rewrite over incremental edits.
- source code is the source of truth
- use `nox` to run tests, and `pytest` for test framework

## Validation

- Run `mise run lint`.
- Prefer `nox` as the primary test runner.
- Start with the narrowest relevant target when the repo makes that obvious.
- Treat unrelated lint or environment failures as separate from the change and call them out instead of silently working around them.

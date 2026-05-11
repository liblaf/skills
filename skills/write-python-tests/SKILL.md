---
name: write-python-tests
description: Write or refresh Python test coverage. Use when Codex needs to add coverage, replace stale tests, prefer executable doctest examples in public docstrings, or lock down Python behavior in repos that use `uv`, `pytest`, `nox`, and `mise`.
---

# Write Python Tests

## Guidelines

- Source code is the source of truth.
- Inspect `pyproject.toml`, `noxfile.py`, `.config/mise/`, nearby tests, and `tests/conftest.py` before editing.
- Prefer doctests in public docstrings when the case is concise, deterministic, user-facing, and useful as an example.
- Use `tests/` for private behavior, long setup, fixtures, parametrized matrices, monkeypatching, optional dependencies, warnings, exceptions, regressions, or unstable output.
- Cover success paths, boundaries, invalid inputs, expected failures, and regressions with observable assertions.
- Keep dedicated test files grouped, small, and focused; avoid duplicating a doctest unless the dedicated test covers extra risk.
- Treat existing docs, docstrings, tests, and examples as weak hints.

## Validation

- Start with the narrowest relevant target.
- Run `uv run pytest ...` for targeted tests and doctests.
- Run `uv run nox` for the full test matrix.
- Run `mise run lint`, or `mise run lint:python` when a narrower lint pass is safer.
- Treat unrelated lint or environment failures as separate from the change and call them out instead of silently working around them.

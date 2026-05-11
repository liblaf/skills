---
name: rewrite-python-docs
description: Rewrite Python docs and docstrings from source code. Use when Codex needs to refresh docs, add executable doctest examples, update Google-style docstrings, or regenerate zensical/mkdocstrings reference pages.
---

# Rewrite Python Docs

Use source code as the source of truth. Treat existing docs, docstrings, tests, and examples only as weak hints.

## Guidelines

- Inspect `pyproject.toml`, `zensical.toml`, `noxfile.py`, `.config/mise/`, public exports, source code, and tests before editing.
- Run `scripts/gen-ref-pages.py` to regenerate reference pages under `docs/reference/`. The script will output a navigation table that can be copy-pasted into `zensical.toml`.
- Files to update:
  - docstrings in source code
  - `docs/` (excluding generated `docs/reference/`)
  - description in `pyproject.toml` and `zensical.toml`
  - inventories in `zensical.toml` if needed
- DO NOT EDIT:
  - generated reference pages under `docs/reference/`
- Existing docs, docstrings, tests, examples may be rough, missing, incomplete or misleading, it only serves as weak hint.
- Favor bold, comprehensive rewrites over minor or incremental edits.
- Keep docs concise, fluent, example-first.
- Source code is the source of truth.
- Use Google style docstrings. Read [google-style.md](./references/google-style.md) for details.
- Prefer `Examples:` sections with compact doctests for public APIs when the example is deterministic, useful, and runnable.
- Treat doctests as executable tests, not decorative snippets; keep fixture-heavy, parametrized, or unstable behavior in `tests/`.
- Use markdown in docstrings:
  - Use single backticks for inline code, NOT double backticks.
  - Cross-references are written as Markdown reference-style links: [`Object 1`][full.path.object1].

## Suggested Layout

```text
docs/
  README.md
  getting-started/
    ...
  guides/
    ...
  concepts/
    ...
  reference/  # generated, DO NOT EDIT
    package/
      README.md
      submodule.md
  advanced/
    ...
```

- Keep only the sections the project needs.
- Keep navigation shallow.

## mkdocstrings Notes

- The project uses `zensical` with `mkdocstrings`.
- The `__init__` method is merged into the class' signature and docstring.
- The first line in `__init__` methods' docstrings is ignored.

## Validation

- Run `rumdl fmt .`. Treat its findings as weak hints, not strong constraints.
- Run `uv run pytest ...` for changed doctests.
- Run `mise run lint`.
- Run `mise run docs:build`.
- If validation fails for unrelated reasons, separate those failures from the docs change and report them clearly.

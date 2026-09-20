---
name: write-conventional-commit
description: Draft one Conventional Commit message that summarizes the dominant intent of Git changes. Use when asked to write a commit message from staged changes, or from unstaged changes when nothing is staged.
---

# Write Conventional Commit

Inspect Git changes and write Conventional Commit message.

## Workflow

- Run `git status --short`.
- If there are no staged or unstaged changes, reply: `No staged or unstaged changes found.`
- Run `git diff --staged --no-ext-diff --stat`.
- Run `git diff --staged --no-ext-diff`.
- If the staged diff is empty but the working tree is dirty, use `git diff --no-ext-diff --stat` and `git diff --no-ext-diff` as a fallback.
- Infer the dominant intent from the diff and write one message only.

## Commit Types

Use exactly one type from this list:

- feat: a new feature
- fix: a bug fix
- docs: documentation only changes
- style: changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- refactor: a code change that neither fixes a bug nor adds a feature
- perf: a code change that improves performance
- test: adding missing tests or correcting existing tests
- build: changes that affect the build system or external dependencies
- ci: changes to our CI configuration files and scripts
- chore: other changes that don't modify src or test files

## Conventional Commit rules

- Choose the dominant intent. DO NOT combine types.
- DO NOT end the subject with a period.
- If the change is breaking, mark it with `!` after the type or scope and include a `BREAKING CHANGE:` footer when additional migration detail is needed.
- Keep the subject concise; aim for 50-72 characters.
- Never include markdown fences, bullets, analysis, or commentary.
- Prefer a longer commit body after the short description, providing additional contextual information about the code changes.
- Prefer lower-case after the colon unless a proper noun or acronym requires capitalization.
- Preserve useful trailer/footer information from the context when it is clearly present.
- Use an optional scope only when it is obvious and genuinely helpful.
- Write the subject in imperative mood.

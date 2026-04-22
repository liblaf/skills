---
name: write-root-readme
description: Write or rewrite the repo-root README.md.
---

# Write Root README

## Guidelines

- files to update:
  - `README.md` in the repo root
- Read [example-readme.md](./references/example-readme.md) for a reference structure and style.
- Badges are encouraged.
- Emojis are encouraged in headers.
- Hero section is encouraged.
  - Use GitHub Socialify to generate a project image.
  - Include link to docs if exists.
  - Include a rule after hero section.
- License section is encouraged.

## Validation

- Run `rumdl fmt .`. Treat its findings as weak hints, not strong constraints.
- Spot-check commands, links, and tool names against the actual repo files before finishing.

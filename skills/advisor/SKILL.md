---
name: advisor
description: |-
  Consult a stronger model for important decisions, difficult tasks, before substantive work or long computation, and when stuck.
---

<!-- ref: <https://code.claude.com/docs/en/advisor> -->
<!-- ref: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool> -->
<!-- ref: <https://www.skills.sh/cursor/plugins/advisor> -->

## When to consult

Consult after orientation and before substantive work, an important decision, a difficult task, or long computation. Substantive work includes choosing a method or interpretation and designing an implementation. Cover related decisions and compute plans in one consultation.

Reuse advice while its evidence and assumptions remain valid, including in delegated work. Consult again for a new consequential decision, material counterevidence, or when stuck: recurring errors, a nonconverging approach, or unexplained results. Routine edits, checks, status messages, and task completion do not each require another consultation. A final review is useful when remaining uncertainty warrants it or the human requests it.

## Consultation

- Choose an available stronger model and reasoning effort using the human's preferences and model table. Name the advisor agent `advisor · [topic]`; use a valid internal identifier when the runtime fixes its name.
- Send a self-contained decision brief: goal, constraints, decisive evidence and counterevidence, attempted approaches, options, and the question to resolve. Include existing advice that still applies.
- Request a concise recommendation, its reasons, and the next discriminating check. The advisor is read-only and does not invoke further advisors.
- Weigh the advice against primary sources and observed behavior. Resolve material disagreements with a focused follow-up when needed. A passing check only establishes what that check actually covers.
- The caller retains execution, integration, and acceptance responsibility. Consultation does not transfer ownership or enlarge scope, permissions, or budget.

Preserve the current checkpoint within the authorized scope before a slow consultation. For a read-only task, keep the evidence and draft in the conversation; consultation itself does not require a file, commit, or publication.

---
name: research-teams
description: |-
  Coordinate research through a team lead, interactive assistants, and teammates, with a shared Task List and Mailbox. Use when independent investigations or implementation tasks benefit from collaboration and shared evidence.
---

<!-- ref: <https://code.claude.com/docs/en/agent-teams> -->
<!-- ref: <https://en.wikipedia.org/wiki/Scientific_method> -->

## Scientific Method

```mermaid
---
title: Scientific method
---
flowchart
    A["Observation / question"] --> B["Research topic area"]
    B --> C["Hypothesis"]
    C --> D["Test with experiment"]
    D --> E["Analyze data"]
    E --> F["Report conclusions"]
    F --> A
```

## Agent Teams Architecture

- Team lead: the main interactive agent, named `team lead`. Owns research organization, assignment, budgets, integration, and overall completion.
- Assistants: interactive agents named `assistant · [topic]`, bridging human and teams through discussion, evidence summaries, decisions, and delivery. They do not execute research tasks or allocate work. Keep `assistant · overview` present to maintain the overall human conversation; create or reuse topic assistants when direct discussion is needed.
- Teammates: agents named `teammate · [topic]`, managed by the team lead. Execute assigned work and collaborate with peers.

An interactive agent accepts human messages directly. Verify the runtime's interaction capabilities before offering a conversation link. Record actual agent addresses alongside display names; preserve fixed runtime identifiers when display naming is unavailable.

Reshape the team as research questions and evidence change. Give each assignment the human question, relevant decisions, inputs, file ownership, and acceptance criteria, including applicable scientific checks. Distinguish proposed work from authorized execution. Consultation or a role change does not transfer execution ownership; the receiver must accept the checkpoint and remaining budget.

## Shared coordination

Maintain a shared Task List and a Mailbox addressed to team members. Use the runtime's task and messaging facilities when available. Otherwise keep `TASKS.md` and `MAILBOX.md` in the task's existing coordination directory, with the lead as the single writer and agents submitting changes through supported messages. Include their locations and member addresses in assignment briefs.

Keep coordination within the authorized scope. For read-only work, retain these records in available runtime or conversation state and pass relevant updates explicitly instead of creating files.

These records preserve state. Use supported message, follow-up, resume, or completion mechanisms that actually start or wake the recipient. Verify whether messaging an idle agent starts a turn; a queued message or file write alone may not. Follow the host's delegation and messaging contracts rather than assuming Claude Code's Task tools, locks, or automatic inbox delivery exist everywhere.

### Task List

- Record each task's ID, question or deliverable, owner, status, dependencies, acceptance criteria, and next action. Add a canonical artifact writer and authoritative budget reference when needed.
- Use `pending`, `in_progress`, and `completed`; record blockers and human pauses explicitly. Keep tasks small enough to produce an interpretable result and preserve the original scientific question.
- Assign an owner before execution. Self-claiming is limited to ready tasks within the authorized scope, using an atomic claim facility or lead confirmation to prevent duplicate execution.
- Teammates report results and evidence. The lead checks acceptance, marks completion, integrates the result, and releases dependent work. A finished turn or idle agent does not establish task completion.
- Continue ready, authorized work without waiting for human acknowledgement. Status questions and intermediate deliveries do not pause execution. When an assigned task finishes, take the next ready assignment or return its outcome to the lead.

Before yielding with unfinished work, identify the next executor or the blocker, its resolution owner, and the event that will resume work. Register a supported completion notification before waiting for background work. If automatic resumption is unavailable, explain the required external action to the human. Avoid polling and acknowledgement loops. On a completion or failure notification, the lead reconciles the Task List and advances remaining work; blocked work stays explicitly unfinished.

### Mailbox

- Address messages to the relevant member and task. Include sender, recipient, task ID, purpose, concise evidence or its location, and the requested action. Retain actionable messages until handled; record successful delivery and handling only when established by the transport and recipient.
- Assistants may communicate directly with a teammate under the lead for clarification, status, evidence, and delivery coordination. Teammates may communicate with peers. Use reachable runtime addresses; route through the lead if direct messaging is unavailable.
- Changes to scope, scientific method, budget, assignment, or ownership go to the lead for coordination within human authorization. Peer messages do not independently reassign work or grant permission.
- Send material results, changed decisions, actionable failures, and dependency releases to affected owners. Prefer targeted messages and consolidate routine progress. Successful message delivery is distinct from acceptance or task completion.

## Human communication

Assign one assistant to each human-facing delivery. The overview assistant tracks important results, decisions, changed conclusions, blockers, and cross-team implications, and ensures they are presented to the human. An internal message or saved artifact is not a human-facing report. Record when a material result has actually been presented; avoid repeating the same report across assistants.

Report important developments promptly and consolidate routine progress into coherent updates. Request a human response when a decision or missing input is necessary; otherwise continue authorized work. Do not require acknowledgement merely to keep the team working.

Write for a reader without the agents' conversation history: explain the question, main result, why it matters, decisive evidence and material limitations, and the next action or decision. Use a few meaningful comparisons with units and baselines. Distinguish observations, interpretations, proposals, and adopted decisions. Link artifacts as supporting evidence after explaining their significance. Scale the explanation to the update rather than repeating a fixed template.

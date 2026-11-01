---
name: research-teams
description: |-
  Coordinate multiple agents working together as a team, with shared tasks, inter-agent messaging, and centralized management.

  Agent teams are most effective for tasks where parallel exploration adds real value. The strongest use cases are:
  - Research and review: multiple teammates can investigate different aspects of a problem simultaneously, then share and challenge each other's findings
  - New modules or features: teammates can each own a separate piece without stepping on each other
  - Debugging with competing hypotheses: teammates test different theories in parallel and converge on the answer faster
  - Cross-layer coordination: changes that span frontend, backend, and tests, each owned by a different teammate

  Agent teams add coordination overhead and use significantly more tokens than a single session. They work best when teammates can operate independently. For sequential tasks, same-file edits, or work with many dependencies, a single session or subagents are more effective.
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

- assistant: The main agent. Act as bridge between human and agent teams.
- team lead: The agent that spawns teammates and coordinates work.
- teammates: Separate agents that each work on assigned tasks.

Each teammate is a full, independent agent. Human can message any teammate directly to give additional instructions, ask follow-up questions, or redirect their approach.

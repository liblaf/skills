---
name: swarm
description: Runs a team of named agents that split your task, work on the pieces at the same time, and coordinate on one shared message board. Use it when a task divides cleanly across separate files, packages, or questions, or when you want a second agent to review and test the changes before you see them.
---

<!-- ref: <https://antigravity.google/docs/swarm/> -->

# Swarm (/swarm)

## How it works

When you run `/swarm <task>`, your current conversation becomes the swarm's **coordinator**:

1. **The coordinator splits the task.** It names the swarm, divides the work into pieces that don't collide (for example, one worker per file or per package), and adds a named worker for each piece, such as `@parser`, `@api-tests`, or `@docs`. For a pool of similar workers, it can add a numbered group, such as `@fix-1` through `@fix-4`.
2. **Each worker gets a public brief.** A worker starts with a clean context in its own conversation. Its brief, which says what it owns, what it must not touch, and what “done” looks like, is posted to the board so every member can see who is doing what.
3. **A verifier checks the work.** The coordinator usually adds a `@verifier` for every two to four workers. The verifier reads the diffs, runs the tests, and reports problems to the worker that wrote the code, which then fixes them.
4. **Everyone talks on the board.** Assignments, questions between workers, diff summaries, and test results are posted to the shared board with `@name`, `@group`, or `@all` mentions. Workers don't message each other privately, so the whole team conversation stays in one place, in order.
5. **Idle members wait for free.** A worker that has nothing to do, or a coordinator waiting for reports, goes to sleep on the board without using tokens. It wakes automatically when another member mentions it.

The coordinator also adds a `@monitor` worker. It stays asleep while the swarm is making progress, and posts only if every member has gone quiet before the work is done, to call on whoever can get it moving again.

The coordinator doesn't do the technical work itself. It hands out tasks, judges what comes back, and reports to you, so it stays free to respond while the workers run.

### Worker models and workspaces

- **Models**: Workers run on the same model as your conversation. To use a different model for one worker or for all of them, say so in your prompt, for example, “run the verifier on a different model than the workers.” The model you ask for must be one you can choose in the model picker. You can also ask the coordinator to move a waiting worker to another model later; the worker keeps its conversation and continues on the new model.
- **Workspaces**: Workers share your workspace by default. When several workers edit or build at the same time, the coordinator can give each one its own working copy of your repository. Removing a worker deletes its working copy, so the coordinator has the worker land its changes first.

### Member states

Each member of a swarm is in one of these states:

| State                | Meaning                                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------------------- |
| **Active** (working) | Running a turn: thinking, running a tool, or waiting on the model.                                   |
| **Waiting**          | Asleep on the board, using no tokens until a post mentions it.                                       |
| **Killed**           | Removed from the swarm. A killed worker can't be revived; the coordinator adds a new worker instead. |

If a member runs out of quota, it pauses instead of retrying: you see the quota error once, and the member stays paused until there's a new post on the board, its model is switched, or you message it. It doesn't restart on its own when your quota refreshes.

## Choose between Swarm, Teamwork, Boost, and subagents

For everyday coding and quick questions, prompt the default agent directly. When a task benefits from multiple agents, compare Antigravity's agent orchestrators and background subagents:

|                           | Subagents                                                                                | Boost (`/boost`)                                                                                            | Swarm (`/swarm`)                                                                                            | Teamwork (`/teamwork`)                                                                                   |
| ------------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Best for**              | Delegating a focused side task, such as codebase research, browser checks, or a test run | Hard bugs, race conditions, algorithms, and tricky refactors that need deep reasoning                       | **Broad tasks that split cleanly across independent files, packages, or investigation tracks**              | Multi-milestone projects, repository-scale migrations, simulations, and deep research                    |
| **How agents coordinate** | Each subagent runs in the background and reports back to the agent that started it       | An orchestrator runs an iterative pipeline where workers implement, challenge, fix, and re-verify solutions | **A coordinator splits the task across named workers and a verifier that talk on one shared message board** | A `Sentinel` and `Project Orchestrator` run specialized roles through a milestone plan with review gates |
| **How you start**         | Automatic delegation or `@subagent` mention                                              | `/boost <task>` (starts immediately)                                                                        | **`/swarm <task>` (starts immediately)**                                                                    | `/teamwork <goal>`, followed by a scoping interview                                                      |
| **Workspace**             | Current workspace (or an isolated branch or working copy when requested)                 | Current workspace across isolated subagent contexts                                                         | **Current workspace by default, or per-worker working copies for overlapping edits**                        | Dedicated project directory (`~/teamwork_projects/{PROJECT_NAME}`) with exclusive file ownership         |
| **Verification**          | Parent agent checks the subagent's reply                                                 | Improvement workers try to break prior attempts and run real tests before the orchestrator spot-checks      | **A dedicated `@verifier` worker reviews diffs and runs tests before sign-off**                             | Independent `Critic`, `Challenger`, `Auditor`, and `Success Auditor` gates verify each milestone         |
| **Typical horizon**       | Seconds to minutes                                                                       | Seconds to hours                                                                                            | **Minutes to hours**                                                                                        | Hours to days                                                                                            |
| **Plan tier**             | All plans                                                                                | Paid plans                                                                                                  | **Google AI Pro and Ultra**                                                                                 | Paid plans                                                                                               |

Use the following guidelines to choose the right approach:

- **Use subagents for focused background delegation**: Let your agent delegate a self-contained side task—such as codebase research, browser validation, or a test run—while you keep working in the main thread.
- **Use `/boost` when the problem is hard rather than broad**: Choose `/boost` for root-cause debugging, race conditions, algorithmic optimization, or tightly coupled refactors where an initial attempt should be challenged, fixed, and verified across multiple rounds.
- **Use `/swarm` when the task is broad and divides cleanly**: Choose `/swarm` when work splits into independent pieces across separate files, packages, test suites, or research questions, and you want named workers and a verifier to coordinate on a live message board you can monitor and steer.
- **Use `/teamwork` for long-horizon, multi-milestone projects**: Choose `/teamwork` when a project spans hours or days—such as a repository-wide migration, system simulation, or formal proof—and needs an upfront scoping interview, dedicated project directory, and milestone audit gates.

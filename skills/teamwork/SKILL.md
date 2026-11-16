---
name: teamwork
description: Runs a collaborative multi-agent team designed for large software projects, complex simulations, and deep research tasks. When work spans multiple days, involves refactoring across dozens of files, or tackles open-ended math and systems challenges, Teamwork coordinates specialized agents to deliver thoroughly tested, working results.
---

<!-- ref: <https://antigravity.google/docs/teamwork/> -->

# Teamwork agent teams (/teamwork)

## Overview

Software engineering and scientific research often run into problems that are simply too large or complex for a single agent session to handle reliably:

1. **Large-scale refactoring and migrations**: Upgrading frameworks, modernizing legacy APIs, or changing dozens of files across coupled subsystems.
2. **Systems research and simulation**: Building complex systems—such as cycle-accurate CPU simulators, distributed consensus engines, or kernel subsystems—that require continuous testing against hardware oracles.
3. **Mathematical proofs and research**: Exploring theoretical proofs, deriving mathematical bounds, and running automated counterexample searches.
4. **Long-running projects without context bloat**: Breaking large tasks into modular milestones where agents coordinate through clean artifact handoffs instead of overloading a single conversation context.

Teamwork solves this by pairing specialized agents together, running independent verification checks at every milestone, and working inside isolated project directories.

## Multi-agent architecture and roles

Teamwork organizes multi-agent collaboration into clear orchestration, implementation, and verification tiers:

| Phase               | Title & Role                                                | Description                                            | Outcome                                                   |
| ------------------- | ----------------------------------------------------------- | ------------------------------------------------------ | --------------------------------------------------------- |
| **1. SCOPING**      | **🛡️ Sentinel** - Permanent Lead                            | Interviews user & agrees scope & success criteria      | **🔒 Specification Plan** - Ground-truth specification    |
| **2. COORDINATION** | **🧠 Project Orchestrator** - Self-Succession Lead          | Decomposes milestones & coordinates parallel tracks    | **📋 Project Roadmap** - Milestone roadmap & tracks       |
| **3. EXECUTION**    | **⚙️ Explorers & Workers** - Parallel Execution Tracks      | Survey codebase topology, implement code & local tests | **Parallel File Locks** - Isolated, non-overlapping diffs |
| **4. VERIFICATION** | **⚖️ Critics & Success Auditor** - Multi-Angle Verification | Independent multi-gate audit → Verified Result signoff | **🏆 SUCCESS CONFIRMED** - Verified Result                |

### Core orchestration and execution roles

The following roles handle task coordination, research, and implementation:

- **Sentinel**: The coordinator that takes over once you approve the prompt. Sentinel records your request, routes tasks, posts periodic progress updates, and spawns the [Success Auditor](#adversarial-verification-gates) before wrapping up.
- **Project Orchestrator**: A dedicated manager spawned to run the project. It breaks the approved brief into structured milestones, coordinates parallel work tracks, delegates every unit of work, and hands off to a fresh successor between milestones to prevent context degradation.
- **Explorers**: Read-only research agents that explore the repository, trace call chains from entry points, and evaluate candidate solutions without modifying any source files.
- **Workers**: Implementation agents equipped with terminal and file tools to build components, refactor code, and write unit tests in focused, non-overlapping tracks.

### Adversarial verification gates

To catch bugs early and ensure code actually works, candidate changes must pass independent verification checks before a milestone is approved:

- **Critic**: Performs independent code reviews, evaluating correctness, logical completeness, robustness, interface conformance, and adherence to project code style.
- **Challenger**: Actively stress-tests the code by building adversarial test suites, edge cases, failure-path probes, and worst-case inputs that stress runtime and memory.
- **Auditor**: Validates work against the selected integrity mode and checks test evidence against real command output, ensuring tests genuinely passed rather than being mocked or skipped.
- **Success Auditor**: The final reviewer spawned by [Sentinel](#core-orchestration-and-execution-roles). It runs a full end-to-end verification pass and must confirm everything works before [Sentinel](#core-orchestration-and-execution-roles) presents the finished project to you.

## Execution paths

Teamwork automatically adjusts team composition, verification depth, and agent roles based on the task and your prompt:

| Execution Path                           | Best For                                                                                                            | Trigger / Opt-in Signal                                                             |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **General (Distributed coding)**         | Multi-file SWE, large-scale refactoring, systems simulation, and research.                                          | _Default_ (automatically selected).                                                 |
| **Iterative coding (lighter SWE tasks)** | One self-contained change—a bug fix, a small feature, or a contained refactor. This path cannot decompose the task. | Explicit prompt signal (for example, _“keep it small”_, _“keep it focused”_).       |
| **Document Review**                      | Multi-angle critique and synthesis of papers, RFCs, and design docs.                                                | Review requests (for example, _“review this paper”_, _“critique this design doc”_). |
| **Math / Proof**                         | Mathematical problem solving, formal bounds, and theorem proving.                                                   | Math prompts (for example, _“prove theorem X”_, _“verify mathematical bounds”_).    |
| **Math / Proof (Large Team)**            | High-scale tournament networks for hard conjectures and combinatorial search.                                       | Explicit scale signal (for example, _“Use a very large team of agents”_).           |

## Two-phase workflow

To ensure alignment before writing code and avoid constant back-and-forth interruptions, Teamwork splits every project into two clear phases.

### Phase 1: prompt crafting (scoping interview)

During Phase 1, the main Antigravity agent conducts a structured interview with you. The interview follows a simple principle—**specify what, not how**:

1. **Scope and objectives**: Clarifies what you want built, its purpose (demo, production, eval, exploration), and the audience.
2. **Requirements**: Drafts several requirement blocks covering only what you actually care about.
3. **Independent verification**: Agrees on an objective check for each requirement—a test suite, reference benchmark or metric script, or an independent agent judging against an explicit rubric.
4. **Acceptance criteria**: Defines clear, testable criteria for considering the project complete.
5. **Project working directory**: Establishes a dedicated workspace folder, defaulting to `~/teamwork_projects/{PROJECT_NAME}`.

At the end of Phase 1, the main Antigravity agent creates a reviewable **prompt artifact**. You can review the prompt, adjust details, and approve execution with a single confirmation.

### Phase 2: autonomous execution (structured handoffs)

Once approved, [Sentinel](#core-orchestration-and-execution-roles) hands off the project to the [Project Orchestrator](#core-orchestration-and-execution-roles), which coordinates the team autonomously without needing step-by-step prompts.

Agents coordinate and share progress using structured artifacts in the workspace:

- **Request artifact**: Captures your initial prompt, goals, constraints, and testable acceptance criteria.
- **Project plan artifact**: Tracks the milestone roadmap, active workstreams, and dependency flow.
- **Progress artifact**: Records live milestone status and completed tracks.

## Integrity modes

Teamwork uses three internal integrity modes to align verification depth with project requirements. During the Phase 1 interview, your agent asks which shortcuts should be off-limits and maps your answers to a mode, which is recorded in the prompt artifact:

| Mode          | Purpose                   | Verification Behavior                                                                                                                                                |
| ------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `development` | Rapid iteration           | Lenient. Flags only fabricated outputs and facade implementations; code reuse, libraries, and pre-built frameworks are all permitted. (Default.)                     |
| `demo`        | Reproducible presentation | Moderate. Adds: no copying core logic from open source, no delegating core work to external tools, and no reading test source to reverse-engineer expected behavior. |
| `benchmark`   | Thorough evaluation       | Maximum strictness. Fully independent, from-scratch implementation; language standard library only.                                                                  |

For example, if you rule out all four shortcuts, the run uses `benchmark` mode, and the [Auditor](#adversarial-verification-gates) enforces strict verification rules: disallowing mocked test passes and validating ground-truth evaluations against real system execution.

## Safety, workspaces, and isolation

Teamwork includes built-in safeguards to ensure parallel agent work remains safe, predictable, and easy to audit:

- **Dedicated project working directories**: All operations run inside dedicated workspace folders (defaulting to `~/teamwork_projects/{PROJECT_NAME}`), keeping your main repository clean and avoiding unintended side effects.
- **Exclusive file ownership**: To prevent merge conflicts and race conditions, the [Project Orchestrator](#core-orchestration-and-execution-roles) assigns specific files to individual [Workers](#core-orchestration-and-execution-roles). Multiple workers never edit the same file at the same time.
- **Per-agent scratch directories**: Each subagent has its own working directory and writes its helper scripts, notes, and logs there rather than in the project root.
- **Structured state and artifact handoffs**: Every state change, command run, review comment, and verification log is recorded in the project plan and progress artifacts, alongside conversation logs. You can monitor live progress across agent tracks in the UI subagent panel or CLI status bar.
- **Autonomous execution with guardrails**: Once you approve the initial prompt, the team works through milestones autonomously, with the [Auditor](#adversarial-verification-gates) and [Success Auditor](#adversarial-verification-gates) verifying results before final handoff.

## When to use /teamwork

For everyday coding and quick questions, prompt the default agent directly. When a task benefits from multiple agents, compare Antigravity's agent orchestrators and background subagents:

|                           | Subagents                                                                                | Boost (`/boost`)                                                                                            | Swarm (`/swarm`)                                                                                        | Teamwork (`/teamwork`)                                                                                       |
| ------------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Best for**              | Delegating a focused side task, such as codebase research, browser checks, or a test run | Hard bugs, race conditions, algorithms, and tricky refactors that need deep reasoning                       | Broad tasks that split cleanly across independent files, packages, or investigation tracks              | **Multi-milestone projects, repository-scale migrations, simulations, and deep research**                    |
| **How agents coordinate** | Each subagent runs in the background and reports back to the agent that started it       | An orchestrator runs an iterative pipeline where workers implement, challenge, fix, and re-verify solutions | A coordinator splits the task across named workers and a verifier that talk on one shared message board | **A `Sentinel` and `Project Orchestrator` run specialized roles through a milestone plan with review gates** |
| **How you start**         | Automatic delegation or `@subagent` mention                                              | `/boost <task>` (starts immediately)                                                                        | `/swarm <task>` (starts immediately)                                                                    | **`/teamwork <goal>`, followed by a scoping interview**                                                      |
| **Workspace**             | Current workspace (or an isolated branch or working copy when requested)                 | Current workspace across isolated subagent contexts                                                         | Current workspace by default, or per-worker working copies for overlapping edits                        | **Dedicated project directory (`~/teamwork_projects/{PROJECT_NAME}`) with exclusive file ownership**         |
| **Verification**          | Parent agent checks the subagent's reply                                                 | Improvement workers try to break prior attempts and run real tests before the orchestrator spot-checks      | A dedicated `@verifier` worker reviews diffs and runs tests before sign-off                             | **Independent `Critic`, `Challenger`, `Auditor`, and `Success Auditor` gates verify each milestone**         |
| **Typical horizon**       | Seconds to minutes                                                                       | Seconds to hours                                                                                            | Minutes to hours                                                                                        | **Hours to days**                                                                                            |
| **Plan tier**             | All plans                                                                                | Paid plans                                                                                                  | Google AI Pro and Ultra                                                                                 | **Paid plans**                                                                                               |

Use the following guidelines to choose the right approach:

- **Use `/teamwork` for long-horizon, multi-milestone projects**: Choose `/teamwork` when a project spans hours or days—such as a repository-wide migration, system simulation, or formal proof—and needs an upfront scoping interview, dedicated project directory, and milestone audit gates.
- **Use `/swarm` when the task is broad and divides cleanly**: Choose `/swarm` when work splits into independent pieces across separate files, packages, test suites, or research questions, and you want named workers and a verifier to coordinate immediately on a live message board you can monitor and steer.
- **Use `/boost` when the problem is hard rather than broad**: Choose `/boost` for root-cause debugging, race conditions, algorithmic optimization, or tightly coupled refactors where an initial attempt should be challenged, fixed, and verified across multiple rounds.
- **Use subagents for focused background delegation**: Let your agent delegate a self-contained side task—such as codebase research, browser validation, or a test run—while you keep working in the main thread.

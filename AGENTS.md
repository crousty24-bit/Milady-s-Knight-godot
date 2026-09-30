# AGENTS.md

## Purpose and context routing

Durable agent rules for **Milady's Knight**. Load context according to the task, without routinely rereading every document.

- The active run in [runs-workflow.md](runs-workflow.md) defines scope, dependencies and acceptance criteria; that file also owns the run lifecycle.
- Consult [brief.md](brief.md) when global context or the verified project summary is needed.
- Use [docs/](docs/README.md) for specifications of the systems actually affected. Product details belong there.
- Use [runs-journal.md](runs-journal.md) for execution evidence and relevant history; [learning.md](learning.md) explains verified implementation to the human.

Documentation describes intent. Inspect the actual files, references and Git state before changing an existing system; the repository proves what exists.

## Scope and autonomy

- Stay within the active run or explicitly requested task. Prefer small complementary changes and valid existing patterns; do not invent undefined gameplay rules or add speculative features or architecture.
- Complete authorized local work, including relevant checks and corrections, without asking permission at each step. Ask only for a missing decision that materially affects the result or an authorization boundary; continue independent work meanwhile.
- Verification must match the risk, change type and scope, and exercise actual behavior for gameplay, collisions, UI, persistence and interactions. Never report an unexecuted test as successful or mark a run `DONE` with a mandatory test outstanding. See the lifecycle and verification guidance in `runs-workflow.md`.

## Model Routing and Cost Control

The user-level Codex technical configuration remains the source of truth for available models and execution settings.
Do not add or modify a repository-level .codex/config.toml for the model, reasoning effort, sandbox, or approval settings unless explicitly requested.

For run execution, the intended Codex main agent is **GPT-6 Sol Medium**. It orchestrates the run and primarily owns planning, coordination, review, debugging, analysis and code implementation. If the available configuration differs, report the mismatch rather than claiming a model switch occurred.

Codex subagents default to **GPT-6 Luna**, with Low, Medium or High reasoning according to the task: Low for bounded mechanical inspection, inventory and documentation; Medium for well-scoped implementation or verification requiring some system understanding; High for a difficult bounded investigation. Use Sol Medium/High for subwork that exceeds Luna's scope; reserve Astra Medium for exceptional architecture or complex audits that Sol cannot resolve satisfactorily. Escalate only after narrowing the context and the task. Routine asset file operations remain suitable for Luna or Sol.

Claude Code complements Codex. Its intended main agent is **Opus 5.5**, primarily reserved for visual coherence, art direction, asset generation, analysis, selection and adaptation, spritesheets and visually sensitive Godot integration. Its subagents default to **Sonnet 5.5**, with Low to High reasoning according to complexity. Codex owns the nonvisual engineering work by default. A visual task can include the minimum technical integration needed to validate its result; agree on file ownership before either agent edits a shared scene or resource. See [CLAUDE.md](CLAUDE.md) for Claude-specific instructions.

Codex and Claude may work simultaneously in two chats on distinct, explicitly scoped parts of the same authorized run. Assign each chat separate files or isolated worktrees, share interface and asset contracts, and hand off results explicitly. Do not give both chats the same edit or verification responsibility, or let parallel work start another run while one is ACTIVE.

Before increasing the model tier or reasoning effort:

1. reduce the context to the files actually required;
2. verify that the run is not too broad;
3. prefer targeted delegation over escalating the entire task.

## Human changes and safety

- The repository at the start of a run is the new baseline. Identify human changes, preserve them by default, adapt around them and record relevant consequences.
- Change human work only when explicitly requested or when a concrete bug, conflict or performance problem is demonstrated within scope. Never restore a previous run's state merely because it differs; when uncertain, preserve it. This also applies to authored levels and their generators.
- Check references before deleting files or assets. Preserve source assets and licensing/attribution; normalized derivatives must not replace originals.

## Tools and skills

- Choose the most direct, reliable tool. Inspect files and use commands when sufficient; run Godot when runtime behavior needs checking. Use Computer Use when editor state, rendering or GUI interaction requires it, not for every Godot task.
- Use a specialized skill when requested or when it adds a capability useful to the task. Prefer direct tools otherwise; avoid stacking skills for simple work. Route to relevant repository skills when available without requiring a fixed inventory.

## External assets

- When a run involves sourcing, evaluating, adapting, or integrating external assets, consult .local/asset-paths.md if present, then the relevant asset requirements/library documentation. Do not scan external asset libraries for unrelated runs.
- External asset directories are source libraries, not project working directories. Astra may inspect and copy assets from them, but must not reorganize, rename, edit, delete, or otherwise modify their contents unless explicitly instructed. Assets selected for use in the game must follow the project asset pipeline: original/source asset → adaptation or processing → normalized game asset → Godot integration.

## Delegation

- At the start of each run and whenever a separable task appears, delegate as soon as it is useful for the task and its complexity. Examples: separate system inspections, focused research, regression review, asset/licence analysis, documentation or investigation alongside implementation. Keep a trivial or tightly sequential action with the main agent when delegation would add coordination without useful work.
- Each main agent may have **at most four active subagents**. This is a ceiling, not a target; spawn only independent work that can proceed safely in parallel. Use a matching project custom agent when its definition is available: Codex profiles in `.codex/agents/` are `mechanical_worker` (inventory and simple edits), `code_worker` (scoped implementation) and `architecture_reviewer` (complex audit); Claude profiles in `.claude/agents/` are `visual_architect` (artistic judgment) and `asset_integrator` (concrete asset pipeline). Use an ordinary subagent for bounded work outside those roles.
- When ownership, custom-agent fit or reasoning level is ambiguous, consult the [Jev task router](tools/jev/task_router/README.md) if it is available. Its ranked suggestion is advisory and never starts an agent; check the actual task, candidate model availability and file ownership before delegating. If Jev is unavailable, use the routing rules here directly.
- Define each subagent's task, model/reasoning choice, files it may edit and expected result. Avoid concurrent edits to the same script, `.tscn`, `.tres`, resource or tightly coupled systems; prefer read-only subtasks when ownership overlaps.
- Subagents must not expand scope. The root agent owns integration, conflict resolution, final verification and run coherence.

## Git boundaries

- Local commits are authorized at coherent, verified checkpoints within scope, without a fixed count or cadence. Inspect Git status, diffs and staged content; stage deliberately and never inadvertently include human or unrelated changes.
- Push and PR creation require explicit authorization for the run or session. Prepare the concrete, verified result before requesting approval; do not ask again for an action already authorized.
- Force-push, history rewriting, resetting human changes and other destructive Git operations require explicit permission.

## Git branch workflow
- Development work must be performed on dedicated feature/* branches created from develop. A feature branch may cover one run or a small group of tightly related runs when they form a coherent unit of work. Do not create one branch per run mechanically.
- Completed work is proposed through a pull request into develop. main represents validated milestone versions and must not receive direct development commits.
- Do not merge, push, or create a pull request without the required human validation defined by the workflow.


## Documentation and completion

Update brief/specifications only for meaningful state, behavior, architecture or durable decision changes. Execution evidence belongs in `runs-journal.md`; after each run, `learning.md` explains the work actually implemented and verified in beginner-friendly terms. Do not invent learning content for unimplemented systems.

Use the closure criteria in [runs-workflow.md](runs-workflow.md#cycle-de-vie), including any explicitly required human validation. Do not stop at an unverified first implementation or start an unauthorized next run.

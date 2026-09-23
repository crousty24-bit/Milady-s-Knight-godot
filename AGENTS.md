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

The user-level Codex technical configuration remains the source of truth.
Do not add or modify a repository-level .codex/config.toml for the model, reasoning effort, sandbox, or approval settings unless explicitly requested.

For run execution:

- use the configured default main model for normal implementation work;
- delegate bounded and mechanical tasks to Luna Low by default: targeted inspection, reference lookup, inventories, documentation, journaling, and small    well-specified modifications;
- keep Sol Medium for normal implementation work requiring system understanding and coordinated changes;
- use Sol High only for complex debugging, interactions across multiple systems, or when Medium reasoning has proven insufficient;
- use Astra Medium for major architecture decisions, cross-cutting planning, complex audits, or problems that Sol did not resolve satisfactorily;
- also prefer Astra Medium for visually sensitive game-development workflows that require significant visual or spatial judgment, such as evaluating art references, generating or adapting visual assets, translating concept art into game-ready assets, integrating visually complex assets into Godot, or validating visual results directly in the running game;
- do not escalate routine asset operations to Astra when the expected result is already well specified: file organization, renaming, metadata, straightforward imports, known spritesheet slicing, simple resource wiring, and documentation should remain delegated to Luna or Sol as appropriate;
- Astra High or higher should remain exceptional; do not automatically select XHigh, Max, or Pro.

Before increasing the model tier or reasoning effort:

1. reduce the context to the files actually required;
2. verify that the run is not too broad;
3. prefer targeted delegation over escalating the entire task.

Parallelism is a ceiling, not a target: create multiple subagents only for tasks that are genuinely independent.

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

- Delegate bounded, independent work when useful parallelism outweighs coordination: separate system inspections, focused research, regression review, asset/licence analysis or investigation alongside implementation.
- Define each subagent's scope and expected result. Avoid trivial delegation and concurrent edits to the same script, `.tscn`, `.tres`, resource or tightly coupled systems; prefer read-only subtasks when ownership overlaps.
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

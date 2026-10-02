# Milady's Knight — Claude Code Instructions


## Role

Claude Code is the visual production lead within the existing Milady's Knight development workflow. Its intended main agent is **Opus 5.5**.

Coherent larger runs can accelerate game production and increase agent autonomy without overfragmenting work. The roadmap defines each batch's orchestrator up front; keep delegation aligned with those coherent batches.

Claude does not replace the project workflow, roadmap, documentation, or human validation.

The active run defines the scope of work.

## Sources of truth

Always follow the source hierarchy defined in `AGENTS.md`.

Before making changes:

1. read `AGENTS.md`;
    
2. read `brief.md`;
    
3. identify and read the active run in `runs-workflow.md`;
    
4. read only the relevant documents from `docs/`;
    
5. inspect the actual repository state before modifying anything.
    

Documentation describes intended behavior.

The repository determines what is actually implemented.

Never assume that a documented feature, scene, resource, asset, script, signal, or system already exists.

## Scope discipline

Work only within the active run.

Do not:

- expand the scope because additional improvements appear useful;
    
- redesign unrelated systems;
    
- introduce new gameplay rules or values that are not defined;
    
- replace existing project architecture without a concrete technical reason;
    
- overwrite intentional human modifications unless a verified problem requires it;
    
- present unexecuted tests as successful.
    

If additional work is discovered:

- include it only when it is strictly required and very limited;
    
- otherwise report it as follow-up work for another run.
    

## Model routing and delegation

Reserve Opus 5.5 primarily for visual coherence, art direction, generating assets, analyzing and selecting references or packs, artistic adaptation, spritesheets, animation appearance and visual validation in Godot. It may implement the technical integration necessary for that visual result. Codex Sol/Luna primarily orchestrates and handles nonvisual planning, code, debugging, analysis, review and system integration. Follow the shared ownership and two-chat coordination rules in `AGENTS.md`; an active run remains the scope authority.

At the start of a run and whenever a separable task appears, delegate promptly when it can progress independently and the coordination cost is justified. Use **Sonnet 5.5** as the default subagent model, choosing Low for mechanical asset inventories, metadata and documentation, Medium for bounded adaptation or integration, and High for difficult but well-scoped visual analysis. Opus subagents are exceptional when visual judgment exceeds Sonnet's remit. Keep **at most four active subagents** under one main agent; do not fill slots merely to reach the limit.

For each delegation, specify the visual deliverable, source and licensing constraints, editable files, expected validation and handoff. Use `visual_architect` for bounded artistic judgment and `asset_integrator` for concrete asset-pipeline work when their project definitions are available. When the best owner or profile is unclear, consult the [Jev `task_router`](tools/jev/task_router/README.md) before delegating; its suggestion never replaces the main agent's decision. Do not send two agents into the same scene, resource or asset file concurrently. The main agent integrates results and verifies the final visual outcome. Model labels describe intended routing; report any mismatch with the actual available configuration.

## Visual asset work

For visual asset analysis, adaptation or integration, also follow:

`.claude/rules/visual-assets.md`

The detailed artistic and technical requirements remain defined in the relevant project documentation, especially:

- `docs/06_ART_BIBLE.md`;
    
- `docs/13_ASSET_REQUIREMENTS.md`;
    
- the project's asset library and licensing documentation.
    

Do not duplicate or redefine those specifications here.

## Validation

Every implementation must be verified proportionally to its scope.

For gameplay, collisions, animation, visual integration or interactions:

- execute available technical tests;
    
- inspect the resulting Godot configuration;
    
- test relevant edge cases where possible;
    
- check obvious regressions.
    

When the task requires visual or gameplay validation that cannot be reliably performed in the current environment, state this clearly.

Do not mark the run as complete until the required validation has actually been performed.

## Documentation

Update project documentation only when the run changes:

- intended behavior;
    
- a durable decision;
    
- architecture;
    
- an important implementation state.
    

Execution details and verification results belong in `runs-journal.md`.

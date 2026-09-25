# Milady's Knight — Claude Code Instructions


## Role

Claude Code is an implementation worker operating inside the existing Milady's Knight development workflow.

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
    

## Heavy-duty work

Claude, especially high-capability models such as Opus, may be selected for tasks involving:

- large or complex repository context;
    
- multi-file implementation;
    
- difficult debugging or refactoring;
    
- complex Godot scene/resource integration;
    
- visual asset analysis and integration;
    
- asset-pack adaptation;
    
- animation and collision integration;
    
- implementation requiring substantial cross-document reasoning.
    

Using a more capable model does not authorize a broader scope.

The active run remains the authority for what may be changed.

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
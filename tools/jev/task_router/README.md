# Jev task router

`route.py` advises the main agent on **one bounded task** in an `ACTIVE` run. It
suggests a Codex or Claude owner, an installed custom agent or ordinary subagent,
and a model and reasoning level. It never starts an agent, changes a run state or
grants file ownership. The main agent remains responsible for those decisions.

## Run

Use the existing TypeSafe environment described in
[`../run_completion_reviewer/README.md`](../run_completion_reviewer/README.md).
From the repository root, prepare a JSON file matching [`example.json`](example.json)
with real, nonsecret task data, then run:

```bash
source .local/typesafe.env
.local/typesafe-venv/bin/python tools/jev/task_router/route.py path/to/task.json
```

`visual_judgment` routes work requiring artistic judgment to Claude; ordinary
engineering and mechanical asset operations route to Codex. List only models
actually available in the current environment. `affected_files` and
`concurrent_edit_files` use repository-relative paths and must not overlap.
`active_subagents` counts active children of this main agent and cannot exceed
four. The tool checks the custom-agent definition files before offering them.

The response contains the selected handler, all candidates ranked by Jev Choice
probability, and a separate Noul probability for whether delegation is useful.
These values are uncalibrated. Review the original task, ownership and model
availability before spawning. For invalid input, a full subagent roster or a
service failure, resolve the stated condition and use `AGENTS.md` directly. No
secrets or asset content should be put in the JSON input.

The candidate catalog corresponds to the five project custom agents:
`mechanical_worker`, `code_worker`, and `architecture_reviewer` in
`.codex/agents/`; `visual_architect` and `asset_integrator` in
`.claude/agents/`. The router checks that each definition exists and that its
model appears in `available_models`. If no specialist fits, it can suggest an
ordinary subagent or the main agent.

The completion reviewer is separate: it reviews run evidence before `DONE` and
does not use these routing probabilities.

## Initial evaluation (30 September 2026)

The CLI was called with `jev-1.13.0` on task summaries drawn from the project
journal, with an `ACTIVE` snapshot and all five models declared available.
Its top Choice matched the intended specialist in these exploratory cases:

| Project task | Top candidate | Choice confidence |
| --- | --- | ---: |
| RUN-002 source-media inventory | `mechanical_worker` | 0.89 |
| RUN-003 sprite-scale comparison | `visual_architect` | 0.97 |
| RUN-007 sword timing and facing fix | `code_worker` | 0.95 |
| RUN-007 protection interaction audit | `architecture_reviewer` | 0.84 |
| Known-layout spritesheet integration example | `asset_integrator` | 0.90 |

The separate delegation-usefulness probabilities varied from 0.38 to 0.58 on
the four journal-derived tasks. They are not calibrated action thresholds and
do not imply those historical tasks actually used these agents. This small
evaluation checks plausible routing and live API wiring; keep reviewing real
task outcomes before treating the probabilities as an automation policy.

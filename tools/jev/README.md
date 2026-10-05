# Jev tools

Project tooling that calls TypeSafe's Jev model lives here. Each dedicated tool has
its own subdirectory; the run-completion review is in
[`run_completion_reviewer/`](run_completion_reviewer/README.md).

The tools use the official Python SDK. The run reviewer returns three independent
yes probabilities and one three-option completion judgment. Every judgment is
advisory; workflow closure remains a human decision based on actual evidence.
Its local virtual environment and
the API key stay under `.local/`, outside Git. See each tool's README for setup and
usage.

## Task-routing advisor

[`task_router/`](task_router/README.md) contains a separate advisory CLI for an
`ACTIVE` run task. Deterministic checks enforce run state, file ownership,
available models and the four-subagent ceiling before Jev compares the eligible
custom agents with an ordinary subagent and the main agent. The response includes
the ranked Choice probabilities and a separate delegation-usefulness Noul. The
main agent reviews the task, chooses whether to delegate, and owns integration
and verification. The tool never spawns an agent or changes run state.

The completion reviewer remains a separate end-of-run check. Do not use task
routing probabilities as evidence that a run is ready for `DONE`.

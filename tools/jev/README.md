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

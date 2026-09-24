# Run Completion Reviewer

This local CLI asks Jev to check whether written evidence supports the completion
claims supplied for a Milady's Knight run. It is an advisory check before
`DONE`; it does not run Godot checks, inspect the truth of test logs, edit run
statuses, or replace human validation.

## Install

From the repository root, with Python 3.10 or newer:

```bash
python3 -m venv .local/typesafe-venv
.local/typesafe-venv/bin/python -m pip install -r tools/jev/run_completion_reviewer/requirements.txt
```

Load the key in the same shell that runs the reviewer:

```bash
source .local/typesafe.env
```

The key file must stay local and untracked. Do not put the key in the JSON input,
the project, Godot, command arguments, or output logs.

## Review

Copy `example.json`, replace every example claim with evidence for one run, then
run:

```bash
.local/typesafe-venv/bin/python tools/jev/run_completion_reviewer/review.py path/to/run-review.json
```

The input is evidence supplied by the caller. It must include the actual
acceptance criteria, mandatory checks, relevant bugtest and regression results,
journal and learning status, human validation requirement/result, and open
blockers. Acceptance criteria and required checks must be `passed`. A bugtest or
regression may be `not_applicable` only with a reason. Journal and learning must
be `passed` when their required updates are complete. The tool does not read raw
test artifacts automatically; cite their location and summarize the observed
result.

Deterministic gates stop the API request if any required item is missing,
pending, failed, or lacks evidence, if a blocker remains, or if the proposed
status is not `VERIFY`. When those gates pass, independent Noul questions are
sent in one Jev request for the evidence items. The JSON output includes each
probability and the token usage. Human validation remains a hard workflow gate
and is not decided by Jev. The example is intentionally pending, so running it
unchanged stops before making an API request.

Jev probabilities are evidence-alignment signals, not proof that a test really
ran. Interpret low or ambiguous results with the original evidence; no decision
threshold has been calibrated yet. Even a high result only means the supplied
text appears to support the claim; it never authorizes `DONE`. Keep the
project's mandatory checks and required human decisions as hard gates. Evaluate
the questions on French run records before relying on them; Jev currently
documents stronger accuracy for English.

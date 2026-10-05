#!/usr/bin/env python3
"""Request an advisory Jev review of a run's written completion evidence."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from typesafe_sdk import Choice, Noul, TypeSafeClient
except ImportError:  # pragma: no cover - user-facing setup error
    Choice = Noul = TypeSafeClient = None  # type: ignore[assignment,misc]


ALLOWED_ITEM_STATUSES = {"passed", "not_applicable"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(payload: Any) -> tuple[list[dict[str, str]], list[str]]:
    """Return reviewable evidence items and deterministic completion blockers."""
    blockers: list[str] = []
    evidence_items: list[dict[str, str]] = []

    if not isinstance(payload, dict):
        return [], ["Input must be a JSON object."]

    run_id = payload.get("run_id")
    if not _nonempty(run_id):
        blockers.append("run_id is missing.")

    if payload.get("proposed_status") != "VERIFY":
        blockers.append("proposed_status must be VERIFY before completion review.")

    def collect_items(
        field: str, label: str, *, required: bool, allowed_statuses: set[str]
    ) -> None:
        rows = payload.get(field)
        if not isinstance(rows, list) or (required and not rows):
            blockers.append(f"{field} must contain at least one evidence item." if required else f"{field} must be a list.")
            return
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict):
                blockers.append(f"{field}[{index}] must be an object.")
                continue
            item_id = row.get("id", f"{field}-{index}")
            description = row.get("description")
            status = row.get("status")
            evidence = row.get("evidence")
            name = f"{label} {item_id}"
            if not _nonempty(description):
                blockers.append(f"{name}: description is missing.")
            if not isinstance(status, str) or status not in allowed_statuses:
                blockers.append(f"{name}: status must be one of {sorted(allowed_statuses)}; got {status!r}.")
            if not _nonempty(evidence):
                blockers.append(f"{name}: evidence or an N/A reason is missing.")
            if _nonempty(description) and isinstance(status, str) and status in allowed_statuses and _nonempty(evidence):
                evidence_items.append({
                    "id": f"{field}_{index}",
                    "label": name,
                    "description": description.strip(),
                    "status": status,
                    "evidence": evidence.strip(),
                })

    collect_items("acceptance_criteria", "Acceptance criterion", required=True, allowed_statuses={"passed"})
    collect_items("required_checks", "Required check", required=True, allowed_statuses={"passed"})
    collect_items(
        "regressions", "Regression", required=False, allowed_statuses=ALLOWED_ITEM_STATUSES
    )

    bugtest = payload.get("bugtest")
    if not isinstance(bugtest, dict):
        blockers.append("bugtest must describe the run's bugtest result.")
    else:
        collect_items_from_object(bugtest, "Bugtest", evidence_items, blockers)

    for field, label in (("journal", "Journal"), ("learning", "Learning")):
        item = payload.get(field)
        if not isinstance(item, dict):
            blockers.append(f"{field} must describe its update status and evidence.")
        else:
            collect_items_from_object(
                item, label, evidence_items, blockers, allowed_statuses={"passed"}
            )

    human = payload.get("human_validation")
    if not isinstance(human, dict) or not isinstance(human.get("required"), bool):
        blockers.append("human_validation must state whether validation is required.")
    elif human["required"]:
        collect_items_from_object(
            human,
            "Required human validation",
            evidence_items,
            blockers,
            review_with_jev=False,
            allowed_statuses={"passed"},
        )
    elif human.get("status") == "not_required" and _nonempty(human.get("evidence")):
        pass
    else:
        blockers.append("When human validation is not required, status must be not_required with a reason.")

    open_blockers = payload.get("open_blockers")
    if not isinstance(open_blockers, list):
        blockers.append("open_blockers must be a list.")
    elif open_blockers:
        blockers.extend(f"Open blocker: {str(blocker)}" for blocker in open_blockers)

    return evidence_items, blockers


def collect_items_from_object(
    row: dict[str, Any],
    label: str,
    evidence_items: list[dict[str, str]],
    blockers: list[str],
    *,
    review_with_jev: bool = True,
    allowed_statuses: set[str] = ALLOWED_ITEM_STATUSES,
) -> None:
    status = row.get("status")
    evidence = row.get("evidence")
    if not isinstance(status, str) or status not in allowed_statuses:
        blockers.append(f"{label}: status must be one of {sorted(allowed_statuses)}; got {status!r}.")
    if not _nonempty(evidence):
        blockers.append(f"{label}: evidence or an N/A reason is missing.")
    description = row.get("description", label)
    if not _nonempty(description):
        blockers.append(f"{label}: description must be a non-empty string when supplied.")
    if (
        review_with_jev
        and isinstance(status, str) and status in allowed_statuses
        and _nonempty(evidence)
        and _nonempty(description)
    ):
        evidence_items.append({
            "id": label.lower().replace(" ", "_"),
            "label": label,
            "description": description.strip(),
            "status": status,
            "evidence": evidence.strip(),
        })


def review(payload: dict[str, Any]) -> dict[str, Any]:
    if TypeSafeClient is None or Noul is None or Choice is None:
        raise RuntimeError("TypeSafe SDK is missing; install tools/jev/run_completion_reviewer/requirements.txt.")
    if not os.environ.get("TYPESAFE_API_KEY"):
        raise RuntimeError("TYPESAFE_API_KEY is not set in this shell.")

    state = {
        "run_id": payload["run_id"],
        "acceptance_criteria": payload["acceptance_criteria"],
        "required_checks": payload["required_checks"],
        "bugtest": payload["bugtest"],
        "regressions": payload["regressions"],
        "journal": payload["journal"],
        "learning": payload["learning"],
        "human_validation": payload["human_validation"],
        "open_blockers": payload["open_blockers"],
        "review_scope": (
            "Evaluate only the supplied written claims and evidence. The Python precheck already verifies "
            "declared statuses and explicit blockers. Neither Jev nor this dossier proves that tests actually ran. "
            "A Jev result never changes the run status or replaces required human validation."
        ),
    }
    questions = {
        "acceptance_criteria_coverage": Noul(instructions=(
            "Do the written results and evidence in `acceptance_criteria` sufficiently cover every declared "
            "acceptance criterion for this run? Judge textual coherence and coverage only, not whether tests ran. "
            "Answer no for vague, absent, or contradictory support."
        )),
        "required_verification_complete": Noul(instructions=(
            "Do the written evidence in `required_checks`, `bugtest`, and `regressions` indicate that every "
            "mandatory verification was completed successfully? Look for unexecuted tests, unresolved failures, "
            "incomplete bugtests, unchecked regressions, and missing controls. Judge the text, not actual execution."
        )),
        "blocking_issue_present": Noul(instructions=(
            "Do the supplied evidence or limitations indicate an unresolved issue that reasonably prevents "
            "closure? Consider unvalidated behavior, known defects, scope conflicts, pending human validation, "
            "and contradictions needing inspection. Answer yes when such an issue is indicated."
        )),
        "completion_status": Choice(
            instructions=(
                "Which advisory completion status best fits the entire written dossier? Judge its coherence "
                "and limitations. If text explicitly reports an unresolved failed mandatory check, choose BLOCKED "
                "even when its declared status says passed. This is never the official workflow status."
            ),
            criteria={
                "READY_FOR_DONE": "The text coherently supports proposing the run for human closure review; no obvious issue is visible.",
                "VERIFY": "The text is insufficient or ambiguous, without a concrete unresolved failure established.",
                "BLOCKED": "The text establishes a concrete unresolved issue or failed mandatory check incompatible with closure.",
            },
        ),
    }

    with TypeSafeClient() as client:
        response = client.system_one(model="jev-latest", state=state, questions=questions)

    nouls = {name: response.answers[name].noul for name in (
        "acceptance_criteria_coverage", "required_verification_complete", "blocking_issue_present"
    )}
    status = response.answers["completion_status"]
    return {
        "run_id": payload["run_id"],
        "model": response.model,
        "decisions": {
            **{name: {"probability_yes": probability} for name, probability in nouls.items()},
            "completion_status": {
                "choice": status.choice,
                "confidence": status.confidence,
                "probabilities": status.probabilities,
            },
        },
        "final_workflow_action": "HUMAN_REVIEW_REQUIRED",
        "note": "Uncalibrated probabilities are advisory; inspect original evidence. Jev never authorizes DONE.",
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


def format_review(result: dict[str, Any]) -> str:
    decisions = result["decisions"]
    labels = (
        ("acceptance_criteria_coverage", "Acceptance criteria coverage"),
        ("required_verification_complete", "Required verification complete"),
        ("blocking_issue_present", "Blocking issue present"),
    )
    lines = ["JEV RUN COMPLETION REVIEW", result["run_id"], ""]
    for key, label in labels:
        lines.extend((label, f"probability of yes: {decisions[key]['probability_yes']:.3f}", ""))
    status = decisions["completion_status"]
    lines.extend((
        "Completion status", status["choice"], f"confidence: {status['confidence']:.3f}",
        "option probabilities: " + ", ".join(
            f"{key}={value:.3f}" for key, value in status["probabilities"].items()
        ), "", "Final workflow action", "HUMAN REVIEW REQUIRED", "",
        "Jev judged written evidence only. Inspect the original records before changing workflow status.",
    ))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON evidence bundle for one run")
    parser.add_argument("--json", action="store_true", help="Print the full machine-readable result")
    args = parser.parse_args()

    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": f"Cannot read valid JSON input: {exc}"}), file=sys.stderr)
        return 2

    _, blockers = validate(payload)
    if blockers:
        print(json.dumps({
            "run_id": payload.get("run_id") if isinstance(payload, dict) else None,
            "recommendation": "not_ready",
            "blockers": blockers,
            "api_called": False,
        }, ensure_ascii=False, indent=2))
        return 1

    if TypeSafeClient is None or Noul is None or Choice is None:
        print(json.dumps({
            "run_id": payload["run_id"],
            "recommendation": "review_unavailable",
            "error": "TypeSafe SDK is missing; install tools/jev/run_completion_reviewer/requirements.txt.",
            "api_called": False,
        }, ensure_ascii=False, indent=2))
        return 2
    if not os.environ.get("TYPESAFE_API_KEY"):
        print(json.dumps({
            "run_id": payload["run_id"],
            "recommendation": "review_unavailable",
            "error": "TYPESAFE_API_KEY is not set in this shell.",
            "api_called": False,
        }, ensure_ascii=False, indent=2))
        return 2

    try:
        result = review(payload)
    except Exception as exc:  # SDK/network errors go back to the operator without a DONE decision.
        print(json.dumps({
            "run_id": payload["run_id"],
            "recommendation": "review_unavailable",
            "error_type": type(exc).__name__,
            "request_attempted": True,
        }, ensure_ascii=False, indent=2))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else format_review(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

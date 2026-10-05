#!/usr/bin/env python3
"""Suggest a bounded project subagent for one active-run task; never start it."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from typesafe_sdk import Choice, Noul, TypeSafeClient
except ImportError:
    Choice = Noul = TypeSafeClient = None  # type: ignore[assignment,misc]


ROOT = Path(__file__).resolve().parents[3]
CATALOG = {
    "mechanical_worker": {
        "owner": "codex", "model": "gpt-6-luna", "effort": "low",
        "file": ".codex/agents/mechanical_worker.toml",
        "role": "Bounded inventories, targeted inspection, simple documentation and mechanical checks.",
    },
    "code_worker": {
        "owner": "codex", "model": "gpt-6.1-sol", "effort": "medium",
        "file": ".codex/agents/code_worker.toml",
        "role": "Scoped code implementation, fixes and focused technical verification.",
    },
    "architecture_reviewer": {
        "owner": "codex", "model": "gpt-6-astra", "effort": "medium",
        "file": ".codex/agents/architecture_reviewer.toml",
        "role": "Difficult bounded architecture audits and system-boundary decisions.",
    },
    "visual_architect": {
        "owner": "claude", "model": "claude-opus-5-5", "effort": "medium",
        "file": ".claude/agents/visual_architect.md",
        "role": "Art direction, visual coherence, asset choice, generation and artistic adaptation.",
    },
    "asset_integrator": {
        "owner": "claude", "model": "claude-sonnet-5-5", "effort": "medium",
        "file": ".claude/agents/asset_integrator.md",
        "role": "Scoped spritesheet preparation, metadata and visual asset integration.",
    },
}
DEFAULTS = {
    "codex": {"main": "gpt-6.1-sol", "subagent": "gpt-6-luna"},
    "claude": {"main": "claude-opus-5-5", "subagent": "claude-sonnet-5-5"},
}


def validate(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Input must be a JSON object."]
    for key in ("run_id", "task_summary"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            errors.append(f"{key} must be a nonempty string.")
    if payload.get("run_status") != "ACTIVE":
        errors.append("run_status must be ACTIVE.")
    if type(payload.get("visual_judgment")) is not bool:
        errors.append("visual_judgment must be a boolean.")
    if payload.get("complexity") not in ("low", "medium", "high"):
        errors.append("complexity must be low, medium or high.")
    slots = payload.get("active_subagents")
    if type(slots) is not int or not 0 <= slots <= 4:
        errors.append("active_subagents must be an integer from 0 to 4.")
    for key in ("affected_files", "concurrent_edit_files", "available_models"):
        value = payload.get(key)
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f"{key} must be a list of nonempty strings.")
    if not errors and set(payload["affected_files"]) & set(payload["concurrent_edit_files"]):
        errors.append("A task file is already assigned for concurrent editing; resolve ownership first.")
    return errors


def candidates(payload: dict[str, Any]) -> tuple[str, dict[str, dict[str, str]]]:
    owner = "claude" if payload["visual_judgment"] else "codex"
    available = set(payload["available_models"])
    selected = {
        name: item for name, item in CATALOG.items()
        if item["owner"] == owner and item["model"] in available and (ROOT / item["file"]).is_file()
    }
    if DEFAULTS[owner]["subagent"] in available:
        selected["ordinary_subagent"] = {
            "owner": owner, "model": DEFAULTS[owner]["subagent"],
            "effort": payload["complexity"], "file": "",
            "role": "A bounded independent task outside the installed custom-agent roles.",
        }
    selected["main_agent"] = {
        "owner": owner, "model": DEFAULTS[owner]["main"],
        "effort": "medium", "file": "",
        "role": "Keep the task with the main agent when delegation is not useful or safe.",
    }
    return owner, selected


def route(payload: dict[str, Any]) -> dict[str, Any]:
    owner, options = candidates(payload)
    if payload["active_subagents"] >= 4:
        return {"status": "manual_routing_required", "owner": owner,
                "reason": "Four subagents are already active; no new delegation is allowed.",
                "api_called": False}
    if TypeSafeClient is None or Choice is None or Noul is None or not os.environ.get("TYPESAFE_API_KEY"):
        return {"status": "advisor_unavailable", "owner": owner,
                "reason": "TypeSafe SDK or TYPESAFE_API_KEY is unavailable; apply AGENTS.md routing directly.",
                "api_called": False}

    state = {
        "run_id": payload["run_id"], "task_summary": payload["task_summary"],
        "affected_files": payload["affected_files"], "complexity": payload["complexity"],
        "visual_judgment_required": payload["visual_judgment"], "owner": owner,
        "available_candidates": {name: item["role"] for name, item in options.items()},
        "scope": "Suggest only. The main agent owns file assignment, spawning, integration and final verification.",
    }
    questions = {
        "best_handler": Choice(
            instructions=(
                "Which available candidate best handles `task_summary` within the active run? "
                "Choose a custom agent only when its role fits the bounded task. Choose ordinary_subagent "
                "for an independent task with no fitting specialist, or main_agent when delegation adds no value. "
                "Respect `owner` and the supplied candidate descriptions."
            ),
            criteria={name: item["role"] for name, item in options.items()},
        ),
        "delegation_useful": Noul(instructions=(
            "Can `task_summary` be assigned as independent, bounded work now while the main agent "
            "continues useful work? Answer no for tightly coupled, trivial or unclear tasks."
        )),
    }
    with TypeSafeClient() as client:
        response = client.system_one(model="jev-latest", state=state, questions=questions)
    choice = response.answers["best_handler"]
    selected = choice.choice
    if selected not in options:
        raise ValueError("Jev returned an unavailable candidate.")
    ranked = sorted(choice.probabilities.items(), key=lambda pair: pair[1], reverse=True)
    return {
        "status": "advisory", "run_id": payload["run_id"], "owner": owner,
        "recommendation": {"name": selected, **options[selected]},
        "ranked_candidates": [{"name": name, "probability": probability} for name, probability in ranked],
        "choice_confidence": choice.confidence,
        "delegation_probability_yes": response.answers["delegation_useful"].noul,
        "api_called": True, "model": response.model,
        "note": "Uncalibrated Jev judgments are advisory. The main agent inspects the task and decides.",
        "usage": {"input_tokens": response.usage.input_tokens,
                  "output_tokens": response.usage.output_tokens},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON description of one task in an ACTIVE run")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "invalid_input", "errors": [str(exc)]}), file=sys.stderr)
        return 2
    errors = validate(payload)
    if errors:
        print(json.dumps({"status": "invalid_input", "errors": errors, "api_called": False}, indent=2))
        return 1
    try:
        result = route(payload)
    except Exception as exc:
        result = {"status": "advisor_unavailable", "owner": "claude" if payload["visual_judgment"] else "codex",
                  "reason": f"Jev request failed ({type(exc).__name__}); apply AGENTS.md routing directly.",
                  "api_called": True}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "advisory" else 2


if __name__ == "__main__":
    raise SystemExit(main())

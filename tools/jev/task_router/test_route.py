"""Exercise routing gates without calling Jev."""

import unittest
import tomllib

from route import CATALOG, ROOT, candidates, route, validate


class RouteGatesTest(unittest.TestCase):
    def setUp(self):
        self.task = {
            "run_id": "test-run", "run_status": "ACTIVE",
            "task_summary": "Inspect a bounded Godot task.",
            "complexity": "low", "visual_judgment": False,
            "affected_files": [], "concurrent_edit_files": [],
            "active_subagents": 0,
            "available_models": ["gpt-6-luna", "gpt-6.1-sol", "claude-opus-5-5", "claude-sonnet-5-5"],
        }

    def test_conflicting_file_prevents_request(self):
        task = dict(self.task, affected_files=["scripts/player.gd"],
                    concurrent_edit_files=["scripts/player.gd"])
        self.assertTrue(any("concurrent editing" in issue for issue in validate(task)))

    def test_full_roster_prevents_request(self):
        task = dict(self.task, active_subagents=4)
        self.assertEqual(route(task)["status"], "manual_routing_required")
        self.assertFalse(route(task)["api_called"])

    def test_owner_and_available_models_filter_candidates(self):
        owner, options = candidates(self.task)
        self.assertEqual(owner, "codex")
        self.assertIn("mechanical_worker", options)
        self.assertNotIn("architecture_reviewer", options)
        self.assertNotIn("visual_architect", options)
        visual = dict(self.task, visual_judgment=True)
        owner, options = candidates(visual)
        self.assertEqual(owner, "claude")
        self.assertIn("visual_architect", options)
        self.assertNotIn("code_worker", options)

    def test_catalog_matches_installed_agent_models(self):
        for name, item in CATALOG.items():
            path = ROOT / item["file"]
            self.assertTrue(path.is_file(), name)
            if path.suffix == ".toml":
                actual = tomllib.loads(path.read_text())
            else:
                frontmatter = path.read_text().split("---", 2)[1]
                actual = dict(line.split(": ", 1) for line in frontmatter.splitlines() if ": " in line)
            self.assertEqual(actual["name"], name)
            self.assertEqual(actual["model"], item["model"])
            self.assertEqual(actual.get("effort", actual.get("model_reasoning_effort")), item["effort"])


if __name__ == "__main__":
    unittest.main()

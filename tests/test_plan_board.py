#!/usr/bin/env python3
"""Tests for scripts/plan-board.py. Run from the repo root:
python3 -m unittest tests/test_plan_board.py
"""
import importlib.util
import json
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "greenfield-with-plan"
FIXTURE_PLAN = FIXTURE / "docs" / "superpowers" / "plans" / "2026-10-01-todo-api.md"


def load_module():
    spec = importlib.util.spec_from_file_location("plan_board", ROOT / "scripts" / "plan-board.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pb = load_module()


class ParsePlan(unittest.TestCase):
    def test_fixture_plan(self):
        board = pb.parse_plan(FIXTURE_PLAN.read_text(encoding="utf-8"))
        self.assertEqual(board["title"], "Todo API Implementation Plan")
        self.assertEqual(board["goal"], "The todo API from the spec, test-first.")
        self.assertEqual([t["number"] for t in board["tasks"]], [1, 2, 3])
        self.assertEqual(board["tasks"][0]["title"], "createTodo and listTodos")
        self.assertEqual(board["tasks"][0]["status"], "done")
        self.assertEqual(len(board["tasks"][0]["steps"]), 3)
        self.assertEqual(board["tasks"][0]["steps"][0]["text"], "Step 1: Failing test for createTodo and listTodos")
        self.assertEqual(board["tasks"][1]["status"], "backlog")
        self.assertEqual(board["tasks"][2]["status"], "backlog")

    def test_in_progress_and_uppercase_tick(self):
        text = "# P\n\n### Task 1: Half\n\n- [X] **Step 1: done**\n- [ ] **Step 2: open**\n"
        task = pb.parse_plan(text)["tasks"][0]
        self.assertEqual(task["status"], "in_progress")
        self.assertEqual([s["done"] for s in task["steps"]], [True, False])
        self.assertEqual(task["steps"][0]["text"], "Step 1: done")

    def test_task_without_steps_is_backlog(self):
        task = pb.parse_plan("# P\n\n### Task 4: Bare\n\nsome prose\n")["tasks"][0]
        self.assertEqual(task["status"], "backlog")
        self.assertEqual(task["steps"], [])

    def test_level_two_heading_ends_the_task(self):
        text = "# P\n\n### Task 1: A\n\n- [ ] one\n\n## Notes\n\n- [ ] not a step\n"
        board = pb.parse_plan(text)
        self.assertEqual(len(board["tasks"]), 1)
        self.assertEqual(len(board["tasks"][0]["steps"]), 1)

    def test_fenced_code_is_ignored(self):
        text = "# P\n\n### Task 1: A\n\n```markdown\n### Task 9: inside fence\n- [ ] fenced\n```\n\n- [x] real\n"
        board = pb.parse_plan(text)
        self.assertEqual([t["number"] for t in board["tasks"]], [1])
        self.assertEqual([s["text"] for s in board["tasks"][0]["steps"]], ["real"])
        self.assertEqual(board["tasks"][0]["status"], "done")

    def test_missing_title_and_goal(self):
        board = pb.parse_plan("no heading here\n")
        self.assertEqual(board["title"], "")
        self.assertEqual(board["goal"], "")
        self.assertEqual(board["tasks"], [])


class PickPlan(unittest.TestCase):
    def test_newest_with_open_step_wins(self):
        self.assertEqual(pb.pick_plan([("2026-10-02-b.md", False), ("2026-10-01-a.md", True)]), "2026-10-01-a.md")

    def test_all_done_picks_newest(self):
        self.assertEqual(pb.pick_plan([("2026-10-01-a.md", False), ("2026-10-02-b.md", False)]), "2026-10-02-b.md")

    def test_empty_is_none(self):
        self.assertIsNone(pb.pick_plan([]))


class PortFor(unittest.TestCase):
    def test_stable_and_in_range(self):
        a = pb.port_for(FIXTURE)
        b = pb.port_for(str(FIXTURE))
        self.assertEqual(a, b)
        self.assertTrue(7800 <= a <= 7899)


class LoadBoard(unittest.TestCase):
    def test_fixture_root(self):
        board = pb.load_board(FIXTURE)
        self.assertEqual(board["plan"], "2026-10-01-todo-api.md")
        self.assertEqual(board["plans"], ["2026-10-01-todo-api.md"])
        self.assertEqual(board["errors"], {})
        self.assertEqual(board["root"], str(FIXTURE.resolve()))
        self.assertEqual([t["status"] for t in board["tasks"]], ["done", "backlog", "backlog"])

    def test_unknown_plan_falls_back_to_default(self):
        board = pb.load_board(FIXTURE, "nope.md")
        self.assertEqual(board["plan"], "2026-10-01-todo-api.md")

    def test_root_without_plans(self):
        board = pb.load_board(ROOT / "tests" / "fixtures" / "new-empty")
        self.assertIsNone(board["plan"])
        self.assertEqual(board["plans"], [])
        self.assertEqual(board["tasks"], [])


class Server(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = pb.make_server(FIXTURE, 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get(self, path):
        with urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=2) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()

    def test_api_board(self):
        status, ctype, body = self.get("/api/board")
        self.assertEqual(status, 200)
        self.assertTrue(ctype.startswith("application/json"))
        board = json.loads(body)
        self.assertEqual(board["plan"], "2026-10-01-todo-api.md")
        self.assertEqual([t["status"] for t in board["tasks"]], ["done", "backlog", "backlog"])

    def test_api_board_with_plan_query(self):
        _, _, body = self.get("/api/board?plan=2026-10-01-todo-api.md")
        self.assertEqual(json.loads(body)["plan"], "2026-10-01-todo-api.md")

    def test_healthz(self):
        status, _, body = self.get("/healthz")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"root": str(FIXTURE.resolve())})
        self.assertEqual(pb.healthz(self.port), str(FIXTURE.resolve()))

    def test_page(self):
        status, ctype, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertTrue(ctype.startswith("text/html"))
        self.assertIn(b"<!doctype html>", body.lower())

    def test_not_found(self):
        from urllib.error import HTTPError
        with self.assertRaises(HTTPError) as cm:
            self.get("/nothing")
        self.assertEqual(cm.exception.code, 404)


class Main(unittest.TestCase):
    def test_bad_root(self):
        import io
        from contextlib import redirect_stderr
        err = io.StringIO()
        with redirect_stderr(err):
            code = pb.main(["--root", str(ROOT / "does-not-exist")])
        self.assertEqual(code, 2)
        self.assertIn("root is not a directory", err.getvalue())

    def test_healthz_without_server_is_none(self):
        probe = pb.make_server(FIXTURE, 0)
        free_port = probe.server_address[1]
        probe.server_close()
        self.assertIsNone(pb.healthz(free_port))


if __name__ == "__main__":
    unittest.main()

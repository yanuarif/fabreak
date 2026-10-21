#!/usr/bin/env python3
"""Tests for scripts/plan-board.py. Run from the repo root:
python3 -m unittest tests/test_plan_board.py
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

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


class BodyAndDepends(unittest.TestCase):
    TEXT = ("# P\n\n### Task 1: A\n\n- [x] one\n\n### Task 2: B\n\nDepends on: Task 1 and Task 3 (not Task 2)\n\n"
            "```text\n### Task 9: fenced\n```\n\n- [ ] two\n\n## Notes\n\ntrailing\n")

    def test_body_keeps_raw_lines_and_fences(self):
        tasks = pb.parse_plan(self.TEXT)["tasks"]
        self.assertEqual(tasks[0]["body"], "- [x] one")
        self.assertEqual(tasks[1]["body"],
                         "Depends on: Task 1 and Task 3 (not Task 2)\n\n```text\n### Task 9: fenced\n```\n\n- [ ] two")

    def test_depends_skips_own_number(self):
        tasks = pb.parse_plan(self.TEXT)["tasks"]
        self.assertEqual(tasks[0]["depends"], [])
        self.assertEqual(tasks[1]["depends"], [1, 3])


def task(number, title, ticks=()):
    return {"number": number, "title": title, "steps": [{"text": "s", "done": t} for t in ticks]}


def worktree(branch, ahead=0, dirty=False, plans=None):
    return {"path": "/wt/" + branch.rsplit("/", 1)[-1], "branch": branch, "ahead": ahead, "dirty": dirty,
            "plans": plans or {}}


def pr(number, title, state="OPEN", head="other", body=""):
    return {"number": number, "title": title, "state": state, "url": "https://example.test/pr/%d" % number,
            "headRefName": head, "body": body}


class Matching(unittest.TestCase):
    def test_slug_and_branch_key(self):
        self.assertEqual(pb.slug("  completeTodo: Sets *done* "), "completetodo-sets-done")
        self.assertEqual(pb.branch_key("claude/complete-todo-3fa2c1"), "complete-todo")
        self.assertEqual(pb.branch_key("feature/complete-todo"), "complete-todo")

    def test_pr_body_names_the_task(self):
        live = pb.match_tasks([task(2, "completeTodo")], [], [pr(7, "Add it", body="### Task 2: completeTodo\n...")])
        self.assertEqual(live[2]["pr"]["number"], 7)

    def test_pr_title_slug(self):
        live = pb.match_tasks([task(1, "Empty title throws")], [], [pr(3, "Empty title throws!")])
        self.assertEqual(live[1]["pr"]["number"], 3)

    def test_branch_key_prefix_and_worktree(self):
        tasks = [task(1, "createTodo and listTodos"), task(2, "completeTodo sets done")]
        live = pb.match_tasks(tasks, [worktree("claude/completetodo-sets-ab12cd", ahead=2)], [])
        self.assertIsNone(live[1])
        self.assertEqual(live[2]["branch"], "claude/completetodo-sets-ab12cd")
        self.assertEqual(live[2]["ahead"], 2)
        self.assertIsNone(live[2]["pr"])

    def test_ambiguous_key_matches_nothing(self):
        tasks = [task(1, "Export invoices as CSV"), task(2, "Export invoices as PDF")]
        live = pb.match_tasks(tasks, [worktree("claude/export-invoices-ab12cd", ahead=1)], [])
        self.assertEqual(live, {1: None, 2: None})

    def test_short_key_needs_equal_slug(self):
        live = pb.match_tasks([task(1, "Fix login flow")], [worktree("claude/fix-ab12cd", ahead=1)], [])
        self.assertIsNone(live[1])

    def test_open_beats_merged_and_closed_is_ignored(self):
        prs = [pr(1, "Task 1: A", "MERGED"), pr(2, "Task 1: A", "OPEN", head="claude/a-x"), pr(3, "Task 1: A", "CLOSED")]
        live = pb.match_tasks([task(1, "A")], [worktree("claude/a-x", ahead=1)], prs)
        self.assertEqual(live[1]["pr"]["number"], 2)
        self.assertEqual(live[1]["worktree"], "/wt/a-x")
        live = pb.match_tasks([task(1, "A")], [], [pr(3, "Task 1: A", "CLOSED")])
        self.assertIsNone(live[1])

    def test_branch_number(self):
        self.assertEqual(pb.branch_number("task/02-import-csv"), 2)
        self.assertEqual(pb.branch_number("feat/03-export-pdf-4d2e1a"), 3)
        self.assertEqual(pb.branch_number("claude/task-07-cleanup-1eff3c"), 7)
        self.assertEqual(pb.branch_number("task-3"), 3)
        self.assertEqual(pb.branch_number("Task3-x"), 3)
        self.assertIsNone(pb.branch_number("claude/2fa-login"))
        self.assertIsNone(pb.branch_number("claude/complete-todo-3fa2c1"))
        self.assertIsNone(pb.branch_number(""))

    def test_number_match_needs_the_plan_file(self):
        tasks = [task(3, "Editor on sections")]
        holds = worktree("feat/03-export-pdf-4d2e1a", ahead=1, plans={"p.md": "# P"})
        lacks = worktree("feat/03-export-pdf-4d2e1a", ahead=1, plans={"old.md": "# O"})
        self.assertEqual(pb.match_tasks(tasks, [holds], [], plan="p.md")[3]["branch"], "feat/03-export-pdf-4d2e1a")
        self.assertIsNone(pb.match_tasks(tasks, [lacks], [], plan="p.md")[3])
        self.assertIsNone(pb.match_tasks(tasks, [holds], [])[3])

    def test_slug_match_beats_number_match(self):
        tasks = [task(1, "Write the parser"), task(2, "Other")]
        wts = [worktree("feat/01-x", plans={"p.md": ""}), worktree("claude/write-the-parser-ab12cd", ahead=1)]
        self.assertEqual(pb.match_tasks(tasks, wts, [], plan="p.md")[1]["branch"], "claude/write-the-parser-ab12cd")

    def test_number_matched_worktree_adopts_its_branch_pr(self):
        tasks = [task(2, "Segmentation in capture")]
        wts = [worktree("task/02-capture", plans={"p.md": ""})]
        prs = [pr(9, "feat: something else", "MERGED", head="task/02-capture"),
               pr(10, "feat: something else", "OPEN", head="task/02-capture"),
               pr(11, "unrelated", "OPEN", head="task/02-other")]
        live = pb.match_tasks(tasks, wts, prs, plan="p.md")
        self.assertEqual(live[2]["pr"]["number"], 10)

    def test_prs_are_not_matched_by_number(self):
        live = pb.match_tasks([task(1, "New task")], [], [pr(4, "Old", "MERGED", head="task/01-old-plan")], plan="p.md")
        self.assertIsNone(live[1])


def steps(*states):
    return [{"text": "s%d" % i, "done": s == "done", "state": s} for i, s in enumerate(states)]


class Markers(unittest.TestCase):
    def test_states_and_done(self):
        text = "# P\n\n### Task 1: M\n\n- [ ] a\n- [/] b\n- [x] c\n- [X] d\n- [-] e\n"
        got = pb.parse_plan(text)["tasks"][0]["steps"]
        self.assertEqual([s["state"] for s in got], ["open", "doing", "done", "done", "skipped"])
        self.assertEqual([s["done"] for s in got], [False, False, True, True, False])
        self.assertEqual(got[1]["text"], "b")

    def test_plan_only_status(self):
        self.assertEqual(pb.status_for(steps("doing", "open")), "in_progress")
        self.assertEqual(pb.status_for(steps("done", "skipped")), "done")
        self.assertEqual(pb.status_for(steps("skipped")), "done")
        self.assertEqual(pb.status_for(steps("skipped", "open")), "backlog")
        self.assertEqual(pb.status_for(steps("open")), "backlog")
        self.assertEqual(pb.status_for([]), "backlog")

    def test_resolve_status_reads_states(self):
        self.assertEqual(pb.resolve_status(steps("doing", "open"), None), "in_progress")
        self.assertEqual(pb.resolve_status(steps("done", "skipped"), None), "done")

    def test_doing_step_keeps_the_plan_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            plans = Path(tmp) / "docs" / "superpowers" / "plans"
            plans.mkdir(parents=True)
            (plans / "2026-10-01-a.md").write_text("# A\n\n### Task 1: A\n\n- [/] a\n", encoding="utf-8")
            (plans / "2026-10-02-b.md").write_text("# B\n\n### Task 1: B\n\n- [x] b\n- [-] c\n", encoding="utf-8")
            self.assertEqual(pb.load_board(tmp)["plan"], "2026-10-01-a.md")


class MergeSteps(unittest.TestCase):
    def test_further_state_wins_per_step(self):
        plan = steps("done", "open", "open", "doing")
        tree = steps("open", "doing", "skipped", "open")
        tree[1]["text"] = "renamed"
        got = pb.merge_steps(plan, tree)
        self.assertEqual([s["state"] for s in got], ["done", "doing", "skipped", "doing"])
        self.assertEqual(got[1]["text"], "renamed")
        self.assertEqual([s["done"] for s in got], [True, False, False, False])

    def test_different_count_takes_the_worktree_copy(self):
        tree = steps("open", "open", "done")
        self.assertEqual(pb.merge_steps(steps("done"), tree), tree)


class ResolveStatus(unittest.TestCase):
    def live(self, ahead=0, dirty=False, state=None):
        return {"branch": "b", "worktree": "/wt", "ahead": ahead, "dirty": dirty,
                "pr": {"number": 1, "state": state, "url": "u", "title": "t"} if state else None}

    def test_table(self):
        steps_none = [{"done": False}, {"done": False}]
        steps_some = [{"done": True}, {"done": False}]
        steps_all = [{"done": True}, {"done": True}]
        self.assertEqual(pb.resolve_status(steps_all, self.live(state="OPEN")), "done")
        self.assertEqual(pb.resolve_status(steps_none, self.live(state="MERGED")), "done")
        self.assertEqual(pb.resolve_status(steps_none, self.live(state="OPEN")), "review")
        self.assertEqual(pb.resolve_status(steps_some, None), "in_progress")
        self.assertEqual(pb.resolve_status(steps_none, self.live(ahead=1)), "in_progress")
        self.assertEqual(pb.resolve_status(steps_none, self.live(dirty=True)), "in_progress")
        self.assertEqual(pb.resolve_status(steps_none, self.live()), "backlog")
        self.assertEqual(pb.resolve_status([], None), "backlog")


PLAN_TEXT = "# Demo\n\n### Task 1: Write the parser\n\n- [ ] one\n\n### Task 2: Task two title\n\n- [ ] two\n"


def git(cwd, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.test", *args],
                   cwd=cwd, check=True, capture_output=True)


class GitSource(unittest.TestCase):
    def test_worktree_with_a_commit_is_in_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            plans = repo / "docs" / "superpowers" / "plans"
            plans.mkdir(parents=True)
            (plans / "2026-10-21-demo.md").write_text(PLAN_TEXT, encoding="utf-8")
            git(repo, "init", "-q", "-b", "main")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "plan")
            wt = Path(tmp) / "wt"
            git(repo, "worktree", "add", "-q", "-b", "claude/task-two-title-abc123", str(wt))
            (wt / "two.txt").write_text("2\n", encoding="utf-8")
            git(wt, "add", ".")
            git(wt, "commit", "-q", "-m", "two")

            data = {"git": pb.read_git(repo), "prs": None}
            self.assertEqual(data["git"]["default"], "main")
            board = pb.load_board(repo, data=data)
            self.assertEqual(board["sources"], {"git": True, "prs": False, "default": "main"})
            self.assertEqual([t["status"] for t in board["tasks"]], ["backlog", "in_progress"])
            self.assertEqual(board["tasks"][1]["live"]["ahead"], 1)
            self.assertFalse(board["tasks"][1]["live"]["dirty"])
            self.assertEqual(board["tasks"][1]["plan_status"], "backlog")

    def test_uncommitted_tick_in_a_number_named_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            plans = repo / "docs" / "superpowers" / "plans"
            plans.mkdir(parents=True)
            (plans / "2026-10-21-demo.md").write_text(PLAN_TEXT, encoding="utf-8")
            git(repo, "init", "-q", "-b", "main")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "plan")
            wt = Path(tmp) / "wt"
            git(repo, "worktree", "add", "-q", "-b", "feat/02-short-a1b2c3", str(wt))
            wt_plan = wt / "docs" / "superpowers" / "plans" / "2026-10-21-demo.md"
            wt_plan.write_text(PLAN_TEXT.replace("- [ ] two", "- [x] two\n- [ ] three"), encoding="utf-8")

            git_data = pb.read_git(repo)
            self.assertIn("2026-10-21-demo.md", git_data["worktrees"][0]["plans"])
            board = pb.load_board(repo, data={"git": git_data, "prs": None})
            one, two = board["tasks"]
            self.assertEqual((one["status"], one["steps_from"]), ("backlog", "plan"))
            self.assertEqual(two["live"]["branch"], "feat/02-short-a1b2c3")
            self.assertTrue(two["live"]["dirty"])
            self.assertEqual(two["steps_from"], "worktree")
            self.assertIn("- [ ] three", two["body"])
            self.assertEqual([s["state"] for s in two["steps"]], ["done", "open"])
            self.assertEqual(two["status"], "in_progress")
            self.assertEqual(two["plan_status"], "backlog")
            self.assertNotIn("plans", two["live"])

    def test_progress_file_in_the_private_git_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            plans = repo / "docs" / "superpowers" / "plans"
            plans.mkdir(parents=True)
            (plans / "2026-10-21-demo.md").write_text(PLAN_TEXT, encoding="utf-8")
            git(repo, "init", "-q", "-b", "main")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "plan")
            wt = Path(tmp) / "wt"
            git(repo, "worktree", "add", "-q", "-b", "feat/02-short-a1b2c3", str(wt))
            path = subprocess.run(["git", "rev-parse", "--git-path", "fabreak-steps.md"], cwd=wt,
                                  check=True, capture_output=True, text=True).stdout.strip()
            progress = (wt / path).resolve()

            def board():
                return pb.load_board(repo, data={"git": pb.read_git(repo), "prs": None})

            self.assertIsNone(pb.read_git(repo)["worktrees"][0]["progress"])
            progress.write_text("### Task 1: Write the parser\n\n- [x] one\n", encoding="utf-8")
            two = board()["tasks"][1]
            self.assertEqual((two["status"], two["steps_from"]), ("backlog", "worktree"))
            self.assertEqual(board()["tasks"][0]["steps_from"], "plan")

            progress.write_text("### Task 2: Task two title\n\n- [/] two\n", encoding="utf-8")
            two = board()["tasks"][1]
            self.assertEqual(two["steps_from"], "progress")
            self.assertEqual([s["state"] for s in two["steps"]], ["doing"])
            self.assertEqual(two["status"], "in_progress")
            self.assertFalse(two["live"]["dirty"])

    def test_not_a_repository_top_level(self):
        self.assertIsNone(pb.read_git(FIXTURE))


class EventStream(unittest.TestCase):
    def test_first_event_then_one_per_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plans = root / "docs" / "superpowers" / "plans"
            plans.mkdir(parents=True)
            plan = plans / "2026-10-21-demo.md"
            plan.write_text(PLAN_TEXT, encoding="utf-8")
            live = pb.Live(root, git=False, prs=False, plan_every=0.05)
            server = pb.make_server(root, 0, live=live)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                stream = urlopen(f"http://127.0.0.1:{server.server_address[1]}/api/events", timeout=5)
                self.assertTrue(stream.headers.get("Content-Type", "").startswith("text/event-stream"))
                first = read_event(stream)
                self.assertEqual([t["status"] for t in first["tasks"]], ["backlog", "backlog"])
                plan.write_text(PLAN_TEXT.replace("- [ ] one", "- [x] one"), encoding="utf-8")
                second = read_event(stream)
                self.assertEqual([t["status"] for t in second["tasks"]], ["done", "backlog"])
                stream.close()
            finally:
                server.shutdown()
                server.server_close()


def read_event(stream):
    """The JSON of the next `event: board` on an open SSE response."""
    event, data = None, []
    while True:
        line = stream.readline().decode("utf-8").rstrip("\n")
        if line.startswith("event: "):
            event = line[7:]
        elif line.startswith("data: "):
            data.append(line[6:])
        elif line == "" and event == "board" and data:
            return json.loads("\n".join(data))


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


class Stop(unittest.TestCase):
    def test_pid_alive_and_watch(self):
        self.assertTrue(pb.pid_alive(pb.os.getpid()))
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.3)"])
        gone = threading.Event()
        threading.Thread(target=pb.watch_pid, args=(child.pid, gone.set, 0.05), daemon=True).start()
        self.assertFalse(gone.wait(0.1))
        child.wait()
        self.assertTrue(gone.wait(2))
        self.assertFalse(pb.pid_alive(child.pid))

    def test_stop_needs_the_header_then_ends_streams_and_the_server(self):
        server = pb.make_server(FIXTURE, 0, live=pb.Live(FIXTURE, git=False, prs=False))
        base = f"http://127.0.0.1:{server.server_address[1]}"
        loop = threading.Thread(target=server.serve_forever, daemon=True)
        loop.start()
        try:
            with self.assertRaises(HTTPError) as refused:
                urlopen(Request(base + "/api/stop", method="POST"), timeout=2)
            self.assertEqual(refused.exception.code, 403)
            stream = urlopen(base + "/api/events", timeout=5)
            read_event(stream)
            req = Request(base + "/api/stop", method="POST", headers={"X-Plan-Board": "stop"})
            with urlopen(req, timeout=2) as r:
                self.assertEqual(json.loads(r.read()), {"stopping": True})
            self.assertEqual(read_named_event(stream), "stopped")
            loop.join(3)
            self.assertFalse(loop.is_alive())
        finally:
            if loop.is_alive():
                server.shutdown()
            server.server_close()


def read_named_event(stream):
    """The name of the next event on an open SSE response, skipping pings."""
    while True:
        line = stream.readline().decode("utf-8").rstrip("\n")
        if line.startswith("event: "):
            return line[7:]


class Server(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = pb.make_server(FIXTURE, 0, live=pb.Live(FIXTURE, git=False, prs=False))
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
        self.assertEqual(json.loads(body), {"root": str(FIXTURE.resolve()), "api": pb.API})
        self.assertEqual(pb.healthz(self.port), str(FIXTURE.resolve()))

    def test_page(self):
        status, ctype, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertTrue(ctype.startswith("text/html"))
        html = body.decode("utf-8")
        self.assertIn("<!doctype html>", html.lower())
        for heading in ("Backlog", "In progress", "Review", "Done"):
            self.assertIn(heading, html)
        self.assertIn("/api/events", html)
        self.assertIn("/api/stop", html)
        self.assertIn("no plan found under docs/superpowers/plans", html)

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
        probe = pb.make_server(FIXTURE, 0, live=pb.Live(FIXTURE, git=False, prs=False))
        free_port = probe.server_address[1]
        probe.server_close()
        self.assertIsNone(pb.healthz(free_port))


if __name__ == "__main__":
    unittest.main()

# Plan Board Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A read-only kanban view of a repository's plan files, served locally by one Python script and opened in the desktop preview pane by `/fabreak:board`.

**Architecture:** `scripts/plan-board.py` holds pure parsing functions (`parse_plan`, `pick_plan`, `port_for`, `load_board`) and a small `http.server` on 127.0.0.1 with three routes. One page, inline CSS and JavaScript, polls the JSON route every 3 seconds. A new `board` skill is the command; `board.md` points at it.

**Tech Stack:** Python 3 standard library only (`argparse`, `http.server`, `json`, `pathlib`, `re`, `zlib`, `urllib`), `unittest`, Markdown skills, GitHub Actions.

Spec: `docs/superpowers/specs/2026-10-17-plan-board-design.md` — read it first.

## Global Constraints

- Every file in the repo is in English. Chat with the owner is in Indonesian.
- No project, client, organization or person names, no home paths, no private links anywhere in the repo. Run `bash scripts/check-forbidden-words.sh --all` before every commit.
- Examples use fictional generic projects: "a todo API".
- `scripts/plan-board.py` imports the standard library only. No `pip`, no third-party package.
- The server binds `127.0.0.1` only and never writes to disk.
- Default port: `7800 + (crc32(absolute root path) % 100)`.
- `skills/fabreak/SKILL.md` stays under 1,500 tokens; the router gains no new text beyond what `board.md` already covers.
- Commits land on this branch with plain messages. Nothing is pushed; the owner opens the PR from the app.
- Version `0.3.0` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.

---

## File map

| Path | Responsibility |
|---|---|
| `scripts/plan-board.py` | Parse plans, pick the default plan, derive the port, serve `/`, `/api/board`, `/healthz`. |
| `tests/test_plan_board.py` | unittest for the pure functions and one HTTP round trip against the fixture plan. |
| `skills/board/SKILL.md` | The `/fabreak:board` command: find the root, start or reuse the server, open the pane, CLI fallback. |
| `skills/fabreak/board.md` | New "Plan board" section before "CLI fallback". |
| `.github/workflows/check.yml` | One new step running the unittest. |
| `README.md`, `CONTRIBUTING.md` | The new command in Entries and Layout; the unittest in the check list. |
| `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Version `0.3.0`. |

---

### Task 1: Parsing, plan selection and the port formula

**Files:**
- Create: `scripts/plan-board.py`
- Create: `tests/test_plan_board.py`

**Interfaces:**
- Produces: `parse_plan(text: str) -> dict` with keys `title`, `goal`, `tasks`; each task `{"number": int, "title": str, "status": "backlog"|"in_progress"|"done", "steps": [{"text": str, "done": bool}]}`.
- Produces: `status_for(steps: list[dict]) -> str`.
- Produces: `pick_plan(candidates: list[tuple[str, bool]]) -> str | None`, candidates are `(basename, has_unchecked)`.
- Produces: `port_for(root) -> int` in `7800..7899`.
- Produces: `PLAN_DIR = Path("docs") / "superpowers" / "plans"`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_plan_board.py`:

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_plan_board.py 2>&1 | tail -3`
Expected: an error from `spec_from_file_location` or `exec_module` because `scripts/plan-board.py` does not exist (`FileNotFoundError` or `AttributeError`), exit code 1.

- [ ] **Step 3: Write the pure functions**

Create `scripts/plan-board.py`:

```python
#!/usr/bin/env python3
"""Plan board: a read-only kanban view of docs/superpowers/plans/*.md.

Usage: plan-board.py [--root DIR] [--port N] [--verbose]

Serves one page on 127.0.0.1 that shows every task of a plan in Backlog,
In progress or Done, from the task's ticked steps alone. Reads the plan
files on every request and writes nothing. Standard library only.
"""
import argparse
import json
import re
import sys
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen

PLAN_DIR = Path("docs") / "superpowers" / "plans"
TASK_RE = re.compile(r"^### Task (\d+): (.+?)\s*$")
STEP_RE = re.compile(r"^- \[([ xX])\] (.*)$")
HEADING_RE = re.compile(r"^#{2,3} ")
GOAL_RE = re.compile(r"\*\*Goal:\*\*\s*(.*)")


def port_for(root):
    """A port in 7800..7899 that is stable for one repository path."""
    return 7800 + zlib.crc32(str(Path(root).resolve()).encode("utf-8")) % 100


def status_for(steps):
    done = sum(1 for s in steps if s["done"])
    if done == 0:
        return "backlog"
    if done == len(steps):
        return "done"
    return "in_progress"


def parse_plan(text):
    """Title, goal and tasks of one plan. Fenced code blocks are skipped."""
    title = ""
    goal = ""
    tasks = []
    current = None
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not title and line.startswith("# "):
            title = line[2:].strip()
            continue
        if not goal:
            m = GOAL_RE.search(line)
            if m:
                goal = m.group(1).strip()
                continue
        m = TASK_RE.match(line)
        if m:
            current = {"number": int(m.group(1)), "title": m.group(2), "steps": []}
            tasks.append(current)
            continue
        if HEADING_RE.match(line):
            current = None
            continue
        m = STEP_RE.match(line)
        if m and current is not None:
            current["steps"].append({"text": m.group(2).replace("**", "").strip(),
                                     "done": m.group(1) in "xX"})
    for task in tasks:
        task["status"] = status_for(task["steps"])
    return {"title": title, "goal": goal, "tasks": tasks}


def pick_plan(candidates):
    """candidates: (basename, has_unchecked). Newest name with an open step, else newest."""
    if not candidates:
        return None
    ordered = sorted(candidates, key=lambda c: c[0], reverse=True)
    for name, has_unchecked in ordered:
        if has_unchecked:
            return name
    return ordered[0][0]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest tests/test_plan_board.py 2>&1 | tail -3`
Expected: `Ran 10 tests` … `OK`, exit code 0.

- [ ] **Step 5: Commit**

```bash
bash scripts/check-forbidden-words.sh scripts/plan-board.py tests/test_plan_board.py
git add scripts/plan-board.py tests/test_plan_board.py
git commit -m "Parse plan files into board tasks"
```

---

### Task 2: Board loading and the HTTP server

**Files:**
- Modify: `scripts/plan-board.py` (append below `pick_plan`)
- Modify: `tests/test_plan_board.py` (append)

**Interfaces:**
- Consumes: `parse_plan`, `pick_plan`, `port_for`, `PLAN_DIR` from Task 1.
- Produces: `list_plans(root) -> list[str]` (sorted basenames of `*.md` files in the plan folder, `[]` when missing).
- Produces: `load_board(root, name=None) -> dict` with keys `root`, `plan`, `plans`, `errors`, `title`, `goal`, `tasks`.
- Produces: `make_server(root, port, verbose=False) -> ThreadingHTTPServer` bound to `127.0.0.1`; `port=0` picks a free one.
- Produces: `healthz(port) -> str | None` (the `root` a running server reports, `None` when nothing answers).
- Produces: `main(argv=None) -> int`.
- Produces: module constant `PAGE: str`, filled in Task 3; for this task it is the placeholder `"<!doctype html><title>plan board</title>"`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_plan_board.py`, above `if __name__ == "__main__":`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_plan_board.py 2>&1 | tail -3`
Expected: `FAILED (errors=N)` with `AttributeError: module 'plan_board' has no attribute 'load_board'` and the like, exit code 1.

- [ ] **Step 3: Write the loader, the server and main**

Append to `scripts/plan-board.py`:

```python
def list_plans(root):
    folder = Path(root) / PLAN_DIR
    if not folder.is_dir():
        return []
    return sorted(p.name for p in folder.iterdir() if p.is_file() and p.suffix == ".md")


def load_board(root, name=None):
    """The JSON the page renders: one plan's tasks plus the list of every plan."""
    root = Path(root).resolve()
    names = list_plans(root)
    parsed = {}
    errors = {}
    for n in names:
        try:
            parsed[n] = parse_plan((root / PLAN_DIR / n).read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            errors[n] = "not UTF-8"
    candidates = [(n, any(not s["done"] for t in p["tasks"] for s in t["steps"]))
                  for n, p in parsed.items()]
    chosen = name if name in parsed else pick_plan(candidates)
    board = {"root": str(root), "plan": chosen, "plans": names, "errors": errors,
             "title": "", "goal": "", "tasks": []}
    if chosen:
        board.update(parsed[chosen])
    return board


PAGE = "<!doctype html><title>plan board</title>"


def make_server(root, port, verbose=False):
    root = Path(root).resolve()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            if verbose:
                super().log_message(fmt, *args)

        def do_GET(self):
            url = urlparse(self.path)
            if url.path == "/healthz":
                return self._json({"root": str(root)})
            if url.path == "/api/board":
                plan = parse_qs(url.query).get("plan", [None])[0]
                return self._json(load_board(root, plan))
            if url.path == "/":
                return self._send(200, "text/html; charset=utf-8", PAGE.encode("utf-8"))
            self._send(404, "text/plain; charset=utf-8", b"not found\n")

        def _json(self, obj):
            self._send(200, "application/json", json.dumps(obj).encode("utf-8"))

        def _send(self, code, ctype, body):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def healthz(port):
    """The root a server on this port reports, or None when nothing answers."""
    try:
        with urlopen(f"http://127.0.0.1:{port}/healthz", timeout=1) as r:
            return json.loads(r.read()).get("root")
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Serve a read-only board of docs/superpowers/plans.")
    ap.add_argument("--root", default=".", help="repository root (default: current directory)")
    ap.add_argument("--port", type=int, help="port on 127.0.0.1 (default: derived from the root path)")
    ap.add_argument("--verbose", action="store_true", help="log one line per request to stderr")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"root is not a directory: {args.root}", file=sys.stderr)
        return 2
    port = args.port or port_for(root)
    url = f"http://127.0.0.1:{port}/"
    try:
        server = make_server(root, port, args.verbose)
    except OSError:
        if healthz(port) == str(root):
            print(url, flush=True)
            return 0
        print(f"port {port} is in use by another process; pass --port", file=sys.stderr)
        return 1
    print(url, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest tests/test_plan_board.py 2>&1 | tail -3`
Expected: `Ran 20 tests` … `OK`, exit code 0.

- [ ] **Step 5: Smoke the CLI once**

Run from the repo root:

```bash
python3 scripts/plan-board.py --root tests/fixtures/greenfield-with-plan --port 7899 & sleep 0.5; curl -s http://127.0.0.1:7899/healthz; echo; python3 scripts/plan-board.py --root tests/fixtures/greenfield-with-plan --port 7899; echo "exit $?"; kill %1
```

Expected: the first process prints `http://127.0.0.1:7899/`; curl prints `{"root": "<abs>/tests/fixtures/greenfield-with-plan"}`; the second invocation prints the same URL and `exit 0` (reuse); the background job is killed.

- [ ] **Step 6: Commit**

```bash
bash scripts/check-forbidden-words.sh scripts/plan-board.py tests/test_plan_board.py
git add scripts/plan-board.py tests/test_plan_board.py
git commit -m "Serve the plan board on 127.0.0.1"
```

---

### Task 3: The board page

**Files:**
- Modify: `scripts/plan-board.py` (replace the `PAGE` placeholder)
- Modify: `tests/test_plan_board.py` (one assertion added to `Server.test_page`)

**Interfaces:**
- Consumes: `/api/board?plan=` JSON from Task 2.
- Produces: `PAGE` as the full page: header, plan dropdown, three columns, cards, 3-second polling, light and dark colours, the empty-state line.

- [ ] **Step 1: Extend the failing test**

In `tests/test_plan_board.py`, replace the body of `Server.test_page` with:

```python
    def test_page(self):
        status, ctype, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertTrue(ctype.startswith("text/html"))
        html = body.decode("utf-8")
        self.assertIn("<!doctype html>", html.lower())
        for heading in ("Backlog", "In progress", "Done"):
            self.assertIn(heading, html)
        self.assertIn("/api/board", html)
        self.assertIn("no plan found under docs/superpowers/plans", html)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest tests.test_plan_board.Server.test_page 2>&1 | tail -3`
Expected: `FAILED (failures=1)`, `'Backlog' not found`, exit code 1.

- [ ] **Step 3: Write the page**

In `scripts/plan-board.py`, replace the line `PAGE = "<!doctype html><title>plan board</title>"` with:

```python
PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plan board</title>
<style>
  :root {
    --bg: #f6f5f2; --panel: #ffffff; --ink: #1d1d1b; --muted: #6b6a66; --line: #e3e1dc;
    --backlog: #8a8f98; --progress: #d98b1f; --done: #3a9d5d; --tick: #3a9d5d;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #161615; --panel: #1f1f1d; --ink: #ecebe7; --muted: #9c9a94; --line: #2e2e2b; }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--ink);
         font: 14px/1.45 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
  header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 16px;
           padding: 14px 16px 10px; border-bottom: 1px solid var(--line); }
  header .repo { font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
  header h1 { font-size: 16px; margin: 0; font-weight: 600; }
  header .goal { flex-basis: 100%; color: var(--muted); margin: 0; }
  header select { margin-left: auto; font: inherit; background: var(--panel); color: var(--ink);
                  border: 1px solid var(--line); border-radius: 6px; padding: 3px 6px; }
  main { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; padding: 12px 16px 24px; }
  @media (max-width: 700px) { main { grid-template-columns: 1fr; } }
  .col h2 { font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted);
            margin: 0 0 8px; display: flex; align-items: center; gap: 8px; }
  .col h2::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--dot); }
  .col h2 .count { margin-left: auto; font-weight: 400; }
  .col-backlog { --dot: var(--backlog); } .col-in_progress { --dot: var(--progress); } .col-done { --dot: var(--done); }
  .card { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; }
  .card .num { font-size: 11px; color: var(--muted); }
  .card .title { font-weight: 600; margin: 1px 0 4px; }
  .card .tally { font-size: 12px; color: var(--muted); margin-bottom: 6px; }
  .card ul { list-style: none; margin: 0; padding: 0; }
  .card li { display: flex; gap: 6px; font-size: 12.5px; color: var(--muted); padding: 1px 0; }
  .card li.done { text-decoration: line-through; }
  .card li .box { flex: none; width: 12px; height: 12px; margin-top: 3px; border: 1px solid var(--muted);
                  border-radius: 3px; }
  .card li.done .box { background: var(--tick); border-color: var(--tick); }
  .empty { grid-column: 1 / -1; color: var(--muted); padding: 24px 0; text-align: center; }
  .errors { grid-column: 1 / -1; color: var(--progress); font-size: 12px; }
</style>
</head>
<body>
<header>
  <span class="repo" id="repo"></span>
  <h1 id="title"></h1>
  <select id="plans" hidden></select>
  <p class="goal" id="goal"></p>
</header>
<main id="board"></main>
<script>
(function () {
  const COLUMNS = [["backlog", "Backlog"], ["in_progress", "In progress"], ["done", "Done"]];
  const EMPTY = "no plan found under docs/superpowers/plans";
  const planParam = new URLSearchParams(location.search).get("plan");
  let last = "";

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function render(board) {
    document.getElementById("repo").textContent = board.root.split("/").pop();
    document.getElementById("title").textContent = board.title || board.plan || "";
    document.getElementById("goal").textContent = board.goal || "";
    document.title = (board.title ? board.title + " · " : "") + "Plan board";

    const select = document.getElementById("plans");
    select.hidden = board.plans.length < 2;
    select.replaceChildren(...board.plans.map(function (name) {
      const o = el("option", "", name); o.value = name; o.selected = name === board.plan; return o;
    }));

    const main = document.getElementById("board");
    main.replaceChildren();
    if (!board.plan) { main.appendChild(el("p", "empty", EMPTY)); return; }
    COLUMNS.forEach(function (c) {
      const tasks = board.tasks.filter(function (t) { return t.status === c[0]; });
      const col = el("section", "col col-" + c[0]);
      const h = el("h2", "", c[1]); h.appendChild(el("span", "count", String(tasks.length))); col.appendChild(h);
      tasks.forEach(function (t) {
        const card = el("article", "card");
        card.appendChild(el("div", "num", "Task " + t.number));
        card.appendChild(el("div", "title", t.title));
        const done = t.steps.filter(function (s) { return s.done; }).length;
        card.appendChild(el("div", "tally", done + "/" + t.steps.length + " steps"));
        const ul = el("ul");
        t.steps.forEach(function (s) {
          const li = el("li", s.done ? "done" : ""); li.appendChild(el("span", "box")); li.appendChild(el("span", "", s.text)); ul.appendChild(li);
        });
        card.appendChild(ul); col.appendChild(card);
      });
      main.appendChild(col);
    });
    const broken = Object.keys(board.errors || {});
    if (broken.length) main.appendChild(el("p", "errors", "skipped (" + board.errors[broken[0]] + "): " + broken.join(", ")));
  }

  async function poll() {
    try {
      const r = await fetch("/api/board" + (planParam ? "?plan=" + encodeURIComponent(planParam) : ""), { cache: "no-store" });
      const text = await r.text();
      if (text !== last) { last = text; render(JSON.parse(text)); }
    } catch (e) { /* server restarting; try again on the next tick */ }
  }

  document.getElementById("plans").addEventListener("change", function (e) {
    location.search = "?plan=" + encodeURIComponent(e.target.value);
  });
  poll();
  setInterval(poll, 3000);
})();
</script>
</body>
</html>
"""
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest tests/test_plan_board.py 2>&1 | tail -3`
Expected: `Ran 20 tests` … `OK`, exit code 0.

- [ ] **Step 5: Look at it once in the preview pane**

Run from the repo root: `python3 scripts/plan-board.py --root tests/fixtures/greenfield-with-plan --port 7898` in the background, then `navigate` (or `preview_start`) to `http://127.0.0.1:7898/`, one screenshot. Expected: header "greenfield-with-plan / Todo API Implementation Plan", the goal line, Backlog with Task 2 and Task 3, In progress empty, Done with Task 1 and three struck-through steps. Then kill the server.

- [ ] **Step 6: Commit**

```bash
bash scripts/check-forbidden-words.sh scripts/plan-board.py tests/test_plan_board.py
git add scripts/plan-board.py tests/test_plan_board.py
git commit -m "Render the plan board page"
```

---

### Task 4: The /fabreak:board command, docs, CI and version

**Files:**
- Create: `skills/board/SKILL.md`
- Modify: `skills/fabreak/board.md` (insert a section before `## CLI fallback`)
- Modify: `.github/workflows/check.yml` (one step after "Checker self-test")
- Modify: `README.md` (Entries table, Layout block)
- Modify: `CONTRIBUTING.md` (check list)
- Modify: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (version)

**Interfaces:**
- Consumes: `scripts/plan-board.py` CLI from Task 2 (`--root`, `--port`, the `/healthz` route, the port formula).

- [ ] **Step 1: Write the command skill**

Create `skills/board/SKILL.md`:

```markdown
---
name: board
description: "fabreak: open the read-only plan board in the preview pane."
disable-model-invocation: true
---

# board

Opens the plan board: a read-only kanban view of `docs/superpowers/plans`, served by `${CLAUDE_PLUGIN_ROOT}/scripts/plan-board.py` on 127.0.0.1. The sidebar board (`${CLAUDE_PLUGIN_ROOT}/skills/fabreak/board.md`) stays the live view of sessions; this page is the live view of the plan.

## Steps

1. Root: `git rev-parse --show-toplevel`. In a task worktree that is the worktree, and the board shows the plan on its branch.
2. Port: `python3 -c 'import zlib,sys,pathlib; print(7800 + zlib.crc32(str(pathlib.Path(sys.argv[1]).resolve()).encode()) % 100)' "<root>"`. Then `curl -s http://127.0.0.1:<port>/healthz`. A reply whose `root` equals the root means the server is up; go to step 4.
3. Start it in the background: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan-board.py" --root "<root>"`. Probe `/healthz` again, up to 10 times 0.3 s apart. Exit 1 from the script means another process owns the port: rerun with `--port <port+100>` and use that port from here on. No `python3` on PATH: say so in one line and go to step 5.
4. Open the pane: `navigate` to `http://127.0.0.1:<port>/`. When `navigate` reports that no pane is open, `preview_start` with the same URL, once. One screenshot. Done when the header and the three columns (Backlog, In progress, Done) are visible.
5. Without browser tools (plain `claude` in a terminal): print the URL and the CLI fallback from `board.md`.

## Done when

The pane shows the board, or the URL and the CLI fallback are printed.
```

- [ ] **Step 2: Point board.md at it**

In `skills/fabreak/board.md`, insert before the line `## CLI fallback`:

```markdown
## Plan board

In the desktop app, "Show the board" also opens the plan board: a read-only page of the plan's tasks in Backlog, In progress and Done, derived from each task's ticked steps alone. Run the steps of the `board` command, `${CLAUDE_PLUGIN_ROOT}/skills/board/SKILL.md`. The sidebar sections above stay the live view of sessions; the plan board reaches Done when a task's last step is ticked, before the merge. Done when the pane shows the board.

```

- [ ] **Step 3: CI, README, CONTRIBUTING, version**

In `.github/workflows/check.yml`, after the "Checker self-test" step add:

```yaml
      - name: Plan board tests
        run: python3 -m unittest tests/test_plan_board.py
```

In `README.md`, add to the Entries table after the `closing` row:

```markdown
| `/fabreak:board` | open the read-only plan board in the preview pane |
```

and in the Layout block, after the `hosting.md` line:

```
skills/board/SKILL.md        the /fabreak:board command: starts the plan board and opens it in the preview pane
scripts/plan-board.py        the plan board server: one page from docs/superpowers/plans, read-only, 127.0.0.1
```

In `README.md` Limits, replace the first bullet with:

```markdown
- The board (Backlog, In progress, Waiting on me, Review, Done) lives in the Claude Code desktop sidebar; `/fabreak:board` adds a read-only page of the plan's tasks in the preview pane. In the terminal CLI, fabreak prints the board as text from the plan instead.
```

In `CONTRIBUTING.md`, step 2's code block gains a line after the self-test:

```bash
python3 -m unittest tests/test_plan_board.py
```

Set `"version": "0.3.0"` in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.

- [ ] **Step 4: Verify**

Run from the repo root:

```bash
bash scripts/check-forbidden-words.sh --all && bash tests/forbidden-words.test.sh && python3 -m unittest tests/test_plan_board.py && claude plugin validate --strict .
```

Expected: no forbidden-word output, `all checks passed`, `OK`, and the validator's success line; exit code 0. Then run the command's steps 1 to 4 on this repository itself (its plan folder holds two plans) and confirm the dropdown shows both and the default is this plan, since it still has unchecked steps.

- [ ] **Step 5: Commit**

```bash
git add skills/board/SKILL.md skills/fabreak/board.md .github/workflows/check.yml README.md CONTRIBUTING.md .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "Add the /fabreak:board command"
```

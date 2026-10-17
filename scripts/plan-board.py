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

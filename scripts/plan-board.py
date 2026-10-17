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

#!/usr/bin/env python3
"""Plan board: a read-only, live kanban view of docs/superpowers/plans/*.md.

Usage: plan-board.py [--root DIR] [--port N] [--verbose]

Serves one page on 127.0.0.1 that shows every task of a plan in Backlog,
In progress, Review or Done, from the plan's steps (ticked in the plan or
in the task's own worktree), the repository's worktrees (git) and its pull
requests (gh, when present). A poller thread
watches all three and pushes each change to the page over Server-Sent
Events. Writes nothing. Standard library only.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen

PLAN_DIR = Path("docs") / "superpowers" / "plans"
TASK_RE = re.compile(r"^### Task (\d+): (.+?)\s*$")
STEP_RE = re.compile(r"^- \[([ xX/-])\] (.*)$")
MARKS = {" ": "open", "/": "doing", "x": "done", "X": "done", "-": "skipped"}
RANK = {"open": 0, "doing": 1, "skipped": 2, "done": 3}
HEADING_RE = re.compile(r"^#{2,3} ")
GOAL_RE = re.compile(r"\*\*Goal:\*\*\s*(.*)")
DEPENDS_RE = re.compile(r"depends on", re.IGNORECASE)
TASK_REF_RE = re.compile(r"\bTask (\d+)\b")
HEX_TAIL_RE = re.compile(r"-[0-9a-f]{6}$")
NUMBER_RE = re.compile(r"^(?:task-?)?0*(\d+)(?:-|$)", re.IGNORECASE)
API = 3
GIT_TIMEOUT = 5
GH_TIMEOUT = 15
PING_EVERY = 15


def port_for(root):
    """A port in 7800..7899 that is stable for one repository path."""
    return 7800 + zlib.crc32(str(Path(root).resolve()).encode("utf-8")) % 100


def step_state(step):
    return step.get("state") or ("done" if step["done"] else "open")


def is_open(step):
    return step_state(step) in ("open", "doing")


def status_for(steps):
    states = [step_state(s) for s in steps]
    if steps and all(st in ("done", "skipped") for st in states):
        return "done"
    if any(st in ("done", "doing") for st in states):
        return "in_progress"
    return "backlog"


def trim_blank(lines):
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


def parse_plan(text):
    """Title, goal and tasks of one plan. Fenced code blocks hold no steps or headings."""
    title = ""
    goal = ""
    tasks = []
    current = None
    in_fence = False
    for line in text.splitlines():
        fence = line.startswith("```")
        if fence:
            in_fence = not in_fence
        if fence or in_fence:
            if current is not None:
                current["lines"].append(line)
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
            current = {"number": int(m.group(1)), "title": m.group(2), "steps": [], "depends": None, "lines": []}
            tasks.append(current)
            continue
        if HEADING_RE.match(line):
            current = None
            continue
        if current is None:
            continue
        current["lines"].append(line)
        if current["depends"] is None and DEPENDS_RE.search(line):
            current["depends"] = [int(n) for n in TASK_REF_RE.findall(line)]
        m = STEP_RE.match(line)
        if m:
            state = MARKS[m.group(1)]
            current["steps"].append({"text": m.group(2).replace("**", "").strip(),
                                     "done": state == "done", "state": state})
    for task in tasks:
        task["status"] = status_for(task["steps"])
        task["body"] = "\n".join(trim_blank(task.pop("lines")))
        refs = task["depends"] or []
        task["depends"] = [n for i, n in enumerate(refs) if n != task["number"] and n not in refs[:i]]
    return {"title": title, "goal": goal, "tasks": tasks}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def branch_key(branch):
    """The part of a branch name that names its task: the last segment without a 6-hex suffix."""
    return slug(HEX_TAIL_RE.sub("", branch.rsplit("/", 1)[-1]))


def branch_number(branch):
    """The task number a branch names in its last segment (`02-capture`, `task-7`), or None."""
    m = NUMBER_RE.match(branch.rsplit("/", 1)[-1])
    return int(m.group(1)) if m else None


def match_tasks(tasks, worktrees, prs, plan=None):
    """{task number: live info or None}, from the repository's worktrees and PRs.

    A worktree whose branch names a task number matches that task only when its
    checkout holds `plan`, so branches cut for an earlier plan stay out."""
    slugs = {t["number"]: slug(t["title"]) for t in tasks}

    def numbered(n):
        hits = [w for w in worktrees if branch_number(w["branch"]) == n and plan in (w.get("plans") or {})]
        return hits[0] if len(hits) == 1 else None

    def branch_pr(branch):
        found = sorted((p for p in prs or [] if p.get("headRefName") == branch and p.get("state") in ("OPEN", "MERGED")),
                       key=lambda p: p["state"] != "OPEN")
        return found[0] if found else None

    def owner(branch):
        key = branch_key(branch or "")
        hits = [n for n, s in slugs.items() if key and s and (key == s or (len(key) >= 8 and s.startswith(key)))]
        return hits[0] if len(hits) == 1 else None

    worktrees = worktrees or []
    by_branch = {w["branch"]: w for w in worktrees}
    out = {}
    for t in tasks:
        n = t["number"]
        heading = f"task {n}: {t['title']}".lower()
        found = [p for p in prs or [] if p.get("state") in ("OPEN", "MERGED") and (
            heading in (p.get("title", "") + "\n" + (p.get("body") or "")).lower()
            or slug(p.get("title", "")) == slugs[n]
            or owner(p.get("headRefName")) == n)]
        found.sort(key=lambda p: p["state"] != "OPEN")
        pr = found[0] if found else None
        wt = by_branch.get(pr.get("headRefName")) if pr else None
        if wt is None:
            wt = next((w for w in worktrees if owner(w["branch"]) == n), None) or numbered(n)
            if pr is None and wt is not None:
                pr = branch_pr(wt["branch"])
        if pr is None and wt is None:
            out[n] = None
            continue
        out[n] = {
            "branch": wt["branch"] if wt else pr.get("headRefName"),
            "worktree": wt["path"] if wt else None,
            "ahead": wt["ahead"] if wt else 0,
            "dirty": wt["dirty"] if wt else False,
            "pr": {k: pr.get(k) for k in ("number", "state", "url", "title")} if pr else None,
        }
    return out


def resolve_status(steps, live):
    plan_only = status_for(steps)
    pr_state = live["pr"]["state"] if live and live.get("pr") else None
    if plan_only == "done" or pr_state == "MERGED":
        return "done"
    if pr_state == "OPEN":
        return "review"
    if plan_only == "in_progress" or (live and (live["ahead"] or live["dirty"])):
        return "in_progress"
    return "backlog"


def merge_steps(plan_steps, tree_steps):
    """A task's steps from the root plan and from its worktree's copy: per step the further state wins.

    When the counts differ, the branch replanned the task and its copy stands as it is."""
    if len(plan_steps) != len(tree_steps):
        return tree_steps
    out = []
    for a, b in zip(plan_steps, tree_steps):
        state = max(step_state(a), step_state(b), key=RANK.get)
        out.append({"text": b["text"], "done": state == "done", "state": state})
    return out


def run(args, cwd, timeout):
    """stdout of a command that exited 0, else None."""
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout if r.returncode == 0 else None


def read_git(root):
    """The default branch and every worktree on another branch, or None outside a repository's top level."""
    root = Path(root).resolve()
    top = run(["git", "rev-parse", "--show-toplevel"], root, GIT_TIMEOUT)
    if top is None or Path(top.strip()).resolve() != root:
        return None

    def has(ref):
        return run(["git", "rev-parse", "--verify", "-q", ref], root, GIT_TIMEOUT) is not None

    head = (run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], root, GIT_TIMEOUT) or "").strip()
    default = head.split("/", 1)[1] if "/" in head else next((b for b in ("main", "master") if has("refs/heads/" + b)), None)
    base = None
    if default:
        base = default if has("refs/heads/" + default) else ("origin/" + default if has("origin/" + default) else None)

    worktrees = []
    listing = run(["git", "worktree", "list", "--porcelain"], root, GIT_TIMEOUT) or ""
    for block in listing.strip().split("\n\n"):
        fields = dict((line.split(" ", 1) + [""])[:2] for line in block.splitlines() if line)
        branch = fields.get("branch", "").removeprefix("refs/heads/")
        if not branch or branch == default or "prunable" in fields:
            continue
        path = fields.get("worktree", "")
        ahead = run(["git", "rev-list", "--count", f"{base}..{branch}"], root, GIT_TIMEOUT) if base else None
        status = run(["git", "-C", path, "status", "--porcelain"], root, GIT_TIMEOUT)
        worktrees.append({"path": path, "branch": branch, "ahead": int(ahead) if ahead else 0,
                          "dirty": bool(status and status.strip()), "plans": plan_texts(path)})
    return {"default": default, "worktrees": worktrees}


def plan_texts(path):
    """{basename: text} of every readable plan in one checkout, uncommitted edits included."""
    texts = {}
    for name in list_plans(path):
        try:
            texts[name] = (Path(path) / PLAN_DIR / name).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            pass
    return texts


def read_prs(root):
    """Recent pull requests from gh, or None when gh is missing or fails."""
    if shutil.which("gh") is None:
        return None
    out = run(["gh", "pr", "list", "--state", "all", "--limit", "100",
               "--json", "number,title,state,url,headRefName,body"], Path(root).resolve(), GH_TIMEOUT)
    try:
        return json.loads(out) if out else None
    except ValueError:
        return None


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


def plan_signature(root):
    """Changes whenever a plan file is added, removed or edited."""
    folder = Path(root) / PLAN_DIR
    sig = []
    for name in list_plans(root):
        try:
            sig.append((name, zlib.crc32((folder / name).read_bytes())))
        except OSError:
            sig.append((name, None))
    return tuple(sig)


def load_board(root, name=None, data=None):
    """The JSON the page renders: one plan's tasks, resolved against git and PRs, plus every plan's name."""
    root = Path(root).resolve()
    git = (data or {}).get("git")
    prs = (data or {}).get("prs")
    names = list_plans(root)
    parsed = {}
    errors = {}
    for n in names:
        try:
            parsed[n] = parse_plan((root / PLAN_DIR / n).read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            errors[n] = "not UTF-8"
    candidates = [(n, any(is_open(s) for t in p["tasks"] for s in t["steps"]))
                  for n, p in parsed.items()]
    chosen = name if name in parsed else pick_plan(candidates)
    board = {"root": str(root), "plan": chosen, "plans": names, "errors": errors,
             "sources": {"git": git is not None, "prs": prs is not None, "default": git["default"] if git else None},
             "title": "", "goal": "", "tasks": []}
    if chosen:
        board.update(parsed[chosen])
        worktrees = git["worktrees"] if git else []
        matches = match_tasks(board["tasks"], worktrees, prs, plan=chosen)
        used = {m["worktree"] for m in matches.values() if m and m["worktree"]}
        copies = {w["path"]: parse_plan(w["plans"][chosen])["tasks"] for w in worktrees
                  if w["path"] in used and chosen in (w.get("plans") or {})}
        for task in board["tasks"]:
            task["live"] = matches[task["number"]]
            task["plan_status"] = task["status"]
            task["steps_from"] = "plan"
            copy = copies.get(task["live"]["worktree"], []) if task["live"] else []
            twin = next((t for t in copy if t["number"] == task["number"]), None)
            if twin is not None:
                task["steps"] = merge_steps(task["steps"], twin["steps"])
                task["body"] = twin["body"]
                task["steps_from"] = "worktree"
            task["status"] = resolve_status(task["steps"], task["live"])
    return board


class Live:
    """Polls the plan files, git and PRs in one daemon thread and wakes every stream when one changes."""

    def __init__(self, root, git=True, prs=True, plan_every=0.5, git_every=3.0, prs_every=30.0):
        self.root = Path(root).resolve()
        self.use_git = git
        self.use_prs = prs
        self.every = {"plans": plan_every, "git": git_every, "prs": prs_every}
        self.due = {k: 0.0 for k in self.every}
        self.data = {"git": None, "prs": None}
        self.version = 0
        self.stopped = False
        self.cond = threading.Condition()
        self._plans = None
        self._halt = threading.Event()
        self._thread = None

    def start(self):
        if self._thread is None:
            self.poll(time.monotonic(), prs=False)
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
        return self

    def stop(self):
        self._halt.set()
        with self.cond:
            self.stopped = True
            self.cond.notify_all()

    def wait(self, version, timeout):
        """The current version, once it differs from `version`, the poller stops, or `timeout` passes."""
        with self.cond:
            self.cond.wait_for(lambda: self.version != version or self.stopped, timeout)
            return self.version

    def _loop(self):
        while not self._halt.wait(min(self.every.values())):
            self.poll(time.monotonic())

    def _due(self, source, now):
        if now < self.due[source]:
            return False
        self.due[source] = now + self.every[source]
        return True

    def poll(self, now, prs=True):
        changed = False
        if self._due("plans", now):
            sig = plan_signature(self.root)
            if sig != self._plans:
                self._plans = sig
                changed = True
        if self.use_git and self._due("git", now):
            git = read_git(self.root)
            if git != self.data["git"]:
                self.data = {**self.data, "git": git}
                changed = True
        if prs and self.use_prs and self.data["git"] is not None and self._due("prs", now):
            found = read_prs(self.root)
            if found is not None and found != self.data["prs"]:
                self.data = {**self.data, "prs": found}
                changed = True
        if changed:
            with self.cond:
                self.version += 1
                self.cond.notify_all()


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plan board</title>
<style>
  :root {
    --bg: #f6f5f2; --panel: #ffffff; --ink: #1d1d1b; --muted: #6b6a66; --line: #e3e1dc; --soft: #efede8;
    --backlog: #8a8f98; --progress: #d98b1f; --review: #6f63d9; --done: #3a9d5d; --tick: #3a9d5d;
    --accent: #2f6fdb; --flash: #fff4d6; --warn: #b5651d;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #161615; --panel: #1f1f1d; --ink: #ecebe7; --muted: #9c9a94; --line: #2e2e2b; --soft: #272725;
            --accent: #6f9bff; --flash: #3a3320; --warn: #e09a55; }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--ink);
         font: 14px/1.45 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
  button, input, select { font: inherit; color: inherit; }
  header { padding: 14px 16px 8px; border-bottom: 1px solid var(--line); }
  header .row { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 14px; }
  header .repo { font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
  header h1 { font-size: 16px; margin: 0; font-weight: 600; }
  header .goal { color: var(--muted); margin: 4px 0 0; }
  header select { margin-left: auto; background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 3px 6px; }
  .live { font-size: 12px; color: var(--muted); display: inline-flex; align-items: center; gap: 6px; }
  .live::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--backlog); }
  .live-live::before { background: var(--done); box-shadow: 0 0 0 3px color-mix(in srgb, var(--done) 25%, transparent); }
  .live-retry::before { background: var(--progress); }
  .tools { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; margin-top: 10px; }
  .tools input { flex: 1 1 220px; min-width: 0; background: var(--panel); border: 1px solid var(--line);
                 border-radius: 6px; padding: 5px 9px; }
  .tools input:focus, .card:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
  #chips { display: flex; flex-wrap: wrap; gap: 6px; }
  #chips button { border: 1px solid var(--line); background: var(--panel); border-radius: 999px; padding: 2px 10px;
                  font-size: 12px; cursor: pointer; color: var(--muted); }
  #chips button[aria-pressed="true"] { color: var(--ink); border-color: var(--muted); }
  #chips button[aria-pressed="false"] { text-decoration: line-through; opacity: .6; }
  .sources { font-size: 12px; color: var(--muted); margin-left: auto; }
  #activity { margin-top: 8px; font-size: 12px; color: var(--muted); }
  #activity summary { cursor: pointer; width: max-content; }
  #activity ol { list-style: none; margin: 6px 0 0; padding: 0; max-height: 140px; overflow: auto; }
  #activity li { padding: 1px 0; } #activity time { font-variant-numeric: tabular-nums; margin-right: 8px; }
  main { display: grid; grid-template-columns: repeat(var(--cols, 4), minmax(0, 1fr)); gap: 12px; padding: 12px 16px 24px; }
  @media (min-width: 1280px) { body.detail-open main { padding-right: 436px; } }
  @media (max-width: 960px) { main { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 560px) { main { grid-template-columns: 1fr; } }
  .col h2 { font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted);
            margin: 0 0 8px; display: flex; align-items: center; gap: 8px; }
  .col h2::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--dot); }
  .col h2 .count { margin-left: auto; font-weight: 400; }
  .col-backlog { --dot: var(--backlog); } .col-in_progress { --dot: var(--progress); }
  .col-review { --dot: var(--review); } .col-done { --dot: var(--done); }
  .card { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;
          cursor: pointer; transition: border-color .15s; }
  .card:hover { border-color: var(--muted); }
  .card.selected { border-color: var(--accent); }
  .card.flash { animation: flash 1.6s ease-out; }
  @keyframes flash { from { background: var(--flash); box-shadow: 0 0 0 3px var(--accent); } to { box-shadow: 0 0 0 0 transparent; } }
  @media (prefers-reduced-motion: reduce) { .card.flash { animation: none; border-color: var(--accent); } }
  .num { font-size: 11px; color: var(--muted); }
  .card .title { font-weight: 600; margin: 1px 0 6px; }
  .progress { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--muted); }
  .bar { flex: 1; height: 4px; border-radius: 2px; background: var(--soft); overflow: hidden; }
  .bar span { display: block; height: 100%; background: var(--dot, var(--tick)); }
  .card .next { font-size: 12.5px; color: var(--muted); margin-top: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .badges { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
  .badge { font-size: 11px; border: 1px solid var(--line); border-radius: 4px; padding: 0 5px; color: var(--muted);
           max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  .warn { color: var(--warn); border-color: currentColor; }
  .pr-open { color: var(--review); border-color: currentColor; } .pr-merged { color: var(--done); border-color: currentColor; }
  .empty { grid-column: 1 / -1; color: var(--muted); padding: 24px 0; text-align: center; }
  .errors { grid-column: 1 / -1; color: var(--progress); font-size: 12px; }
  #detail { position: fixed; top: 0; right: 0; bottom: 0; width: min(420px, 100%); background: var(--panel);
            border-left: 1px solid var(--line); box-shadow: -8px 0 24px rgba(0,0,0,.08); overflow: auto; padding: 16px 18px 24px; }
  #detail[hidden] { display: none; }
  #detail-close { position: absolute; top: 10px; right: 12px; border: 0; background: none; font-size: 20px;
                  line-height: 1; cursor: pointer; color: var(--muted); padding: 4px 6px; }
  #detail h2 { font-size: 16px; margin: 2px 32px 8px 0; }
  #detail h3 { font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 18px 0 6px; }
  .pill { display: inline-block; font-size: 11px; padding: 1px 8px; border-radius: 999px; color: #fff; background: var(--dot); }
  .pill-backlog { --dot: var(--backlog); } .pill-in_progress { --dot: var(--progress); }
  .pill-review { --dot: var(--review); } .pill-done { --dot: var(--done); }
  .muted { color: var(--muted); font-size: 12px; margin-left: 6px; }
  dl { display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; margin: 14px 0 0; font-size: 12.5px; }
  dt { color: var(--muted); } dd { margin: 0; overflow-wrap: anywhere; }
  dd a { color: var(--accent); }
  .link { border: 0; background: none; color: var(--accent); padding: 0; margin-right: 8px; cursor: pointer; text-decoration: underline; }
  .steps { list-style: none; margin: 0; padding: 0; }
  .steps li { display: flex; gap: 6px; font-size: 12.5px; color: var(--muted); padding: 2px 0; }
  .steps li.done { text-decoration: line-through; }
  .steps .box { flex: none; width: 12px; height: 12px; margin-top: 3px; border: 1px solid var(--muted); border-radius: 3px; }
  .steps li.done .box { background: var(--tick); border-color: var(--tick); }
  .steps li.doing { color: var(--ink); }
  .steps li.doing .box { border-color: var(--progress); background: linear-gradient(90deg, var(--progress) 50%, transparent 50%); }
  .steps li.skipped { text-decoration: line-through; opacity: .6; }
  .steps li.skipped .box { border-style: dashed; }
  pre { background: var(--soft); border-radius: 6px; padding: 10px; font-size: 12px; overflow: auto; white-space: pre-wrap; margin: 0; }
  .keys { font-size: 11px; color: var(--muted); padding: 0 16px 16px; }
  kbd { font: 11px ui-monospace, Menlo, monospace; border: 1px solid var(--line); border-radius: 3px; padding: 0 4px; }
</style>
</head>
<body>
<header>
  <div class="row">
    <span class="repo" id="repo"></span>
    <h1 id="title"></h1>
    <span class="live" id="live" role="status">Connecting</span>
    <select id="plans" hidden aria-label="Plan"></select>
  </div>
  <p class="goal" id="goal"></p>
  <div class="tools">
    <input id="search" type="search" placeholder="Search tasks and steps" aria-label="Search tasks and steps">
    <div id="chips" role="group" aria-label="Columns">
      <button type="button" data-col="backlog">Backlog</button>
      <button type="button" data-col="in_progress">In progress</button>
      <button type="button" data-col="review">Review</button>
      <button type="button" data-col="done">Done</button>
    </div>
    <span class="sources" id="sources"></span>
  </div>
  <details id="activity"><summary>Activity (<span id="log-count">0</span>)</summary><ol id="log"></ol></details>
</header>
<main id="board"></main>
<p class="keys"><kbd>/</kbd> search · <kbd>←</kbd><kbd>↑</kbd><kbd>↓</kbd><kbd>→</kbd> move · <kbd>Enter</kbd> details · <kbd>Esc</kbd> close · <kbd>1</kbd>–<kbd>9</kbd> plan</p>
<aside id="detail" hidden aria-label="Task detail">
  <button type="button" id="detail-close" aria-label="Close">×</button>
  <div id="detail-body"></div>
</aside>
<script>
(function () {
  const COLUMNS = [["backlog", "Backlog"], ["in_progress", "In progress"], ["review", "Review"], ["done", "Done"]];
  const NAMES = Object.fromEntries(COLUMNS);
  const PR_WORDS = { OPEN: "opened", MERGED: "merged", CLOSED: "closed" };
  const STEP_WORDS = { doing: "started", done: "ticked", skipped: "skipped" };
  function stepState(s) { return s.state || (s.done ? "done" : "open"); }
  function stepItem(s) {
    const li = el("li", stepState(s)); li.appendChild(el("span", "box")); li.appendChild(el("span", "", s.text)); return li;
  }
  const EMPTY = "no plan found under docs/superpowers/plans";
  const params = new URLSearchParams(location.search);
  const state = {
    plan: params.get("plan") || "", q: params.get("q") || "",
    hide: new Set((params.get("hide") || "").split(",").filter(Boolean)),
    board: null, open: null, flash: new Set(), log: []
  };
  let source = null;
  const $ = function (id) { return document.getElementById(id); };

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function saveUrl() {
    const p = new URLSearchParams();
    if (state.plan) p.set("plan", state.plan);
    if (state.q) p.set("q", state.q);
    if (state.hide.size) p.set("hide", Array.from(state.hide).join(","));
    const qs = p.toString();
    history.replaceState(null, "", qs ? "?" + qs : location.pathname);
  }

  function setLive(mode) {
    const words = { connecting: "Connecting", live: "Live", retry: "Reconnecting" };
    $("live").className = "live live-" + mode;
    $("live").textContent = words[mode];
  }

  function connect() {
    if (source) source.close();
    setLive("connecting");
    source = new EventSource("/api/events" + (state.plan ? "?plan=" + encodeURIComponent(state.plan) : ""));
    source.addEventListener("open", function () { setLive("live"); });
    source.addEventListener("board", function (e) { setLive("live"); update(JSON.parse(e.data)); });
    source.addEventListener("error", function () {
      setLive("retry");
      if (source.readyState === EventSource.CLOSED) setTimeout(connect, 3000);
    });
  }

  function update(board) {
    const switched = !state.board || state.board.plan !== board.plan;
    state.flash = switched ? new Set() : diff(state.board, board);
    state.board = board;
    render();
    const flashed = state.flash;
    setTimeout(function () { flashed.clear(); }, 1600);
  }

  function diff(prev, next) {
    const before = new Map(prev.tasks.map(function (t) { return [t.number, t]; }));
    const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    const flash = new Set();
    next.tasks.forEach(function (t) {
      const o = before.get(t.number);
      const lines = [];
      if (!o) lines.push("added to " + NAMES[t.status]);
      else {
        if (o.status !== t.status) lines.push("moved to " + NAMES[t.status]);
        t.steps.forEach(function (s, i) {
          const now = stepState(s), was = o.steps[i] ? stepState(o.steps[i]) : "open";
          if (now !== was && STEP_WORDS[now]) lines.push(s.text + " " + STEP_WORDS[now]);
        });
        const op = o.live && o.live.pr, np = t.live && t.live.pr;
        if (np && (!op || op.number !== np.number || op.state !== np.state)) lines.push("PR #" + np.number + " " + (PR_WORDS[np.state] || np.state.toLowerCase()));
        if (t.live && t.live.branch && !(o.live && o.live.branch)) lines.push("branch " + t.live.branch);
      }
      if (lines.length) {
        flash.add(t.number);
        lines.forEach(function (l) { state.log.unshift({ time: time, text: "Task " + t.number + ": " + l }); });
      }
    });
    state.log = state.log.slice(0, 50);
    return flash;
  }

  function matches(t) {
    const q = state.q.trim().toLowerCase();
    if (!q) return true;
    return t.title.toLowerCase().includes(q) || ("task " + t.number) === q ||
      t.steps.some(function (s) { return s.text.toLowerCase().includes(q); });
  }

  function card(t) {
    const a = el("article", "card" + (state.flash.has(t.number) ? " flash" : "") + (state.open === t.number ? " selected" : ""));
    a.tabIndex = 0;
    a.dataset.task = t.number;
    a.setAttribute("role", "button");
    a.setAttribute("aria-label", "Task " + t.number + ": " + t.title + ", " + NAMES[t.status]);
    a.appendChild(el("div", "num", "Task " + t.number));
    a.appendChild(el("div", "title", t.title));
    const done = t.steps.filter(function (s) { return s.done; }).length;
    const skipped = t.steps.filter(function (s) { return stepState(s) === "skipped"; }).length;
    const total = t.steps.length - skipped;
    if (t.steps.length) {
      const row = el("div", "progress");
      const bar = el("div", "bar"), fill = el("span");
      fill.style.width = (total ? 100 * done / total : 100) + "%";
      bar.appendChild(fill); row.appendChild(bar);
      row.appendChild(el("span", "", done + "/" + total + (skipped ? " · " + skipped + " skipped" : "")));
      a.appendChild(row);
      const next = t.steps.find(function (s) { return stepState(s) === "doing"; }) ||
        t.steps.find(function (s) { return stepState(s) === "open"; });
      if (next) a.appendChild(el("div", "next", next.text));
    }
    const badges = el("div", "badges");
    const L = t.live;
    if (L && L.branch) { const b = el("span", "badge mono", L.branch.split("/").pop()); b.title = L.branch; badges.appendChild(b); }
    if (L && L.ahead) badges.appendChild(el("span", "badge", "+" + L.ahead));
    if (L && L.dirty) badges.appendChild(el("span", "badge warn", "dirty"));
    if (L && L.pr) badges.appendChild(el("span", "badge pr-" + L.pr.state.toLowerCase(), "#" + L.pr.number + " " + L.pr.state.toLowerCase()));
    if (t.depends && t.depends.length) badges.appendChild(el("span", "badge", "after " + t.depends.join(", ")));
    if (badges.childNodes.length) a.appendChild(badges);
    return a;
  }

  function render() {
    const b = state.board;
    if (!b) return;
    $("repo").textContent = b.root.split("/").pop();
    $("title").textContent = b.title || b.plan || "";
    $("goal").textContent = b.goal || "";
    document.title = (b.title ? b.title + " · " : "") + "Plan board";

    const select = $("plans");
    select.hidden = b.plans.length < 2;
    select.replaceChildren.apply(select, b.plans.map(function (name, i) {
      const o = el("option", "", (i < 9 ? (i + 1) + ". " : "") + name);
      o.value = name; o.selected = name === b.plan; return o;
    }));

    const src = b.sources || {};
    $("sources").textContent = [src.git ? "git" + (src.default ? " · " + src.default : "") : "no git", src.prs ? "PRs" : "no PRs"].join(" · ");
    document.querySelectorAll("#chips button").forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(!state.hide.has(btn.dataset.col)));
    });

    const active = document.activeElement;
    const focused = active && active.classList && active.classList.contains("card") ? active.dataset.task : null;
    const main = $("board");
    main.replaceChildren();
    if (!b.plan) {
      main.appendChild(el("p", "empty", EMPTY));
    } else {
      const shown = COLUMNS.filter(function (c) { return !state.hide.has(c[0]); });
      main.style.setProperty("--cols", String(Math.max(shown.length, 1)));
      shown.forEach(function (c) {
        const tasks = b.tasks.filter(function (t) { return t.status === c[0] && matches(t); });
        const col = el("section", "col col-" + c[0]);
        const h = el("h2", "", c[1]); h.appendChild(el("span", "count", String(tasks.length))); col.appendChild(h);
        tasks.forEach(function (t) { col.appendChild(card(t)); });
        main.appendChild(col);
      });
      const broken = Object.keys(b.errors || {});
      if (broken.length) main.appendChild(el("p", "errors", "skipped (" + b.errors[broken[0]] + "): " + broken.join(", ")));
    }
    if (focused) { const f = main.querySelector('.card[data-task="' + focused + '"]'); if (f) f.focus({ preventScroll: true }); }
    renderDetail();
    renderLog();
  }

  function renderDetail() {
    const panel = $("detail");
    const t = state.board && state.open !== null ? state.board.tasks.find(function (x) { return x.number === state.open; }) : null;
    document.body.classList.toggle("detail-open", Boolean(t));
    panel.hidden = !t;
    if (!t) return;
    const body = $("detail-body");
    body.replaceChildren();
    body.appendChild(el("div", "num", "Task " + t.number));
    body.appendChild(el("h2", "", t.title));
    body.appendChild(el("span", "pill pill-" + t.status, NAMES[t.status]));
    if (t.plan_status && t.plan_status !== t.status) body.appendChild(el("span", "muted", "the root plan says " + NAMES[t.plan_status]));

    const dl = el("dl");
    function fact(k, v) {
      dl.appendChild(el("dt", "", k));
      const dd = el("dd");
      if (typeof v === "string") dd.textContent = v; else dd.appendChild(v);
      dl.appendChild(dd);
    }
    if (t.depends.length) {
      const span = el("span");
      t.depends.forEach(function (n) {
        const btn = el("button", "link", "Task " + n); btn.type = "button";
        btn.addEventListener("click", function () { openDetail(n); });
        span.appendChild(btn);
      });
      fact("Depends on", span);
    }
    const L = t.live;
    fact("Ticks", t.steps_from === "worktree" ? "from the worktree" : "from the plan");
    if (L && L.branch) fact("Branch", L.branch);
    if (L && L.worktree) {
      fact("Worktree", L.worktree);
      fact("Ahead", L.ahead + " commit" + (L.ahead === 1 ? "" : "s") + (L.dirty ? ", uncommitted changes" : ""));
    }
    if (L && L.pr) {
      const a = el("a", "", "#" + L.pr.number + " " + L.pr.title + " (" + L.pr.state.toLowerCase() + ")");
      a.href = L.pr.url; a.target = "_blank"; a.rel = "noopener";
      fact("PR", a);
    }
    if (!L) fact("Git", state.board.sources && state.board.sources.git ? "no branch or PR matched" : "not read");
    body.appendChild(dl);

    if (t.steps.length) {
      body.appendChild(el("h3", "", "Steps"));
      const ul = el("ul", "steps");
      t.steps.forEach(function (s) { ul.appendChild(stepItem(s)); });
      body.appendChild(ul);
    }
    if (t.body) { body.appendChild(el("h3", "", "Plan text")); body.appendChild(el("pre", "", t.body)); }
  }

  function renderLog() {
    $("log-count").textContent = String(state.log.length);
    const ol = $("log");
    ol.replaceChildren();
    if (!state.log.length) { ol.appendChild(el("li", "", "No changes since this page opened.")); return; }
    state.log.forEach(function (e) {
      const li = el("li"); li.appendChild(el("time", "", e.time)); li.appendChild(document.createTextNode(e.text)); ol.appendChild(li);
    });
  }

  function markSelected() {
    document.querySelectorAll("#board .card").forEach(function (c) { c.classList.toggle("selected", Number(c.dataset.task) === state.open); });
  }

  function openDetail(n) {
    state.open = n;
    markSelected();
    renderDetail();
    const c = document.querySelector('#board .card[data-task="' + n + '"]');
    if (c) c.focus({ preventScroll: false });
  }

  function closeDetail() {
    const n = state.open;
    state.open = null;
    markSelected();
    renderDetail();
    const c = document.querySelector('#board .card[data-task="' + n + '"]');
    if (c) c.focus();
  }

  function switchPlan(name) {
    state.plan = name; state.board = null; state.open = null;
    saveUrl();
    connect();
  }

  function move(current, key) {
    const cols = Array.from(document.querySelectorAll("#board .col"))
      .map(function (c) { return Array.from(c.querySelectorAll(".card")); })
      .filter(function (c) { return c.length; });
    if (!cols.length) return;
    let target = null;
    const ci = current ? cols.findIndex(function (c) { return c.includes(current); }) : -1;
    if (ci < 0) target = cols[0][0];
    else {
      const ri = cols[ci].indexOf(current);
      if (key === "ArrowUp") target = cols[ci][Math.max(0, ri - 1)];
      else if (key === "ArrowDown") target = cols[ci][Math.min(cols[ci].length - 1, ri + 1)];
      else {
        const nc = cols[ci + (key === "ArrowRight" ? 1 : -1)];
        if (nc) target = nc[Math.min(ri, nc.length - 1)];
      }
    }
    if (!target) return;
    target.focus();
    target.scrollIntoView({ block: "nearest" });
    if (state.open !== null) { state.open = Number(target.dataset.task); markSelected(); renderDetail(); }
  }

  $("board").addEventListener("click", function (e) {
    const c = e.target.closest(".card");
    if (c) openDetail(Number(c.dataset.task));
  });
  $("detail-close").addEventListener("click", closeDetail);
  $("plans").addEventListener("change", function (e) { switchPlan(e.target.value); });
  $("search").value = state.q;
  $("search").addEventListener("input", function (e) { state.q = e.target.value; saveUrl(); render(); });
  $("chips").addEventListener("click", function (e) {
    const btn = e.target.closest("button");
    if (!btn) return;
    const col = btn.dataset.col;
    if (state.hide.has(col)) state.hide.delete(col); else state.hide.add(col);
    saveUrl(); render();
  });
  document.addEventListener("keydown", function (e) {
    const typing = e.target.matches && e.target.matches("input, select, textarea");
    if (e.key === "Escape") {
      if (typing) { e.target.blur(); return; }
      if (state.open !== null) { e.preventDefault(); closeDetail(); }
      return;
    }
    if (typing || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "/") { e.preventDefault(); $("search").focus(); $("search").select(); return; }
    if (/^[1-9]$/.test(e.key) && state.board && state.board.plans.length > 1) {
      const name = state.board.plans[Number(e.key) - 1];
      if (name && name !== state.board.plan) { e.preventDefault(); switchPlan(name); }
      return;
    }
    const current = e.target.closest ? e.target.closest("#board .card") : null;
    if (e.key === "Enter" || e.key === " ") {
      if (current) { e.preventDefault(); openDetail(Number(current.dataset.task)); }
      return;
    }
    if (e.key.indexOf("Arrow") === 0) { e.preventDefault(); move(current, e.key); }
  });

  renderLog();
  connect();
})();
</script>
</body>
</html>
"""


def make_server(root, port, verbose=False, live=None):
    root = Path(root).resolve()
    live = live or Live(root)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            if verbose:
                super().log_message(fmt, *args)

        def do_GET(self):
            url = urlparse(self.path)
            plan = parse_qs(url.query).get("plan", [None])[0]
            if url.path == "/healthz":
                return self._json({"root": str(root), "api": API})
            if url.path == "/api/board":
                return self._json(load_board(root, plan, live.data))
            if url.path == "/api/events":
                return self._events(plan)
            if url.path == "/":
                return self._send(200, "text/html; charset=utf-8", PAGE.encode("utf-8"))
            self._send(404, "text/plain; charset=utf-8", b"not found\n")

        def _events(self, plan):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            sent = None
            try:
                while not live.stopped:
                    version = live.version
                    text = json.dumps(load_board(root, plan, live.data))
                    if text != sent:
                        self.wfile.write(b"event: board\ndata: " + text.encode("utf-8") + b"\n\n")
                        self.wfile.flush()
                        sent = text
                    if live.wait(version, PING_EVERY) == version and not live.stopped:
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass

        def _json(self, obj):
            self._send(200, "application/json", json.dumps(obj).encode("utf-8"))

        def _send(self, code, ctype, body):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    class Server(ThreadingHTTPServer):
        daemon_threads = True

        def server_close(self):
            live.stop()
            super().server_close()

    server = Server(("127.0.0.1", port), Handler)
    server.live = live.start()
    return server


def healthz(port):
    """The root a server on this port reports, or None when nothing answers."""
    try:
        with urlopen(f"http://127.0.0.1:{port}/healthz", timeout=1) as r:
            return json.loads(r.read()).get("root")
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Serve a live, read-only board of docs/superpowers/plans.")
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

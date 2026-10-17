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

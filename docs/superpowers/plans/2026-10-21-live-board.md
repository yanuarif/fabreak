# Live Plan Board Implementation Plan

**Goal:** The plan board updates over Server-Sent Events, shows Backlog, In progress, Review and Done from the plan, git and PRs, and adds card detail, filter, change highlights and keyboard navigation, still read-only.

**Architecture:** `scripts/plan-board.py` keeps its pure functions and gains pure matching and status functions, a `Live` poller thread, and an `/api/events` stream. The page is rewritten in place, still one inline response.

**Tech Stack:** Python 3 standard library only (`subprocess`, `threading`, `shutil` added), `unittest`, inline HTML, CSS and JavaScript.

Spec: `docs/superpowers/specs/2026-10-21-live-board-design.md`.

## Global Constraints

- English only, no private names or paths; `bash scripts/check-forbidden-words.sh --all` before the commit.
- Standard library only; the server binds `127.0.0.1` and writes nothing.
- Every git and gh call has a timeout and a fallback; the board serves without either tool.

### Task 1: Task body and dependencies

- [x] **Step 1: Failing tests for `body` and `depends`**
- [x] **Step 2: `parse_plan` collects them**

### Task 2: Matching and status

Depends on: Task 1

- [x] **Step 1: Failing tests for `slug`, `branch_key`, `match_tasks`, `resolve_status`**
- [x] **Step 2: Pure functions**
- [x] **Step 3: git and gh readers with timeouts, and `load_board` with sources**
- [x] **Step 4: Temporary git repository test**

### Task 3: Live poller and event stream

Depends on: Task 2

- [x] **Step 1: Failing test: first event, then a second after the plan changes**
- [x] **Step 2: `Live` thread and `/api/events`**

### Task 4: Interactive page

Depends on: Task 3

- [x] **Step 1: Four columns, cards with progress and badges, live dot**
- [x] **Step 2: Detail panel, search and column chips in the URL**
- [x] **Step 3: Change highlights, activity list, keyboard**
- [x] **Step 4: Checked in the preview pane against a temporary repository**

### Task 5: Docs and version

Depends on: Task 4

- [x] **Step 1: `board.md`, `skills/board/SKILL.md`, README, dry runs, design spec changes**
- [x] **Step 2: Version 0.7.0 and the full check list**

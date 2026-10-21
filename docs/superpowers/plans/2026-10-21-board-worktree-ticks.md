# Board Worktree Ticks Implementation Plan

**Goal:** The plan board shows a task as In progress while its session works: branches match by task number, step ticks come from the task's worktree, and `[/]` and `[-]` read as doing and skipped.

**Architecture:** `scripts/plan-board.py` gains a step `state`, `branch_number`, `merge_steps` and per-worktree plan texts in `read_git`; `load_board` merges the worktree copy into each matched task. The page draws the two new step states.

**Tech Stack:** Python 3 standard library only, `unittest`, inline HTML, CSS and JavaScript.

Spec: `docs/superpowers/specs/2026-10-21-board-worktree-ticks-design.md`.

## Global Constraints

- English only, no private names or paths; `bash scripts/check-forbidden-words.sh --all` before the commit.
- Standard library only; the server binds `127.0.0.1` and writes nothing.

### Task 1: Step markers

- [x] **Step 1: Failing tests for `[/]` and `[-]` states and plan-only status**
- [x] **Step 2: `parse_plan`, `status_for`, `resolve_status` and plan selection read the states**

### Task 2: Worktree matching and ticks

Depends on: Task 1

- [x] **Step 1: Failing tests for `branch_number`, number matching, PR adoption and `merge_steps`**
- [x] **Step 2: `read_git` collects worktree plans; `match_tasks` and `load_board` use them**
- [x] **Step 3: Temporary git repository test with an uncommitted tick in a number-named worktree**

### Task 3: Page and docs

Depends on: Task 2

- [x] **Step 1: Step boxes, progress, next step, ticks fact and activity lines**
- [x] **Step 2: Checked in the preview pane against a temporary repository**
- [x] **Step 3: `board.md`, `skills/board/SKILL.md`, live board spec, README, version 0.8.0 and the full check list**

# Board Progress and Lifecycle Implementation Plan

**Goal:** Card step progress is realtime from a progress file the task session writes outside the tree, the board stops with the session that started it or from a button, and the command stops an older server without touching its clients.

**Architecture:** `scripts/plan-board.py` reads each worktree's `fabreak-steps.md` from its private git folder, adds `POST /api/stop`, an `event: stopped`, and a `--watch-pid` watcher thread. `loop.md` step 2 writes the progress file; `skills/board/SKILL.md` passes `--watch-pid $PPID` and kills only the listener.

**Tech Stack:** Python 3 standard library only, `unittest`, inline HTML, CSS and JavaScript.

Spec: `docs/superpowers/specs/2026-10-21-board-lifecycle-design.md`.

## Global Constraints

- English only, no private names or paths; `bash scripts/check-forbidden-words.sh --all` before the commit.
- Standard library only; the server binds `127.0.0.1` and writes nothing to the repository.

### Task 1: Progress file

- [x] **Step 1: Failing temporary repository test for a progress file**
- [x] **Step 2: `read_git` reads it; `load_board` merges it**

### Task 2: Stop

Depends on: Task 1

- [x] **Step 1: Failing tests for `POST /api/stop`, `event: stopped`, `pid_alive` and `watch_pid`**
- [x] **Step 2: Server stop, stream event and the watcher thread**
- [x] **Step 3: Stop button and the stopped state on the page**

### Task 3: Command, loop and release

Depends on: Task 2

- [x] **Step 1: `skills/board/SKILL.md` kill and start lines, `loop.md` step 2, `board.md` Plan board**
- [x] **Step 2: Checked in the preview pane: progress file, Stop button, watcher**
- [x] **Step 3: Dry runs, version 0.7.2 and the full check list**

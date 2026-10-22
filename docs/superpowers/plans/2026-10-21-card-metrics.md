# Card Metrics Implementation Plan

**Goal:** Every card leaves a `Metrics:` line (lead, work, review rounds, load-bearing findings, tier) in the plan, and the plan board shows it per card and as a summary.

**Architecture:** `scripts/plan-board.py` parses `Metrics:` lines from the plan and from each worktree's progress file, resolves one `metrics` object per task, and adds a `summary` to the board; the page renders chips, a header strip and detail facts, and computes live durations in the browser. `loop.md` and `board.md` say who writes the line and when.

**Tech Stack:** Python 3 standard library only, `unittest`, inline HTML, CSS and JavaScript.

Spec: `docs/superpowers/specs/2026-10-21-card-metrics-design.md`.

## Global Constraints

- English only, no private names or paths; `bash scripts/check-forbidden-words.sh --all` before the commit.
- Standard library only; the server binds `127.0.0.1` and writes nothing to the repository.
- `skills/fabreak/SKILL.md` stays under 1,500 tokens; this change does not touch it.
- Duration format `2d3h`, `3h10m`, `45m`, `0m`; key separator ` · `; timestamps `2026-10-21T08:00Z`.

### Task 1: Parse metrics

**Files:** `scripts/plan-board.py` (`parse_duration`, `parse_metrics`, `parse_plan`), `tests/test_plan_board.py`.

**Produces:** `parse_duration(text) -> int | None` (minutes); `parse_metrics(text) -> dict` with keys among `lead`, `work` (int minutes), `review`, `load_bearing` (int), `tier`, `started`, `began` (str); `parse_plan` sets `task["metrics"]` to that dict or `None`.

- [x] **Step 1: Failing tests for `parse_duration`, `parse_metrics` and the first `Metrics:` line outside a fence**
- [x] **Step 2: `METRICS_RE`, `DURATION_RE`, both parsers and the `parse_plan` hook**

### Task 2: Resolve metrics and the summary

Depends on: Task 1

**Files:** `scripts/plan-board.py` (`load_board`, `summarize`), `tests/test_plan_board.py`.

**Produces:** each board task has `metrics` = `{..., "source": "plan" | "live"}` or `None`; `board["summary"]` = `{tasks, done, measured, lead, work, review, load_bearing, tiers}`; `API = 5`.

- [x] **Step 1: Failing tests: summary medians (lower middle), sums and tier mix; a progress-file line gives `"source": "live"`; a plan line wins**
- [x] **Step 2: `summarize(tasks)` with `statistics.median_low`, the plan-then-progress resolution in `load_board`, `API = 5`**

### Task 3: Page

Depends on: Task 2

**Files:** `scripts/plan-board.py` (`PAGE`), `tests/test_plan_board.py`.

- [x] **Step 1: Failing test: the page contains `id="summary"`**
- [x] **Step 2: Card chips, header summary strip, detail facts, `fmt` for durations and a one-minute re-render while a card is live**
- [x] **Step 3: Checked in the preview pane against a temporary repository: a measured Done card, a live card, the strip**

### Task 4: Skills, docs and release

Depends on: Task 3

**Files:** `skills/fabreak/loop.md`, `skills/fabreak/board.md`, `skills/board/SKILL.md`, `README.md`, `docs/dry-runs.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`.

- [x] **Step 1: `loop.md` steps 2, 4, 5 and 6; `board.md` Start item 8 and 9, Done steps 1 and 2, Plan board and CLI fallback**
- [x] **Step 2: README bullet, dry-run entry, version 0.7.3**
- [x] **Step 3: The full check list from CONTRIBUTING.md**

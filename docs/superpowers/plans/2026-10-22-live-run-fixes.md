# Live-Run Fixes Implementation Plan

**Goal:** The 0.8.0 live-run findings fixed in the skills: a merge the card can make, CI that never starts, no merge by the orchestrator, ticks only from merge reports, the app's branch, required skills, uniform review runs, silent held cards, and a lock for a shared stack.

**Architecture:** Markdown only: `board.md` (card round, brief items 3 and 6, Held cards, Done), `loop.md` (steps 1, 2, 4, 5, 6 and a Shared stack section), `hosting.md` (CI that never started), README, dry runs, version.

**Tech Stack:** Markdown skills; the existing shell and Python checks.

Spec: `docs/superpowers/specs/2026-10-22-live-run-fixes-design.md`.

## Global Constraints

- English only, no private names or paths; `bash scripts/check-forbidden-words.sh --all` before the commit.
- `skills/fabreak/SKILL.md` unchanged and under 1,500 tokens.
- Every changed step ends on a completion criterion.

### Task 1: Skills

- [x] **Step 1: `board.md` merge permission, branch line, brief items 3 and 6, Held cards, Done and the no-merge rule**
- [x] **Step 2: `loop.md` steps 1, 2, 4, 5, 6 and Shared stack; `hosting.md` CI that never started**

### Task 2: Docs and release

Depends on: Task 1

- [x] **Step 1: README, dry-run entry, version 0.8.1**
- [x] **Step 2: The full check list from CONTRIBUTING.md**

# Factory Gates Implementation Plan

**Goal:** A security gate in every card, merge without a question when the gates hold, a `triage` entry that turns issues, a red default branch and an intake hook into cards, and a scheduled triage offered by `bootstrap`.

**Architecture:** Markdown only. `loop.md` steps 3, 4 and 6 gain the audit, the security axis and the merge conditions; `board.md` names what the merge grant means; a new `skills/triage/SKILL.md` entry keeps `docs/superpowers/triage.md`; `bootstrap` gains step 5; `hosting.md` gains two command rows; the router gains one table row.

**Tech Stack:** Markdown skills; the existing shell and Python checks.

Spec: `docs/superpowers/specs/2026-10-21-factory-gates-design.md`.

## Global Constraints

- English only, no private names or paths; `bash scripts/check-forbidden-words.sh --all` before the commit.
- `skills/fabreak/SKILL.md` under 1,500 tokens, estimated as words × 1.4.
- An entry file keeps the opening paragraph that points at the router and `disable-model-invocation: true`.
- Every step ends on a completion criterion.

### Task 1: Security gate and merge

- [x] **Step 1: `loop.md` step 3 audit table and split, step 4 security axis, step 6 merge conditions**
- [x] **Step 2: `board.md` card round names the merge grant; `hosting.md` Open issues and Review state rows**

### Task 2: Triage and the schedule

Depends on: Task 1

- [x] **Step 1: `skills/triage/SKILL.md`**
- [x] **Step 2: `bootstrap` step 5, router entry row**

### Task 3: Docs and release

Depends on: Task 2

- [x] **Step 1: README entries, enforcement bullets, limits and layout; dry-run entry; version 0.8.0**
- [x] **Step 2: The full check list from CONTRIBUTING.md and the router's word count**

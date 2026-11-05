# Stack Templates Implementation Plan

**Goal:** A new product starts from the owner's template repo for its stack, and each release leaves a stack profile that the next `new` reads as brainstorming input.

**Architecture:** Markdown only: `skills/new/SKILL.md` (a stack-start step), `skills/release/SKILL.md` (a stack-profile step), `skills/bootstrap/SKILL.md` (keep a template's files), README, the ADLC chart, dry runs, version.

**Tech Stack:** Markdown skills; the existing shell and Python checks.

Spec: `docs/superpowers/specs/2026-11-05-stack-templates-design.md`.

## Global Constraints

- English only, no private names or paths; `bash scripts/check-forbidden-words.sh --all` before the commit.
- `skills/fabreak/SKILL.md` unchanged and under 1,500 tokens.
- Every changed step ends on a completion criterion.
- Example URLs use `git.example.com`.

### Task 1: Skills

- [x] **Step 1: `new` step 2, stack start; steps renumbered; Artifacts and Done when**
- [x] **Step 2: `release` step 5, stack profile; Artifacts and Done when**
- [x] **Step 3: `bootstrap` keeps a template's files and reads the profile**

### Task 2: Docs and release

Depends on: Task 1

- [x] **Step 1: README section on stack templates, the chart's release node and feedback label, dry-run entry, version 0.9.0**
- [ ] **Step 2: The full check list from CONTRIBUTING.md and a fresh review on Standards and Spec**

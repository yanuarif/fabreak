# Portfolio Page Implementation Plan

**Goal:** One live, read-only page across the owner's repositories: a row per repository with its open plan, Done/total, running cards, median lead and load-bearing findings, each row opening that repository's board.

**Architecture:** `scripts/plan-board.py --portfolio` reads `~/.claude/fabreak/repos.md`, runs one `Live` poller per repository and serves the portfolio page plus each repository's board under `/r/<key>/`. `skills/portfolio/SKILL.md` starts it; `bootstrap` and `new` add their repository to `repos.md`.

**Tech Stack:** Python standard library; Markdown skills; the existing shell and Python checks.

Spec: `docs/superpowers/specs/2026-11-05-portfolio-design.md`.

## Global Constraints

- English only, no private names or paths; `bash scripts/check-forbidden-words.sh --all` before the commit.
- `skills/fabreak/SKILL.md` unchanged and under 1,500 tokens.
- Standard library only; the server binds 127.0.0.1 and writes nothing.
- Version stays 0.9.0: the portfolio ships with stack templates.

### Task 1: Portfolio data, test-first

- [x] **Step 1: Failing tests for `read_repos`, `portfolio_row` and `load_portfolio`**
- [x] **Step 2: Implement them until the tests pass**

### Task 2: Portfolio server and page, test-first

Depends on: Task 1

- [x] **Step 1: Failing server tests: `/healthz`, `/api/portfolio`, `/r/<key>/api/board`, an unknown key, an event when `repos.md` changes**
- [x] **Step 2: `Portfolio` poller, routes, the page, relative API paths in the board page, `--portfolio` and `--repos` in `main`**

### Task 3: Skills and docs

Depends on: Task 2

- [x] **Step 1: `skills/portfolio/SKILL.md`; `bootstrap` step 6 and `new` step 6 add the repository to `repos.md`**
- [x] **Step 2: README, the ADLC chart, the dry-run entry with a preview-pane check against temporary repositories**
- [x] **Step 3: The full check list from CONTRIBUTING.md and a fresh review on Standards and Spec**

---
name: fabreak
description: Use when a development request arrives in a repository, when /fabreak is typed with or without an entry name, or when a repo has an open plan or an active task worktree and the next step is unclear. Development work only.
argument-hint: "[new|feature|takeover|spike|bootstrap|fix|refactor|upgrade|docs-only|replan|release|closing] [--grill] [--release]"
---

# fabreak

fabreak routes a development request to one ADLC entry, then runs that entry by invoking installed skills (superpowers, mattpocock-skills, frontend-design). Three parties: the owner, this orchestrator session, and a fresh subagent per task. Roles are skills; the model tier is picked per dispatch.

## Read the state

Run these lookups in order before choosing an entry. Keep the results; entries reuse them.

1. Domain model: `test -f CONTEXT.md`.
2. Test suite: a test script or test config exists. Green means the default branch's CI passes (hosting.md); with no remote, run the suite once and keep its summary line.
3. Open plan: `grep -l '^- \[ \]' docs/superpowers/plans/*.md`.
4. Task worktree: `git rev-parse --git-dir` differs from `git rev-parse --git-common-dir`, and `git rev-parse --show-superproject-working-tree` prints nothing.
5. The argument.

| State | Entry |
|---|---|
| Argument given | That entry. State still informs it: `feature` without CONTEXT.md asks whether `takeover` was meant. |
| Task worktree | loop.md, resuming this worktree's task. |
| Open plan, no argument | Show the board (board.md), then loop.md on the next unchecked task. |
| No CONTEXT.md, no source files | new |
| No CONTEXT.md, source files present | takeover |
| CONTEXT.md, no open plan, the request is a bug | fix |
| CONTEXT.md, no open plan, the request is a change | feature |

Two entries fit: ask one question with both entries as the answers. Choosing silently is a routing bug.

## Entries

Read `entries/<name>.md` only after the entry is chosen.

| Argument | Enter when |
|---|---|
| new | an empty or nearly empty repo; a product shaped from scratch |
| feature | a change to a repo that has CONTEXT.md |
| takeover | first contact with code that has no domain model |
| spike | a feasibility question that needs throwaway code, time-boxed |
| bootstrap | a repo needs CLAUDE.md, CI, pre-commit, branch protection |
| fix | a bug report |
| refactor | structure changes, behaviour stays |
| upgrade | a dependency, runtime or platform version jump |
| docs-only | documentation changes only |
| replan | the spec changed while plan tasks remain |
| release | every plan card is Done and main CI is green |
| closing | handover to a client: UAT, evidence, access |

## Rules for every entry

- Plan before code. Exceptions: fix, refactor, upgrade, docs-only.
- One task = one card = one session = one worktree = one PR or MR.
- Reviewers are fresh subagents. The implementer never reviews its own work.
- Verification evidence is command output: the runner's summary line and its exit code, printed verbatim.
- Steps only a human can take (secrets, deploys, store consoles, branch protection, access) run through mattpocock-skills:wizard and park the session in Waiting on me.
- A question stops the session: one question, answer buttons, then wait. The owner's answer resumes the same session.
- The durable record is the plan in git: tick a task when its PR merges; record replans, archived spikes and wrong task splits there.

## Mechanisms

- `board.md` — when the board is shown or a card changes section.
- `loop.md` — when code is written: worktree, implement, verify, review, finish.
- `hosting.md` — when a PR or MR, CI status, merge or branch protection is needed.

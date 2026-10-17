---
name: fabreak
description: Use when a development request arrives in a repository, or when a repo has an open plan or an active task worktree and the next step is unclear. Development work only.
argument-hint: "[request]"
---

# fabreak

fabreak routes a development request to one ADLC entry, then runs that entry by invoking installed skills (superpowers, mattpocock-skills, frontend-design). Each entry is also its own command, `/fabreak:<entry>`; typed that way, the entry's file names this router as its first step. Three parties: the owner, this orchestrator session, and one task session per card, which implements its task. Fresh subagents review, research, and may take a mechanical task. Roles are skills; the model tier is picked per dispatch.

## Read the state

Run these lookups from the repository root, in order, before choosing an entry. Keep the results; entries reuse them.

1. Domain model: `test -f CONTEXT.md`.
2. Test suite: a test script or test config exists; none means "absent". Green: the default branch's CI status when the remote has CI (hosting.md, Commands); with no remote, or no CI run listed for the default branch, run the suite once from the repository root and keep its summary line. The app's worktrees live under `.claude/worktrees/` inside the repository and most runners discover their tests too; exclude that folder in the runner's config (bootstrap adds it).
3. Open plan: `grep -rl '^- \[ \]' docs/superpowers/plans 2>/dev/null`.
4. Task worktree: `git rev-parse --git-dir` differs from `git rev-parse --git-common-dir`, and `git rev-parse --show-superproject-working-tree` prints nothing.
5. The entry, when one was named: by its command `/fabreak:<entry>`, or as the first word of this skill's argument. Flags: `--grill` (feature): grilling before brainstorming. `--release` (fix): the release branch first, then a backport.

Rows are read top-down; the first match wins.

| State | Entry |
|---|---|
| Entry named | That entry. Name any open plan in one line first, with its unchecked task count. `feature` without CONTEXT.md asks whether `takeover` was meant; fix, refactor, upgrade and docs-only run without one. |
| Task worktree | loop.md, resuming this worktree's task. |
| Open plan, no entry named | Show the board (board.md), then the card round for the unchecked tasks that have no card (board.md, Cards); a held card waits for its wake-up. A plan whose unchecked tasks already exist in the code is stale: one question, `replan` to tick it or ignore it. |
| No CONTEXT.md, no source files | new |
| No CONTEXT.md, source files present | takeover |
| CONTEXT.md, no open plan, the request is a bug | fix |
| CONTEXT.md, no open plan, the request is a change | feature |

Two entries fit: ask one question with both entries as the answers.

## Entries

Read `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md` only after the entry is chosen; its opening paragraph points back here and is already done. fabreak owns every hand-off between skills: where an invoked skill names its own next skill, the entry's next step replaces it.

| Entry | Enter when |
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
- Reviewers are fresh subagents. The implementer never reviews its own work. Model tier per dispatch: reviewers of a diff under about 200 lines and a mechanical task's implementer subagent run on the cheaper tier; design-heavy work runs on the session's own tier.
- A skill a step names is invoked with the Skill tool when the step starts, even when its commands look obvious. Running the commands by hand does not count as the step.
- Verification evidence is command output: the runner's summary line and its exit code, printed verbatim.
- Steps only a human can take (secrets, deploys, store consoles, branch protection, access) run through mattpocock-skills:wizard and park the session in Waiting on me. Before parking, the message lists every stage in order: its purpose, the URL it opens, what to click there, each value it asks for (secret or public), and each decision with its options; then the run command, `bash <script> 2>&1 | tee <log>`, which keeps every stage on screen (the template clears the screen only on a terminal) and leaves the log as the evidence the wizard reports done with.
- A question stops the session. The message states the question in full, then every option as one line with what choosing it means and what happens next, so the owner can answer from the message alone. With two options the closing box repeats the question and carries one button per option; with more, or when an option needs more than its label, the app's question tool asks it (a label and a description per option) and the closing box is a recap only. In the orchestrator the interview round of the skill in use (a grilling round, a brainstorming section) is the question, in the same form. Either way, wait; the owner's answer resumes the same session. A guess past a question is a defect; so is a box whose short question or button labels are the only place an option is spelled out.
- The durable record is the plan in git, edited by the orchestrator only: tick a task when its PR merges; record replans, archived spikes and wrong task splits there.
- Work that belongs to another entry (a release, a fix, a spike) switches to that entry's file; its plan is never written by hand. An entry ends only when its "Done when" holds; an unmet line (a wizard not run, evidence not written) is named to the owner, never skipped.

## Mechanisms

- `board.md` — when the board is shown or a card changes section.
- `loop.md` — when code is written: worktree, implement, verify, review, finish.
- `hosting.md` — when a PR or MR, CI status, merge or branch protection is needed.

# Loop C

It runs inside one task session, in that session's worktree, for one task from the plan whose card is in run state (board.md): from its brief, or from the orchestrator's wake-up message after it was held. The session moves its own card at every event in board.md, Moves; the steps below name each move.

## Steps

1. **Worktree** — The app created the worktree when the card started and named its branch. A card that was held syncs first, because the worktree was cut when the cards were started: `sync_with_base_branch` (the app's host tool; without the app, `git fetch origin` and `git merge origin/<default>`); a conflict here is the rebase-conflict rule below. Then move the card to In progress (board.md, Moves) and check the worktree: `git rev-parse --git-dir` differs from `git rev-parse --git-common-dir`, `git branch --show-current` prints the branch; run the project's install step when its dependencies folder is missing. superpowers:using-git-worktrees only when there is no worktree. Done when the two `rev-parse` outputs differ, the branch is printed, dependencies are present, the card sits in In progress and, for a woken card, the sync reported no conflict.
2. **Implement** — This session is the implementer. One card is one task, so the card session already is the fresh context per task; superpowers:subagent-driven-development and superpowers:executing-plans are not invoked (their per-task dispatch and review repeat this card and step 4). The card's tier was picked when it started (board.md, Tier), so this session implements in its own context and dispatches no implementer subagent. Work the steps under this task's heading in the plan in order, with mattpocock-skills:tdd at the seams the plan names. For an entry without a plan (fix, refactor, upgrade, docs-only) the entry's own implementation step is this step. Done when every step of the task is done and committed.
3. **Verify** — superpowers:verification-before-completion. Run the whole suite, the type-check and build scripts when the project has them, and any verification hook `CLAUDE.md` names. Print each runner's summary line and exit code verbatim; those lines are the evidence, and on a repository without CI they stand in for CI green (hosting.md). Done when every exit code is 0.
4. **Review** — mattpocock-skills:code-review with the fixed point = this branch's merge-base with the default branch, and the Spec source from the card's brief: the plan path plus task heading, the bug report (fix), or "`tests/` unchanged and green" (refactor). No entry skips this step: docs-only runs the Standards axis, every other entry both axes, and a single reviewer without the skill does not count. Each reviewer's brief ends with: "Mark each finding load-bearing (would block a merge) or cosmetic." Load-bearing findings go back to step 2 for one fix round, then step 3 and step 4 again on the changed files; cosmetic ones go in the PR description. Done when neither axis reports a load-bearing finding.
5. **Finish** — superpowers:finishing-a-development-branch with the PR or MR option already chosen and the base = the default branch from hosting.md; neither is a question when the brief carries the owner's push-and-PR permission (board.md, brief item 5), otherwise one question and card to Waiting on me. hosting.md gives the command; the PR body carries the step 3 lines and the step 4 result. Card to Review. Done when the PR or MR URL is printed.
6. **Merge** — CI green (hosting.md). This session asks the owner for the go-ahead (one question, card to Waiting on me) and runs the merge command from the worktree, ignoring the command's local-branch cleanup hint: the app removes the worktree when the session is archived. The orchestrator never asks for a merge; it reads the host's state. Then the merge report, one message to the orchestrator: "Merged: <task title>, <PR or MR URL>" (`SendMessage` to the id in the brief); card to Done (board.md, Done); the orchestrator ticks the task in the plan and wakes the next held card. Lessons: a gotcha this task taught goes into `CLAUDE.md` through mattpocock-skills:writing-for-agents, in this PR when known before step 5, otherwise in a docs-only card; a repository without `CLAUDE.md` gets one through `bootstrap`. A technique worth reusing becomes a skill through superpowers:writing-skills. Done when the host reports the PR or MR as merged (hosting.md, confirm line), not when the merge command exits 0.

## Rules inside the loop

### The plan file

The plan belongs to the orchestrator. A task session does not edit it: parallel cards that each edit the plan conflict at merge. A finding about the plan (a wrong split, a surprise in the code, a follow-up task) goes in the PR or MR body under "For the plan"; the orchestrator records it when it ticks the task (step 6). Done when `git diff <merge-base> --stat -- docs/superpowers/plans` is empty.

### Rebase conflict

Another card merged first and the rebase onto the default branch fails. mattpocock-skills:resolving-merge-conflicts on this branch, then step 3 on the whole suite and step 4 on the conflicting files only. Report to the orchestrator; it records the task split as wrong in the plan ("Task splits that were wrong", with the two tasks) and adds the shared seam to `CLAUDE.md`. Done when the branch is rebased, green and re-reviewed.

### Human review requests changes

The PR comment wakes this same session. superpowers:receiving-code-review first: verify the comment against the code and push back with reasoning when it is wrong. When it is right, update the spec (a plan change goes under "For the plan" in the PR or MR body), then the tests, then the code, in that order. Then step 3, step 4, push. Done when every comment has a commit or a reasoned reply.

### Something fails mid-loop

superpowers:systematic-debugging. When no tight pass/fail signal exists for the failure, mattpocock-skills:diagnosing-bugs builds one first. The fix starts with a red test. Done when that test is green and the whole suite is green.

### Cross-repo

One spec, one plan, cards in several repos, each card naming the cards it depends on. A card whose dependency has not merged is held as board.md, Held cards, says: a recap naming the dependency, no move, end the turn; the orchestrator of the repo that merged reports to this card's orchestrator, which wakes it. Once the dependency merges, cards in different repos run in parallel. Verification that needs a specific machine (a mobile end-to-end run) stays on that machine; the card names it. Done when the held card's dependency is Done.

### A question stops the session

The rule from SKILL.md, in its form: an interview round as the closing message after a recap-only box, a discrete choice in the question tool, a git go-ahead on the box's buttons; card to Waiting on me, end the turn.

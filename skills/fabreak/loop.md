# Loop C

It runs inside one task session, in that session's worktree, for one task from the plan. The card for this task is already In progress (board.md).

## Steps

1. **Worktree** — superpowers:using-git-worktrees. The app created the worktree when the card started; the skill verifies it and runs project setup. Done when `git rev-parse --git-dir` differs from `git rev-parse --git-common-dir` and the branch name is known.
2. **Implement** — superpowers:subagent-driven-development with the plan path and this task's heading. Without subagents, superpowers:executing-plans. Every implementer follows mattpocock-skills:tdd at the seams the plan names; the model tier is chosen per dispatch. Done when every step of the task is ticked and committed.
3. **Verify** — superpowers:verification-before-completion. Run the whole suite and any verification hook `CLAUDE.md` names. Print the runner's summary line and the exit code verbatim; that line is the evidence. Done when the exit code is 0.
4. **Review** — mattpocock-skills:code-review with the fixed point = this branch's merge-base with the default branch, and the Spec source from the card's brief: the plan path plus task heading, the bug report (fix), or "`tests/` unchanged and green" (refactor). Findings go back to step 2 for one fix round, then step 3 and step 4 again on the changed files. Done when neither axis reports a load-bearing finding.
5. **Finish** — superpowers:finishing-a-development-branch, choosing the PR or MR option; hosting.md gives the command. Card to Review. Done when the PR or MR URL is printed.
6. **Merge** — CI green (hosting.md), human approval when the repo requires it, merge. Card to Done; the orchestrator ticks the task in the plan (board.md, Done). Lessons: a gotcha this task taught goes into `CLAUDE.md` through mattpocock-skills:writing-for-agents; a technique worth reusing becomes a skill through superpowers:writing-skills.

## Rules inside the loop

### Rebase conflict

Another card merged first and the rebase onto the default branch fails. mattpocock-skills:resolving-merge-conflicts on this branch, then step 3 on the whole suite and step 4 on the conflicting files only. Report to the orchestrator; it records the task split as wrong in the plan ("Task splits that were wrong", with the two tasks) and adds the shared seam to `CLAUDE.md`. Done when the branch is rebased, green and re-reviewed.

### Human review requests changes

The PR comment wakes this same session. superpowers:receiving-code-review first: verify the comment against the code and push back with reasoning when it is wrong. When it is right, update the spec or plan task, then the tests, then the code, in that order. Then step 3, step 4, push. Done when every comment has a commit or a reasoned reply.

### Something fails mid-loop

superpowers:systematic-debugging. When no tight pass/fail signal exists for the failure, mattpocock-skills:diagnosing-bugs builds one first. The fix starts with a red test. Done when that test is green and the whole suite is green.

### Cross-repo

One spec, one plan, cards in several repos, each card naming the cards it depends on. A card whose dependency has not merged is held: move it to Backlog (board.md) and end the turn. Once the dependency merges, cards in different repos run in parallel. Verification that needs a specific machine (a mobile end-to-end run) stays on that machine; the card names it. Done when the held card's dependency is Done.

### A question stops the session

The rule from SKILL.md, inside a task session: one question with answer buttons, card to Waiting on me, end the turn.

# Loop C

It runs inside one task session, in that session's worktree, for one task from the plan whose card is in run state (board.md): from its brief, or from the orchestrator's wake-up message after it was held.

## Steps

1. **Worktree** — The app created the worktree when the card started and named its branch. A card that was held syncs first, because the worktree was cut when the cards were started: `sync_with_base_branch` (the app's host tool; without the app, `git fetch origin` and `git merge origin/<default>`); a conflict here is the rebase-conflict rule below. Then check the worktree: `git rev-parse --git-dir` differs from `git rev-parse --git-common-dir`, `git branch --show-current` prints the branch; run the project's install step when its dependencies folder is missing. The card works on this branch, the one the app created, and opens its PR or MR from it; it creates or renames no branch. The app may reuse a folder from an earlier task: untracked files (`git status --porcelain --ignored`: `.env`, local data) are compared with the repository's example config and this task's needs, and fixed before step 2. superpowers:using-git-worktrees only when there is no worktree. Done when the two `rev-parse` outputs differ, the branch is printed, dependencies are present, untracked config matches this task and, for a woken card, the sync reported no conflict.
2. **Implement** — This session is the implementer. One card is one task, so the card session already is the fresh context per task; superpowers:subagent-driven-development and superpowers:executing-plans are not invoked (their per-task dispatch and review repeat this card and step 4). The card's tier was picked when it started (board.md, Tier), so this session implements in its own context and dispatches no implementer subagent. Work the steps under this task's heading in the plan in order, with mattpocock-skills:tdd at the seams the plan names. Progress for the plan board, on every tier, for a card from a plan (an entry without a plan keeps its steps and counts in its own context, Metrics): before the first step, copy the task heading and its step lines from the plan into the file `git rev-parse --git-path fabreak-steps.md` names (the worktree's private git folder: never committed, never in a diff); mark a step `- [/]` when it starts, `- [x]` when it is done and committed, `- [-]` when the task drops it, with the reason under "For the plan" (The plan file, below). Under the heading goes the metrics line (Metrics, below), `Metrics: started <brief's Started> · review 0 · load-bearing 0 · tier <this session's model id>`, and ` · began <UTC time>` after `started` when the first step is marked `[/]`. A task that names a design canvas reads it first (the Artifact tool, `action: "read"`, with the canvas URL; the result names the saved file) and invokes frontend-design:frontend-design, then builds each named artboard's screen against it. For an entry without a plan (fix, refactor, upgrade, docs-only) the entry's own implementation step is this step. Done when every step of the task is done and committed, and, for a card from a plan, the progress file shows each one `[x]` or `[-]`.
3. **Verify** — superpowers:verification-before-completion. Run the whole suite, the type-check and build scripts when the project has them, and any verification hook `CLAUDE.md` names, then the dependency audit (Dependency audit, below). Print each runner's summary line and exit code verbatim; those lines are the evidence, and on a repository without CI they stand in for CI green (hosting.md). Done when every exit code is 0, or the audit's non-zero exit holds only advisories already on the default branch (Dependency audit).
4. **Review** — mattpocock-skills:code-review with the fixed point = this branch's merge-base with the default branch, and the Spec source from the card's brief: the plan path plus task heading, the bug report (fix), or "`tests/` unchanged and green" (refactor); for a task that names a design canvas, the saved canvas file from step 2 too, and the Spec axis checks each screen against its artboard. Beside them, a third fresh subagent runs the security axis (Security axis, below) on the same diff. No entry skips this step: docs-only runs the Standards axis, every other entry all three axes. Every run, the first and every re-review, runs each axis as its own fresh subagent in the same way: Standards and Spec through the skill, security as its section says; a re-review may be limited to the changed files, and a single reviewer for several axes, or one without the skill, does not count. A commit made after the last run that adds to this branch's own diff (a flake fix, a conflict resolution: Rebase conflict says which files) gets a run of its own before step 6; a sync with the default branch that merges cleanly adds nothing of this branch's own and needs none. The Standards and Spec reviewers' briefs end with: "Mark each finding load-bearing (would block a merge) or cosmetic." The security reviewer's brief ends with: "Rate each finding critical, high, medium or low; critical and high are load-bearing, medium and low cosmetic." Load-bearing findings go back to step 2 for one fix round, then step 3 and step 4 again on the changed files; cosmetic ones go in the PR description. Each run of this step, whichever axes ran, adds 1 to `review` and its load-bearing count across every axis to `load-bearing` in the metrics line, written at the end of the run, before the next step starts. Done when no axis reports a load-bearing finding, no commit of this branch's own diff is newer than the last run, and the metrics line counts this run.
5. **Finish** — superpowers:finishing-a-development-branch with the PR or MR option already chosen and the base = the default branch from hosting.md; neither is a question when the brief carries the owner's push-and-PR permission (board.md, brief item 5), otherwise one question. hosting.md gives the command; the PR body carries the step 3 lines, the step 4 result, `Metrics: review <n> · load-bearing <n> · tier <model id>` and `Skills: <each skill this session or its reviewers invoked with the Skill tool, as Skills, below, lists them>`. Done when the PR or MR URL is printed.
6. **Merge** — The gates: (a) CI green; or, on a repository without CI or whose CI never started (hosting.md, CI that never started), the step 3 lines in the PR or MR body, with the host's annotation quoted for CI that never started; (b) the last run of step 4 reported no load-bearing finding on any axis, no commit of this branch's own diff is newer than it, and the PR or MR body's `Skills:` line names every skill Skills (below) requires for this entry; (c) no human review requests changes and no review comment is unanswered (hosting.md, Review state). Any lock this session holds is released first (Shared stack). When the brief carries the merge permission (board.md, brief item 5) and every gate holds, this session merges without a question; otherwise, or when the permission classifier denies the merge command, it asks the owner for the go-ahead in this session (one question), naming the gate or the denial. It runs the merge command from the worktree, ignoring the command's local-branch cleanup hint: the app removes the worktree when the session is archived. The merge is this session's alone: the orchestrator never merges a card's PR or MR, never asks for one, and reads the host's state. Then the merge report, one message to the orchestrator: "Merged: <task title>, <PR or MR URL>. Metrics: lead … · work … · review … · load-bearing … · tier …" (`SendMessage` to the id in the brief, board.md, Done), with `lead` and `work` measured to the host's merge confirmation (Metrics, below); the orchestrator ticks the task in the plan and wakes the next held card. Lessons: a gotcha this task taught goes into `CLAUDE.md` through mattpocock-skills:writing-for-agents, in this PR when known before step 5, otherwise in a docs-only card; a repository without `CLAUDE.md` gets one through `bootstrap`. A technique worth reusing becomes a skill through superpowers:writing-skills. Done when the host reports the PR or MR as merged (hosting.md, confirm line), not when the merge command exits 0.

## Rules inside the loop

### The plan file

The plan belongs to the orchestrator. A task session does not edit it: parallel cards that each edit the plan conflict at merge. A finding about the plan (a wrong split, a surprise in the code, a follow-up task) goes in the PR or MR body under "For the plan"; the orchestrator records it when it ticks the task (step 6). Done when `git diff <merge-base> --stat -- docs/superpowers/plans` is empty.

### Metrics

One line per card, keys in this order, separated by ` · `:

| Key | Value |
|---|---|
| `lead` | The brief's `Started` time to the merge confirmation. |
| `work` | `began` to the merge confirmation. |
| `review` | Runs of step 4, the ones after a fix, a rebase conflict or a human review comment included. |
| `load-bearing` | The load-bearing findings of every run, added up. |
| `tier` | The model id this session runs on. |

Times are UTC, `date -u +%Y-%m-%dT%H:%MZ`. A duration is days, hours and minutes rounded down, zero units left out: `2d3h`, `3h10m`, `45m`, `0m`. While the card runs, the progress file's line carries `started` and `began` in place of `lead` and `work`. An entry without a plan has no progress file: the session keeps `started` (from the brief), `began` (when its implementation step starts) and the counts in its own context. Done when the merge report carries all five keys.

### Skills

The skills a card invokes with the Skill tool, by entry; the brief (board.md, item 3) points here and the PR or MR body's `Skills:` line names them:

| Entry | Skills |
|---|---|
| From a plan, fix, upgrade | mattpocock-skills:tdd (step 2, or the entry's own step), superpowers:verification-before-completion (step 3), mattpocock-skills:code-review (step 4, Standards and Spec), `security-review` (step 4, by the security reviewer), superpowers:finishing-a-development-branch (step 5) |
| refactor | the same, with mattpocock-skills:tdd only where the entry runs a characterization card |
| docs-only | superpowers:verification-before-completion, mattpocock-skills:code-review (Standards), superpowers:finishing-a-development-branch |

Plus the skills the entry's own steps name (superpowers:systematic-debugging for fix, frontend-design:frontend-design for a task with a canvas). Where `security-review` is not listed, the security reviewer's checklist stands in and the `Skills:` line says "security checklist". Done when the `Skills:` line names every skill this table requires for the entry.

### Shared stack

A stack outside the worktree that several cards use (a staging compose, a shared database, a device) is used under a lock in the repository's common git folder: `mkdir -p "$(git rev-parse --git-common-dir)/fabreak-locks"`, then `mkdir "$(git rev-parse --git-common-dir)/fabreak-locks/<stack>"` as the atomic test, before the first command that starts, resets or tests against it, with this branch's name written to a file inside; `rm -r` of that folder after the last such command. The second `mkdir` failing means another card holds it: wait, checking every 30 s, up to 20 minutes, then one question to the owner naming the holder's branch. A card stops or resets only a stack whose lock it holds. A lock older than 60 minutes whose holder's branch has merged or has no worktree any more (`git worktree list`) is stale and may be removed. Step 6 releases every lock this session holds before it merges. Done when this session holds no lock.

### Dependency audit

Step 3 runs the audit of each package manager the repository uses, when its tool is on `PATH`:

| Lockfile | Command |
|---|---|
| `package-lock.json` | `npm audit --audit-level=high` |
| `pnpm-lock.yaml` | `pnpm audit --audit-level high` |
| `yarn.lock` (Berry) | `yarn npm audit --severity high` |
| `requirements*.txt` | `pip-audit -r <file>` per file |
| `poetry.lock` | `poetry export -f requirements.txt \| pip-audit -r /dev/stdin` |
| `uv.lock` | `uv export --format requirements-txt \| pip-audit -r /dev/stdin` |
| `Cargo.lock` | `cargo audit` |
| `go.sum` | `govulncheck ./...` |
| `Gemfile.lock` | `bundle audit check --update` |

A missing tool is printed as `audit: <tool> not installed`; nobody installs it. A non-zero exit is split by `git diff <merge-base> -- <manifest> <lockfile>` (`go.mod` and `go.sum` for Go): an advisory on a package this branch added or changed is load-bearing, counts toward `load-bearing` in the metrics line, and goes back to step 2 for one fix round like a review finding; an advisory already on the default branch is kept for the PR or MR body, under "For the plan", as an `upgrade` follow-up (step 5). docs-only runs no audit; upgrade runs it on every target. Done when every advisory is fixed or kept for "For the plan".

### Security axis

The third reviewer of step 4, a fresh subagent, invokes Claude Code's built-in `security-review` skill on this branch. Where that skill is not listed, it reviews the diff against this list, and the PR or MR body says so: injection (SQL, shell, template), broken access control, secrets in code or logs, unsafe deserialization, path traversal, SSRF, a dependency added without need. It rates each finding critical, high, medium or low: critical and high are load-bearing, medium and low cosmetic. Done when the reviewer has rated every finding.

### Rebase conflict

Another card merged first and the rebase onto the default branch fails. mattpocock-skills:resolving-merge-conflicts on this branch, then step 3 on the whole suite and step 4 on the conflicting files only. Report to the orchestrator; it records the task split as wrong in the plan ("Task splits that were wrong", with the two tasks) and adds the shared seam to `CLAUDE.md`. Done when the branch is rebased, green and re-reviewed.

### Human review requests changes

The PR comment wakes this same session. superpowers:receiving-code-review first: verify the comment against the code and push back with reasoning when it is wrong. When it is right, update the spec (a plan change goes under "For the plan" in the PR or MR body), then the tests, then the code, in that order. Then step 3, step 4, push. Done when every comment has a commit or a reasoned reply.

### Something fails mid-loop

superpowers:systematic-debugging. When no tight pass/fail signal exists for the failure, mattpocock-skills:diagnosing-bugs builds one first. The fix starts with a red test. Done when that test is green and the whole suite is green.

### Cross-repo

One spec, one plan, cards in several repos, each card naming the cards it depends on. A card whose dependency has not merged is held as board.md, Held cards, says: a recap naming the dependency, end the turn; the orchestrator of the repo that merged reports to this card's orchestrator, which wakes it. Once the dependency merges, cards in different repos run in parallel. Verification that needs a specific machine (a mobile end-to-end run) stays on that machine; the card names it. Done when the held card's dependency is Done.

### A question stops the session

The rule from SKILL.md, in its form: an interview round as the closing message after a recap-only box, a discrete choice in the question tool, a git go-ahead on the box's buttons; end the turn.

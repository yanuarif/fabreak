# Live-run fixes design (0.8.1)

The first live run of 0.8.0, on a private repository with a nine-task plan, held the plan flow (design, spec, plan, card round, held and woken cards, live metrics) and broke at the merge. This spec fixes what it found. It amends `2026-10-21-factory-gates-design.md` and `2026-10-21-card-metrics-design.md`; what it does not mention stays as they say.

Decisions the owner locked on 2026-10-22: a merge permission the card can use, a CI gate for a CI that never starts, no merge by the orchestrator, a tick only from the merge report, the app's branch, the skills a card must invoke, review axes the same in every round, held cards that read nothing, a lock for a shared stack; the release is 0.8.1.

## What the run showed

1. The permission classifier denied `gh pr merge` in every card session, so "merge without a question" never ran.
2. The orchestrator then merged a card's PR itself, on a turn the card's notification started, citing an earlier owner instruction.
3. The repository's CI never started (the host refused the jobs for billing). Gate (a) has no case for that; the owner settled it by message.
4. The orchestrator ticked a task before the card's merge report and built the `Metrics:` line itself, without `work`.
5. A card on the cheaper tier invoked no skill (no tdd, verification-before-completion, code-review, finishing-a-development-branch) and wrote no progress file; no card invoked tdd or verification-before-completion; one card ran verify without the audit.
6. Briefs named a branch from the repository's `CLAUDE.md`; cards left or renamed the app's branch, and the app later moved a session back onto the stale one. The app also reused worktree folders from an earlier plan, whose untracked `.env` pointed at old databases.
7. Review rounds differed: the security axis used the skill in one round and the checklist in the next, a re-review was one reviewer for all axes, a fix commit after the last round went unreviewed, and a card's `review` count stayed 0 after two rounds.
8. Held cards read loop.md and board.md and two ran `git fetch` before ending, and each took a second turn when the orchestrator relayed a brief change.
9. Two cards shared one staging stack; one tore it down while the other's integration run used it.

## Changes

### Merge permission (board.md, Card round)

When the owner grants merge, the same round adds the host's merge command to the repository's `.claude/settings.local.json` allow list, through the `update-config` skill: `Bash(gh pr merge:*)` on GitHub, `Bash(glab mr merge:*)` on GitLab. Bitbucket merges through the REST API; its cards keep asking. The owner's yes to the round is the approval; the app may show its own prompt for the settings change. Done when the allow rule is in the file, or the round says why it is not (Bitbucket, the owner declined).

A card whose merge is still denied asks the owner in its own session (loop.md step 6). It never hands the merge to the orchestrator.

### The orchestrator never merges (board.md, Done; loop.md step 6)

The orchestrator never merges a card's PR or MR and never runs a merge command for one, whatever the owner said earlier: an owner's standing instruction changes a card's gates, sent to the card, not who merges. A turn started by a card's message or an app event takes no owner action.

### CI that never starts (loop.md step 6; hosting.md)

Gate (a) becomes: CI green; or no CI; or CI that never started, where every check of the head commit failed before any job ran (on GitHub, the run's annotation says the job was not started, for billing or a spending limit, and the job took 0 s; a `startup_failure` run, or no run for the head commit after 10 minutes while a pull-request workflow exists, counts too; on GitLab no job ran and the pipeline's `failure_reason` says why). In the last two cases the step 3 lines are in the PR or MR body, and for CI that never started the body quotes the annotation. hosting.md gives the command to read it: `gh run view <run id>` (its ANNOTATIONS block).

### A tick only from the merge report (board.md, Done)

The orchestrator ticks a task only on the card's "Merged:" report and copies its `Metrics:` line verbatim. A PR the host shows merged without a report gets one `SendMessage` to the card asking for the report; the tick waits for the answer. The orchestrator never writes a `Metrics:` line itself.

### The app's branch and a reused folder (board.md, Start; loop.md step 1)

The brief names no branch: the card works on the branch the app created and opens its PR from it. A repository whose `CLAUDE.md` prescribes a branch pattern gets it from the app's branch-prefix setting; the orchestrator names a mismatch once in the card round. Step 1 adds: the folder may be one the app reused, so untracked files (`.env`, local data) are compared with the repository's example config and the brief's needs before step 2.

### Skills a card must invoke (board.md, brief item 3; loop.md steps 2-5)

A new loop.md section, Skills, lists per entry the skills the card or its reviewers invoke with the Skill tool: from a plan, fix and upgrade get tdd, verification-before-completion, code-review, `security-review` (by the security reviewer) and finishing-a-development-branch; refactor the same with tdd only for a characterization card; docs-only verification-before-completion, code-review (Standards) and finishing-a-development-branch; plus the entry's own skills. Brief item 3 points to it. The PR or MR body carries a `Skills:` line; gate (b) adds that it names every skill the table requires ("security checklist" where `security-review` is not listed). The progress file is written before the first step on every tier, for a card from a plan.

### Review axes the same in every round (loop.md step 4)

Every run of step 4, the first and every re-review, runs all its axes as separate fresh subagents in the same way: Standards and Spec through mattpocock-skills:code-review, security through a subagent that invokes `security-review` (the checklist only where the skill is not listed, said in the PR body). A re-review may be limited to the changed files; it never merges axes into one reviewer. A commit after the last run that adds to the branch's own diff (a flake fix, a conflict resolution) gets a run of its own before step 6; a clean sync with the default branch needs none. The metrics line is updated at the end of each run, before the next step starts.

### Held cards read nothing (board.md, Start item 6 and Held cards)

A held card's brief item 6 says: end the turn now with the recap "Held until <titles> merge"; read no file, run no command. The orchestrator sends a held card nothing until its wake-up: a change to the briefs (a new owner rule) goes into the wake-up message, and only running cards get it at once.

### A lock for a shared stack (loop.md, new section Shared stack)

A stack outside the worktree that several cards use (a staging compose, a shared database, a device) is used under a lock in the repository's common git folder: `mkdir -p` of `$(git rev-parse --git-common-dir)/fabreak-locks`, then `mkdir` of `<stack>` inside it as the atomic test, before the first command that starts, resets or tests against it, with the branch name written inside; `rm -r` of that folder after the last. The second `mkdir` failing means another card holds it: wait, checking every 30 s, up to 20 minutes, then one question to the owner naming the holder. A card stops or resets only a stack it holds the lock for. A lock older than 60 minutes whose holder's branch has merged or has no worktree any more is stale and may be removed. Step 6 releases every lock the card holds before it merges.

## Testing

Markdown only: the full check list from CONTRIBUTING.md and a read of each changed step for a completion criterion. Untested until the next live run: the allow rule letting a card's merge through the classifier in auto mode, the lock under two cards, and a held card ending without a tool call.

## Versioning

`0.8.1` in `plugin.json` and `marketplace.json`.

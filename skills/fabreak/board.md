# Board

A card is a task session the orchestrator starts; a session's title is the task's title. The plan in git stays the source of truth. The board is the plan board, a live, read-only page of the plan's tasks (Plan board, below); a card's own state is read from the sessions themselves (State, below).

## Cards

One plan task becomes one card: a task session the orchestrator starts. Every unchecked task gets its card in the same turn, as soon as the plan is committed, so the whole plan has sessions at once; a task that cannot run yet waits as a held card, not as a line in the plan.

**Stale plan.** A plan whose unchecked tasks already exist in the code is stale: before the card round, one question, `replan` to tick it or ignore it.

**Card round.** Before the first card, one question to the owner (SKILL.md form): the git permissions every card gets (commit on the branch; push and open the PR or MR; merge) and whether to start the cards now. The question says what the merge permission means: a card merges without asking when loop.md step 6's gates hold, and asks when one does not. A repository whose `CLAUDE.md` prescribes a branch pattern the app's branches do not follow gets one line in the question: the cards work on the app's branches, and the pattern comes from the app's branch-prefix setting. The owner's yes is the ask that lets the orchestrator start sessions, and the starts must happen in the turn the owner's answer began: a turn that another session's message or an automated event started can start nothing (the app refuses), so the orchestrator then repeats the question in its recap and starts the cards on the owner's next message. For an entry without a plan (fix, refactor, upgrade, docs-only, spike) the same round precedes its one card.

**Merge permission.** When the owner grants merge, the round's turn adds the host's merge command to the repository's `.claude/settings.local.json` allow list through the `update-config` skill: `Bash(gh pr merge:*)` on GitHub, `Bash(glab mr merge:*)` on GitLab; without it the permission classifier denies the card's merge. The owner's yes to the round is the approval; the app may show its own prompt for the change. Bitbucket merges through the REST API, and its cards keep asking. Done when the allow rule is in the file, or the round's recap says why it is not.

**Tier.** The orchestrator picks each card's model from its task before the start. A mechanical task runs on the cheaper tier: the plan or the entry's brief names every file and every change, and no design choice is left. Its start passes `model` = a Sonnet model id (the newest one the orchestrator's own system prompt lists). Every other task, and every task when in doubt, inherits the orchestrator's tier: `model` is omitted. An orchestrator already on Sonnet or below omits `model` for every card. Done when every card's tier is named in its brief (item 8).

**Start.** `start_session` per task, in plan order: `initiation: "user_asked"`, `context: "fresh"`, `use_worktree: true`, `title` = the task's title from the plan, and `model` as Tier says. The brief (`prompt`) carries, in this order:

1. The task's full text from the plan, pasted verbatim: steps and verification. For an entry without a plan (fix, refactor, upgrade, docs-only): the entry's own brief text, such as the bug report with the seam the regression test goes through (function and test file), the module design, the breaking-change list or the page list.
2. The spec path and the plan path, when they exist.
3. The entry and the steps the session runs: "Follow the `<name>` entry, `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`, from step N, then `loop.md` next to the router." The brief carries the substituted absolute paths, and the line "Invoke with the Skill tool every skill loop.md, Skills, lists for this entry; the PR body's `Skills:` line names them." The brief names no branch: the card works on the branch the app created.
4. The Spec source for review, as loop.md step 4 defines it for this entry.
5. The git permissions the owner gave in the card round: commit on the branch; push and open the PR or MR; merge. What is not listed stops the session with a question (SKILL.md rule).
6. The tasks this one depends on, by title, and this card's state: **run** when every dependency is ticked in the plan and fewer than three cards run, otherwise **held**, with the line "Held: end the turn now with the recap 'Held until <titles> merge'; read no file, run no command." At most three cards run at once; a running card is a session of this plan that has not merged and is not held.
7. The orchestrator's session id, from `get_session "self"`, for the merge report (Done).
8. The card's tier, its model id and its reason, one line: "Tier: cheaper (<model id>), mechanical: <the files the plan names>" or "Tier: orchestrator's (<model id>), <the design choice left>".
9. `Started: <time>`: one `date -u +%Y-%m-%dT%H:%MZ` the orchestrator runs before the round's first start, the same for every card of the round. The card's lead time counts from it (loop.md, Metrics).

`background` carries the project in two or three sentences and the rules for every entry from SKILL.md.

After the starts the orchestrator ends its turn. The first card in a repository may stop at a Trust repository prompt in its own window before it reads the brief; the owner trusts the folder there, and when the card reports that it has no brief the orchestrator sends the brief again with `SendMessage`. Later cards in that repository start at once. Done when every unchecked task has a session started at its tier.

## Held cards

A card whose brief says held ends its turn at once, before any tool call: a recap "Held until <titles> merge", no question, no file read, no command. A woken card that finds a dependency still unmerged (`git fetch origin`, then the ticks in the plan on the default branch) ends the same way. The orchestrator sends a held card nothing before its wake-up: a change to the briefs, such as a new owner rule, goes to the running cards at once and into each held card's wake-up message. The orchestrator wakes it with one message (`SendMessage` to the card's session id): "Go: <dependencies> merged. Sync the worktree with the default branch, then loop.md from step 1.", followed by any brief change made since the card started. The woken card syncs first (loop.md step 1) because its worktree was cut when the cards were started. Done when the woken card is in loop.md step 1.

## State

Every card is its own row under the orchestrator from the start. Read per-card state from the row (running marker, PR badge), from `list_sessions {linked: true}` (`prState`) and from the plan's ticks: a held card has ended its turn with "Held until", a card that stopped with a question or a wizard waits for the owner in its own session, a card with an open PR or MR is in review, and a ticked task is done. fabreak creates no sidebar sections and moves no sessions.

## Wizard

A step only a human can take runs through mattpocock-skills:wizard and stops the session until the owner reports it done. Before stopping, the message lists every stage in order: its purpose, the URL it opens, what to click there, each value it asks for (secret or public), and each decision with its options; then the run command, `bash <script> 2>&1 | tee <log>`, which keeps every stage on screen (the template clears the screen only on a terminal) and leaves the log as the evidence the wizard reports done with. Done when the message lists every stage and the run command.

## Done

When a PR or MR merges:

1. The task session, at the end of loop.md step 6: the merge report to the orchestrator, "Merged: <task title>, <PR or MR URL>. Metrics: lead … · work … · review … · load-bearing … · tier …" (`SendMessage` to brief item 7). Archiving the card session later removes its worktree; nothing in the loop deletes it.
2. The orchestrator, on the report, when the card came from a plan: `git pull --ff-only` on the default branch, tick the task (`- [x]`), copy the report's `Metrics:` line verbatim under the task's last step after one blank line, and commit the plan: "Tick <task title>". The tick happens only on a "Merged:" report: a PR or MR the host shows merged without one, or a report without the `Metrics:` line, gets one `SendMessage` to the card asking for it, and the tick waits for the answer. The orchestrator never writes a `Metrics:` line itself. For an entry without a plan the merged PR or MR is the record.
3. The orchestrator wakes held cards (Held cards): in plan order, every held card whose dependencies are all ticked, while fewer than three cards run. Done when every task is ticked or has a running or held card.

The orchestrator never merges a card's PR or MR and never runs a merge command for one, whatever the owner said earlier: an owner's standing instruction ("merge when the local run is green") changes the cards' gates and is sent to them; the card merges. A turn that a card's message or an app event started takes no owner action.

## Plan board

In the desktop app, "Show the board" opens the plan board: a live, read-only page of the plan's tasks in Backlog, In progress, Review and Done. A task's column comes from its steps, the worktree on its branch (a commit past the default branch, an uncommitted change, or a step ticked in the worktree's own copy of the plan or in the session's progress file, loop.md step 2, is In progress) and its PR (open is Review, merged is Done; `gh`, GitHub only), and the page updates as any of them changes. A card opens its details: dependencies, branch, worktree, PR and the task's plan text. A branch belongs to a task by its title or by its number (`03-editor`, `task-3`); a number counts only for a worktree that holds this plan. Besides `- [ ]` and `- [x]`, the board reads `- [/]` as a step being worked on and `- [-]` as a skipped step. Each card shows its metrics as chips: from the plan's `Metrics:` line once the task is ticked, live from the session's progress file before that; the header sums them for the plan (Done count, median lead and work, review rounds, load-bearing findings, tier mix). The board stops when the session that started it ends, or from its Stop button. Run the steps of the `board` command, `${CLAUDE_PLUGIN_ROOT}/skills/board/SKILL.md`. Done when the pane shows the board.

## CLI fallback

Without the preview pane (plain `claude` in a terminal), print the board as text from the plan, `git worktree list`, and hosting.md:

```
Backlog       - [ ] tasks with no open PR or MR whose worktree is missing or has no commit past the default branch (held cards)
In progress   - [ ] tasks whose branch has commits past the default branch and no PR or MR
Review        - [ ] tasks whose branch has an open PR or MR
Done          - [x] tasks, each with its Metrics: line
```

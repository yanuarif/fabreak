# Board

The board is the Claude Code desktop sidebar: sections are columns, sessions are cards, a session's title is the task's title. The plan in git stays the source of truth; the board is its live view.

## Sections

Five, in this order: **Backlog**, **In progress**, **Waiting on me**, **Review**, **Done**.

Before the first card: `list_sections`, then `create_section` for each name that is missing. Reuse an existing section with the same name; other sections the owner already has stay as they are. Done when all five names are listed.

## Cards

One plan task becomes one card: a task session the orchestrator starts. Every unchecked task gets its card in the same turn, as soon as the plan is committed, so the whole plan is on the board at once; a task that cannot run yet waits as a held card, not as a line in the plan.

**Card round.** Before the first card, one question to the owner (SKILL.md form): the git permissions every card gets (commit on the branch; push and open the PR or MR; merge) and whether to start the cards now. The owner's yes is the ask that lets the orchestrator start sessions, and the starts must happen in the turn the owner's answer began: a turn that another session's message or an automated event started can start nothing (the app refuses), so the orchestrator then repeats the question in its recap and starts the cards on the owner's next message. For an entry without a plan (fix, refactor, upgrade, docs-only, spike) the same round precedes its one card.

**Tier.** The orchestrator picks each card's model from its task before the start. A mechanical task runs on the cheaper tier: the plan or the entry's brief names every file and every change, and no design choice is left. Its start passes `model` = a Sonnet model id (the newest one the orchestrator's own system prompt lists). Every other task, and every task when in doubt, inherits the orchestrator's tier: `model` is omitted. An orchestrator already on Sonnet or below omits `model` for every card. Done when every card's tier is named in its brief (item 9).

**Start.** `start_session` per task, in plan order: `initiation: "user_asked"`, `context: "fresh"`, `use_worktree: true`, `title` = the task's title from the plan, and `model` as Tier says. The brief (`prompt`) carries, in this order:

1. The task's full text from the plan, pasted verbatim: steps and verification. For an entry without a plan (fix, refactor, upgrade, docs-only): the entry's own brief text, such as the bug report with the seam the regression test goes through (function and test file), the module design, the breaking-change list or the page list.
2. The spec path and the plan path, when they exist.
3. The entry and the steps the session runs: "Follow the `<name>` entry, `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`, from step N, then `loop.md` next to the router." The brief carries the substituted absolute paths.
4. The Spec source for review, as loop.md step 4 defines it for this entry.
5. The git permissions the owner gave in the card round: commit on the branch; push and open the PR or MR; merge. What is not listed stops the session with a question (SKILL.md rule).
6. The tasks this one depends on, by title, and this card's state: **run** when every dependency is ticked in the plan and fewer than three cards run, otherwise **held**. At most three cards run at once; a running card is a session of this plan that is neither Done nor held.
7. The orchestrator's session id, from `get_session "self"`, for the merge report (Done).
8. The board moves this session makes (Moves, below): `move_sessions` with `session_ids: [<root>, "self"]` to In progress when it enters loop.md step 1 in run state, Waiting on me at a question, Review when the PR or MR opens, Done after the merge; a held card makes no move. The brief names the root id when the orchestrator knows it; otherwise the card's first `["self"]` refusal names it.
9. The card's tier and its reason, one line: "Tier: cheaper, mechanical: <the files the plan names>" or "Tier: orchestrator's, <the design choice left>".

`background` carries the project in two or three sentences and the rules for every entry from SKILL.md.

After the starts the orchestrator moves the family to Backlog once (Moves) and ends its turn. The first card in a repository may stop at a Trust repository prompt in its own window before it reads the brief; the owner trusts the folder there, and when the card reports that it has no brief the orchestrator sends the brief again with `SendMessage`. Later cards in that repository start at once. Done when every unchecked task has a session started at its tier.

## Held cards

A card whose brief says held, or that is woken and finds a dependency still unmerged (`git fetch origin`, then the ticks in the plan on the default branch), ends its turn at once: a recap "Held until <titles> merge", no question, no move, nothing touched in the worktree. The orchestrator wakes it with one message (`SendMessage` to the card's session id): "Go: <dependencies> merged. Sync the worktree with the default branch, then loop.md from step 1." The woken card syncs first (loop.md step 1) because its worktree was cut when the cards were started. Done when the woken card is in loop.md step 1.

## Moves

| Event | Section | Who moves |
|---|---|---|
| Cards started | Backlog | the orchestrator, once: `move_sessions` with `session_ids: ["self"]`, or the root id the refusal names alongside it |
| Card in run state, loop.md step 1 | In progress | the task session: `move_sessions` with `session_ids: [<root>, "self"]` |
| Session stops with a question or a wizard | Waiting on me | the task session, the same call |
| Owner answers, session resumes | In progress | the task session, the same call |
| PR or MR opened | Review | the task session, the same call |
| Human review requests changes | In progress | the task session, the same call |
| Merged | Done | the task session, after the merge it ran (loop.md step 6) |

A card is nested under the session family's root and cannot move alone: `["self"]` is refused and the refusal names the root id to pass alongside. The family moves as one, so the column shows the card that moved last; with several cards running, the columns are not per card. Every card is still visible as its own row under the orchestrator from the start: read per-card state from the row (running marker, PR badge), from `list_sessions {linked: true}` (`prState`, `group`) and from the plan's ticks. A held card never moves the family. Moving a session other than "self" may ask the owner first; accept that prompt. Done when the section matches the latest event of the card that moved.

## Done

When a PR or MR merges:

1. The task session, at the end of loop.md step 6: the merge report to the orchestrator, "Merged: <task title>, <PR or MR URL>" (`SendMessage` to brief item 7), then `mark_completed` on itself and the move to Done. Archiving the card session later removes its worktree; nothing in the loop deletes it.
2. The orchestrator, on the report (or when the app continues it because its cards are idle), when the card came from a plan: `git pull --ff-only` on the default branch, tick the task (`- [x]`) and commit the plan: "Tick <task title>". For an entry without a plan the merged PR or MR is the record.
3. The orchestrator wakes held cards (Held cards): in plan order, every held card whose dependencies are all ticked, while fewer than three cards run. Done when every task is ticked or has a running or held card.

## Plan board

In the desktop app, "Show the board" also opens the plan board: a read-only page of the plan's tasks in Backlog, In progress and Done, derived from each task's ticked steps alone. Run the steps of the `board` command, `${CLAUDE_PLUGIN_ROOT}/skills/board/SKILL.md`. The sidebar sections above stay the live view of sessions; the plan board reaches Done when a task's last step is ticked, before the merge. Done when the pane shows the board.

## CLI fallback

Without the sidebar tools (plain `claude` in a terminal), print the board as text from the plan, `git worktree list`, and hosting.md:

```
Backlog       - [ ] tasks with no open PR or MR whose worktree is missing or has no commit past the default branch (held cards)
In progress   - [ ] tasks whose branch has commits past the default branch and no PR or MR
Review        - [ ] tasks whose branch has an open PR or MR
Done          - [x] tasks
```

Waiting on me is empty in the CLI: a stopped session is the terminal in front of the owner.

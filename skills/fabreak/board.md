# Board

The board is the Claude Code desktop sidebar: sections are columns, sessions are cards, a session's title is the task's title. The plan in git stays the source of truth; the board is its live view.

## Sections

Five, in this order: **Backlog**, **In progress**, **Waiting on me**, **Review**, **Done**.

Before the first card: `list_sections`, then `create_section` for each name that is missing. Reuse an existing section with the same name; other sections the owner already has stay as they are. Done when all five names are listed.

## Cards

One plan task becomes one card: a session proposal via `start_session` with `initiation: "own_initiative"`, `context: "fresh"`, `use_worktree: true`, `title` = the task's title from the plan. The brief (`prompt`) carries, in this order:

1. The task's full text from the plan, pasted verbatim: steps and verification. For an entry without a plan (fix, refactor, upgrade, docs-only): the entry's own brief text, such as the bug report with the seam the regression test goes through (function and test file), the module design, the breaking-change list or the page list.
2. The spec path and the plan path, when they exist.
3. The entry and the steps the session runs: "Follow the `<name>` entry, `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`, from step N, then `loop.md` next to the router." The brief carries the substituted absolute paths.
4. The Spec source for review, as loop.md step 4 defines it for this entry.
5. The git permissions the owner gave for this card: commit on the branch; push and open the PR or MR; merge. What is not listed stops the session with a question (SKILL.md rule).

`background` carries the project in two or three sentences and the rules for every entry from SKILL.md.

Proposal cards live in the orchestrator's transcript until the owner starts one. The first card in a repository may stop at a Trust repository prompt in its own window before it reads the brief; the owner trusts the folder there and starts the same card again. Propose at most three per turn; the rest wait in the plan as unchecked tasks. Propose a task only when every task it depends on is Done. Done when every unblocked, unchecked task has a card.

## Moves

| Event | Section | Who moves |
|---|---|---|
| Card started, linked session exists | In progress | the task session: `move_sessions` with `session_ids: [<root>, "self"]` |
| Session stops with a question or a wizard | Waiting on me | the task session, the same call |
| Owner answers, session resumes | In progress | the task session, the same call |
| PR or MR opened | Review | the task session, the same call |
| Human review requests changes | In progress | the task session, the same call |
| Held: a cross-repo dependency has not merged | Backlog | the task session, the same call |
| Merged | Done | the task session, after the merge it ran (loop.md step 6) |

A card is nested under the session family's root and cannot move alone: `["self"]` is refused and the refusal names the root id to pass alongside. The family moves as one, so the columns are exact while one card is in flight; with several cards running, read the board from the CLI fallback below. Moving a session other than "self" may ask the owner first; accept that prompt. Done when the section matches the latest event.

## Done

When a PR or MR merges:

1. `mark_completed` on the task session and move it to Done (the task session, at the end of loop.md step 6). Archiving the card session later removes its worktree; nothing in the loop deletes it.
2. When the card came from a plan: `git pull --ff-only` on the default branch, tick the task (`- [x]`) and commit the plan: "Tick <task title>". For an entry without a plan the merged PR or MR is the record.
3. Propose the cards that merge unblocks.

## Plan board

In the desktop app, "Show the board" also opens the plan board: a read-only page of the plan's tasks in Backlog, In progress and Done, derived from each task's ticked steps alone. Run the steps of the `board` command, `${CLAUDE_PLUGIN_ROOT}/skills/board/SKILL.md`. The sidebar sections above stay the live view of sessions; the plan board reaches Done when a task's last step is ticked, before the merge. Done when the pane shows the board.

## CLI fallback

Without the sidebar tools (plain `claude` in a terminal), print the board as text from the plan, `git worktree list`, and hosting.md:

```
Backlog       - [ ] tasks with neither a worktree nor an open PR or MR
In progress   - [ ] tasks whose branch has a worktree and no PR or MR
Review        - [ ] tasks whose branch has an open PR or MR
Done          - [x] tasks
```

Waiting on me is empty in the CLI: a stopped session is the terminal in front of the owner.

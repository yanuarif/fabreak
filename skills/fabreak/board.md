# Board

The board is the Claude Code desktop sidebar: sections are columns, sessions are cards, a session's title is the task's title. The plan in git stays the source of truth; the board is its live view.

## Sections

Five, in this order: **Backlog**, **In progress**, **Waiting on me**, **Review**, **Done**.

Before the first card: `list_sections`, then `create_section` for each name that is missing. Reuse an existing section with the same name. Done when all five names are listed.

## Cards

One plan task becomes one card: a session proposal via `start_session` with `initiation: "own_initiative"`, `context: "fresh"`, `use_worktree: true`, `title` = the task's title from the plan. The brief (`prompt`) carries, in this order:

1. The task's full text from the plan, pasted verbatim: steps and verification. For an entry without a plan (fix, refactor, upgrade, docs-only): the entry's own brief text, such as the bug report, the module design, the breaking-change list or the page list.
2. The spec path and the plan path, when they exist.
3. The entry and the steps the session runs: "Follow `entries/<name>.md` from step N, then `loop.md`, from the fabreak skill."
4. The Spec source for review: the plan path plus task heading (feature), the bug report (fix), or "`tests/` unchanged and green" (refactor).

`background` carries the project in two or three sentences and the rules for every entry from SKILL.md.

Proposal cards live in the orchestrator's transcript until the owner starts one. Propose at most three per turn; the rest wait in the plan as unchecked tasks. Propose a task only when every task it depends on is Done. Done when every unblocked, unchecked task has a card.

## Moves

| Event | Section | Who moves |
|---|---|---|
| Card started, linked session exists | In progress | the task session: `move_sessions` with `session_ids: ["self"]` |
| Session stops with a question or a wizard | Waiting on me | the task session, "self" |
| Owner answers, session resumes | In progress | the task session, "self" |
| PR or MR opened | Review | the task session, "self" |
| Human review requests changes | In progress | the task session, "self" |
| Held: a cross-repo dependency has not merged | Backlog | the task session, "self" |
| Merged | Done | the orchestrator; the app asks the owner once |

Moving a session other than "self" asks the owner first; accept that prompt. Done when the section matches the latest event.

## Done

When a PR or MR merges:

1. `mark_completed` on the task session and move it to Done.
2. Tick the task in the plan (`- [x]`) and commit the plan on the default branch: "Tick <task title>".
3. Propose the cards that merge unblocks.

## CLI fallback

Without the sidebar tools (plain `claude` in a terminal), print the board as text from the plan, `git worktree list`, and hosting.md:

```
Backlog       - [ ] tasks with neither a worktree nor an open PR or MR
In progress   - [ ] tasks whose branch has a worktree and no PR or MR
Review        - [ ] tasks whose branch has an open PR or MR
Done          - [x] tasks
```

Waiting on me is empty in the CLI: a stopped session is the terminal in front of the owner.

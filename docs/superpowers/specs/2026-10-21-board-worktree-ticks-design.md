# Board worktree ticks design

The live plan board (`2026-10-21-live-board-design.md`) misses work in flight. A task session ticks steps in the plan copy inside its own worktree, which the board never reads, and the app names card branches like `feat/03-export-pdf-4d2e1a` or `task/02-import-csv`, whose keys match no task title slug. In a real run a task sat in Backlog for its whole implementation and jumped to Review when its PR opened. This spec amends the live board spec; what it does not mention stays as that spec says.

Decisions the owner locked on 2026-10-21: match branches by task number as well, read step ticks from the task's worktree, and read two more step markers, `[/]` and `[-]`. The board stays read-only; nothing in the loop writes the new markers yet.

## Step markers

| Marker | `state` | Meaning |
|---|---|---|
| `- [ ]` | `open` | not started |
| `- [/]` | `doing` | being worked on |
| `- [x]`, `- [X]` | `done` | finished |
| `- [-]` | `skipped` | dropped; counts as resolved |

Each step keeps `done` (true only for `x`) and gains `state`. A plan has an open step when any step is `open` or `doing`; plan selection uses that.

Plan-only status: `done` when every step is `done` or `skipped` and there is at least one step; `in_progress` when any step is `done` or `doing`; else `backlog`. `resolve_status` uses the same counts in place of ticks.

## Branch matching by number

`branch_number(branch)`: the branch's last `/` segment, matched against `^(?:task-?)?0*(\d+)(?:-|$)` (case-insensitive), gives a task number; otherwise none. `02-import-csv`, `03-export-pdf-4d2e1a`, `task-07-cleanup-1eff3c` and `task-3` give 2, 3, 7 and 3; `2fa-login` gives none.

A worktree matches a task by its title slug first, as before. When no worktree matches by slug, a worktree matches by number only when its checkout holds the board's chosen plan file (same basename). A branch cut for an earlier plan lacks that file, so its numbers do not leak into a later plan. PRs are not matched by number: merged PRs from earlier plans would mark new tasks Done.

A worktree matched without a PR adopts the PR whose head branch is that worktree's branch, open before merged, closed ignored.

## Ticks from the worktree

`read_git` adds `plans` to each worktree: `{basename: text}` for every `.md` file under the worktree's plan folder. The poller already compares the whole result every 3 s, so a tick in a worktree reaches the page within about 3 s.

When a task's matched worktree holds the chosen plan and that copy has the same task number:

- same number of steps: each step takes the further state of the two copies, ranked `open` < `doing` < `skipped` < `done`, and the text of the worktree copy;
- a different number of steps: the worktree copy's steps as they are, since the branch replanned the task.

The task's `body` becomes the worktree copy's, and the task carries `steps_from: "worktree"`; otherwise `"plan"`. `plan_status` stays the root copy's plan-only status.

## Page

- Step boxes: `doing` is a half-filled box in the In progress colour, `skipped` a dashed box with the text struck through and dimmed.
- Card progress counts `done` over steps that are not skipped, and the line reads `<done>/<total>` plus ` · <n> skipped` when any are. The next step shown is the first `doing` step, else the first `open` one.
- Detail panel: a "Ticks" fact, "from the worktree" or "from the plan".
- Activity: "<step> started" when a step becomes `doing`, "<step> skipped" when it becomes `skipped`, alongside "ticked".

## Testing

`tests/test_plan_board.py` gains:

- `parse_plan` on `[/]` and `[-]`: states, `done`, and the plan-only status table above.
- `branch_number` on the examples above.
- `match_tasks` with a number-named worktree: matched when its `plans` holds the chosen plan, unmatched when it does not; a matched worktree adopts its branch's PR.
- `merge_steps`: further state wins per step; differing step counts take the worktree copy.
- The temporary git repository test: a worktree on `feat/02-short-a1b2c3` that ticks task 2's first step in its own plan copy, uncommitted; `load_board` reports task 2 `in_progress`, `steps_from` `worktree`, and the step `done`.

## Versioning

`/healthz` reports `"api": 3`; the command treats a server with this root and any other `api`, or none, as an older version, stops it and starts this one. `0.7.1` in `plugin.json` and `marketplace.json`. `board.md` (Plan board), `skills/board/SKILL.md` and the live board spec's matching section name the number match, the worktree ticks and the markers.

# Live plan board design

The plan board (`/fabreak:board`, `scripts/plan-board.py`) becomes realtime and interactive. It still writes nothing. This spec amends `2026-10-17-plan-board-design.md`; what it does not mention stays as that spec says.

Decisions the owner locked on 2026-10-21: push updates over Server-Sent Events; four columns from the plan, git and the PR host; card detail, filter and search, change highlights and keyboard navigation; the board stays read-only.

## Sources

A task's status now comes from three sources, read by the server:

| Source | How | When it is skipped |
|---|---|---|
| plan ticks | the plan files under `docs/superpowers/plans`, as before | never |
| worktrees | `git worktree list --porcelain`; per worktree on a branch other than the default: `git rev-list --count <default>..<branch>` and `git -C <path> status --porcelain` | the root is not the top level of a git repository (`git rev-parse --show-toplevel` differs), or `git` is missing |
| PRs | `gh pr list --state all --limit 100 --json number,title,state,url,headRefName,body` | `gh` is missing, not logged in, or the remote is not GitHub; GitLab and Bitbucket stay out of scope |

The default branch is `git symbolic-ref --short refs/remotes/origin/HEAD` without `origin/`, falling back to `main`, then `master`, whichever exists locally.

### Matching a task

`2026-10-21-board-worktree-ticks-design.md` adds matching by task number, step ticks read from the task's worktree, and the `[/]` and `[-]` step markers.

- **PR**: the PR's title or body contains `Task <N>: <title>` (case-insensitive; hosting.md puts the task heading in the body), or the PR title's slug equals the task title's slug, or the PR's head branch matches the task (below). An open PR wins over a merged one; closed PRs are ignored.
- **Branch**: a branch's key is its last `/` segment with a trailing `-<6 hex>` removed (the app names a card's branch from its title, as in `claude/complete-todo-3fa2c1`). It matches a task when the key equals the task title's slug, or the key is at least 8 characters and the slug starts with it. A key that matches more than one task matches none.
- **Worktree**: the worktree on the matched PR's head branch, else the worktree whose branch matches the task.

A slug is the lowercase title with every run of characters outside `a-z0-9` replaced by `-`, trimmed of `-`.

### Status

First match wins:

| Status | When |
|---|---|
| `done` | every step is ticked (at least one step), or the matched PR is merged |
| `review` | the matched PR is open |
| `in_progress` | some steps are ticked, or the matched worktree has a commit past the default branch or an uncommitted change |
| `backlog` | otherwise |

A ticked plan stays the record: a task whose steps are all ticked is Done even when its PR is still open.

## Parsing additions

`parse_plan` keeps what it returns and adds per task:

- `body`: the raw lines under the task heading up to the next heading of level 2 or 3 outside a fence, fences included, trimmed of blank lines at both ends.
- `depends`: the numbers `N` of every `Task <N>` on the first line under the task (outside a fence) that contains `depends on` (case-insensitive), without the task's own number; `[]` when no such line.

`status` from `parse_plan` is the plan-only status (`backlog`, `in_progress`, `done`); `load_board` replaces it with the resolved status and keeps the plan-only one as `plan_status`.

## Server

- A `Live` object per server polls in one daemon thread: plan file names, sizes and mtimes every 0.5 s; worktrees every 3 s; PRs every 30 s. When any result differs from the last one, it bumps a version and wakes every waiting stream.
- New route `GET /api/events?plan=<basename>`: `text/event-stream`. It sends `event: board` with the board JSON at once, then again whenever the version changes and the JSON for that plan differs from what it last sent; a `: ping` comment every 15 s keeps the connection open. The stream ends when the client goes away or the server stops.
- `GET /healthz` adds `"api": 2`; the command treats a server with this root and no `api` as an older version, stops it and starts this one.
- `GET /api/board` stays, now with the resolved statuses. Both carry `sources`: `{"git": bool, "prs": bool, "default": "<branch or null>"}`, and per task `live`: `{"branch", "worktree", "ahead", "dirty", "pr": {"number", "state", "url", "title"} or null}`, or `null` when nothing matched.
- A failing or slow command (5 s timeout for git, 15 s for gh) leaves that source as it was; the board keeps serving.

## Page

- Four columns: Backlog, In progress, Review, Done, each with a count.
- Header: repository, plan title, goal, plan dropdown (switches the stream without a reload), a search box, one toggle chip per column, the source line (`git`, `PRs`, or what is unavailable), and a live dot: green "Live" while the stream is open, amber "Reconnecting" while the browser retries.
- Card: `Task <N>`, the title, a progress bar with `<done>/<total>`, the next open step, and badges for the branch, `+<ahead>`, `dirty` and the PR (`#<n>` with its state).
- Detail: a click or Enter on a card opens a side panel with the status, the dependencies (each opens that task), branch, worktree path, ahead count, PR link, every step with its box, and the task's raw text. Esc or the close button closes it. On a narrow pane the panel covers the board.
- Filter: the search matches the title and step texts; the chips hide columns. The plan, search and hidden columns live in the URL (`?plan=&q=&hide=`), so a reload keeps them.
- Highlight: after an update, a card whose status changed, whose step got ticked, or whose PR appeared or changed state flashes for about 1.5 s, and one line per change goes to the activity list ("14:02 Task 3: Step 2 ticked"), newest first, at most 50, kept in memory for the page's life. Nothing is logged on the first load or a plan switch.
- Keyboard: arrows move between cards (up and down in a column, left and right to the nearest card in the next non-empty column), Enter opens the detail, Esc closes it or leaves the search box, `/` focuses the search, `1` to `9` pick a plan by its position in the dropdown.
- Still nothing writes: no drag, no tick, no form posts.

## Testing

`tests/test_plan_board.py` gains:

- `parse_plan`: `body` and `depends` on an inline plan.
- `slug`, `branch_key` and `match_tasks` on inline worktrees and PRs: body match, title slug match, branch key match, ambiguous key matches nothing, open beats merged, closed ignored.
- `resolve_status` for each row of the status table.
- A temporary git repository (created with `git init` in a temp folder): a plan with two tasks and a worktree on a branch named from task 2's title with one commit; `load_board` with git on reports task 2 `in_progress` with `ahead` 1.
- The SSE route: the first `event: board` arrives and parses; after the plan file is rewritten, a second event arrives with the new status.
- The page contains the four column names and `/api/events`.

## Out of scope

Writing to the plan, GitLab and Bitbucket PRs, session state from the desktop app, and persisting the activity list.

## Versioning

`0.7.0` in `plugin.json` and `marketplace.json`. `board.md`, Plan board, and `skills/board/SKILL.md` name the four columns and the sources; README's Limits line names the sources.

# Board progress and lifecycle design

Three gaps from the first live run with 0.7.1. This spec amends `2026-10-21-live-board-design.md` and `2026-10-21-board-worktree-ticks-design.md`; what it does not mention stays as they say.

Decisions the owner locked on 2026-10-21: step progress on a card must be realtime or not shown; the board stops when the session that started it ends, and the page has a button to stop it; the release is 0.7.2.

## Step progress from the session

A task session never edits the plan (loop.md, The plan file), so the plan's ticks reach the board only when the orchestrator ticks a merged task. A card in flight showed 0 of 8 steps while its branch was six commits ahead.

The session now writes its progress to a file outside the tree: the path `git rev-parse --git-path fabreak-steps.md` prints in its worktree. That path is inside the worktree's private git folder, so the file is never committed, never in a diff and never conflicts. Its content is the task heading and step lines copied from the plan, with the markers the board reads:

```
### Task 4: Export as PDF

- [x] **Step 1: Failing test for the PDF writer**
- [/] **Step 2: PDF writer**
- [ ] **Step 3: Docs**
```

loop.md step 2: before the first step, write the file; mark a step `- [/]` when it starts, `- [x]` when it is done and committed, `- [-]` when the task drops it (the reason goes in the PR or MR body under "For the plan"). An entry without a plan writes no file.

`read_git` adds `progress` to each worktree: the file's text, or `null` when it is missing. In `load_board`, after the worktree's plan copy, a matched task whose worktree has a progress file with the same task heading merges those steps by the same rule (`merge_steps`): the further state per step, or the file's steps when the counts differ. `steps_from` is then `"progress"`; the detail panel's Ticks fact reads "from the session".

## Stopping the board

- `POST /api/stop` with the header `X-Plan-Board: stop` stops the server: it answers `{"stopping": true}`, sends `event: stopped` on every open event stream, and exits 0. Without that header it answers 403. A custom header forces a CORS preflight, which the server never approves, so another site open in a browser cannot stop it.
- `--watch-pid <pid>`: the server checks every 2 s whether that process still exists and stops the same way when it is gone. The `board` command passes `$PPID` from its shell, which is the Claude Code process of the session that runs the command, so archiving or closing that session stops the board. A server another session reuses still stops with the session that started it; the next `/fabreak:board` starts a new one.
- Page: a Stop button in the header posts the stop. On `event: stopped`, from the button or the watcher, the page closes its stream and the live dot reads "Stopped" with the line "run /fabreak:board to start it again"; it does not reconnect.

## The command

- Step 2 stops an older server with `kill $(lsof -ti tcp:<port> -sTCP:LISTEN)`. Without `-sTCP:LISTEN`, `lsof -ti tcp:<port>` also lists every client connected to the port, such as the desktop app's network process while the preview pane shows the board, and `kill` ends those too.
- Step 3 starts the server with `--watch-pid $PPID`.
- `/healthz` reports `"api": 4`.

## Testing

`tests/test_plan_board.py` gains:

- `POST /api/stop` without the header is 403 and the server keeps serving; with it, 200, an open event stream receives `event: stopped`, and `serve_forever` returns.
- `pid_alive` for this process and for a finished child; `watch_pid` calls back once the child is gone.
- The temporary git repository: a progress file at the worktree's `--git-path` with task 2's heading and a `[/]` step makes task 2 `in_progress` with `steps_from` `"progress"`; a progress file for another task number changes nothing.
- The page contains `/api/stop`.

## Versioning

`0.7.2` in `plugin.json` and `marketplace.json`.

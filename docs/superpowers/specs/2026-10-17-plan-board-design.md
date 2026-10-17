# Plan board design

A read-only kanban view of a repository's plan, rendered in the Claude Code desktop preview pane. The plan in git stays the only source of truth; the board reads `docs/superpowers/plans/*.md` and shows every task in one of three columns. It writes nothing. One command, `/fabreak:board`, starts it and opens it beside the chat.

The sidebar board in `board.md` is unchanged: sessions stay the cards there, and the moves stay with the task session. The plan board is a second view of the same plan, for reading.

## Parts

```
scripts/plan-board.py        the server: parses plans, serves the page and the JSON
skills/board/SKILL.md        the /fabreak:board command: start the server, open the pane
skills/fabreak/board.md      gains a "Plan board" section that the router uses on "Show the board"
tests/test_plan_board.py     unittest: parser, plan selection, one HTTP round trip
```

`plan-board.py` is Python 3 standard library only: `argparse`, `http.server`, `json`, `pathlib`, `re`, `zlib`. No third-party package, no `pip`.

## Server

`python3 scripts/plan-board.py --root <repo> [--port N]`

- `--root` defaults to the current directory. The plan folder is `<root>/docs/superpowers/plans`.
- Binds `127.0.0.1` only. The default port is `7800 + (crc32(absolute root path) % 100)`, so two repositories served at once land on different ports and the same repository always lands on the same one. `--port` overrides it.
- Three routes, all `GET`:
  - `/` — the board page (HTML, CSS and JavaScript in one response, no external resource).
  - `/api/board?plan=<basename>` — JSON for one plan; without `plan`, the default plan. `plans` lists every plan file so the page can offer the others.
  - `/healthz` — `{"root": "<absolute root>"}`, used by the command to recognise a server that is already up for this repository.
- Every request reads the plan files from disk again. No cache, no file watcher. The page polls `/api/board` every 3 seconds and redraws when the JSON changed.
- Logging: one line per request to stderr is off by default; `--verbose` turns it on. Startup prints the URL on stdout: `http://127.0.0.1:<port>/`.

Port already taken by something that does not answer `/healthz` with this root: one line on stderr, `port <N> is in use by another process; pass --port`, exit 1. A `/healthz` that answers with this root: the server is already running; print its URL and exit 0.

## Parsing

A plan is a Markdown file under the plan folder. From it:

| Field | Source |
|---|---|
| title | the first line starting with `# ` |
| goal | the text after `**Goal:**` on the first line that has it, empty when absent |
| tasks | every heading `### Task <N>: <title>`, in file order, `<N>` an integer |
| steps | under a task heading, every line matching `^- \[( |x)\] ` until the next heading of level 2 or 3; `x` is case-insensitive |

The step text is the rest of the line with the surrounding `**` removed. Lines between tasks that are not steps (code blocks, file lists, notes) are ignored.

A task's status comes from its steps and nothing else:

| Steps ticked | Status |
|---|---|
| none, or no steps at all | Backlog |
| some | In progress |
| all | Done |

The CLI fallback in `board.md` also reads worktrees and PRs; the plan board does not. A task shows Done as soon as its last step is ticked, which `loop.md` step 2 does while implementing, before the PR opens. The plan board therefore reaches Done earlier than the sidebar board, whose Done waits for the merge; the plan is what the board shows.

Plan selection when `plan` is not given: the newest file by name (the names start with a date) that still contains an unchecked step; when none does, the newest file. "Newest by name" is a lexicographic sort of the basenames, descending. In code: `pick_plan(candidates)` takes a list of `(basename, has_unchecked)` pairs and returns the chosen basename, or `None` for an empty list.

JSON shape:

```json
{
  "root": "/abs/path",
  "plan": "2026-10-01-todo-api.md",
  "plans": ["2026-10-01-todo-api.md"],
  "errors": {},
  "title": "Todo API Implementation Plan",
  "goal": "The todo API from the spec, test-first.",
  "tasks": [
    {"number": 1, "title": "createTodo and listTodos", "status": "done",
     "steps": [{"text": "Step 1: Failing test for createTodo and listTodos", "done": true}]}
  ]
}
```

`status` is one of `backlog`, `in_progress`, `done`.

## Page

- Header: the repository's folder name, the plan title, the goal, and a plan dropdown that appears only when `plans` has more than one entry. Changing it reloads with `?plan=`.
- Three columns in this order: Backlog, In progress, Done, each with a count.
- One card per task: `Task <N>` small, the title, `<done>/<total>` steps, then the step list with a ticked or empty box per step. Cards keep plan order inside a column.
- Nothing on the page writes: no drag, no click handlers beyond the dropdown.
- Light and dark follow `prefers-color-scheme`. Layout stays readable at the preview pane's width (three columns that wrap to one under about 700 px).
- No plan folder, or no plan file in it: the page shows one line, `no plan found under docs/superpowers/plans`, and keeps polling so a plan written later appears without a reload.

## The command

`skills/board/SKILL.md`, frontmatter `name: board`, `disable-model-invocation: true`, no `argument-hint`. Steps:

1. Repository root: `git rev-parse --show-toplevel`. In a task worktree this is the worktree; the plan folder is the same files on that branch, which is what the owner wants to see from there.
2. Port: the same formula as the server. `curl -s http://127.0.0.1:<port>/healthz`; a reply whose `root` matches means the server is up.
3. Otherwise start it: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan-board.py" --root "<root>"` in the background, then `/healthz` again, up to 10 tries 0.3 s apart.
4. Open the pane: `navigate` to `http://127.0.0.1:<port>/`; when `navigate` reports no pane, `preview_start` with the same URL, once. One screenshot to confirm the header and the three columns rendered.
5. Without browser tools (plain `claude` in a terminal): print the URL and the CLI fallback from `board.md`.

Done when the pane shows the board, or the URL is printed.

The router's "Show the board (board.md)" row keeps pointing at `board.md`. `board.md` gets a short "Plan board" section before "CLI fallback": in the desktop app, show the board by running the `board` command's steps; the sidebar sections stay the live view of sessions. The CLI fallback stays as it is.

## Error handling

| Condition | Behaviour |
|---|---|
| `--root` is not a directory | stderr `root is not a directory: <path>`, exit 2 |
| plan folder missing or empty | serves normally; the page shows the one-line notice |
| a plan file fails to decode as UTF-8 | that file stays in `plans`, its reason lands in `errors` (`{"<name>": "not UTF-8"}`), and the page lists it under the columns; the others serve |
| a task heading without steps | status Backlog, `steps: []` |
| `python3` missing | the command reports it in one line and prints the CLI fallback |

## Testing

`tests/test_plan_board.py`, run with `python3 -m unittest tests/test_plan_board.py` from the repository root. It imports the script by path, so the script keeps its parsing in plain functions (`parse_plan(text)`, `pick_plan(names)`, `port_for(root)`) with no I/O.

- `parse_plan` on `tests/fixtures/greenfield-with-plan/docs/superpowers/plans/2026-10-01-todo-api.md`: title, goal, three tasks; task 1 `done` with 3 steps, tasks 2 and 3 `backlog`.
- `parse_plan` on an inline string with one ticked and one unticked step: `in_progress`. A task heading with no steps: `backlog`, empty steps. A `- [X]` line counts as ticked. A heading `## Notes` after a task ends its step list.
- `pick_plan`: two candidates, the newer fully ticked and the older with an unchecked step → the older; both fully ticked → the newer; empty list → `None`.
- `port_for`: stable for the same path, in `7800..7899`.
- One server round trip: start the handler on port 0 in a thread against the fixture, `GET /api/board`, assert the JSON `plan` and task statuses, `GET /healthz` returns the root; shut down.

CI gets one step after the checker self-test: `python3 -m unittest tests/test_plan_board.py`.

## Out of scope

Review and Waiting on me columns, drag and drop, ticking from the page, authentication, serving several repositories from one process, and any GitHub or GitLab call. The sidebar board and the CLI fallback keep covering session state.

## Versioning

`plugin.json` and `marketplace.json` go to `0.4.0` (main had already reached `0.3.0`). README: a `/fabreak:board` row in the Entries table and a line for `scripts/plan-board.py` and `skills/board/SKILL.md` in Layout. CONTRIBUTING's check list gains the unittest command.

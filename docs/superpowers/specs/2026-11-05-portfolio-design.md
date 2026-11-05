# Portfolio page design (0.9.0)

Each repository has its own plan board, so an owner with several products opens one board per repository to see where they all stand. This spec closes gap 6 of the software-factory roadmap with one page across repositories. It ships in 0.9.0 with stack templates.

Decisions the owner locked on 2026-10-21 and confirmed on 2026-11-05: a new command `/fabreak:portfolio`, modelled on `/fabreak:board`, runs `scripts/plan-board.py --portfolio`; the list of repositories is `~/.claude/fabreak/repos.md`, and `bootstrap` and `new` add their repository to it; one row per repository with its open plan, Done/total, running cards, median lead and load-bearing count, from `summarize()` and the `Metrics:` lines; a click on a row opens that repository's board; standard library only, 127.0.0.1, writes nothing; unit tests first.

## `repos.md`

The owner's file, next to `templates.md`:

```markdown
# Repositories

- /work/todo-api
- /work/invoicing-app
```

A line `- <path>` names one repository's main checkout: an absolute path, or one starting with `~`. Every other line is ignored, so the owner can add headings and notes. A relative path is reported as an error and skipped; a path listed twice is shown once.

`bootstrap` (a new step 6) and `new` (in step 6, before the bootstrap entry, because bootstrap runs only for a product's first repo) append the repository with one idempotent shell line:

```bash
root="$(cd "$(git rev-parse --path-format=absolute --git-common-dir)/.." && pwd)"
mkdir -p ~/.claude/fabreak && touch ~/.claude/fabreak/repos.md
grep -qxF -- "- $root" ~/.claude/fabreak/repos.md || printf -- '- %s\n' "$root" >> ~/.claude/fabreak/repos.md
```

The common git folder's parent is the main checkout, also when the entry runs inside a task worktree. Repositories set up before 0.9.0 are added by hand, or by running `/fabreak:bootstrap` again (each of its steps fills only what is missing).

## Server: `plan-board.py --portfolio`

`--portfolio` serves the portfolio instead of one board; `--repos FILE` overrides `~/.claude/fabreak/repos.md`; `--port` and `--watch-pid` work as for a board. The default port is 7900, outside the boards' 7800–7899. `/healthz` reports `{"root": "<repos file>", "api": 5, "portfolio": true}`, so a second start on a busy port finds the running server the same way a board does. A missing repos file is an empty list, and the page explains how to fill it.

One `Live` poller per listed folder, created when the folder appears in the file and stopped when it leaves the file or stops being a folder; its git reads run outside the portfolio's lock, so a request never waits on them. Pollers run on slower intervals than a board's (plans 2 s, git 10 s, PRs 60 s). A portfolio poller rereads `repos.md` every second and bumps its version when the file or any repository's poller changes, so the page's event stream pushes a new snapshot on every change, as a board's does.

### Rows

`portfolio_row(path, data)` builds one row from `load_board(path, None, data)`, so the plan it shows is the plan the board would open (the newest with an open step, else the newest):

| Field | From |
|---|---|
| `key` | 8 hex digits of the path's CRC-32, stable while the file changes |
| `name`, `path` | the folder name and the resolved path |
| `plan`, `title` | the chosen plan's file and title; `null` and `""` without a plan |
| `open` | a plan is chosen and not every task is Done |
| `done`, `tasks` | `summary.done`, `summary.tasks` |
| `running` | tasks In progress or in Review: cards in flight |
| `review` | tasks in Review, a part of `running` |
| `lead` | `summary.lead`, the median lead of the tasks with a `Metrics:` line in the plan |
| `load_bearing` | `summary.load_bearing` |
| `sources` | the board's `sources` (git, PRs) |
| `error` | `"not found"` for a path that is not a folder; every other field is then empty |

`load_portfolio(repos_file, data)`, with each repository's poller data by path, returns the rows in file order, the file's path, its errors and totals (repositories, open plans, running cards, load-bearing findings).

### Routes

| Route | Serves |
|---|---|
| `/` | the portfolio page |
| `/api/portfolio`, `/api/events` | the snapshot, and its event stream |
| `/api/stop` | stops the server, with the same `X-Plan-Board: stop` header a board needs |
| `/r/<key>/` | that repository's board page |
| `/r/<key>/api/board`, `/r/<key>/api/events` | that board's snapshot and event stream, from the repository's poller |

The board page uses relative API paths, so the same page works at `/` and under `/r/<key>/`. Under `/r/<key>/` it shows a "Portfolio" link back and hides its Stop button, since the server it would stop is the portfolio's.

## Page

A header with the repos file's path, the live dot, the totals and a Stop button, then one row per repository: name and path, the open plan's title (or "no open plan", or "no plan"), a progress bar with Done/total, running cards (with how many are in review), median lead and load-bearing findings, the last two in the board's chip style. A row is a link to `/r/<key>/`; keyboard focus and Enter follow from that. A row that changed since the last snapshot flashes, as a board card does. A missing path is a muted row with "not found". With no repositories: "No repositories in <file>. /fabreak:bootstrap and /fabreak:new add the repository they set up; add others as `- /path/to/repo` lines."

## Command

`skills/portfolio/SKILL.md` follows `skills/board/SKILL.md`: probe `/healthz` on 7900, start the server in the background with `--watch-pid $PPID` when it is not up (exit 1: retry on 8000), open the pane, one screenshot. Without browser tools it prints the URL. The router does not change: like `/fabreak:board`, the command is typed by the owner.

## Tests, written first

`read_repos` (absolute, `~`, relative skipped with an error, duplicates, other lines ignored, a missing file), `portfolio_row` (a plan with metrics, no plan, a missing path, running and review counts from a worktree and a PR), `load_portfolio` totals, and a server test: `/healthz`, `/api/portfolio`, `/r/<key>/api/board`, an unknown key's 404, and an event after `repos.md` gains a line.

## Out of scope

Sorting and filtering rows, more than one plan per repository in a row, GitLab and Bitbucket PR state (the board's own limit), and writing `repos.md` from the page.

# Card metrics design

fabreak runs every task through the same line (card, worktree, implement, verify, review, merge) but measures none of it. This spec adds one metrics line per card: two durations, the review rounds, the load-bearing findings and the model tier. It amends `2026-10-21-board-lifecycle-design.md`; what it does not mention stays as that spec says.

Decisions the owner locked on 2026-10-21: the durable record is a `Metrics:` line under the task in the plan, written by the orchestrator when it ticks the task; two durations, lead and work; the board shows chips on each card and a summary strip in the header; the release is 0.7.3.

## The metrics

| Key | Meaning |
|---|---|
| `lead` | From the card's start (brief item 9) to the host's merge confirmation (loop.md step 6). It includes the time a card was held. |
| `work` | From the first step marked `[/]` (loop.md step 2) to the same merge confirmation. |
| `review` | How many times loop.md step 4 ran for this card, rounds after a fix, a rebase conflict or a human review comment included. |
| `load-bearing` | The load-bearing findings of every round, added up. |
| `tier` | The model id the card session runs on, from its own system prompt. |
| `started`, `began` | UTC times, `2026-10-21T08:00Z`, of the card's start and of its first `[/]` step. Only in the progress file, while the card runs. |

A duration is written in days, hours and minutes, zero units left out, rounded down to the minute: `2d3h`, `3h10m`, `45m`, `0m`. Keys are separated by ` · `; the order is the table's.

## The line

In the plan, under the task's last step, written by the orchestrator in the same commit that ticks the task:

```
### Task 4: Export as PDF

- [x] **Step 1: Failing test for the PDF writer**
- [x] **Step 2: PDF writer**

Metrics: lead 3h10m · work 1h40m · review 2 · load-bearing 3 · tier claude-sonnet-5-5
```

In the progress file (`git rev-parse --git-path fabreak-steps.md`), under the task heading, written and kept current by the task session:

```
### Task 4: Export as PDF

Metrics: started 2026-10-21T08:00Z · began 2026-10-21T09:10Z · review 1 · load-bearing 2 · tier claude-sonnet-5-5

- [x] **Step 1: Failing test for the PDF writer**
- [/] **Step 2: PDF writer**
```

## Who writes what

- **Orchestrator, card start** (board.md, Start): one `date -u +%Y-%m-%dT%H:%MZ` before the starts; brief item 9 is `Started: <that time>`. Item 8 names the model id the card starts on.
- **Task session, loop.md step 2**: the progress file's `Metrics:` line goes under the heading with `started` from the brief, `review 0 · load-bearing 0` and `tier` = its own model id; `began` is added when the first step is marked `[/]`.
- **Task session, loop.md step 4**: each run adds 1 to `review` and that run's load-bearing count to `load-bearing`.
- **Task session, loop.md step 5**: the PR or MR body carries `Metrics: review <n> · load-bearing <n> · tier <id>`.
- **Task session, loop.md step 6**: after the host confirms the merge, it computes `lead` and `work` from `started` and `began` and appends the plan's form of the line to the merge report: "Merged: <task title>, <PR or MR URL>. Metrics: lead … · work … · review … · load-bearing … · tier …".
- **Orchestrator, board.md Done step 2**: writes that `Metrics:` line under the task's last step, then commits "Tick <task title>". A report without the line gets one question to the card session for it before the commit.

An entry without a plan (fix, refactor, upgrade, docs-only) has no progress file and no plan line: the session keeps the counts itself, and the PR or MR body and the merge report carry the line.

## The board

`parse_plan` reads the first line of a task that starts with `Metrics:` outside a fenced block into `task["metrics"]`: `lead` and `work` as minutes, `review` and `load_bearing` as integers, `tier` as text, `started` and `began` as the timestamps' text. Unknown keys and values that do not parse are left out.

`load_board` sets each task's `metrics`: the plan's line with `"source": "plan"`; otherwise, for a task matched to a worktree, the progress file's line with `"source": "live"`; otherwise `null`. It adds `board["summary"]`:

| Field | Value |
|---|---|
| `tasks`, `done` | The plan's task count and its Done count. |
| `measured` | Tasks with a plan line. |
| `lead`, `work` | The median of the plan lines' values in minutes, the lower middle value for an even count, `null` when none has one. |
| `review`, `load_bearing` | The sums over every task with metrics, plan and live. |
| `tiers` | `{tier: count}` over every task with metrics. |

The page:

- Card: chips after the badges: the tier without its `claude-` prefix, `review <n>`, `<n> load-bearing` (warning colour when above 0), and `lead <duration>`. A live card shows `lead` and, once `began` is set, `work` as the time since then, marked as running.
- Header: a strip under the goal: `<done>/<tasks> done`, then, when any task has metrics, `median lead`, `median work`, `review rounds`, `load-bearing` and the tier mix (`sonnet-5-5 ×3 · opus-5-5 ×2`).
- Detail panel: Lead, Work, Review rounds, Load-bearing and Tier facts, and Metrics "from the plan" or "live from the session".
- Live durations come from the timestamps in the browser; the page re-renders once a minute while any card is live. The server's JSON holds no clock, so an unchanged board sends no event.

`/healthz` reports `"api": 5`, and the `board` command's step 2 reuses a server only at `api` 5.

## CLI fallback

Each Done task is printed with its `Metrics:` line.

## Testing

`tests/test_plan_board.py` gains:

- `parse_duration` for `2d3h`, `3h10m`, `45m`, `0m` and a bad value; `parse_metrics` for the plan form, the progress form, an unknown key and a bad value.
- `parse_plan` takes the first `Metrics:` line of a task and ignores one inside a fence.
- `load_board` on a plan with two measured tasks and one bare task: the summary's medians, sums and tier mix; the temporary git repository: a progress file with a `Metrics:` line gives an unticked task `"source": "live"`, and a plan line wins over a progress line.
- The page contains the summary strip's element.

## Out of scope

Metrics across plans or repositories, cost in tokens, a metrics file beside the plan, and a summary in `release` evidence.

## Versioning

`0.7.3` in `plugin.json` and `marketplace.json`.

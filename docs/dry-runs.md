# Dry runs

Each run copied a fixture from `tests/fixtures/` to a scratch folder, made it a git repo, and ran one entry from a fresh subagent that had only the `skills/fabreak/` files and the installed prerequisite plugins. The rule for every run: stop at the first action that would write to the repo, dispatch a subagent, or need the owner's answer. The fixtures were not modified.

Date: 2026-10-17. Prerequisites: superpowers 6.2.0, mattpocock-skills 1.2.3.

## Baseline: `fix` without fabreak

Request: "fix this: invoice totals are off by one cent when a line has a discount: qty 3, unit price 0.10, discount 10% gives 0.27 but the finance team expects 0.26", on `legacy-no-context`, no fabreak files.

- Read the repo, ran the suite (1 pass), reproduced with `node -e`: the code and exact cent arithmetic both give 0.27.
- Looked for a spec, plan, `CONTEXT.md`, `CLAUDE.md`: none. Treated README plus the one test as the spec.
- Next action: a question to the owner about the rounding rule; had the expectation been taken at face value, a failing test in `test/invoice.test.js`, not a change to `src/`.
- Branch, review and PR were considered and deferred; no worktree, no card, no board.

The baseline reached the same question as the fabreak run below, but with no card, no worktree, no stated review step and no board. fabreak adds the structure, not the judgement.

## `new` on `new-empty`

Request: "a todo API for one user: create, complete, list".

| | |
|---|---|
| State | CONTEXT.md absent; no suite; no plan; not a worktree; argument `new` |
| Entry | `new`; argument and state agree; no routing question |
| Skills invoked | 1. mattpocock-skills:grilling |
| Stopped at | `skills/new/SKILL.md` step 1: grilling's first round of questions (seven, with recommendations) ready for the owner |

Findings fixed afterwards: the "one question" rule contradicted grilling's rounds (now scoped: task sessions ask one question, the orchestrator asks the skill's round); `--grill` and `--release` were listed in the argument hint and defined nowhere (now in state check 5); the empty-suite case in state check 2 was silent (now "absent").

## `fix` on `legacy-no-context`

Request: "invoice totals are off by one cent when a line has a discount: qty 3, unit price 0.10, discount 10% gives 0.27 but the finance team expects 0.26".

| | |
|---|---|
| State | CONTEXT.md absent; suite exists, no remote, ran once: `ℹ tests 1 / ℹ pass 1 / ℹ fail 0`, exit 0; no plan; not a worktree; argument `fix` |
| Entry | `fix`; no routing question |
| Skills invoked | none before the stop; the card brief named superpowers:systematic-debugging, mattpocock-skills:diagnosing-bugs (conditional), mattpocock-skills:tdd for the card session |
| Stopped at | `skills/fix/SKILL.md` step 1: the card brief was assembled; `create_section` and `start_session` were the next actions |
| Reproduction | symptom reproduced (0.27); the expected 0.26 is not what exact cent arithmetic gives, so the session's first question would be where 0.26 comes from |

Findings fixed afterwards: `fix` without CONTEXT.md routed silently (now stated as intended for fix, refactor, upgrade, docs-only); board.md's brief template assumed a plan task (now has a slot for the entry's own brief text); it was unclear who runs fix steps 2 to 5 (now the card session, named in the brief); "stop asking when the bug reproduces" ignored a wrong expected value (now a second case for the one question).

## `feature` on `greenfield-with-plan`

Request: "add due dates to todos, with an overdue flag in listTodos".

| | |
|---|---|
| State | CONTEXT.md present; suite green by a local run; open plan `2026-10-01-todo-api.md` with Tasks 2 and 3 unchecked; not a worktree; argument `feature` |
| Entry | `feature`; the argument won over the open plan; no routing question |
| Skills invoked | 1. superpowers:brainstorming (reads CONTEXT.md first, writes the spec) |
| Stopped at | `skills/feature/SKILL.md` step 2, brainstorming checklist item 3: the first clarifying question (calendar date or timestamp, with a recommendation) |

Findings fixed afterwards: brainstorming's own terminal rule ("the only skill after brainstorming is writing-plans") would have skipped fabreak's domain-modeling step (now: fabreak owns every hand-off, stated in SKILL.md and in new, feature, replan); `docs/adr/` was assumed to exist (now "when present"); an open plan with an explicit argument was silent (now the router names the open plan in one line first); the routing table's precedence was implicit (now "rows are read top-down; the first match wins").

## `takeover` on `legacy-no-context`

Request: "we inherited this invoicing module from a contractor; get it under control before we change anything".

| | |
|---|---|
| State | CONTEXT.md absent; suite green by a local run (no remote); no plan; not a worktree; argument `takeover` |
| Entry | `takeover`; argument and state agree; no routing question |
| Skills invoked | 1. mattpocock-skills:research with the codebase-map question and the output path |
| Stopped at | `skills/takeover/SKILL.md` step 1: the research skill dispatches a background agent that writes `docs/research/`; the brief was ready |

Findings fixed afterwards: SKILL.md's "no remote: run the suite locally" and hosting.md's "no remote: stop with a question" disagreed (now hosting.md has a "no remote" row: local suite, question only at the first PR or MR); state check 3's glob aborted the whole command in zsh (now `grep -rl ... 2>/dev/null`); the research skill's own output location could disagree with the entry's path (now the entry's path wins); the characterization module-list question lived only under "Stop asking when" (now in step 5); "green on the default branch" with no remote (now "a local run counts").

## Live run: `fix` on a private repository

Date: 2026-10-17. The orchestrator was a Claude Code desktop session; the repo a small TypeScript MCP server on GitHub with a vitest suite (99 tests), no CI workflow, origin/HEAD unset, and a stale plan (49 unchecked steps, all shipped). Request: three CLI validation errors named only the env var while a fourth named `ENV / --flag`. The card ran in an app-made worktree; the owner started it from the proposal card, merged the PR and answered four questions in all.

| | |
|---|---|
| State | CONTEXT.md absent; suite green by a local run (`gh run list` printed nothing); open plan named with its count; not a worktree; argument `fix` |
| Board | five sections created; the card could not move as `"self"` (nested under the family root) and moved with the root instead; the first start stopped at a Trust repository prompt |
| Card | systematic-debugging reproduced; tdd ran three red-green slices (the fix was green before loop.md step 2); verify printed `Tests 102 passed (102)`, exit 0; two fresh reviewers, no load-bearing finding; `gh pr create` with `--title`/`--body-file`; `gh pr checks` exited 1 with "no checks reported" |
| Merge | owner answered in both sessions; the card merged (squash, remote branch deleted) and the orchestrator's merge got "Merge already in progress"; `gh pr view --json state` = MERGED |
| Not reached | human review requests changes; rebase conflict; cross-repo; wizard; GitLab and Bitbucket commands; `release` and `closing` |

Findings fixed afterwards (33 in all, recorded outside the repo): no-CI fallback for state check 2 and hosting.md; default branch from `gh repo view` when origin/HEAD is unset; run the suite from the root with `.claude/worktrees` excluded (the main checkout counted every test twice while the worktree existed); open plan named with its unchecked count and a stale-plan question; model tier rule; loop.md step 1 is two commands; step 2 for plan-less entries; type-check and build in step 3; reviewers mark findings load-bearing or cosmetic; step 5 pre-chooses the PR option and needs the brief's permission; step 6 belongs to the task session and is done when the host reports merged; lessons when `CLAUDE.md` exists; board moves name the family root; Done list for plan-less cards and `git pull --ff-only` before the tick; Trust prompt on the first card; PR body instead of `--fill`; merge confirm line; GitHub Free has no branch protection; fix.md steps 2 to 4 reordered so red-green is one step.

## Installed-plugin sessions, 2026-10-17

Two takeovers on private repositories ran from the installed plugin (0.1.0 and 0.2.0), with thirteen card sessions: characterization, fix, docs-only and release cards. Held: takeover steps 1 to 5 in order, one card per module, cards proposed at most three per turn, the suite's summary line printed before every PR, two-axis review on ten cards, the merge run by the card session after the owner's go-ahead, lessons proposed as a docs-only card. Missed: no card moved on the board; card sessions wrote findings into the plan and conflicted at merge; verification-before-completion and finishing-a-development-branch were never invoked and tdd only in four cards; no fix card invoked systematic-debugging; the docs-only card had no review; no wizard ran; a change step became a hand-written release plan; no implementer subagent was dispatched. Each miss has a rule in the spec's 2026-10-18 changes.

## What the runs did not cover

A card that receives a review comment, a rebase conflict between two cards, a cross-repo plan, a wizard step, and the GitLab and Bitbucket command cells. The merge, Done and nesting rules were fixed from one card; a second card in the same repository is the test of those fixes.

## Changes from live use: cards and questions

Date: 2026-10-17. After a day of live use (a product built from scratch with an eighteen-task plan, and a takeover with characterization cards) the owner reported two things. A task session's question showed only the closing box's short question and its one-to-three-word buttons, so the options could not be understood; and plan tasks appeared only as proposal cards, at most three per turn and only once their dependencies were Done, and a proposal was sometimes not shown at all (a turn started by another session's message cannot start or propose sessions).

Changes, recorded in `docs/superpowers/specs/2026-10-17-cards-and-questions-design.md`: the question rule now requires the message to spell out every option, with the app's question tool for more than two; a wizard prints its stage list before parking and runs through `tee`; the orchestrator starts every task as a session after one card round (git permissions, start now), with run or held state in the brief and at most three running; a held card ends its turn with a recap and is woken by the orchestrator's message when a merge unblocks it; a merged card reports to the orchestrator. Version 0.3.0. Untested until the next plan runs: the wake-up message, the sync of a held card's worktree, and the three-running cap.

## Changes from live use: interview rounds as plain chat

Date: 2026-10-18. A `feature` run on a private repository asked its two scoping questions through the app's question tool, each option with a description, and the owner answered both from the message. The first brainstorming section then reached the owner as the closing box alone: the section was written only in the model's thinking, the box held a two-sentence recap, a short approval question and two buttons, and one button carried a design option found nowhere else. The 0.3.0 rule already called that a defect; it was the second time the box hid what the owner had to decide.

Change: an interview round (a grilling round, a brainstorming section, a spec approval) is plain chat. The closing box is a recap only and the section with its question is the closing message after it, so the content is the last thing the turn shows and the owner can answer in free text. A discrete choice of two to four options stays with the question tool. The box's question and buttons are kept for git go-aheads the app offers. Version 0.4.2. Untested until the next brainstorming run.

## Changes: a design step on a Claude Design canvas

Date: 2026-10-18. The owner asked whether fabreak used Claude Design; it did not. `new` and `feature` went from brainstorming's chosen approach to a spec in words, and frontend-design:frontend-design appeared only as visual direction in `spike` and `docs-only`.

Change, recorded in `docs/superpowers/specs/2026-10-18-design-step-design.md`: a new mechanism, `skills/fabreak/design.md`. In `new`, `feature` and `spike`'s UI branch, once the owner picks an approach, the screens go on a canvas made from the Artifact type "Design" (found through the Artifact tool's quickstart, never a hard-coded type link), the owner approves it in an interview round, and the spec's Screens section (a spike's ADR) records the canvas URL and artboards. Screen tasks in the plan name the canvas; loop step 2 reads it and invokes frontend-design:frontend-design, and the Spec axis checks each screen against its artboard. `docs-only` is unchanged. Version 0.5.0. Untested until the next `feature` with a screen: the canvas create, the approval round, the artboard names reaching a card brief, and a card reading the canvas.

## Changes: the router back under its token limit

Date: 2026-10-18. CONTRIBUTING.md keeps `skills/fabreak/SKILL.md` under 1,500 tokens, estimated as words × 1.4. The router was already over at 0.4.2 (1,118 words, about 1,565 tokens) and the design step's mechanism line took it to 1,127 words (about 1,578).

Change: text that one entry or one mechanism owns left the router, with a pointer in its place. The wizard's parking message (stage list and `tee` run command) moved to board.md, Wizard; the stale-plan question moved to board.md, Cards; the question for `feature` named without `CONTEXT.md` moved to the feature entry's When section. The routing rows lost the held-card note that board.md, Held cards, already gives and the list of entries that run without `CONTEXT.md`, which "Entry named: that entry" already implies. No rule changed. The router is 1,018 words, about 1,425 tokens. Version 0.5.1.

## Changes: no sidebar board, optional CI

Date: 2026-10-21. The owner asked to remove the sidebar board and to make writing CI optional.

Change, recorded in the fabreak design spec's 2026-10-21 changes: board.md keeps the card round, tier, brief, held cards, merge report and plan board, and drops the sidebar sections and every move; a new State section says where per-card state is read. `bootstrap` asks whether to write CI; without it, the local suite run stands in for CI green in loop step 6, `release` and branch protection. Version 0.6.0. Untested until the next live run: a plan's cards without any sidebar call, and a `bootstrap` that answers "no CI".

## Changes: a live, interactive plan board

Date: 2026-10-21. The owner asked for `/fabreak:board` to be more realtime and interactive, and chose push over polling, four columns from the plan, git and PRs, every proposed interaction, and a board that still writes nothing.

Change, recorded in `docs/superpowers/specs/2026-10-21-live-board-design.md`: a poller thread in `scripts/plan-board.py` watches the plan files (0.5 s), the worktrees (3 s) and the PRs through `gh` (30 s), and `/api/events` pushes the board to the page over Server-Sent Events. A task is Review while its PR is open and Done once it merges or every step is ticked; a worktree on its branch with a commit or an uncommitted change makes it In progress. The page adds a card detail panel, search and column chips kept in the URL, a flash and an activity line per change, and keyboard navigation. `/healthz` reports `api: 2`, so the command replaces a server from an older version. Version 0.7.0.

Checked in the preview pane against a temporary repository with two task worktrees: ticking a step in the plan and adding a worktree with an uncommitted file moved both cards within about a second, each with a flash and an activity line; stopping the server showed "Reconnecting" and restarting it returned to "Live" without a reload; the detail panel, arrow keys, Enter, Esc, search, column chips and the URL state worked; at 375 px wide the page had no horizontal scroll. `gh` listed this repository's PRs in about a second. Untested: a real card's branch name matching its task, and a PR open on a plan task.

## Changes: worktree ticks and two more step markers

Date: 2026-10-21. In a live run the board left a task in Backlog for its whole implementation and moved it to Review when its PR opened. The card's branch, `task/02-import-csv`, matched no task title slug, and the session ticked steps in the plan copy inside its own worktree, which the board did not read. The owner asked for both fixes, plus `[/]` and `[-]` read as more step states.

Change, recorded in `docs/superpowers/specs/2026-10-21-board-worktree-ticks-design.md`: a branch also matches a task by the number at the start of its last segment (`02-…`, `task-7`), only for a worktree that holds the board's plan; a worktree matched that way adopts the PR on its branch. `read_git` reads each worktree's plan files, and a matched task takes the further state of each step from the root plan and its worktree's copy. `- [/]` is a step being worked on (In progress) and `- [-]` a skipped step (resolved). `/healthz` reports `api: 3`. Version 0.7.1.

Checked against the same repository, read-only: the task in flight showed In progress with ticks from its worktree, and the merged tasks stayed Done with their PRs. Checked in the preview pane against a temporary repository with a worktree on `feat/02-editor-abc123`: the card sat in In progress with the doing step as its next step; changing a step to `[x]` and another to `[/]` in the worktree's uncommitted plan copy updated the card within 3 s, with "ticked" and "started" activity lines; the detail panel showed "Ticks: from the worktree", the half-filled doing box, and the worktree's plan text; a task with a `[-]` step read "2/2 · 1 skipped" in Done. Untested: nothing in the loop writes `[/]` or `[-]` yet.

## Changes: realtime step progress and a board that stops

Date: 2026-10-21. With 0.7.1 in a live run, a card six commits ahead still showed 0 of 8 steps: a task session never edits the plan, so ticks reached the board only after the merge. Replacing an older server with `kill $(lsof -ti tcp:<port>)` also ended the desktop app's network process, which was connected to the port while the preview pane showed the board; the app restarted it at once. A server started from a session kept running after that session was gone. The owner asked for realtime step progress or none, a board that stops with its session or from a button, and release 0.7.2.

Change, recorded in `docs/superpowers/specs/2026-10-21-board-lifecycle-design.md`: loop.md step 2 writes the task's steps with `[/]`, `[x]` and `[-]` to `fabreak-steps.md` in the worktree's private git folder (`git rev-parse --git-path`), which is never committed; the board reads it every 3 s and merges it like the worktree's plan copy. `POST /api/stop` with `X-Plan-Board: stop` stops the server and sends `event: stopped`; `--watch-pid` stops it when the given process ends, and the `board` command passes `$PPID`, its session's Claude Code process. The command kills only the port's listener (`-sTCP:LISTEN`). `/healthz` reports `api: 4`. Version 0.7.2.

Checked in the preview pane against a temporary repository with a clean worktree on `feat/02-editor-abc123`: a progress file alone put task 2 in In progress at 1/3; rewriting it moved the card to 2/3 within 3 s with two activity lines and no dirty badge; ending the watched process stopped the server (exit 0) and the page read "Stopped · run /fabreak:board to start it again" without reconnecting; the Stop button did the same. On a live board port, `lsof -ti tcp:<port>` listed the app's network process and the server, `-sTCP:LISTEN` the server alone. Untested: a real card session writing its progress file, and archiving a session in the desktop app ending its Claude Code process.

## Changes: card metrics

Date: 2026-10-21. Every card ran through the same line, but nothing measured it: no lead time, no count of review rounds or load-bearing findings, and the tier a card ran on lived only in its brief. The owner chose a `Metrics:` line under each ticked task in the plan, two durations (lead from the card's start, work from its first step, both to the merge), chips on each card with a summary in the board's header, and release 0.7.3.

Change, recorded in `docs/superpowers/specs/2026-10-21-card-metrics-design.md`: brief item 9 carries `Started`; loop.md step 2 adds a `Metrics:` line to the progress file (`started`, `began`, `review`, `load-bearing`, `tier`), step 4 counts each run, step 5 puts the counts in the PR body, and step 6 appends the plan's form of the line to the merge report; board.md Done step 2 copies that line under the task when it ticks it. The board parses the line from the plan, or live from the progress file, adds `summary` to its JSON and shows chips, a header strip and detail facts; live durations are computed in the browser and refreshed once a minute. `/healthz` reports `api: 5`. Version 0.7.3.

Checked in the preview pane against a temporary repository with two measured Done tasks, one card in a worktree with a progress file and one backlog task: the strip read 2/4 done, 3h10m median lead, 55m median work, 4 review rounds, 4 load-bearing and the tier mix; the live card showed `lead 2h` and `work 35m` with dashed chips; raising `review` in the progress file updated the chip and the strip within 3 s and logged "review round 2"; the detail panel read "live from the session". Untested: a real card session writing the line through review rounds and a merge, and the orchestrator copying it into the plan.

## Changes: factory gates

Date: 2026-10-21. Measured against a software factory, three more gaps remained after card metrics: no security gate, no intake from outside the owner's request, and nothing that runs without the owner typing a command. The merge permission from the card round also changed nothing, because loop.md step 6 asked for the go-ahead anyway. The owner chose a security axis plus a dependency audit with high and critical findings load-bearing, a `triage` entry with a scheduled run offered by `bootstrap`, merge without a question when the gates hold, and one release with card metrics as 0.8.0.

Change, recorded in `docs/superpowers/specs/2026-10-21-factory-gates-design.md`: loop.md step 3 runs each package manager's audit and splits advisories by the lockfile's diff against the merge-base (new ones are load-bearing, old ones become `upgrade` follow-ups under "For the plan"); step 4 adds a third fresh reviewer that invokes Claude Code's `security-review` skill or a fixed checklist; step 6 merges without a question when the brief grants merge and CI, review and human review gates hold. `skills/triage/SKILL.md` reads the default branch's CI, the host's open issues, an `Intake hook:` command named in `CLAUDE.md` and the request, sorts each item into an entry, asks once with a table, logs every decision in `docs/superpowers/triage.md` and runs one card round for the picks. `bootstrap` step 5 offers a weekday triage as a desktop-app scheduled task. hosting.md gains Open issues and Review state rows. The router gains one row and stays at 1,037 words, about 1,452 tokens. Version 0.8.0, which also carries card metrics.

A fresh reviewer found four load-bearing gaps before the commit, all fixed: the security reviewer now rates critical, high, medium or low instead of load-bearing or cosmetic; `pip-audit` reads each lockfile through `-r` instead of the installed environment; GitHub's review gate reads each reviewer's latest review and unresolved review threads, not `reviewDecision` alone; and triage treats issue and hook text as data that a brief quotes and nobody obeys. No fixture covers these steps; they are Markdown only and were read for a completion criterion per step. Untested until a live run: an audit's split by lockfile diff, the `security-review` skill inside a reviewer subagent, a card merging without a question, triage against a repository with open issues and an intake hook, and a scheduled task firing. `docs/adlc.svg` now shows triage, the dependency audit, the security reviewer, the merge gates and metrics on the board; every changed label was measured inside its box.

## Live run: 0.8.0 on a private repository

Date: 2026-10-22. A `feature` entry on a private TypeScript monorepo with CI whose jobs the host refused for billing: brainstorming, a design canvas, spec, domain model and a nine-task plan, then one card round and nine cards (one on the cheaper tier, eight held). Held: the design-first order, `Started:` and the tier with its model id in every brief, held cards ending with "Held until", wake-ups after each tick, never more than three running, live metrics in the progress file of the Opus cards, the audit and two review rounds with a load-bearing fix on the second card, and a merge report with all five keys copied verbatim.

Missed: the permission classifier denied `gh pr merge` in every card, so no card merged without a question; the orchestrator then merged one card's PR itself, on a turn the card's notification started; gate (a) had no case for CI that never starts, and the owner settled it by message; the first task was ticked before its merge report with a `Metrics:` line the orchestrator built (no `work`); the cheaper-tier card invoked no skill and wrote no progress file, and no card invoked tdd or verification-before-completion; briefs named branches from the repository's `CLAUDE.md`, so cards left or renamed the app's branch, and the app reused folders from an earlier plan with stale `.env` files; review rounds switched between the security skill and the checklist, merged axes into one reviewer, left a fix commit unreviewed and a `review` count at 0; held cards read files and two ran `git fetch` before ending; two cards shared one staging stack and one tore it down under the other.

Change, recorded in `docs/superpowers/specs/2026-10-22-live-run-fixes-design.md`: granting merge adds the host's merge command to `.claude/settings.local.json` through `update-config`; a denied merge is asked in the card's own session; the orchestrator never merges and ticks only on a "Merged:" report, asking the card when one is missing; gate (a) treats CI that never started as no CI, with the annotation quoted (hosting.md says how to read it); the brief names no branch and lists the skills per loop step, the PR body carries a `Skills:` line that gate (b) checks, and loop.md step 1 checks untracked config in a reused folder; every review run runs each axis as its own fresh subagent, and a commit after the last run gets a run of its own; a held card ends before any tool call and gets brief changes only in its wake-up message; a new Shared stack section locks a stack several cards use with `mkdir` in the common git folder. A fresh reviewer found six load-bearing gaps in the first draft, all fixed before the commit: the lock's `mkdir` needed its parent made first, a crashed holder's lock could never go stale, the `Skills:` gate asked docs-only for skills it never runs (now a per-entry table in loop.md, Skills), the progress file had no heading for an entry without a plan, a clean sync looked like a commit needing review, and a held lock was a gate with nothing to ask. Version 0.8.1. Untested until the next live run: the allow rule letting the merge through in auto mode, the lock under two cards, and a held card ending without a tool call.

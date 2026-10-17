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

# fabreak design

fabreak is a Claude Code plugin with one skill: a router that runs the Agentic Development Lifecycle (ADLC) by invoking skills from three public plugins (superpowers, mattpocock-skills, frontend-design). It reads the state of a repository, picks an entry, and then calls the installed skills in a fixed order. It copies nothing from those skills.

## Parties

Three, and only three:

- **Owner** — the human who owns the repo. Does what only a human can do: secrets, deploys, store consoles, branch protection, access. Answers questions.
- **Orchestrator session** — the Claude Code session where `/fabreak` was invoked. Reads state, runs the entry, keeps the board and the plan, proposes task cards.
- **Fresh subagent per task** — implementer, reviewer, researcher. Roles are skills, not named agents. The model tier is chosen per task when the subagent is dispatched. Reviewers are always fresh; an implementer never reviews its own work.

## Plugin layout

```
.claude-plugin/plugin.json          plugin manifest
.claude-plugin/marketplace.json     the repo is its own marketplace
skills/fabreak/SKILL.md             router: state detection, argument table, rules for every entry
skills/fabreak/entries/<arg>.md     one file per entry (12)
skills/fabreak/board.md             sidebar board mechanics and CLI fallback
skills/fabreak/loop.md              loop C and its rules
skills/fabreak/hosting.md           hosting detection, PR/MR, CI, branch protection
docs/adlc.svg                       the ADLC chart, generic
docs/dry-runs.md                    fixture dry-run log
docs/superpowers/{specs,plans}/     this spec and its plan (the repo dogfoods fabreak)
tests/fixtures/<name>/              synthetic repos for dry runs
scripts/check-forbidden-words.sh    the word check (pre-commit and CI)
scripts/forbidden-words.sha256      hashed word list
.githooks/pre-commit                runs the word check on staged files
.github/workflows/check.yml         plugin validate + word check
README.md, LICENSE, CONTRIBUTING.md
```

### SKILL.md is a context pointer

The router stays under 1,500 tokens. It holds only: frontmatter, the state detection order, the argument-to-entry table, the rules that bind every entry, and pointers to `board.md`, `loop.md`, `hosting.md`. Entry files load only when their entry is chosen. The skill is model-invoked (it keeps a `description`) because the per-repo `CLAUDE.md` line "Every development request starts with /fabreak" asks the agent itself to reach it.

## State detection

Checked in this order, before any entry runs. Each check is a shell lookup, not a guess.

1. `CONTEXT.md` at the repo root (the domain model exists).
2. A test suite exists, and whether it is green: the default branch's CI status via `hosting.md` when a remote exists; otherwise run the suite once and keep its summary line.
3. A plan under `docs/superpowers/plans/` with unchecked tasks (`- [ ]`).
4. An active worktree: `git rev-parse --git-dir` differs from `--git-common-dir` (and not a submodule) — this session is a task session.
5. The argument given to `/fabreak`.

Resolution:

| State | Entry |
|---|---|
| Argument given | That entry. Detection still informs it (for example `feature` on a repo without `CONTEXT.md` asks whether `takeover` was meant). |
| Active worktree | `loop.md`, resuming the task this worktree belongs to. |
| Open plan, no argument | `loop.md`, next unchecked task; the board is shown first. |
| No `CONTEXT.md`, no source files | `new` |
| No `CONTEXT.md`, source files present | `takeover` |
| `CONTEXT.md`, no open plan, request describes a bug | `fix` |
| `CONTEXT.md`, no open plan, request describes a change | `feature` |

When two entries both fit, the router asks one question with the two entries as answers. It never picks one silently.

## Rules for every entry

Written once, in SKILL.md:

- No code before a plan, except `fix`, `refactor`, `upgrade`, `docs-only`.
- One task = one card = one session = one worktree = one PR or MR.
- Reviewers are fresh subagents; the implementer never reviews itself.
- Verification evidence is command output: the runner's summary line printed verbatim with its exit code.
- Actions only a human may take (secrets, deploys, store consoles, branch protection, access) go through a wizard and park the session in Waiting on me.
- A question stops the session: one question, answer buttons, never a guess.

## Entries

Each `entries/<arg>.md` has the same five sections: **When** (enter here if), **Steps** (skills invoked, in order, with the arguments fabreak passes), **Artifacts** (what is produced and where), **Stop asking when**, **Done when**.

| Entry | Lane | Skills, in order | What differs from the full lane |
|---|---|---|---|
| `new` | A1 | mattpocock-skills:grilling → superpowers:brainstorming → mattpocock-skills:domain-modeling → superpowers:writing-plans → `bootstrap` | Full lane A, then bootstrap before the first card. |
| `feature` | A2 | superpowers:brainstorming → mattpocock-skills:domain-modeling → superpowers:writing-plans | Grilling skipped unless `--grill`; brainstorming narrowed to the feature; new terms go to `CONTEXT.md`. |
| `takeover` | B1 | mattpocock-skills:research → mattpocock-skills:domain-modeling → mattpocock-skills:codebase-design → mattpocock-skills:writing-for-agents → mattpocock-skills:tdd (characterization) → grilling → brainstorming → writing-plans | Repo stays on the owner's hosting; characterization tests before any change; one card per module. |
| `spike` | A3 branch | mattpocock-skills:research → mattpocock-skills:prototype (+ frontend-design when UI) → mattpocock-skills:domain-modeling | Time-boxed; branch archived, never merged; output is an ADR and an updated plan. |
| `bootstrap` | A5 | mattpocock-skills:writing-for-agents → mattpocock-skills:setup-pre-commit (when a `package.json` exists) → mattpocock-skills:wizard | `CLAUDE.md`, CI, pre-commit by fabreak; branch protection and CI secrets by the owner through the wizard. |
| `fix` | C1 | superpowers:systematic-debugging → mattpocock-skills:diagnosing-bugs (when the loop is not tight) → mattpocock-skills:tdd → `loop.md` | No spec; reproduce and red test first; Spec axis = the bug report; `--release` uses the release branch then backports. |
| `refactor` | C1 | mattpocock-skills:codebase-design → mattpocock-skills:tdd (characterization when missing) → `loop.md` | Spec axis = "`tests/` unchanged and green". |
| `upgrade` | C1 | superpowers:systematic-debugging → `loop.md` → mattpocock-skills:wizard | One card per version jump; verification = whole suite plus build of every target; store console changes by the owner. |
| `docs-only` | C1 light | frontend-design (when the docs are rendered) → mattpocock-skills:code-review (Standards only) → `loop.md` light | No unit tests; verification = lint or preview; Standards axis only. |
| `replan` | A4 | superpowers:brainstorming → superpowers:writing-plans | Spec updated in place; remaining tasks rewritten; stale Backlog cards withdrawn; the plan records the replacement. |
| `release` | after D | superpowers:verification-before-completion → mattpocock-skills:wizard | All plan cards Done and main CI green; version, changelog, evidence under `evidence/`; store steps by wizard; tag last. |
| `closing` | after D | superpowers:writing-plans → superpowers:verification-before-completion → mattpocock-skills:wizard | One card per feature: UAT scenario, evidence, closing note; client steps park the session; access revocation by wizard. |

Entry files name skills with the `plugin:skill` form the Skill tool accepts. Arguments fabreak passes (a spec path, a fixed point for review, a bug report) are written in the Steps section of each entry.

## Board (`board.md`)

The board is the Claude Code desktop sidebar. Five sections, created when missing (`list_sections`, then `create_section`): **Backlog**, **In progress**, **Waiting on me**, **Review**, **Done**.

- A plan task becomes a **card**: a session proposal (`start_session`, `own_initiative`) whose brief is the task's text from the plan, the spec path, and the plan path. One task, one card. Proposal cards live in the orchestrator's transcript until the owner starts them.
- Starting a card creates a linked session in its own worktree. The task session files itself under **In progress** (`move_sessions` with `"self"`).
- **Waiting on me**: a session that stopped with a question or a wizard. **Review**: a PR or MR is open. **Done**: merged; the task session is marked completed and the orchestrator ticks the plan task.
- **Backlog** holds started sessions that are held: a cross-repo card waiting for its dependency to merge.
- Moving a session that is not "self" asks the owner first; fabreak accepts that prompt rather than working around it.
- **CLI fallback**: when the sidebar tools are absent, the board is printed as text from the plan: unchecked tasks as Backlog, tasks with an open PR as Review (from `hosting.md`), checked tasks as Done.

## Loop C (`loop.md`)

The same loop for every entry that writes code. Per task session:

1. superpowers:using-git-worktrees — the app gives each session a worktree; the skill verifies it.
2. Implementation: superpowers:subagent-driven-development when subagents are available, else superpowers:executing-plans. TDD per task via mattpocock-skills:tdd at agreed seams.
3. superpowers:verification-before-completion — the runner's summary line printed verbatim, with the exit code.
4. mattpocock-skills:code-review by fresh subagents, two axes. Spec source = the task's plan path. For `fix`, the bug report. For `refactor`, "`tests/` unchanged and green".
5. superpowers:finishing-a-development-branch — green suite, then PR or MR via `hosting.md`. Card to Review.
6. Merge: card to Done; the orchestrator ticks the task in the plan and commits the plan.

Rules inside the loop:

- **Rebase conflict** (another card merged first): mattpocock-skills:resolving-merge-conflicts on the own branch, suite rerun, review rerun on the conflicting files only. The orchestrator records in the plan that the task split was wrong; the shared seam goes into `CLAUDE.md`.
- **Human review rejects**: the PR comment wakes the same session. superpowers:receiving-code-review verifies the comment first; spec and tests are updated before code.
- **Debugging** when something fails mid-loop: superpowers:systematic-debugging, or mattpocock-skills:diagnosing-bugs when a tight feedback loop is missing. Red test first.
- **Cross-repo**: one spec, one plan, cards in several repos with dependencies. The client card is held in Backlog until the API contract merges; then repos run in parallel.
- **A question stops the session**: one question, answer buttons, card to Waiting on me. The answer resumes the same session.

## Hosting (`hosting.md`)

Detected from `git remote get-url origin`. Only the PR/MR → CI → merge box depends on it.

| Host | Tooling | PR/MR | CI status | Merge | Branch protection |
|---|---|---|---|---|---|
| GitHub | `gh` | `gh pr create` | `gh pr checks` | `gh pr merge` | wizard (repo settings); app PR monitor and Auto-fix available |
| GitLab | `glab` | `glab mr create` | `glab ci status` | `glab mr merge` | wizard; merge check "pipeline must succeed" |
| Bitbucket | REST API with an app password from the environment, else manual instructions | API or instructions | API or instructions | API or instructions | wizard; no app monitor, the session polls its own status |
| Unknown or no remote | — | the session stops with a question | — | — | — |

## Durable record

Sessions are not an archive. The plan in git is: tasks ticked when their PR merges, replans recorded with the replaced tasks, archived spikes recorded with their ADR, wrong task splits recorded. Specs, ADRs, `evidence/`, and PRs or MRs are the history.

## Public repo rules

- No project, client, organization, or person names, no home paths, no private links. The list of forbidden words is stored as SHA-256 hashes in `scripts/forbidden-words.sha256`; the words themselves never appear in the repo.
- Matching: whole word, case-insensitive, after lowercasing; tokens are taken both with and without hyphens so hyphenated names match. `/Users/` and `claude.ai/artifact` are matched as plain substrings. The exact install URL `github.com/<owner>/fabreak` is stripped before scanning, so the owner's handle may appear only there.
- The pre-commit hook scans staged files; CI scans all tracked files. Same script.
- Examples use fictional generic projects ("a todo API", "a legacy invoicing app").
- MIT license, copyright holder "Yanuar Arifin".
- README names prerequisites as public plugins with links to their repos.

## Fixtures and dry runs

Three small synthetic repos under `tests/fixtures/`, plain directories (a dry run copies one to a scratch folder and runs `git init` there):

- `new-empty` — empty.
- `greenfield-with-plan` — `CONTEXT.md`, a spec, a plan with unchecked tasks, a tiny source tree.
- `legacy-no-context` — small code with a passing test, no `CONTEXT.md`.

Dry runs of `new`, `fix`, `feature`, `takeover` go only up to the first step that would modify the fixture. `docs/dry-runs.md` records, per run: skills invoked, their order, and where it stopped.

## Out of scope

Business development, hypothesis research, project-specific tools. A repo may add a verification hook in its `CLAUDE.md` (for example a mobile end-to-end run); fabreak calls it only when it exists.

## Known limits (stated in README)

- The board exists only in the Claude Code desktop app; the CLI gets the text fallback.
- The PR monitor and Auto-fix exist only for GitHub.

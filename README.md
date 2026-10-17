# fabreak

fabreak is one Claude Code skill that runs the Agentic Development Lifecycle (ADLC). It reads the state of a repository, picks an entry (new product, feature, takeover of legacy code, fix, refactor, release, and so on), and then invokes the right skills from [superpowers](https://github.com/obra/superpowers), [mattpocock-skills](https://github.com/mattpocock/skills) and [frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design) in a fixed order. It copies nothing from those skills; it routes to them.

Three parties take part: the repo owner, the orchestrator session where `/fabreak` was typed, and a fresh subagent per task. Roles are skills, not named agents.

![The ADLC as fabreak runs it](docs/adlc.svg)

## Install

Prerequisites, installed as plugins at user scope:

| Plugin | Repo |
|---|---|
| superpowers | https://github.com/obra/superpowers |
| mattpocock-skills | https://github.com/mattpocock/skills |
| frontend-design | https://github.com/anthropics/claude-plugins-official |

Then:

```bash
claude plugin marketplace add https://github.com/yanuarif/fabreak
claude plugin install fabreak@fabreak --scope user
```

Add one line to the `CLAUDE.md` of every repo that should use it:

```
Every development request starts with /fabreak
```

## Entries

`/fabreak` alone reads the repo state and picks an entry, asking one question when two fit. `/fabreak <entry>` goes straight there.

| Entry | Enter when |
|---|---|
| `new` | an empty or nearly empty repo; a product shaped from scratch |
| `feature` | a change to a repo that has `CONTEXT.md` |
| `takeover` | first contact with code that has no domain model |
| `spike` | a feasibility question that needs throwaway code, time-boxed |
| `bootstrap` | a repo needs `CLAUDE.md`, CI, pre-commit, branch protection |
| `fix` | a bug report |
| `refactor` | structure changes, behaviour stays |
| `upgrade` | a dependency, runtime or platform version jump |
| `docs-only` | documentation changes only |
| `replan` | the spec changed while plan tasks remain |
| `release` | every plan card is Done and main CI is green |
| `closing` | handover to a client: UAT, evidence, access |

Flags: `feature --grill` runs a grilling interview before brainstorming; `fix --release` lands the fix on the release branch first, then backports it.

## What it enforces

- Plan before code, except for `fix`, `refactor`, `upgrade` and `docs-only`.
- One task = one card = one session = one worktree = one PR or MR.
- Reviewers are fresh subagents; the implementer never reviews its own work.
- Verification evidence is command output: the test runner's summary line and exit code, printed verbatim.
- Steps only a human can take (secrets, deploys, store consoles, branch protection, access) run through a wizard and park the session.
- A question stops the session, never a guess: a task session asks one question with answer buttons; an interview (grilling, brainstorming) asks its round.
- The plan in git is the durable record: tasks are ticked when their PR merges; replans, archived spikes and wrong task splits are recorded there.

## Layout

```
skills/fabreak/SKILL.md      the router: state detection, entry table, rules for every entry
skills/fabreak/entries/      one file per entry, read only when that entry is chosen
skills/fabreak/board.md      the board: sidebar sections, cards, moves, CLI fallback
skills/fabreak/loop.md       loop C: worktree, implement, verify, review, finish, merge
skills/fabreak/hosting.md    GitHub, GitLab, Bitbucket: PR or MR, CI status, merge, protection
```

## Limits

- The board (Backlog, In progress, Waiting on me, Review, Done) lives in the Claude Code desktop sidebar. In the terminal CLI, fabreak prints the board as text from the plan instead.
- The PR monitor that wakes a session on review comments, and Auto-fix, exist only for GitHub. On GitLab the session uses `glab`; on Bitbucket it uses the REST API or prints manual steps, and checks CI status itself.
- fabreak is for development work. Business development, hypothesis research and project-specific tooling are out of scope; a repo may name its own verification hook in `CLAUDE.md`, and fabreak calls it when it exists.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).

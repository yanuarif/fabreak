# fabreak

fabreak is a Claude Code plugin that runs the Agentic Development Lifecycle (ADLC): one command per entry (`/fabreak:new`, `/fabreak:fix`, `/fabreak:release`, and so on) and a router, `/fabreak`, that reads the state of a repository and picks the entry. Every entry then invokes the right skills from [superpowers](https://github.com/obra/superpowers), [mattpocock-skills](https://github.com/mattpocock/skills) and [frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design) in a fixed order. It copies nothing from those skills; it routes to them.

Three parties take part: the repo owner, the orchestrator session where a `/fabreak` command was typed, and one task session per card, which implements its task while fresh subagents review it. Roles are skills, not named agents.

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

`/fabreak` (the router, listed as `/fabreak:fabreak`) reads the repo state and picks an entry, asking one question when two fit. `/fabreak:<entry>` goes straight there; the request can follow it on the same line, as in `/fabreak:fix totals are off by one cent`.

| Entry | Enter when |
|---|---|
| `/fabreak:new` | an empty or nearly empty repo; a product shaped from scratch |
| `/fabreak:feature` | a change to a repo that has `CONTEXT.md` |
| `/fabreak:takeover` | first contact with code that has no domain model |
| `/fabreak:spike` | a feasibility question that needs throwaway code, time-boxed |
| `/fabreak:bootstrap` | a repo needs `CLAUDE.md`, CI, pre-commit, branch protection |
| `/fabreak:fix` | a bug report |
| `/fabreak:refactor` | structure changes, behaviour stays |
| `/fabreak:upgrade` | a dependency, runtime or platform version jump |
| `/fabreak:docs-only` | documentation changes only |
| `/fabreak:replan` | the spec changed while plan tasks remain |
| `/fabreak:release` | every plan card is Done and main CI is green |
| `/fabreak:closing` | handover to a client: UAT, evidence, access |

Flags: `/fabreak:feature --grill` runs a grilling interview before brainstorming; `/fabreak:fix --release` lands the fix on the release branch first, then backports it.

## What it enforces

- Plan before code, except for `fix`, `refactor`, `upgrade` and `docs-only`.
- One task = one card = one session = one worktree = one PR or MR.
- Reviewers are fresh subagents; the implementer never reviews its own work.
- Verification evidence is command output: the test runner's summary line and exit code, printed verbatim.
- Steps only a human can take (secrets, deploys, store consoles, branch protection, access) run through a wizard and park the session.
- A question stops the session, never a guess: the message spells out the question and every option, and the buttons below repeat it; an interview (grilling, brainstorming) asks its round in the same form.
- The plan in git is the durable record: tasks are ticked when their PR merges; replans, archived spikes and wrong task splits are recorded there.

## Layout

```
skills/fabreak/SKILL.md      the router: state detection, entry table, rules for every entry
skills/<entry>/SKILL.md      one skill per entry, the /fabreak:<entry> command; read by the router only when that entry is chosen
skills/fabreak/board.md      the board: sidebar sections, cards, moves, CLI fallback
skills/fabreak/loop.md       loop C: worktree, implement, verify, review, finish, merge
skills/fabreak/hosting.md    GitHub, GitLab, Bitbucket: PR or MR, CI status, merge, protection
```

## Limits

- The board (Backlog, In progress, Waiting on me, Review, Done) lives in the Claude Code desktop sidebar. Every plan task is a card from the moment the plan is committed; at most three run at once, the rest wait as held cards until a merge wakes them. The sidebar moves a session family together, so the column shows the card that moved last; per-card state is on the card's row and in the plan. In the terminal CLI, fabreak prints the board as text from the plan instead.
- The PR monitor that wakes a session on review comments, and Auto-fix, exist only for GitHub. On GitLab the session uses `glab`; on Bitbucket it uses the REST API or prints manual steps, and checks CI status itself.
- fabreak is for development work. Business development, hypothesis research and project-specific tooling are out of scope; a repo may name its own verification hook in `CLAUDE.md`, and fabreak calls it when it exists.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).

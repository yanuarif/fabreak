# Stack templates design (0.9.0)

A new product starts from nothing every time: `new` grills, brainstorms and plans on an empty repo, and what the owner learned about a stack in earlier products (its commands, its folder layout, the decisions that held, the gotchas) reaches the next product only through the owner's memory. This spec closes gap 5 of the software-factory roadmap with two kinds of stack template. Gap 6, the portfolio page, is out of scope and stays a separate card.

Decisions the owner locked on 2026-10-21 and confirmed on 2026-11-05: both kinds; template repos are the owner's own, listed per stack in a file in the owner's home folder, and fabreak ships none; `new` copies the matching template without git history and continues brainstorming from it; `release` writes a stack profile that the next `new` reads as brainstorming input, and no code is copied from it; the release is 0.9.0 with templates only.

## Files outside the repository

Both live in `~/.claude/fabreak/`, the owner's own folder, never in a product repository and never in fabreak.

### `templates.md`, written by the owner

One table, one row per template repo:

```markdown
| Stack | Repo | Fits |
|---|---|---|
| nextjs-postgres | https://git.example.com/me/nextjs-postgres-template | web app with accounts and a relational database |
| expo-supabase | git@git.example.com:me/expo-template.git | mobile app with a hosted backend |
```

`Stack` is a kebab-case key; a stack profile with the same name belongs to the same stack. `Repo` is any URL `git clone` accepts with the owner's credentials. `Fits` says in one line what kind of product the template is for; it is what the match reads. fabreak only reads this file.

### `stacks/<stack>.md`, written by `release`

```markdown
# Stack profile: nextjs-postgres

Sources:
- invoicing-app 1.2.0, 2026-11-05

## Commands
- install: `pnpm install`
- test: `pnpm test`

## Structure
- `src/app/`: routes, one folder per screen

## Decisions
- Server actions over a separate API: one deploy unit (ADR 0003)

## Gotchas
- The test database needs `TZ=UTC`, or date tests fail after midnight.
```

Four fixed sections, so `new` can read them. A profile holds stack facts only: nothing that names the product, its client or its domain, and no secret, host name, URL of a deployment or environment value. The source line names the repository folder and the version, which stays in the owner's home folder.

## `new`: a stack start after grilling

A new step 2 sits between grilling (step 1) and brainstorming (now step 3).

1. Read `~/.claude/fabreak/templates.md` and list `~/.claude/fabreak/stacks/`. Neither exists: one line, "No templates or stack profiles in ~/.claude/fabreak: starting empty", and the step is done.
2. Match: compare the stack grilling settled (or, when it settled none, the product grilling described) with each row's `Stack` and `Fits`. A row that fits is a candidate; at most three, the closest first.
3. With one or more candidates: one discrete-choice question in the app's question tool, one option per candidate (label: the stack; description: its `Fits` and its URL) plus "Start empty". With none: one line naming the stack and saying no template fits.
4. A template picked: clone it with `git clone --depth 1` into a new folder from `mktemp -d`, copy every file except `.git` into the repository root, keeping each file the repository already has, then delete the temporary folder. One commit on the default branch, `Start from the <stack> template`, whose body names the URL, the cloned commit and every path kept from the repository. A failed clone is named in one line with git's error, and the step continues as "Start empty".
5. Profile: the profile whose file name is the picked template's stack, or else the stack grilling settled. When grilling settled no stack, brainstorming's chosen approach settles it, and a matching profile is read before the next brainstorming section.
6. Brainstorming's input gains what the step found: the template's files are the starting structure the design builds on, a profile's Commands, Structure and Decisions are defaults each approach starts from, and its Gotchas are constraints. The owner can override any of them. The spec gets a `## Stack` section: the template (stack, URL, commit) or "none", and the profile (its name and the lines adopted) or "no profile".

Done when the question was answered (or no candidate was found and said so), the template commit exists when one was picked, and brainstorming has the profile when one matched.

Routing: after the template commit the repository has source files and no `CONTEXT.md` until domain-modeling, so the router's state rows would pick `takeover`. A `new` run that is resumed in a later session is resumed with `/fabreak:new`, and the router's "Entry named" row wins. The step says so.

## `release`: a stack profile after the tag

A new step 5 follows the tag (the hotfix line becomes step 6).

1. Name: the stack named in the `## Stack` section of a spec in `docs/superpowers/specs/`, when the repository started from a template; otherwise a kebab-case name of language, framework and datastore (`python-django-postgres`). An existing profile in `~/.claude/fabreak/stacks/` that names the same stack under another spelling is reused instead of a near duplicate. The name is stated in one line.
2. Sources read: `CLAUDE.md` (commands, the verification hook, every gotcha or warning line), the repository's top two folder levels from `git ls-files`, and `docs/adr/` (each decision and the alternative it beat).
3. Write: `mkdir -p ~/.claude/fabreak/stacks`, then the profile in the four sections. An existing profile is merged: its lines stay, a line this repository contradicts is replaced by this repository's, new lines are added, and `Sources:` gains a line. Before writing, each line is checked against the stack-facts rule above; a line that fails is left out.

Done when the profile exists with this release's source line, and the name and the number of lines added and replaced are in the release report.

## `bootstrap`: a template's files are kept

A repository that started from a template may already have a `CLAUDE.md`, a CI workflow or a pre-commit hook. Each bootstrap step checks for its file first and fills only what is missing; step 1 also starts from the Commands and Gotchas of the stack profile a spec's `## Stack` section names, when there is one, checked against the repo before they are written. The CI question in step 2 is asked only when no CI file exists.

## Not changed

The router: `new` and `release` keep their rows, and `skills/fabreak/SKILL.md` stays at 1,039 words. No script reads either file, so there is no code and no unit test; the plan board is unchanged.

## Testing

Markdown only: the full check list from CONTRIBUTING.md and a read of each changed step for a completion criterion. A dry run against a temporary `~/.claude/fabreak` copy is out of reach for Markdown; untested until a live run: the match and question in `new`, a private template's clone with the owner's credentials, and a profile merge on a second release.

## Versioning

`0.9.0` in `plugin.json` and `marketplace.json`.

---
name: release
description: "fabreak entry: every plan card is Done and the default branch is green."
argument-hint: "[version]"
disable-model-invocation: true
---

# release

Entry `release` of fabreak. The router, `${CLAUDE_PLUGIN_ROOT}/skills/fabreak/SKILL.md`, runs first: its state read with `release` as the argument, then its rules for every entry. `board.md`, `loop.md` and `hosting.md` are in that folder. Another entry is `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Request and flags: $ARGUMENTS

## When

Every card of the plan is Done and the default branch is green: its CI, or a local suite run when it has no CI (state check 2, board.md). Otherwise the one question: release anyway, or wait.

## Steps

1. superpowers:verification-before-completion: the whole suite and every target's build from a clean checkout of the default branch; summary lines and exit codes to `evidence/<version>/verification.txt`.
2. Version and changelog: bump the version where the stack keeps it; a `CHANGELOG.md` entry from the merged PR or MR titles since the last tag. One card, one PR or MR, merged through loop.md steps 5 and 6.
3. Store, deploy or publish steps: mattpocock-skills:wizard; the owner performs them, and the wizard records what was done in `evidence/<version>/release-notes.md`. The session waits until the wizard reports done.
4. Tag last: `git tag -a v<version>` on the merged commit, after the wizard reports done.
5. Stack profile in `~/.claude/fabreak/stacks/<stack>.md`, read by the next `new` (its step 2); no code is copied.
   - Name: the stack in the `## Stack` section of a spec in `docs/superpowers/specs/` when the repository started from a template; otherwise a kebab-case name of language, framework and datastore (`python-django-postgres`). An existing profile there that names the same stack under another spelling is reused. State the name in one line.
   - Read `CLAUDE.md` (commands, the verification hook, every gotcha or warning line), the top two folder levels from `git ls-files`, and `docs/adr/` (each decision and the alternative it beat).
   - `mkdir -p ~/.claude/fabreak/stacks`, then write four sections, `## Commands`, `## Structure`, `## Decisions`, `## Gotchas`, under `# Stack profile: <stack>` and a `Sources:` list. An existing profile is merged: its lines stay, a line this repository contradicts is replaced, new lines are added, and `Sources:` gains `<repository folder name> <version>, <date>`.
   - Stack facts only: a line that names the product, its client or its domain, or holds a secret, a host name, a deployment URL or an environment value, is left out.
   Done when the profile has this release's source line and the release report states the name and how many lines were added and replaced.
6. A hotfix after the tag: the `fix` entry with `--release`.

## Artifacts

`evidence/<version>/`, the changelog entry, the tag, and the stack profile outside the repository.

## Stop asking when

The wizard has run.

## Done when

The tag exists on the default branch, `evidence/<version>/` is committed, the owner's steps are reported done, and the stack profile carries this release's source line.

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
5. A hotfix after the tag: the `fix` entry with `--release`.

## Artifacts

`evidence/<version>/`, the changelog entry, the tag.

## Stop asking when

The wizard has run.

## Done when

The tag exists on the default branch, `evidence/<version>/` is committed, and the owner's steps are reported done.

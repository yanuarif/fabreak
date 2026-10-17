# release

## When

Every card of the plan is Done and the default branch's CI is green (state check 2, board.md). Otherwise the one question: release anyway, or wait.

## Steps

1. superpowers:verification-before-completion: the whole suite and every target's build from a clean checkout of the default branch; summary lines and exit codes to `evidence/<version>/verification.txt`.
2. Version and changelog: bump the version where the stack keeps it; a `CHANGELOG.md` entry from the merged PR or MR titles since the last tag. One card, one PR or MR, merged through loop.md steps 5 and 6.
3. Store, deploy or publish steps: mattpocock-skills:wizard; the owner performs them, and the wizard records what was done in `evidence/<version>/release-notes.md`. Card to Waiting on me.
4. Tag last: `git tag -a v<version>` on the merged commit, after the wizard reports done.
5. A hotfix after the tag: `entries/fix.md` with `--release`.

## Artifacts

`evidence/<version>/`, the changelog entry, the tag.

## Stop asking when

The wizard has run.

## Done when

The tag exists on the default branch, `evidence/<version>/` is committed, and the owner's steps are reported done.

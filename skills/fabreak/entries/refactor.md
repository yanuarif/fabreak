# refactor

## When

Structure changes, behaviour stays. The spec is "`tests/` unchanged and green", where `tests/` means the repo's test directory, whatever its name.

## Steps

1. mattpocock-skills:codebase-design: name the module, its interface, the seam, and the deepening the refactor achieves. That text is the card brief (board.md); the brief names steps 2 and 3 as the card session's work.
2. State check 2 for this module: tests at that seam pass. Without them, a characterization card first: loop.md with mattpocock-skills:tdd at the seam from step 1, locking today's behaviour, merged before the refactor starts.
3. loop.md with Spec source = "`tests/` unchanged and green". The implementer edits source files only. The Spec axis of mattpocock-skills:code-review checks that `git diff <merge-base> --stat -- <test directory>` is empty and the suite is green.
4. The PR or MR description names the module's new interface.

## Artifacts

The refactored module, the PR or MR.

## Stop asking when

The seam is agreed: one question when the module has more than one candidate seam.

## Done when

Test files are unchanged, the suite is green, and the PR or MR is merged.

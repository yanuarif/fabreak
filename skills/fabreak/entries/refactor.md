# refactor

## When

Structure changes, behaviour stays. Code before a plan is allowed; the spec is "`tests/` unchanged and green".

## Steps

1. State check 2: the module has tests that pass. Without them, a characterization card first (takeover.md step 5, scoped to this module), merged before the refactor starts.
2. mattpocock-skills:codebase-design: name the module, its interface, the seam, and the deepening the refactor achieves. That text is the card brief (board.md).
3. loop.md with Spec source = "`tests/` unchanged and green". The implementer touches nothing under the test directory. The Spec axis of mattpocock-skills:code-review checks that `git diff <merge-base> --stat -- tests/` is empty and the suite is green.
4. The PR or MR description names the module's new interface.

## Artifacts

The refactored module, the PR or MR.

## Stop asking when

The seam is agreed: one question when the module has more than one candidate seam.

## Done when

Test files are unchanged, the suite is green, and the PR or MR is merged.

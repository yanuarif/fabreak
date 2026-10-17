# fix

## When

A bug report, in a repo with or without an open plan. The bug report is the spec. `--release`: the fix lands on the release branch first, then backports to the default branch.

## Steps

1. Write the bug report as the card brief (board.md): symptom, expected behaviour, steps, environment, the error text verbatim, and the seam the regression test goes through (function and test file). One card, one worktree; `--release` cuts the worktree from the release branch. The brief names steps 2 to 5 as the card session's work; the orchestrator stops after proposing the card.
2. superpowers:systematic-debugging: reproduce with the report's steps, then root cause. When the report's steps give no tight pass/fail signal, mattpocock-skills:diagnosing-bugs builds one first.
3. mattpocock-skills:tdd at the seam the brief names (a brief without one earns the one question): red, with the runner's summary line showing the failure printed, then the smallest fix that makes it green, committed. This is loop.md step 2 for a fix.
4. loop.md from step 3 (verify) through step 6, with Spec source = the bug report.
5. `--release` only: after the merge, cherry-pick onto the default branch in a second card.

## Artifacts

The regression test, the fix, the PR or MR naming the root cause.

## Stop asking when

The bug reproduces. Two cases earn the one question: the report's steps do not reproduce it (what differs in the owner's environment), or the code's arithmetic and the report's expected value disagree (where the expected value comes from).

## Done when

The regression test is green, the suite is green, and the PR or MR is merged. With `--release`, both branches carry the fix.

# fix

## When

A bug report, in a repo with or without an open plan. Code before a plan is allowed here: the bug report is the spec. `--release`: the fix lands on the release branch first, then backports to the default branch.

## Steps

1. Write the bug report as the card brief (board.md): symptom, expected behaviour, steps, environment, the error text verbatim. One card, one worktree; `--release` cuts the worktree from the release branch.
2. superpowers:systematic-debugging: reproduce, then root cause. When no tight pass/fail signal exists, mattpocock-skills:diagnosing-bugs builds one first (a test, a curl script, a CLI diff).
3. mattpocock-skills:tdd: a failing test at the seam that reaches the bug, red before any fix. The runner's summary line showing that failure is printed.
4. loop.md from step 2 (implement the fix) through step 6, with Spec source = the bug report.
5. `--release` only: after the merge, cherry-pick onto the default branch in a second card.

## Artifacts

The regression test, the fix, the PR or MR naming the root cause.

## Stop asking when

The bug reproduces. When the report's steps do not reproduce it, that is the one question: what differs in the owner's environment.

## Done when

The regression test is green, the suite is green, and the PR or MR is merged. With `--release`, both branches carry the fix.

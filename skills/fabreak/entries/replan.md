# replan

## When

The spec changed while plan tasks remain: a decision reversed, a scope cut, a spike's ADR that reshapes tasks.

## Steps

1. superpowers:brainstorming on the change only. The existing spec is updated in place, with a dated "Changes" section at the end naming what changed and why. fabreak's step 2 follows.
2. superpowers:writing-plans: the remaining unchecked tasks are rewritten in the existing plan; ticked tasks stay. A "Replan <date>" section lists each withdrawn task and its replacement.
3. Board: unstarted proposals for withdrawn tasks are dismissed (`dismiss_task`); a started session for a withdrawn task is stopped with a one-line note and archived (`archive_session`). New cards are proposed (board.md).
4. Commit the spec and the plan on the default branch.

## Artifacts

The updated spec and plan, each with its change section.

## Stop asking when

The owner has approved the updated spec sections.

## Done when

Spec and plan are committed with their change sections, stale cards are gone, and the new cards are proposed.

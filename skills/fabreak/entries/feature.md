# feature

## When

A change to a repo that has `CONTEXT.md` and no open plan for this change. Without `CONTEXT.md`, ask whether `takeover` was meant.

## Steps

1. `--grill` only: mattpocock-skills:grilling on the feature.
2. superpowers:brainstorming, narrowed to this feature. It reads `CONTEXT.md` and `docs/adr/` first so the design uses the project's terms, and writes `docs/superpowers/specs/<date>-<feature>-design.md`.
3. mattpocock-skills:domain-modeling: new terms into `CONTEXT.md`, decisions into `docs/adr/`. A spec that introduces no term and no decision skips this step.
4. superpowers:writing-plans: `docs/superpowers/plans/<date>-<feature>.md`.
5. board.md: one card per unblocked task.

## Artifacts

The spec, the plan, and any new entries in `CONTEXT.md` and `docs/adr/`.

## Stop asking when

The spec's last section is approved.

## Done when

The plan is committed on the default branch and the first cards are proposed. Code waits for a card.

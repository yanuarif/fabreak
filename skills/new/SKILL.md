---
name: new
description: "fabreak entry: an empty or nearly empty repo; a product shaped from scratch."
argument-hint: "[product idea]"
disable-model-invocation: true
---

# new

Entry `new` of fabreak. The router, `${CLAUDE_PLUGIN_ROOT}/skills/fabreak/SKILL.md`, runs first: its state read with `new` as the argument, then its rules for every entry. `board.md`, `loop.md` and `hosting.md` are in that folder. Another entry is `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Request and flags: $ARGUMENTS

## When

An empty or nearly empty repo; a product shaped from scratch. State: no `CONTEXT.md`, no source files.

## Steps

1. mattpocock-skills:grilling on the product idea, in rounds until the frontier is empty. The answers are the agreement the spec builds on.
2. superpowers:brainstorming, narrowed to what grilling settled: the design is approved section by section and written to `docs/superpowers/specs/<date>-<topic>-design.md`, committed by brainstorming itself; fabreak's step 3 follows. An open question with a factual answer goes to mattpocock-skills:research (findings to `docs/research/`); a question only code answers goes to the `spike` entry.
3. mattpocock-skills:domain-modeling on the spec: every term the spec uses lands in `CONTEXT.md`; every decision that had alternatives lands in `docs/adr/`.
4. superpowers:writing-plans from the spec: `docs/superpowers/plans/<date>-<topic>.md`, small tasks, each naming the tasks it depends on and the seams it tests at.
5. The `bootstrap` entry, for the first repo only.
6. board.md: the card round, then one card per task.

## Artifacts

The spec, `CONTEXT.md`, `docs/adr/`, the plan, and bootstrap's files.

## Stop asking when

Grilling's frontier is empty and brainstorming's last section is approved.

## Done when

The plan is committed on the default branch, bootstrap is done, and every task has a card. Code is written only by a card in run state.

---
name: spike
description: "fabreak entry: a feasibility question that needs throwaway code, time-boxed."
argument-hint: "[question]"
disable-model-invocation: true
---

# spike

Entry `spike` of fabreak. The router, `${CLAUDE_PLUGIN_ROOT}/skills/fabreak/SKILL.md`, runs first: its state read with `spike` as the argument, then its rules for every entry. `board.md`, `loop.md` and `hosting.md` are in that folder. Another entry is `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Request and flags: $ARGUMENTS

## When

A feasibility or design question that only throwaway code answers, inside a time box. Called from brainstorming (`new`, `feature`) or on its own.

## Steps

1. Write the question and the time box (hours, at most one day) as the first line of one card brief. The branch is `spike/<question-slug>`.
2. mattpocock-skills:research when a primary source may answer it without code; findings to `docs/research/`. A settled answer skips to step 4.
3. mattpocock-skills:prototype: the logic branch for a state model, the UI branch for a screen. For UI, frontend-design:frontend-design sets the visual direction once the variations exist. Throwaway and marked as such.
4. mattpocock-skills:domain-modeling: the answer becomes an ADR in `docs/adr/` with the decision, the alternatives tried, and the spike's evidence.
5. Archive the branch: `git tag archive/spike-<slug> <branch>`, then delete the branch. In the plan, put the ADR path next to the tasks it affects and add "spike archived: `archive/spike-<slug>`".

## Artifacts

`docs/adr/NNNN-<decision>.md`, `docs/research/` when used, the archive tag, the plan note.

## Stop asking when

The question and the time box are written. Inside the box the spike runs on its own; at the box's end it reports what it has.

## Done when

The ADR is committed, the branch is archived, and the plan names the ADR.

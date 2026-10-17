---
name: docs-only
description: "fabreak entry: documentation changes only."
argument-hint: "[request]"
disable-model-invocation: true
---

# docs-only

Entry `docs-only` of fabreak. The router, `${CLAUDE_PLUGIN_ROOT}/skills/fabreak/SKILL.md`, runs first: its state read with `docs-only` as the argument, then its rules for every entry. `board.md`, `loop.md` and `hosting.md` are in that folder. Another entry is `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Request and flags: $ARGUMENTS

## When

Documentation changes only: README, guides, ADR text, a rendered docs site. Source and test files stay untouched.

## Steps

1. Card brief: which pages change and why (board.md).
2. A rendered docs site whose layout or design changes: frontend-design:frontend-design for the visual direction.
3. loop.md, light: step 3's verification is the docs lint, the site build, or a preview, summary line printed; step 4 runs the Standards axis of mattpocock-skills:code-review only; steps 5 and 6 as usual.

## Artifacts

The changed pages, the PR or MR.

## Stop asking when

The page list is written.

## Done when

The lint or build is green, the Standards review has no load-bearing finding, and the PR or MR is merged.

# takeover

## When

First contact with code that has no domain model: no `CONTEXT.md`, source files present. The repo stays on the owner's hosting; hosting.md detects it.

## Steps

1. mattpocock-skills:research with the question "What does this codebase do, and how is it built, tested and run?" The primary source is the code itself: entry points, modules, build and test commands, external services. Findings to `docs/research/<date>-codebase-map.md`; this path wins over the research skill's own default.
2. mattpocock-skills:domain-modeling on the map: the glossary into `CONTEXT.md`; decisions already visible in the code become retroactive ADRs in `docs/adr/`, marked retroactive.
3. mattpocock-skills:codebase-design: name the deep modules, the seams, and where tests belong. Output: a "Seams" section in `CONTEXT.md`.
4. `entries/bootstrap.md`: step 1 writes `CLAUDE.md`, then CI, pre-commit and the owner's wizard.
5. Characterization tests. Ask the one question of this entry: "One card per module; the modules are <list from step 3>. Confirm?" Then one card per module (board.md), each running loop.md with mattpocock-skills:tdd at the seams from step 3, locking today's behaviour. Spec source for review: "behaviour unchanged: the tests describe what the code does today". Wait until the suite is green on the default branch (state check 2; a local run counts when there is no remote).
6. The change itself: mattpocock-skills:grilling ("change what, keep what"), superpowers:brainstorming, superpowers:writing-plans; one plan per change. Cards.

## Artifacts

`docs/research/`, `CONTEXT.md`, `docs/adr/`, `CLAUDE.md`, the characterization suite, the first change plan.

## Stop asking when

The owner has confirmed the module list for characterization (one question), and later grilling's frontier is empty.

## Done when

`CONTEXT.md`, `CLAUDE.md`, `docs/research/` and `docs/adr/` exist, the characterization suite is green on the default branch, and the first change plan is committed.

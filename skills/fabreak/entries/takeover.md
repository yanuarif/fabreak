# takeover

## When

First contact with code that has no domain model: no `CONTEXT.md`, source files present. The repo stays on the owner's hosting; hosting.md detects it and nothing is moved.

## Steps

1. mattpocock-skills:research with the question "What does this codebase do, and how is it built, tested and run?" The primary source is the code itself: entry points, modules, build and test commands, external services. Findings to `docs/research/<date>-codebase-map.md`.
2. mattpocock-skills:domain-modeling on the map: the glossary into `CONTEXT.md`; decisions already visible in the code become retroactive ADRs in `docs/adr/`, marked retroactive.
3. mattpocock-skills:codebase-design: name the deep modules, the seams, and where tests belong. Output: a "Seams" section in `CONTEXT.md`.
4. mattpocock-skills:writing-for-agents: `CLAUDE.md` with build, test and run commands, the host's PR or MR rules, and the line `Every development request starts with /fabreak`. Then `entries/bootstrap.md` for pre-commit and CI.
5. Characterization tests: one card per module (board.md), each running loop.md with mattpocock-skills:tdd at the seams from step 3, locking today's behaviour. Spec source for review: "behaviour unchanged: the tests describe what the code does today". Wait until the suite is green on the default branch (state check 2).
6. The change itself: mattpocock-skills:grilling ("change what, keep what"), superpowers:brainstorming, superpowers:writing-plans; one plan per change. Cards.

## Artifacts

`docs/research/`, `CONTEXT.md`, `docs/adr/`, `CLAUDE.md`, the characterization suite, the first change plan.

## Stop asking when

The owner has confirmed the module list for characterization (one question), and later grilling's frontier is empty.

## Done when

`CONTEXT.md`, `CLAUDE.md`, `docs/research/` and `docs/adr/` exist, the characterization suite is green on the default branch, and the first change plan is committed.

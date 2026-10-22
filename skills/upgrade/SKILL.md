---
name: upgrade
description: "fabreak entry: a dependency, runtime or platform version jump."
argument-hint: "[what to upgrade]"
disable-model-invocation: true
---

# upgrade

Entry `upgrade` of fabreak. The router, `${CLAUDE_PLUGIN_ROOT}/skills/fabreak/SKILL.md`, runs first: its state read with `upgrade` as the argument, then its rules for every entry. `board.md`, `loop.md` and `hosting.md` are in that folder. Another entry is `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Request and flags: $ARGUMENTS

## When

A dependency, runtime or platform version jump. One card per jump: a major, a minor with breaking changes, a toolchain, an SDK.

## Steps

1. Read the upgrade's changelog or migration guide (mattpocock-skills:research when it spans several sources). The card brief lists every breaking change that touches this repo and every build target.
2. loop.md, with step 3's verification = the whole suite plus a build of every target (each platform, each flavour) and the dependency audit (loop.md, Dependency audit); the summary line of each run is printed. Spec source = the list of breaking changes.
3. When a build or the suite breaks: superpowers:systematic-debugging, with a red test for every behaviour change the upgrade introduced.
4. Store or console changes (a new minimum OS, an SDK requirement, a signing change): mattpocock-skills:wizard for the owner; the session waits until it reports done.

## Artifacts

The upgrade PR or MR, the per-target verification lines in its description.

## Stop asking when

The target list and the breaking-change list are written in the brief.

## Done when

Every target builds, the suite is green on every target, the PR or MR is merged, and the owner's console steps are reported done.

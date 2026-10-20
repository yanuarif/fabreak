---
name: bootstrap
description: "fabreak entry: a repo needs CLAUDE.md, pre-commit, branch protection, and CI when wanted."
argument-hint: "[request]"
disable-model-invocation: true
---

# bootstrap

Entry `bootstrap` of fabreak. The router, `${CLAUDE_PLUGIN_ROOT}/skills/fabreak/SKILL.md`, runs first: its state read with `bootstrap` as the argument, then its rules for every entry. `board.md`, `loop.md` and `hosting.md` are in that folder. Another entry is `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Request and flags: $ARGUMENTS

## When

A repo needs `CLAUDE.md`, pre-commit and branch protection, and CI when the owner wants it: the first repo of a new product, a takeover, or an existing repo that lacks them. Runs once per repo.

## Steps

1. mattpocock-skills:writing-for-agents: `CLAUDE.md` with build, test, run and lint commands, the host's PR or MR rules, any stack-specific verification hook (named so loop.md step 3 finds it), and the line `Every development request starts with /fabreak`.
2. CI, optional: one question in the app's question tool, write a CI workflow or not. With CI: one workflow that runs the suite on every PR or MR, in the host's format (hosting.md): `.github/workflows/ci.yml`, `.gitlab-ci.yml`, or `bitbucket-pipelines.yml`; done when a pushed branch shows a status. Without CI: no CI file, and `CLAUDE.md` gets the line `No CI: the local suite run (loop.md step 3) stands in for CI green`; done when that line is committed.
3. Pre-commit: a hook that runs the lint and test commands from `CLAUDE.md`. With `package.json`, husky plus lint-staged; otherwise `.githooks/pre-commit`, enabled with `git config core.hooksPath .githooks`.
4. mattpocock-skills:wizard for the owner's steps: branch protection (hosting.md, Branch protection), CI secrets when step 2 wrote CI, any store or deploy credential. The session waits until the wizard reports done.

## Artifacts

`CLAUDE.md`, the CI file when step 2 wrote one, the pre-commit config, the wizard script (ephemeral unless the owner keeps it in `scripts/`).

## Stop asking when

The CI question is answered and the wizard has every value it needs from the owner.

## Done when

CI runs on a pushed branch (or `CLAUDE.md` records that the repo has none), the hook runs on a commit, and a direct push to the default branch is rejected.

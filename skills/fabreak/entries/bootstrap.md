# bootstrap

## When

A repo needs `CLAUDE.md`, CI, pre-commit and branch protection: the first repo of a new product, a takeover, or an existing repo that lacks them. Runs once per repo.

## Steps

1. mattpocock-skills:writing-for-agents: `CLAUDE.md` with build, test, run and lint commands, the host's PR or MR rules, any stack-specific verification hook (named so loop.md step 3 finds it), and the line `Every development request starts with /fabreak`.
2. CI: one workflow that runs the suite on every PR or MR, in the host's format (hosting.md): `.github/workflows/ci.yml`, `.gitlab-ci.yml`, or `bitbucket-pipelines.yml`. Done when a pushed branch shows a status.
3. Pre-commit: a hook that runs the lint and test commands from `CLAUDE.md`. With `package.json`, husky plus lint-staged; otherwise `.githooks/pre-commit`, enabled with `git config core.hooksPath .githooks`.
4. mattpocock-skills:wizard for the owner's steps: branch protection (hosting.md, Branch protection), CI secrets, any store or deploy credential. Card to Waiting on me until the wizard reports done.

## Artifacts

`CLAUDE.md`, the CI file, the pre-commit config, the wizard script (ephemeral unless the owner keeps it in `scripts/`).

## Stop asking when

The wizard has every value it needs from the owner.

## Done when

CI runs on a pushed branch, the hook runs on a commit, and a direct push to the default branch is rejected.

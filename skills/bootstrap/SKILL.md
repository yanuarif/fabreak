---
name: bootstrap
description: "fabreak entry: a repo needs CLAUDE.md, pre-commit, branch protection, and CI when wanted."
argument-hint: "[request]"
disable-model-invocation: true
---

# bootstrap

Entry `bootstrap` of fabreak. The router, `${CLAUDE_PLUGIN_ROOT}/skills/fabreak/SKILL.md`, runs first: its state read with `bootstrap` as the argument, then its rules for every entry. `board.md`, `loop.md` and `hosting.md` are in that folder. Another entry is `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Request and flags: $ARGUMENTS

## When

A repo needs `CLAUDE.md`, pre-commit and branch protection, and CI when the owner wants it: the first repo of a new product, a takeover, or an existing repo that lacks them. Runs once per repo; a second run fills only what is missing, which also lists a repository set up before the portfolio in `repos.md`. A repo that started from a template (the `new` entry's stack start) may already have some of these files: each step checks for its file first and fills only what is missing, and the CI question in step 2 is asked only when no CI file exists.

## Steps

1. mattpocock-skills:writing-for-agents: `CLAUDE.md` with build, test, run and lint commands, the host's PR or MR rules, any stack-specific verification hook (named so loop.md step 3 finds it), and the line `Every development request starts with /fabreak`. When the `## Stack` section (`new` step 2, Record) names a stack profile, its Commands and Gotchas are the starting lines, checked against the repo before they are written.
2. CI, optional: one question in the app's question tool, write a CI workflow or not. With CI: one workflow that runs the suite on every PR or MR, in the host's format (hosting.md): `.github/workflows/ci.yml`, `.gitlab-ci.yml`, or `bitbucket-pipelines.yml`; done when a pushed branch shows a status. Without CI: no CI file, and `CLAUDE.md` gets the line `No CI: the local suite run (loop.md step 3) stands in for CI green`; done when that line is committed.
3. Pre-commit: a hook that runs the lint and test commands from `CLAUDE.md`. With `package.json`, husky plus lint-staged; otherwise `.githooks/pre-commit`, enabled with `git config core.hooksPath .githooks`.
4. mattpocock-skills:wizard for the owner's steps: branch protection (hosting.md, Branch protection), CI secrets when step 2 wrote CI, any store or deploy credential. The session waits until the wizard reports done.
5. Scheduled triage, optional: one question in the app's question tool, a weekday `triage` run (with its time) or none. In the desktop app, a yes creates a scheduled task with the app's scheduled-tasks tool: cron `<minute> <hour> * * 1-5` in local time, task id `fabreak-triage-<repository folder name>`, and a prompt that names the repository's absolute path and runs `/fabreak:triage` there. It runs while the app is open, or at its next launch. Without the app, or when the owner chose none, `CLAUDE.md` gets the line `Triage is manual: run /fabreak:triage`, and a later `bootstrap` does not ask again. Done when the scheduled task exists or `CLAUDE.md` has the manual line.
6. Portfolio: add the repository's main checkout to `~/.claude/fabreak/repos.md`, the list `/fabreak:portfolio` reads. The common git folder's parent is the main checkout, also inside a task worktree, and the line is added only once:

   ```bash
   root="$(cd "$(git rev-parse --path-format=absolute --git-common-dir)/.." && pwd)"
   mkdir -p ~/.claude/fabreak && touch ~/.claude/fabreak/repos.md
   grep -qxF -- "- $root" ~/.claude/fabreak/repos.md || printf -- '- %s\n' "$root" >> ~/.claude/fabreak/repos.md
   ```

   Done when `grep -qxF -- "- $root" ~/.claude/fabreak/repos.md` exits 0.

## Artifacts

`CLAUDE.md`, the CI file when step 2 wrote one, the pre-commit config, the wizard script (ephemeral unless the owner keeps it in `scripts/`), and the repository's line in `~/.claude/fabreak/repos.md`, outside the repository.

## Stop asking when

The CI and triage questions are answered and the wizard has every value it needs from the owner.

## Done when

CI runs on a pushed branch (or `CLAUDE.md` records that the repo has none), the hook runs on a commit, a direct push to the default branch is rejected, step 5's triage choice is in place, and `repos.md` lists the repository.

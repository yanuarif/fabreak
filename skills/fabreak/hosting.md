# Hosting

Only the PR/MR → CI → merge box depends on the git host. Everything else in fabreak is host-agnostic.

## Detect

`git remote get-url origin`, matched in this order:

| Match | Host | Tooling |
|---|---|---|
| `github.com` | GitHub | `gh` |
| `gitlab.com`, or a host for which `glab auth status --hostname <host>` succeeds | GitLab | `glab` |
| `bitbucket.org` | Bitbucket Cloud | REST API 2.0 via `curl`, with `BITBUCKET_USER` and `BITBUCKET_APP_PASSWORD` from the environment |
| anything else, or no remote | unknown | stop with one question: which host, or no hosting |

A missing or logged-out CLI (`gh auth status`, `glab auth status`) is a human step: mattpocock-skills:wizard, card to Waiting on me.

Default branch: `git symbolic-ref --short refs/remotes/origin/HEAD` with the `origin/` prefix removed, falling back to `main`.

## Commands

| Need | GitHub | GitLab | Bitbucket |
|---|---|---|---|
| Open PR or MR | `gh pr create --fill --base <default>` | `glab mr create --fill --target-branch <default>` | `POST /2.0/repositories/{ws}/{repo}/pullrequests` |
| CI status of this branch | `gh pr checks --watch` | `glab ci status --live` | `GET /2.0/repositories/{ws}/{repo}/commit/{sha}/statuses` |
| CI status of the default branch | `gh run list --branch <default> --limit 1` | `glab ci list --per-page 1` on the default branch | the statuses endpoint with the default branch's head sha |
| Merge | `gh pr merge --squash --delete-branch` | `glab mr merge --squash --remove-source-branch` | `POST /2.0/repositories/{ws}/{repo}/pullrequests/{id}/merge` |
| Review comments | `gh pr view --comments`; the app's PR monitor wakes the session | `glab mr view --comments` | `GET /2.0/repositories/{ws}/{repo}/pullrequests/{id}/comments` |

Without API credentials on Bitbucket, print the manual steps for the owner (the PR page, both branch names, the merge option) and park the card in Waiting on me.

## Branch protection

Set by the owner through mattpocock-skills:wizard; the wizard opens the settings page and names what to tick:

- **GitHub**: Settings → Branches → rule for the default branch: require a pull request, require status checks (name the CI job), block force pushes. The app's PR monitor and Auto-fix exist here only.
- **GitLab**: Settings → Repository → Protected branches (Maintainers merge, nobody pushes) and Settings → Merge requests → "Pipelines must succeed".
- **Bitbucket**: Repository settings → Branch restrictions (prevent pushes, require one approval) and "Minimum successful builds" set to 1. No app monitor: the session checks status itself with the commands above.

Done when a push straight to the default branch is rejected.

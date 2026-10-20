# Hosting

Only the PR/MR → CI → merge box depends on the git host.

## Detect

`git remote get-url origin`, matched in this order:

| Match | Host | Tooling |
|---|---|---|
| `github.com` | GitHub | `gh` |
| `gitlab.com`, or a host for which `glab auth status --hostname <host>` succeeds | GitLab | `glab` |
| `bitbucket.org` | Bitbucket Cloud | REST API 2.0 via `curl`, with `BITBUCKET_USER` and `BITBUCKET_APP_PASSWORD` from the environment |
| anything else | unknown | stop with one question: which host |
| no remote | none yet | state check 2 runs the suite locally; the first PR or MR stops with one question: which host |

A repository with a remote but no CI reports no checks and no runs (`gh pr checks` exits 1 with "no checks reported", `gh run list` prints nothing); loop.md step 3's summary lines and exit codes stand in for CI green, and the PR or MR body carries them.

A missing or logged-out CLI (`gh auth status`, `glab auth status`) is a human step: mattpocock-skills:wizard.

Default branch: `git symbolic-ref --short refs/remotes/origin/HEAD` with the `origin/` prefix removed; when that prints nothing (origin/HEAD unset, common after `gh repo create`), `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` on GitHub, `glab repo view -F json` on GitLab, falling back to `main`.

## Commands

| Need | GitHub | GitLab | Bitbucket |
|---|---|---|---|
| Open PR or MR | `gh pr create --base <default> --title <subject> --body-file <body>` | `glab mr create --target-branch <default> --title <subject> --description-file <body>` | `POST /2.0/repositories/{ws}/{repo}/pullrequests` |
| CI status of this branch | `gh pr checks --watch` | `glab ci status --live` | `GET /2.0/repositories/{ws}/{repo}/commit/{sha}/statuses` |
| CI status of the default branch | `gh run list --branch <default> --limit 1` | `glab ci list --per-page 1` on the default branch | the statuses endpoint with the default branch's head sha |
| Merge | `gh pr merge --squash --delete-branch`, then confirm `gh pr view --json state -q .state` prints `MERGED` | `glab mr merge --squash --remove-source-branch`, then confirm `glab mr view -F json` reports `merged` | `POST /2.0/repositories/{ws}/{repo}/pullrequests/{id}/merge`, then confirm `GET .../pullrequests/{id}` has state `MERGED` |
| Review comments | `gh pr view --comments`; the app's PR monitor wakes the session | `glab mr view --comments` | `GET /2.0/repositories/{ws}/{repo}/pullrequests/{id}/comments` |

The PR or MR body (`<body>`) carries, in order: the root cause (fix) or the task heading, the step 3 summary lines and exit codes, the step 4 result with cosmetic findings, and any footer the host session requires. The merge runs asynchronously on the host, so the merge command can exit non-zero ("merge already in progress") after a merge that succeeded; the confirm line is the evidence.

Without API credentials on Bitbucket, print the manual steps for the owner (the PR page, both branch names, the merge option) and stop the card until the owner reports it merged.

## Branch protection

Set by the owner through mattpocock-skills:wizard; the wizard opens the settings page and names what to tick. The status-check settings apply only when the repository has CI; without CI the rule requires the PR or MR and blocks direct pushes:

- **GitHub**: Settings → Branches → rule for the default branch: require a pull request, require status checks (name the CI job), block force pushes. The app's PR monitor and Auto-fix exist here only. A private repository on GitHub Free has no branch protection (the API answers 403): record that in `CLAUDE.md` and rely on the PR flow.
- **GitLab**: Settings → Repository → Protected branches (Maintainers merge, nobody pushes) and Settings → Merge requests → "Pipelines must succeed".
- **Bitbucket**: Repository settings → Branch restrictions (prevent pushes, require one approval) and "Minimum successful builds" set to 1. No app monitor: the session checks status itself with the commands above.

Done when a push straight to the default branch is rejected.

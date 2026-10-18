#!/usr/bin/env bash
# Router lookup 4: is this checkout a task worktree? Run from the repository root.
# Usage: task-worktree.sh [default-branch]   (default: origin/HEAD's branch, else main)
# Exit 0 = task worktree, exit 1 = not, exit 2 = the default branch was not found.
# The app gives every session a worktree, so a linked worktree alone is not a task:
# it also needs a commit past the default branch or an uncommitted change.
set -u
git_dir=$(cd "$(git rev-parse --git-dir)" && pwd -P) || exit 1
common_dir=$(cd "$(git rev-parse --git-common-dir)" && pwd -P) || exit 1
[ "$git_dir" != "$common_dir" ] || exit 1
[ -z "$(git rev-parse --show-superproject-working-tree)" ] || exit 1

default=${1:-}
if [ -z "$default" ]; then
  default=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
  default=${default#origin/}
  default=${default:-main}
fi
# A commit counts as past the default branch when neither the local branch nor
# its origin copy contains it; either one may be the fresher of the two.
bases=()
for ref in "refs/heads/$default" "refs/remotes/origin/$default"; do
  git rev-parse --verify --quiet "$ref" >/dev/null && bases+=("$ref")
done
if [ ${#bases[@]} -eq 0 ]; then
  echo "task-worktree.sh: default branch '$default' not found; pass it as the argument" >&2
  exit 2
fi
[ -n "$(git rev-list -n 1 HEAD --not "${bases[@]}")" ] && exit 0
[ -n "$(git status --porcelain)" ] && exit 0
exit 1

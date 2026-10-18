#!/usr/bin/env bash
# Self-test for scripts/task-worktree.sh (router lookup 4). Run from anywhere.
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
check="$root/scripts/task-worktree.sh"
tmp=$(mktemp -d)
fail=0
assert_exit() { # expected actual label
  if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (expected exit $1, got $2)"; fail=1; fi
}
# Temp repos ignore the user's git config and carry their own identity.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.com
export GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.com
run() { (cd "$1" && "$check" >/dev/null 2>&1); }

git init -q -b main "$tmp/repo"
git -C "$tmp/repo" commit -q --allow-empty -m init
git -C "$tmp/repo" worktree add -q -b clean "$tmp/wt-clean" main
git -C "$tmp/repo" worktree add -q -b ahead "$tmp/wt-ahead" main
git -C "$tmp/wt-ahead" commit -q --allow-empty -m work
git -C "$tmp/repo" worktree add -q -b dirty "$tmp/wt-dirty" main
printf 'draft\n' > "$tmp/wt-dirty/new.txt"

git init -q -b main "$tmp/sub"
git -C "$tmp/sub" commit -q --allow-empty -m init
git init -q -b main "$tmp/super"
git -C "$tmp/super" -c protocol.file.allow=always submodule add -q "$tmp/sub" sub
git -C "$tmp/super" commit -q -m 'add submodule'

run "$tmp/repo";      assert_exit 1 $? "main checkout is not a task worktree"
run "$tmp/wt-clean";  assert_exit 1 $? "worktree at the default-branch tip, clean, is not a task worktree"
run "$tmp/wt-ahead";  assert_exit 0 $? "worktree with a commit past the default branch is a task worktree"
run "$tmp/wt-dirty";  assert_exit 0 $? "worktree with an uncommitted change is a task worktree"
run "$tmp/super/sub"; assert_exit 1 $? "submodule is not a task worktree"
rm -rf "$tmp"
[ $fail -eq 0 ] && echo "all checks passed"
exit $fail

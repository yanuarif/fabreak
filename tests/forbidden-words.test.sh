#!/usr/bin/env bash
# Self-test for scripts/check-forbidden-words.sh. Run from anywhere.
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
check="$root/scripts/check-forbidden-words.sh"
tmp=$(mktemp -d)
fail=0
assert_exit() { # expected actual label
  if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (expected exit $1, got $2)"; fail=1; fi
}
# The real list is hashed; the test uses its own list with one made-up word.
export FORBIDDEN_HASHES="$tmp/hashes"
printf 'zorblat' | shasum -a 256 | cut -c1-64 > "$FORBIDDEN_HASHES"
printf 'the zorblat is here\n' > "$tmp/hit.md"
printf 'the Zorblat-app is here\n' > "$tmp/hit-hyphen.md"
printf 'zorblatter is fine\n' > "$tmp/clean.md"
printf 'see /%s/someone/x\n' Users > "$tmp/path.md"
printf 'see %s.ai/artifact/abc\n' claude > "$tmp/link.md"
printf 'install: github.com/zorblat/fabreak\n' > "$tmp/url.md"
printf 'install: github.com/zorblat/fabreak and zorblat again\n' > "$tmp/url-twice.md"
"$check" "$tmp/hit.md" >/dev/null 2>&1;        assert_exit 1 $? "whole word hit"
"$check" "$tmp/hit-hyphen.md" >/dev/null 2>&1; assert_exit 1 $? "hyphenated, case-insensitive hit"
"$check" "$tmp/clean.md" >/dev/null 2>&1;      assert_exit 0 $? "substring of a longer word is clean"
"$check" "$tmp/path.md" >/dev/null 2>&1;       assert_exit 1 $? "home path hit"
"$check" "$tmp/link.md" >/dev/null 2>&1;       assert_exit 1 $? "private link hit"
"$check" "$tmp/url.md" >/dev/null 2>&1;        assert_exit 0 $? "install URL is allowed"
"$check" "$tmp/url-twice.md" >/dev/null 2>&1;  assert_exit 1 $? "word outside the install URL still hits"
"$check" "$tmp/clean.md" "$tmp/hit.md" >/dev/null 2>&1; assert_exit 1 $? "several files, one hit"
rm -rf "$tmp"
[ $fail -eq 0 ] && echo "all checks passed"
exit $fail

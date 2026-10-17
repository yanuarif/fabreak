#!/usr/bin/env bash
# Add words to the forbidden list without ever writing the words into the repo.
# Usage: scripts/forbidden-words-add.sh WORD...
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
list="$root/scripts/forbidden-words.sha256"
touch "$list"
for w in "$@"; do
  printf '%s' "$w" | tr 'A-Z' 'a-z' | shasum -a 256 | cut -c1-64 >> "$list"
done
sort -u -o "$list" "$list"
echo "$(wc -l < "$list" | tr -d ' ') hashes in $list"

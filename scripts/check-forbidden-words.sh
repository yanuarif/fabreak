#!/usr/bin/env bash
# Reject private names, home paths and private links before they reach the public repo.
#
# Usage: scripts/check-forbidden-words.sh [--staged | --all | FILE...]
#   --staged   files staged for commit (the pre-commit hook)
#   --all      every tracked file (CI)
#   FILE...    the given files
#
# The word list is stored as SHA-256 hashes in scripts/forbidden-words.sha256, so the
# words themselves never appear in the repo. Add one with scripts/forbidden-words-add.sh.
# Matching is whole-word and case-insensitive; tokens are taken both with and without
# hyphens, so a hyphenated name matches as a whole and by its parts. Two plain substrings
# are always rejected: a macOS home path prefix and a private artifact link. The install URL
# github.com/<owner>/fabreak is stripped before scanning, so an owner handle may appear
# there and nowhere else.
#
# Exit 0 when clean, 1 with "path:line: reason" on stderr for each hit, 2 on bad usage.
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
hashes="${FORBIDDEN_HASHES:-$root/scripts/forbidden-words.sha256}"

files=()
case "${1:-}" in
  --staged) while IFS= read -r f; do files+=("$root/$f"); done < <(git -C "$root" diff --cached --name-only --diff-filter=ACMR) ;;
  --all)    while IFS= read -r f; do files+=("$root/$f"); done < <(git -C "$root" ls-files) ;;
  "")       echo "usage: $0 [--staged | --all | FILE...]" >&2; exit 2 ;;
  *)        files=("$@") ;;
esac
[ ${#files[@]} -eq 0 ] && exit 0

exec perl -e '
  use strict; use warnings; use Digest::SHA qw(sha256_hex);
  my ($hashfile, @files) = @ARGV;
  open my $h, "<", $hashfile or die "cannot read $hashfile\n";
  my %bad = map { chomp; ($_ => 1) } grep { /\S/ } <$h>;
  close $h;
  my $plain = join "|", "/" . "Users/", "claude" . "\\.ai/" . "artifact";
  my $status = 0;
  for my $f (@files) {
    next unless -f $f;
    next if $f =~ /\.(png|jpe?g|gif|webp|woff2?|ttf|ico|pdf|zip)$/i;
    next if $f eq $hashfile;
    open my $in, "<", $f or next;
    my $n = 0;
    while (my $line = <$in>) {
      $n++;
      (my $s = $line) =~ s{github\.com/[A-Za-z0-9_-]+/fabreak}{}g;
      if ($s =~ m{$plain}) {
        print STDERR "$f:$n: forbidden path or link\n"; $status = 1; next;
      }
      my $l = lc $s;
      my %seen;
      for my $t ($l =~ /[a-z0-9]+(?:-[a-z0-9]+)*/g, $l =~ /[a-z0-9]+/g) {
        next if $seen{$t}++;
        if ($bad{sha256_hex($t)}) { print STDERR "$f:$n: forbidden word\n"; $status = 1; last; }
      }
    }
    close $in;
  }
  exit $status;
' "$hashes" "${files[@]}"

# fabreak Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the fabreak Claude Code plugin — a router skill that runs the ADLC by invoking installed superpowers, mattpocock-skills and frontend-design skills — ready for an open-source release.

**Architecture:** One model-invoked skill whose `SKILL.md` is a short router (state detection, argument table, rules for every entry). Twelve entry files load only when their entry is chosen; three mechanism files (`board.md`, `loop.md`, `hosting.md`) hold the sidebar board, loop C and hosting rules. A hashed forbidden-word list guards the public repo at pre-commit and in CI.

**Tech Stack:** Markdown skills (Claude Code plugin format), bash + `shasum` for the word check, GitHub Actions for CI, `claude plugin validate` for manifest checks.

Spec: `docs/superpowers/specs/2026-10-17-fabreak-design.md` — read it first; every file below is derived from it.

## Global Constraints

- Every file in the repo is in English. Chat with the owner is in Indonesian.
- No project, client, organization or person names, no home paths, no private links anywhere in the repo. The forbidden words live only as SHA-256 hashes in `scripts/forbidden-words.sha256`.
- The owner's GitHub handle may appear only inside the exact install URL `github.com/<owner>/fabreak`.
- Examples in guidance use fictional generic projects: "a todo API", "a legacy invoicing app".
- `skills/fabreak/SKILL.md` stays under 1,500 tokens. Entry files are read only when their entry is chosen.
- Skills are invoked, never copied: entry files name `plugin:skill` and the arguments fabreak passes, nothing of the skill's body.
- Writing follows mattpocock-skills:writing-for-agents and superpowers:writing-skills: positive phrasing, leading words, every step ends on a completion criterion, no restating what the environment already says.
- MIT license, copyright holder "Yanuar Arifin".
- Commits land on `main` of this repo with plain messages. Nothing is pushed. No other repo is modified.
- Notes from any test on a private repo go to `../fabreak-notes/`, never committed.

---

## File map

| Path | Responsibility |
|---|---|
| `.claude-plugin/plugin.json` | Plugin manifest: name, version, description, author, license, repository, skills. |
| `.claude-plugin/marketplace.json` | Makes the repo installable as a marketplace named `fabreak`. |
| `scripts/check-forbidden-words.sh` | Scans given files (or staged files, or all tracked files) for hashed forbidden words and plain path patterns. Exit 1 on a hit. |
| `scripts/forbidden-words.sha256` | One hash per line: `sha256(lowercased word)`. |
| `scripts/forbidden-words-add.sh` | Appends the hash of a word so maintainers never type the word into the repo. |
| `.githooks/pre-commit` | Runs the check on staged files. |
| `.github/workflows/check.yml` | `claude plugin validate --strict` + word check on all tracked files. |
| `skills/fabreak/SKILL.md` | Router. |
| `skills/fabreak/board.md` | Board mechanics and CLI fallback. |
| `skills/fabreak/loop.md` | Loop C and its rules. |
| `skills/fabreak/hosting.md` | Hosting detection, PR/MR, CI, merge, branch protection. |
| `skills/fabreak/entries/*.md` | One per entry: new, feature, takeover, spike, bootstrap, fix, refactor, upgrade, docs-only, replan, release, closing. |
| `tests/fixtures/*` | Synthetic repos for dry runs, plus a README on how to run one. |
| `docs/adlc.svg` | Generic ADLC chart for the README. |
| `docs/dry-runs.md` | Dry-run log. |
| `README.md`, `LICENSE`, `CONTRIBUTING.md` | Public face. |

---

### Task 1: Forbidden-word guard (script, hashed list, hook, CI)

**Files:**
- Create: `scripts/check-forbidden-words.sh`
- Create: `scripts/forbidden-words-add.sh`
- Create: `scripts/forbidden-words.sha256`
- Create: `.githooks/pre-commit`
- Create: `.github/workflows/check.yml`
- Create: `tests/forbidden-words.test.sh`

**Interfaces:**
- Produces: `scripts/check-forbidden-words.sh [--staged | --all | FILE...]`, exit 0 clean, exit 1 with `path:line: forbidden word` lines on stderr. `scripts/forbidden-words-add.sh WORD` appends to the hash file.

- [ ] **Step 1: Write the failing test**

```bash
#!/usr/bin/env bash
# tests/forbidden-words.test.sh — run from the repo root
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
check="$root/scripts/check-forbidden-words.sh"
fail=0
assert_exit() { # expected actual label
  if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (expected $1, got $2)"; fail=1; fi
}
# a word that is in the hashed list, exercised through a hash we add to a temp list
export FORBIDDEN_HASHES="$tmp/hashes"
printf '%s\n' "$(printf 'zorblat' | shasum -a 256 | cut -c1-64)" > "$FORBIDDEN_HASHES"
printf 'the zorblat is here\n' > "$tmp/hit.md"
printf 'the Zorblat-app is here\n' > "$tmp/hit-hyphen.md"
printf 'zorblatter is fine\n' > "$tmp/clean.md"
printf 'see /%s/someone/x\n' Users > "$tmp/path.md"
printf 'see %s.ai/artifact/abc\n' claude > "$tmp/link.md"
printf 'install: github.com/zorblat/fabreak\n' > "$tmp/url.md"
"$check" "$tmp/hit.md" >/dev/null 2>&1;        assert_exit 1 $? "whole word hit"
"$check" "$tmp/hit-hyphen.md" >/dev/null 2>&1; assert_exit 1 $? "hyphenated, case-insensitive hit"
"$check" "$tmp/clean.md" >/dev/null 2>&1;      assert_exit 0 $? "substring of a longer word is clean"
"$check" "$tmp/path.md" >/dev/null 2>&1;       assert_exit 1 $? "home path hit"
"$check" "$tmp/link.md" >/dev/null 2>&1;       assert_exit 1 $? "private link hit"
"$check" "$tmp/url.md" >/dev/null 2>&1;        assert_exit 0 $? "install URL is allowed"
rm -rf "$tmp"
exit $fail
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash tests/forbidden-words.test.sh`
Expected: every line `FAIL` (script missing, exit 127).

- [ ] **Step 3: Write the checker**

```bash
#!/usr/bin/env bash
# scripts/check-forbidden-words.sh — reject private names, home paths and private links.
# Usage: check-forbidden-words.sh [--staged | --all | FILE...]
# The word list is stored as SHA-256 hashes (scripts/forbidden-words.sha256) so the
# words themselves never appear in the repo. Matching is whole-word, case-insensitive;
# tokens are taken with and without hyphens. Two plain substrings are always rejected:
# a macOS home path prefix and a private artifact link. The exact install URL github.com/<owner>/fabreak
# is stripped before scanning.
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
hashes="${FORBIDDEN_HASHES:-$root/scripts/forbidden-words.sha256}"
plain_patterns="/$(printf Users)/|$(printf claude)\.ai/artifact"

files=()
case "${1:-}" in
  --staged) while IFS= read -r f; do files+=("$f"); done < <(git -C "$root" diff --cached --name-only --diff-filter=ACMR) ;;
  --all)    while IFS= read -r f; do files+=("$root/$f"); done < <(git -C "$root" ls-files) ;;
  "")       echo "usage: $0 [--staged | --all | FILE...]" >&2; exit 2 ;;
  *)        files=("$@") ;;
esac

status=0
for f in "${files[@]}"; do
  [ -f "$f" ] || continue
  case "$f" in *.png|*.jpg|*.jpeg|*.gif|*.woff|*.woff2|*.ico) continue ;; esac
  [ "$(cd "$(dirname "$f")" && pwd)/$(basename "$f")" = "$hashes" ] && continue
  n=0
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1))
    scrubbed=$(printf '%s' "$line" | sed -E 's#github\.com/[A-Za-z0-9_-]+/fabreak##g')
    if printf '%s' "$scrubbed" | grep -Eq "$plain_patterns"; then
      echo "$f:$n: forbidden path or link" >&2; status=1; continue
    fi
    tokens=$(printf '%s' "$scrubbed" | tr 'A-Z' 'a-z' | grep -oE '[a-z0-9]+(-[a-z0-9]+)*' ; printf '%s' "$scrubbed" | tr 'A-Z' 'a-z' | grep -oE '[a-z0-9]+')
    for t in $tokens; do
      h=$(printf '%s' "$t" | shasum -a 256 | cut -c1-64)
      if grep -qx "$h" "$hashes"; then
        echo "$f:$n: forbidden word" >&2; status=1; break
      fi
    done
  done < "$f"
done
exit $status
```

- [ ] **Step 4: Write the add helper and seed the hash list**

```bash
#!/usr/bin/env bash
# scripts/forbidden-words-add.sh WORD... — append hashes without ever committing the word.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
for w in "$@"; do
  printf '%s' "$w" | tr 'A-Z' 'a-z' | shasum -a 256 | cut -c1-64 >> "$root/scripts/forbidden-words.sha256"
done
sort -u -o "$root/scripts/forbidden-words.sha256" "$root/scripts/forbidden-words.sha256"
```

Seed the list by running the helper once with the owner's forbidden names (typed on the command line, never written to a file in the repo). The owner's handle goes in too: it is allowed only inside the install URL, which the checker strips.

- [ ] **Step 5: Run the test to verify it passes**

Run: `chmod +x scripts/*.sh tests/*.sh && bash tests/forbidden-words.test.sh`
Expected: six `ok` lines, exit 0.

- [ ] **Step 6: Write the pre-commit hook and CI workflow**

```bash
#!/usr/bin/env bash
# .githooks/pre-commit — enable with: git config core.hooksPath .githooks
exec "$(git rev-parse --show-toplevel)/scripts/check-forbidden-words.sh" --staged
```

```yaml
# .github/workflows/check.yml
name: check
on:
  push:
    branches: [main]
  pull_request:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Forbidden words
        run: bash scripts/check-forbidden-words.sh --all
      - name: Checker self-test
        run: bash tests/forbidden-words.test.sh
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code
      - name: Validate plugin
        run: claude plugin validate --strict .
```

- [ ] **Step 7: Enable the hook locally and commit**

```bash
git config core.hooksPath .githooks
git add scripts .githooks .github tests/forbidden-words.test.sh
git commit -m "Add forbidden-word guard, pre-commit hook and CI workflow"
```

---

### Task 2: Plugin manifests

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `skills/fabreak/SKILL.md` (placeholder frontmatter only, replaced in Task 3)

- [ ] **Step 1: Write the manifests**

```json
{
  "name": "fabreak",
  "version": "0.1.0",
  "description": "One router skill that runs the Agentic Development Lifecycle by invoking superpowers, mattpocock-skills and frontend-design.",
  "author": { "name": "Yanuar Arifin" },
  "homepage": "https://github.com/yanuarif/fabreak",
  "repository": "https://github.com/yanuarif/fabreak",
  "license": "MIT",
  "keywords": ["skills", "workflow", "adlc", "router", "superpowers", "mattpocock"],
  "skills": ["./skills/fabreak"]
}
```

```json
{
  "name": "fabreak",
  "description": "Marketplace for the fabreak plugin",
  "owner": { "name": "Yanuar Arifin" },
  "plugins": [
    {
      "name": "fabreak",
      "description": "One router skill that runs the Agentic Development Lifecycle by invoking superpowers, mattpocock-skills and frontend-design.",
      "version": "0.1.0",
      "source": "./",
      "author": { "name": "Yanuar Arifin" }
    }
  ]
}
```

- [ ] **Step 2: Validate**

Run: `claude plugin validate --strict .`
Expected: exit 0 (with the placeholder SKILL.md carrying valid `name` and `description`).

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin skills/fabreak/SKILL.md
git commit -m "Add plugin and marketplace manifests"
```

---

### Task 3: Router `SKILL.md`

**Files:**
- Create: `skills/fabreak/SKILL.md`

**Interfaces:**
- Produces: the names the entries and mechanism files are referenced by: `entries/<arg>.md`, `board.md`, `loop.md`, `hosting.md`; the five board section names; the rule list every entry inherits.

- [ ] **Step 1: Write the router**

Frontmatter: `name: fabreak`, `description` that starts with "Use when" and lists trigger branches only (a development request in a repo, a `/fabreak <entry>` call, a repo with an open plan or an active worktree), `argument-hint: "[new|feature|takeover|spike|bootstrap|fix|refactor|upgrade|docs-only|replan|release|closing] [--grill] [--release]"`.

Body sections, in order:
1. One line: what fabreak is (router; skills invoked, not copied; three parties).
2. **Read the state** — the five checks from the spec, each as a shell lookup, and the resolution table from the spec. Ends: "When two entries fit, ask one question with both as answers."
3. **Entries** — table: argument → `entries/<arg>.md` → one-line when. Twelve rows. "Read the entry file only after the entry is chosen."
4. **Rules for every entry** — the six rules from the spec, verbatim in meaning.
5. **Mechanisms** — three pointers: `board.md` (when a card moves or the board is shown), `loop.md` (when code is written), `hosting.md` (when a PR or MR, CI status or merge is needed).

- [ ] **Step 2: Measure**

Run: `wc -w skills/fabreak/SKILL.md` and `claude plugin details fabreak` after a local marketplace add is not available, so estimate tokens as words × 1.4 and also count with a tokenizer when one is installed (`python3 -c "import tiktoken"`). Expected: under 1,500 tokens.

- [ ] **Step 3: Validate and commit**

Run: `claude plugin validate --strict . && bash scripts/check-forbidden-words.sh --all`
Expected: exit 0.

```bash
git add skills/fabreak/SKILL.md
git commit -m "Write the fabreak router"
```

---

### Task 4: Mechanism files `board.md`, `loop.md`, `hosting.md`

**Files:**
- Create: `skills/fabreak/board.md`
- Create: `skills/fabreak/loop.md`
- Create: `skills/fabreak/hosting.md`

**Interfaces:**
- Consumes: section names and rules from Task 3.
- Produces: the section names `Backlog`, `In progress`, `Waiting on me`, `Review`, `Done`; the loop steps numbered 1–6 the entries refer to; the hosting table the loop's step 5 refers to.

- [ ] **Step 1: Write `board.md`** from the spec's Board section. Sections: Sections (create when missing, with the tool names `list_sections`, `create_section`), Cards (one plan task → one `start_session` proposal, brief = task text + spec path + plan path, `own_initiative`, `fresh`), Moves (which event moves a session where, `move_sessions` with `"self"`, the owner's confirmation prompt for other sessions), Done (`mark_completed`, tick the plan, commit the plan), CLI fallback (text board from plan checkboxes and `hosting.md` PR state, with the exact table shape).

- [ ] **Step 2: Write `loop.md`** from the spec's Loop C section. Sections: the six numbered steps with the skill each invokes and the argument fabreak passes (Spec source per entry), then one subsection per rule: Rebase conflict, Human review rejects, Debugging, Cross-repo, A question stops the session. Each ends on a completion criterion.

- [ ] **Step 3: Write `hosting.md`** from the spec's Hosting section. Sections: Detect (`git remote get-url origin`, the match for each host), the table (PR/MR create, CI status, merge, branch protection) with the exact commands for `gh` and `glab` and the REST endpoints for Bitbucket, Unknown host (stop with a question), Default-branch CI status (used by state detection and `release`).

- [ ] **Step 4: Check and commit**

Run: `bash scripts/check-forbidden-words.sh --all`
Expected: exit 0.

```bash
git add skills/fabreak/board.md skills/fabreak/loop.md skills/fabreak/hosting.md
git commit -m "Add board, loop and hosting mechanisms"
```

---

### Task 5: Entry files

**Files:**
- Create: `skills/fabreak/entries/new.md`, `feature.md`, `takeover.md`, `spike.md`, `bootstrap.md`, `fix.md`, `refactor.md`, `upgrade.md`, `docs-only.md`, `replan.md`, `release.md`, `closing.md`

**Interfaces:**
- Consumes: loop step numbers, board section names, hosting table from Task 4.

- [ ] **Step 1: Write each entry** with the same five headings: `## When`, `## Steps`, `## Artifacts`, `## Stop asking when`, `## Done when`. Steps name skills as `plugin:skill` with the argument fabreak passes, in the order from the spec's Entries table. Artifacts list paths: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, `docs/superpowers/plans/YYYY-MM-DD-<topic>.md`, `CONTEXT.md`, `docs/adr/NNNN-*.md`, `docs/research/*.md`, `evidence/<version>/`, `CLAUDE.md`.

- [ ] **Step 2: Check and commit**

Run: `bash scripts/check-forbidden-words.sh --all && claude plugin validate --strict .`
Expected: exit 0.

```bash
git add skills/fabreak/entries
git commit -m "Add the twelve entry files"
```

---

### Task 6: Fixtures

**Files:**
- Create: `tests/fixtures/README.md`
- Create: `tests/fixtures/new-empty/.gitkeep`
- Create: `tests/fixtures/greenfield-with-plan/{CONTEXT.md,docs/superpowers/specs/2026-10-01-todo-api-design.md,docs/superpowers/plans/2026-10-01-todo-api.md,src/todo.js,test/todo.test.js,package.json}`
- Create: `tests/fixtures/legacy-no-context/{src/invoice.js,test/invoice.test.js,package.json,README.md}`

- [ ] **Step 1: Write the fixtures.** `greenfield-with-plan`: a todo API with `CONTEXT.md` (three terms), a short spec, a plan with three tasks, two of them unchecked. `legacy-no-context`: a legacy invoicing app with one module and one passing test using `node --test`, no `CONTEXT.md`. `tests/fixtures/README.md`: how a dry run copies a fixture to a scratch folder, runs `git init` and `git add -A && git commit`, and stops before the first modifying step.

- [ ] **Step 2: Verify the legacy suite is green**

Run: `cd tests/fixtures/legacy-no-context && node --test`
Expected: `# pass 1`, `# fail 0`, exit 0.

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures
git commit -m "Add synthetic fixture repos"
```

---

### Task 7: Dry runs

**Files:**
- Create: `docs/dry-runs.md`

- [ ] **Step 1: Run four dry runs.** For each of `new` on `new-empty`, `fix` on `legacy-no-context`, `feature` on `greenfield-with-plan`, `takeover` on `legacy-no-context`: copy the fixture to a scratch folder, `git init`, commit, then dispatch a fresh subagent with the fabreak skill files and the instruction to run `/fabreak <entry>` with a one-line request ("add due dates to todos", "totals are off by one cent when a line has a discount") and to stop at the first step that would modify the repo, reporting skills invoked in order and the stop point.

- [ ] **Step 2: Record** each run in `docs/dry-runs.md`: entry, fixture, request, state detected, skills invoked in order, where it stopped, any question it asked, and anything the router got wrong (fixed in the skill files before the final commit).

- [ ] **Step 3: Commit**

```bash
git add docs/dry-runs.md skills
git commit -m "Record fixture dry runs"
```

---

### Task 8: README, chart, license, contributing

**Files:**
- Create: `docs/adlc.svg`
- Create: `README.md`
- Create: `LICENSE`
- Create: `CONTRIBUTING.md`
- Create: `.gitignore`

- [ ] **Step 1: Draw `docs/adlc.svg`** — a generic redraw of the chart: router on top; lane A (grilling, brainstorming, domain-modeling, writing-plans, bootstrap, with research/prototype/spike on the side); lane B (research, domain-modeling, codebase-design, characterization tdd, grilling → brainstorming, with writing-for-agents and setup on the side); the session-per-task node; loop C band with its five nodes and four rule nodes; PR/MR → CI → merge, release, closing; Waiting on me + wizard, writing-skills + writing-for-agents; the three back edges. English labels, no links, inline styles only.

- [ ] **Step 2: Write `README.md`**: what fabreak is (three sentences), the SVG, install (`claude plugin marketplace add https://github.com/yanuarif/fabreak`, `claude plugin install fabreak@fabreak --scope user`), the CLAUDE.md line `Every development request starts with /fabreak`, prerequisites with repo links (superpowers: https://github.com/obra/superpowers, mattpocock-skills: https://github.com/mattpocock/skills, frontend-design: https://github.com/anthropics/claude-plugins-official), the entry table (argument, when), honest limits (board only in the Claude Code desktop app; PR monitor and Auto-fix only on GitHub; Bitbucket through the REST API or manual steps).

- [ ] **Step 3: Write `LICENSE`** (MIT, `Copyright (c) 2026 Yanuar Arifin`), `CONTRIBUTING.md` (enable the hook with `git config core.hooksPath .githooks`, run `bash scripts/check-forbidden-words.sh --all` and `claude plugin validate --strict .` before a PR, English only, generic examples, add a word to the guard with `scripts/forbidden-words-add.sh`), `.gitignore` (`.DS_Store`, `node_modules/`, `../fabreak-notes` is outside the repo and needs no entry).

- [ ] **Step 4: Check and commit**

Run: `bash scripts/check-forbidden-words.sh --all && claude plugin validate --strict .`
Expected: exit 0.

```bash
git add README.md LICENSE CONTRIBUTING.md .gitignore docs/adlc.svg
git commit -m "Add README, ADLC chart, license and contributing guide"
```

---

### Task 9: Final verification

- [ ] **Step 1: Fresh review.** Dispatch a fresh reviewer subagent with the spec path and the plugin files; two axes: Standards (writing-for-agents and writing-skills rules) and Spec (every spec section has its file and no file contradicts the spec). Fix findings, re-run the word check.

- [ ] **Step 2: Measure `SKILL.md`** with a real tokenizer when available; record the number in the final report.

- [ ] **Step 3: Run everything once more**

Run: `bash tests/forbidden-words.test.sh && bash scripts/check-forbidden-words.sh --all && claude plugin validate --strict . && (cd tests/fixtures/legacy-no-context && node --test)`
Expected: all exit 0; keep the output for the report.

- [ ] **Step 4: Tick this plan's tasks and commit**

```bash
git add -A
git commit -m "Tick the implementation plan"
```

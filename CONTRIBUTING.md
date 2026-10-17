# Contributing

fabreak is a set of Markdown files that route to other plugins' skills. Changes are small and reviewable.

## Before a pull request

1. Enable the pre-commit hook once per clone:

   ```bash
   git config core.hooksPath .githooks
   ```

2. Run the same checks CI runs:

   ```bash
   bash scripts/check-forbidden-words.sh --all
   bash tests/forbidden-words.test.sh
   claude plugin validate --strict .
   ```

3. Keep `skills/fabreak/SKILL.md` under 1,500 tokens. Anything an entry needs goes into that entry's file, not the router.

## Writing rules

- English only, in every file.
- Examples use fictional generic projects: "a todo API", "a legacy invoicing app". No real project, client, organization or person names, no home paths, no private links.
- Skills are invoked, never copied. An entry names `plugin:skill` and the argument fabreak passes; the skill's body stays in its own plugin.
- Follow mattpocock-skills:writing-for-agents and superpowers:writing-skills: positive phrasing, one source of truth per rule, every step ends on a completion criterion.

## The forbidden-word guard

`scripts/forbidden-words.sha256` holds SHA-256 hashes of words that must never appear in this repo. To add one, run the helper with the word on the command line; the word itself is never written to a file:

```bash
scripts/forbidden-words-add.sh "some-private-name"
```

A commit that contains a listed word is rejected by the hook; CI rejects it again.

## Dry runs

Changes to the router or an entry are checked against the fixtures under `tests/fixtures/` (see its README) and recorded in `docs/dry-runs.md`.

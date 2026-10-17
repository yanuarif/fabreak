# Fixtures

Three small synthetic repos for dry-running fabreak entries. They are plain directories, not git repos.

| Fixture | State | Entries to dry-run |
|---|---|---|
| `new-empty` | nothing but a `.gitkeep` | `new` |
| `greenfield-with-plan` | `CONTEXT.md`, a spec, a plan with unchecked tasks, a tiny todo API | `feature` |
| `legacy-no-context` | a legacy invoicing module with one passing test, no `CONTEXT.md` | `fix`, `takeover` |

## Running a dry run

1. Copy the fixture to a scratch folder and make it a repo:

   ```bash
   cp -R tests/fixtures/<name> /tmp/fabreak-dry/<name>
   cd /tmp/fabreak-dry/<name> && git init -q -b main && git add -A && git commit -q -m "fixture"
   ```

2. Run `/fabreak:<entry>` with a one-line request from a session (or a fresh subagent given the `skills/fabreak/` files) in that folder.
3. Stop at the first step that would modify the repo. Record the detected state, the skills invoked in order, and the stop point in `docs/dry-runs.md`.

The fixtures themselves stay unchanged.

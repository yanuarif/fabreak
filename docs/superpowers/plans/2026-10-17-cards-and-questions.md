# Plan: cards started at plan time, readable questions

Spec: `docs/superpowers/specs/2026-10-17-cards-and-questions-design.md`. Documentation-only change to the plugin's skill text; no code. Version 0.3.0 (the board flow changes).

- [x] **Task 1: SKILL.md** — rewrite the rule "A question stops the session" (message spells out every option; two options → box buttons, more → the question tool); extend the wizard rule (stage list in chat, `tee` run); router table row "Open plan, no entry named" starts cards through the card round. Verify: the rules list still has one bullet per rule, no line contradicts board.md.
- [x] **Task 2: board.md** — Cards: the card round, `user_asked` start in the owner's turn, brief items 6 and 7, running cap of three; new section Held cards (recap, no move, wake message, sync); Moves: the family paragraph rewritten, cross-repo row dropped; Done: merge report, tick, wake. Verify: no "propose" left in the file.
- [x] **Task 3: loop.md** — step 1 sync for a woken card, step 6 merge report, cross-repo held rule, question rule pointer. Verify: `grep -n Backlog loop.md` shows only the pointer to board.md.
- [x] **Task 4: entries, spec, README, dry-runs, manifests** — `feature`, `new`, `takeover`, `fix`, `replan` wording; the Board and Rules sections of the design spec; README's question and board lines; a "Changes from live use" paragraph in `docs/dry-runs.md`; version 0.3.0 in both manifests. Verify: `grep -rn -i propos skills docs README.md` shows only the design-history lines.
- [x] **Task 5: verify and commit** — `bash tests/forbidden-words.test.sh && bash scripts/check-forbidden-words.sh --all && claude plugin validate --strict .`; token size of `skills/fabreak/SKILL.md`; commit.

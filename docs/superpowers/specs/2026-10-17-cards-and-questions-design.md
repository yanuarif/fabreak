# Cards started at plan time, and questions the owner can read in full

Date: 2026-10-17. Amends the board and question rules of the fabreak design (`2026-10-17-fabreak-design.md`). Source: two pieces of owner feedback after a day of live use on two repositories (a product built from scratch with an eighteen-task plan, and a takeover).

## Feedback

1. **Questions were unreadable.** A task session asked through the app's closing box: a question of at most 100 characters and buttons of one to three words. The option descriptions lived nowhere the owner read, so a question that offered several paths (a wizard's stages, a merge choice) could not be answered with confidence.
2. **Cards did not appear.** The owner expected every plan task to show on the board at once. Instead a task appeared only as a proposal card in the orchestrator's transcript, at most three per turn, and only once its dependencies were Done; and a proposal was sometimes not shown at all (a turn started by another session's message cannot start or propose sessions, and a proposal expires after a week).

## Decisions (one round with the owner)

- The board stays the Claude Code desktop sidebar sections.
- The orchestrator starts a task session for every plan task as soon as the plan is committed, instead of proposing cards. At most three cards run at once; the orchestrator wakes the next held card when a card merges.
- A question's message spells out every option; the box or question tool below it only repeats the question with buttons.
- The wizard stays a bash script; the session prints the full stage list in chat before parking, and the run command keeps every stage on screen.

## Design

### Questions (SKILL.md, rule "A question stops the session")

A question is two things in the same turn:

1. The message: the question in full, then every option as one line each, with what choosing it means and what happens next. The owner can answer from the message alone.
2. The buttons: with two options, the closing box carries the same question shortened and one button per option. With more than two options, or an option that needs more than its label to be understood, the app's question tool asks it (one label and one description per option) and the closing box is a recap only.

A box whose short question or button labels are the only place an option is spelled out is a defect, the same class as a guess.

The wizard rule gets the same treatment. Before the session parks for a wizard, its message lists every stage in order: the stage's purpose, the URL it opens, what to click there, each value it asks for (marked secret or public), and each decision with its options. The run command is printed as `bash <script> 2>&1 | tee <log>`: with stdout not a terminal the template's stage frames do not clear the screen, every stage stays readable, and the log is the evidence the wizard reports done with.

### Cards (board.md)

**Card round.** After the plan is committed (entries `new`, `feature`, `takeover` and the characterization step; `replan` for new tasks) and before any card exists, the orchestrator asks one question: the git permissions the cards get (commit; push and open the PR or MR; merge) and whether to start the cards now. The owner's yes is what lets the orchestrator start sessions (`start_session` with `initiation: "user_asked"`); that start must happen in a turn the owner's own message began. For an entry without a plan (fix, refactor, upgrade, docs-only, spike) the same round precedes its single card.

**Start.** One session per unchecked task, in plan order, all in the same turn: `user_asked`, `context: "fresh"`, `use_worktree: true`, `title` = the task's title. Brief items 1 to 5 stay (task text, paths, entry and steps, Spec source, git permissions). Two items are added:

6. The tasks this one depends on, by title, and the card's state: **run** (every dependency is ticked and fewer than three cards run) or **held** (otherwise).
7. The orchestrator's session id, from `get_session "self"`, so the card can message it.

Proposals are gone from the flow, and with them the three-per-turn limit and the "propose only when dependencies are Done" rule. The cap moves to running: at most three cards in run state at once, counted as sessions of this plan that are not Done and not held.

**Held cards.** A card whose brief says held, or that is woken but finds a dependency still unmerged, ends its first turn at once: a recap "Held until <titles> merge", no question, no board move. It does nothing in its worktree. The orchestrator wakes it with one message: "Go: <dependencies> merged. Sync the worktree with the default branch, then loop.md from step 1." A woken card runs `sync_with_base_branch` (the app's host tool; `git fetch origin` and `git merge origin/<default>` without the app) before loop.md step 1, because its worktree was cut when the cards were started.

**Merge report.** When a card's PR or MR merges (loop.md step 6), the card sends the orchestrator one message: "Merged: <task title>, <PR or MR URL>" (`SendMessage` to the id from brief item 7). The orchestrator's Done list becomes: pull and tick the task; count running cards; wake held cards whose dependencies are all ticked, in plan order, while fewer than three run. The app also continues the orchestrator when all its cards are idle; the message makes the wake-up happen as soon as the merge does.

**Sidebar limits, stated.** A card is nested under the session family's root and the family moves as one. The orchestrator moves the family to Backlog once, when it starts the cards; from then on the column shows the card that moved last, and with several cards running the columns are not per card. Per-card state is read from the card's row (running marker, PR badge), from `list_sessions {linked: true}` (`prState`, `group`) and from the plan's ticks. Every card is visible from the start as a row under the orchestrator, which is what the owner asked for. Held cards never move the family (they would drag running cards into Backlog).

### Loop (loop.md)

- Step 1 adds the sync for a card that was held, and names the message that woke it as the start of its work.
- Step 6 adds the merge report message after the host confirms the merge, before the Done moves.
- Cross-repo: a held card is held as board.md says (recap, no move), not moved to Backlog.
- "A question stops the session" refers to the SKILL.md form.

### Entries

- `feature` step 5, `new` step 6, `takeover` step 5: "board.md: the card round, then one card per task". Done when: every task has a card (not "the first cards are proposed").
- `fix` step 1: the orchestrator stops after starting the card. `replan` step 3: stale held cards are stopped and archived; new tasks get cards through the card round.
- Router table row "Open plan, no entry named": show the board, then start cards for unchecked tasks that have none (the card round).

### Out of scope

Reading the board from GitHub Issues, limits other than three, and a per-card column in the sidebar (the app nests a family and moves it together).

## Verification

`claude plugin validate --strict .`, `scripts/check-forbidden-words.sh --all`, `tests/forbidden-words.test.sh`, and a read-through of SKILL.md, board.md and loop.md for a contradiction with the lines above. The live test is the next plan the owner runs: every task shows as a row at once, three run, a merge wakes the next, and every question can be answered from its message.

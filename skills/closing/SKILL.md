---
name: closing
description: "fabreak entry: handover to a client: e2e evidence, UAT sign-off by the client, access."
argument-hint: "[request]"
disable-model-invocation: true
---

# closing

Entry `closing` of fabreak. The router, `${CLAUDE_PLUGIN_ROOT}/skills/fabreak/SKILL.md`, runs first: its state read with `closing` as the argument, then its rules for every entry. `board.md`, `loop.md` and `hosting.md` are in that folder. Another entry is `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Request and flags: $ARGUMENTS

## When

Handover of a delivered product to a client: e2e evidence, the client's UAT sign-off, a closing note, access.

Two kinds of check, never mixed: an **e2e scenario** is run by an agent or a test runner, and its output is evidence; **UAT** (user acceptance testing) is done by the client or a real user, and its result is a sign-off. An e2e run is never reported as UAT.

## Steps

1. superpowers:writing-plans: a closing plan with one task per feature: the e2e scenario (steps, expected result, the command or script that runs it), the evidence to capture, and the UAT script the client follows (steps, expected result, who signs off). One card per task (board.md). Done when every feature has both.
2. Per card, e2e: superpowers:verification-before-completion runs the e2e scenario; its output (summary lines, screenshots) goes to `evidence/closing/<feature>/e2e/`. Done when the scenario passes and its evidence is committed.
3. Per card, UAT: the card stops with the UAT script until the owner reports the client's result. The result goes to `evidence/closing/<feature>/uat.md`: who tested, when, pass or fail per step, notes, sign-off. A failed step becomes a `fix` card. Done when the client signed off.
4. Closing note: `docs/closing-note.md` with what was delivered, what was deferred, how to run and deploy, and where the e2e evidence and the UAT sign-offs live.
5. mattpocock-skills:wizard for access: transfer or revoke repo, hosting, store and cloud access; the owner performs it.

## Artifacts

The closing plan, `evidence/closing/<feature>/e2e/` and `uat.md` per feature, `docs/closing-note.md`.

## Stop asking when

The owner has approved the e2e scenarios and the UAT scripts.

## Done when

Every closing card is Done with its e2e evidence and the client's UAT sign-off, the closing note is committed, and the wizard reports access handled.

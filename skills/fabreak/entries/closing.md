# closing

## When

Handover of a delivered product to a client: UAT, evidence, a closing note, access.

## Steps

1. superpowers:writing-plans: a closing plan with one task per feature: the UAT scenario (steps, expected result), the evidence to capture, the sign-off. One card per task (board.md).
2. Per card: superpowers:verification-before-completion runs the scenario; evidence (command output, screenshots) goes to `evidence/closing/<feature>/`. A step the client performs parks the card in Waiting on me with the scenario text.
3. Closing note: `docs/closing-note.md` with what was delivered, what was deferred, how to run and deploy, and where the evidence lives.
4. mattpocock-skills:wizard for access: transfer or revoke repo, hosting, store and cloud access; the owner performs it.

## Artifacts

The closing plan, `evidence/closing/`, `docs/closing-note.md`.

## Stop asking when

The owner has approved the UAT scenarios.

## Done when

Every closing card is Done, the closing note is committed, and the wizard reports access handled.

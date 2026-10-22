# E2E and UAT design (0.8.2)

The `closing` entry called every scenario check "UAT". UAT means user acceptance testing, done by the client or a real user. Most of what a closing card runs is done by an agent or a test runner, and that is end-to-end (e2e) testing. Decision the owner locked on 2026-10-22: keep both checks and name each one for who does it. The release is 0.8.2.

## Terms

- **e2e scenario**: run by an agent or a test runner. Its output (summary lines, screenshots) is evidence.
- **UAT**: done by the client or a real user. Its result is a sign-off: who tested, when, pass or fail per step, and notes.

An e2e run is never reported as UAT.

## closing

- Step 1: the closing plan holds two things per feature. The first is the e2e scenario: steps, expected result, and the command or script that runs it. The second is the UAT script the client follows: steps, expected result, and who signs off.
- Step 2 (e2e): `verification-before-completion` runs the scenario. Its evidence goes to `evidence/closing/<feature>/e2e/`.
- Step 3 (UAT): the card stops with the UAT script until the owner reports the client's result, which is recorded in `evidence/closing/<feature>/uat.md`. A failed step becomes a `fix` card.
- Steps 4 and 5 are the closing note and the access wizard, as before. The closing note says where both kinds of record live.
- "Stop asking when" covers both the e2e scenarios and the UAT scripts. "Done when" needs both the e2e evidence and the client's sign-off for every feature.

The router row, the README row and the ADLC chart's handover node use the same terms. Earlier specs keep their wording as the record of their time.

## Versioning

`0.8.2` in `plugin.json` and `marketplace.json`.

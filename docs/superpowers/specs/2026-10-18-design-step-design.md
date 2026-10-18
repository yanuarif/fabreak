# A design step on a Claude Design canvas

Date: 2026-10-18. Amends the entries `new`, `feature` and `spike` and loop steps 2 and 4 of the fabreak design (`2026-10-17-fabreak-design.md`). Version 0.5.0.

## Problem

fabreak has no step that shows the owner a screen before code is written. `new` and `feature` go from brainstorming's chosen approach straight to a spec in words; a UI feature's layout is first seen in a PR. frontend-design:frontend-design appears in `spike` step 3 and `docs-only` step 2 as "visual direction", which is guidance for whoever writes the UI code, not a design the owner approves.

The Claude desktop app has an Artifact type, "Design": live artboards on a canvas, built from the account's design systems. The orchestrator can publish one, the owner can open, comment on and share it, and a task session can read it back.

## Decisions (one round with the owner)

- **Entries.** `new`, `feature`, and the UI branch of `spike` get the design step. `docs-only` keeps frontend-design for a docs site layout.
- **Design replaces frontend-design at the design step.** The canvas is the design the owner approves. frontend-design moves to the implementer: the task session that builds a screen invokes it while it implements against the approved artboards.
- **Timing and record.** The step runs inside brainstorming, after the owner picks an approach and before the spec is written. The owner approves the canvas in chat. The canvas link and its artboards are recorded in the spec's **Screens** section; for `spike`, in the ADR.
- **Cards implement against the design.** A plan task that builds or changes a screen names the canvas URL and its artboards, so the card brief carries them verbatim (board.md, brief item 1). The Spec reviewer checks the screens against the artboards.
- **Version.** 0.5.0: a new step in three entries is a new capability.

## Design

### `skills/fabreak/design.md` (new mechanism)

One mechanism file holds the step, so the three entries name it instead of repeating it. The router's Mechanisms list gets one line for it; the router stays under 1,500 tokens.

1. **When.** The change adds or changes a screen. With no screen, the entry names that in one line and goes on.
2. **Canvas.** The Artifact tool with `action: "quickstart"`, `intent: "design"`; publish with the `type_url` it returns, `title` = the feature or product name, no files, `auto_open: "after_first_write"`; then follow the instructions the create result carries. The `type_url` is read from the quickstart every time, never written into the plugin: types are set per account.
3. **Design system.** The one the owner names; otherwise the default the quickstart attaches; otherwise none, said in one line. In a repo that already has screens, the artboards follow its look: colours, type and components read from the code.
4. **Artboards.** One per screen the chosen approach adds or changes, plus the states the approach names (empty, loading, error) as their own artboards. Each artboard's name is the name the spec and plan use.
5. **Approval.** An interview round (router rule): the canvas link, one line per artboard, and the question "approve, or what changes". A change request updates the same artifact by its URL; comments the owner leaves on the canvas are read with `ArtifactComments`. Done when the owner approves.
6. **Record.** The spec's Screens section: the canvas URL, one line per artboard (name, what it shows), and the approval date. writing-plans then names, in every task that builds or changes a screen, the canvas URL and the artboard names.
7. **No canvas.** Without the Artifact tool or a Design type (a terminal without the app, an account without it), the Screens section describes each screen in words, its layout and its states, and says in one line that the canvas was unavailable. Approval is the same interview round.

Done when the owner approved the canvas (or the words fallback) and the Screens section holds its link and artboards.

### Entries

- `new` step 2 and `feature` step 2: after the owner picks an approach and before the spec is written, design.md when the change has screens; the spec has a Screens section. Step 4 (writing-plans): every screen task names the canvas URL and its artboards.
- `spike` step 3, UI branch: design.md sets the visual direction once the prototype's variations exist: one artboard per variation, and the owner's pick goes into the ADR with the canvas URL (step 4).
- `docs-only` is unchanged.

### Loop

- Step 2 (implement): a task that names a canvas reads it first (`Artifact`, `action: "read"`, with the URL; the result names the saved file) and invokes frontend-design:frontend-design, then builds each named artboard's screen.
- Step 4 (review): for such a task the Spec source adds the saved canvas file; the Spec axis checks each screen against its artboard.

## Out of scope

A design system created by fabreak; screenshots of the built screen compared pixel by pixel; a canvas per card.

## Untested

The step has not run on a live repository. The first `feature` with a screen tests the canvas create, the approval round, the artboard names reaching a card brief, and a card reading the canvas.

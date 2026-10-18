# Design

The design step puts the screens of the chosen approach on a Claude Design canvas, an Artifact of the type "Design", and the owner approves them before the spec is written. It runs in the orchestrator, inside brainstorming, for `new` and `feature`; and in the spike's session for `spike`'s UI branch, where the artboards are the prototype's variations and the owner's pick goes to the ADR instead of a spec. The canvas is the design; frontend-design:frontend-design belongs to the task session that builds the screens (loop.md step 2).

## Steps

1. **When** — The change adds or changes a screen. With no screen, name that in one line and return to the entry. Done when the screens are listed or the line is said.
2. **Canvas** — The Artifact tool with `action: "quickstart"`, `intent: "design"`; publish with the `type_url` it returns, `title` = the feature or product name, no files, `auto_open: "after_first_write"`; then follow the instructions the create result carries. Read the `type_url` from the quickstart every time: types are set per account. Done when the canvas URL is printed.
3. **Design system** — The one the owner named; otherwise the default the quickstart attaches; otherwise none, said in one line. In a repo that already has screens, the artboards follow its look: colours, type and components read from the code. Done when the system, or "none", is named.
4. **Artboards** — One per screen the approach adds or changes (per variation, in a spike), plus each state the approach names (empty, loading, error) as its own artboard. An artboard's name is the name the spec and plan use for that screen. Done when every listed screen and state has an artboard.
5. **Approval** — An interview round (SKILL.md question rule): the canvas URL, one line per artboard, and "approve, or what changes". A change request updates the same artifact by its URL, never a new one; comments the owner left on the canvas are read with `ArtifactComments`. Done when the owner approves.
6. **Record** — The spec gets a **Screens** section: the canvas URL, one line per artboard (name, what it shows), and the approval date. Return to the entry, which writes it; a spike writes the canvas URL and the picked artboard for its ADR instead. Done when the entry has that text.

## No canvas

Without the Artifact tool or a Design type (a terminal without the app, an account without the type), the Screens section describes each screen in words, its layout and its states, and says in one line that the canvas was unavailable. Step 5's round approves the words instead.

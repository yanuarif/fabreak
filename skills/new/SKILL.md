---
name: new
description: "fabreak entry: an empty or nearly empty repo; a product shaped from scratch."
argument-hint: "[product idea]"
disable-model-invocation: true
---

# new

Entry `new` of fabreak. The router, `${CLAUDE_PLUGIN_ROOT}/skills/fabreak/SKILL.md`, runs first: its state read with `new` as the argument, then its rules for every entry. `board.md`, `loop.md` and `hosting.md` are in that folder. Another entry is `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Request and flags: $ARGUMENTS

## When

An empty or nearly empty repo; a product shaped from scratch. State: no `CONTEXT.md`, no source files.

## Steps

1. mattpocock-skills:grilling on the product idea, in rounds until the frontier is empty. The answers are the agreement the spec builds on.
2. Stack start, from the owner's own files in `~/.claude/fabreak/`: `templates.md`, a table with the columns Stack (a kebab-case key), Repo (a URL `git clone` accepts) and Fits (the kind of product it is for), and `stacks/<stack>.md`, profiles written by `release`. Neither exists: one line, "No templates or stack profiles in ~/.claude/fabreak: starting empty", and the step is done. A resumed run whose `git log` has a `Start from the` commit goes straight to the profile.
   - Template: match the stack grilling settled, or else the product it described, against each row's Stack and Fits. Up to three rows that fit become one discrete-choice question: one option per row (label: the stack; description: its Fits and URL) plus "Start empty". No row fits: one line saying so.
   - Copy: `git clone --depth 1` into a new `mktemp -d` folder, copy every file except `.git` into the repository root, keeping each file the repository already has, then delete the folder. One commit on the default branch, `Start from the <stack> template`, its body naming the URL, the cloned commit and each path kept. A failed clone: one line with git's error, then continue as "Start empty".
   - Profile, with or without a template: the profile with the picked template's stack name, or else with the name of the stack grilling settled. When grilling settled no stack, every profile goes to step 3 as a candidate, and the approach the owner picks names the one that applies.
   - Record: the spec step 3 writes gets a `## Stack` section: the template (stack, URL, cloned commit) or "none", and the profile (its name and the lines adopted) or "no profile". `release` and `bootstrap` read the earliest spec, by its date prefix, that has this section.
   - Resume: after the copy the repository has source files and no `CONTEXT.md`, which the router reads as `takeover`, so a later session resumes this run with `/fabreak:new`.
   Done when the question is answered or no fit is said, the template commit exists when one was picked, and the profile, or the candidate profiles, are ready for step 3.
3. superpowers:brainstorming, narrowed to what grilling settled: the design is approved section by section and written to `docs/superpowers/specs/<date>-<topic>-design.md`, committed by brainstorming itself; fabreak's step 4 follows. Its input carries step 2's result: the template's files are the structure the design starts from, the profile's Commands, Structure and Decisions are the defaults every approach starts from, and its Gotchas are constraints; the owner may override any of them. The design step: once the owner picks an approach and before the spec is written, `design.md`, next to the router, runs when the product has screens; done when the owner approved the canvas and the spec has a Screens section with its URL and artboards. An open question with a factual answer goes to mattpocock-skills:research (findings to `docs/research/`); a question only code answers goes to the `spike` entry.
4. mattpocock-skills:domain-modeling on the spec: every term the spec uses lands in `CONTEXT.md`; every decision that had alternatives lands in `docs/adr/`.
5. superpowers:writing-plans from the spec: `docs/superpowers/plans/<date>-<topic>.md`, small tasks, each naming the tasks it depends on and the seams it tests at; a task that builds or changes a screen also names the canvas URL and its artboards from the Screens section.
6. The `bootstrap` entry, for the first repo only.
7. board.md: the card round, then one card per task.

## Artifacts

The template commit when one was picked, the spec (with its Stack section, and its Screens section and canvas when the product has screens), `CONTEXT.md`, `docs/adr/`, the plan, and bootstrap's files.

## Stop asking when

Grilling's frontier is empty, the stack-start question is answered, and brainstorming's last section is approved.

## Done when

The plan is committed on the default branch, bootstrap is done, and every task has a card. Code is written only by a card in run state.

# docs-only

## When

Documentation changes only: README, guides, ADR text, a rendered docs site. Source and test files stay untouched.

## Steps

1. Card brief: which pages change and why (board.md).
2. A rendered docs site whose layout or design changes: frontend-design:frontend-design for the visual direction.
3. loop.md, light: step 3's verification is the docs lint, the site build, or a preview, summary line printed; step 4 runs the Standards axis of mattpocock-skills:code-review only; steps 5 and 6 as usual.

## Artifacts

The changed pages, the PR or MR.

## Stop asking when

The page list is written.

## Done when

The lint or build is green, the Standards review has no load-bearing finding, and the PR or MR is merged.

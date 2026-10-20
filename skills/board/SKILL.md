---
name: board
description: "fabreak: open the read-only plan board in the preview pane."
disable-model-invocation: true
---

# board

Opens the plan board: a read-only kanban view of `docs/superpowers/plans`, served by `${CLAUDE_PLUGIN_ROOT}/scripts/plan-board.py` on 127.0.0.1. Cards are sessions (`${CLAUDE_PLUGIN_ROOT}/skills/fabreak/board.md`, State); this page is the live view of the plan.

## Steps

1. Root: `git rev-parse --show-toplevel`. In a task worktree that is the worktree, and the board shows the plan on its branch.
2. Port: `python3 -c 'import zlib,sys,pathlib; print(7800 + zlib.crc32(str(pathlib.Path(sys.argv[1]).resolve()).encode()) % 100)' "<root>"`. Then `curl -s http://127.0.0.1:<port>/healthz`. A reply whose `root` equals the root means the server is up; go to step 4.
3. Start it in the background: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan-board.py" --root "<root>"`. Probe `/healthz` again, up to 10 times 0.3 s apart. Exit 1 from the script means another process owns the port: rerun with `--port <port+100>` and use that port from here on. No `python3` on PATH: say so in one line and go to step 5.
4. Open the pane: `navigate` to `http://127.0.0.1:<port>/`. When `navigate` reports that no pane is open, `preview_start` with the same URL, once. One screenshot. Done when the header and the three columns (Backlog, In progress, Done) are visible.
5. Without browser tools (plain `claude` in a terminal): print the URL and the CLI fallback from `board.md`.

## Done when

The pane shows the board, or the URL and the CLI fallback are printed.

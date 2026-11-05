---
name: portfolio
description: "fabreak: open the live, read-only portfolio of every repository in the preview pane."
disable-model-invocation: true
---

# portfolio

Opens the portfolio: one live, read-only page across the repositories listed in `~/.claude/fabreak/repos.md`, served by `${CLAUDE_PLUGIN_ROOT}/scripts/plan-board.py --portfolio` on 127.0.0.1. Each repository is a row: the plan its board would open, Done/total, running cards (In progress or Review), median lead and load-bearing findings, from the same plan, git and PR reads as `/fabreak:board`. A row opens that repository's board, served by the same process. `bootstrap` and `new` add the repository they set up to `repos.md`; the owner adds others as `- /path/to/repo` lines.

## Steps

1. Port 7900. `curl -s http://127.0.0.1:7900/healthz`. A reply with `"portfolio": true`, `api` 5 and a `root` that is the resolved path of `~/.claude/fabreak/repos.md` means the server is up; go to step 3. A reply with that root and any other `api`, or without `portfolio`, is an older server: stop only its listener, `kill $(lsof -ti tcp:7900 -sTCP:LISTEN)`, and go to step 2. No reply, or a reply with another `root` (a board that fell back to this port): go to step 2.
2. Start it in the background: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan-board.py" --portfolio --watch-pid $PPID`. `$PPID` is this session's Claude Code process, so the server stops when the session ends; the page's Stop button stops it sooner. Probe `/healthz` again, up to 10 times 0.3 s apart. Exit 1 from the script means another process owns the port: rerun with `--port 8000` and use that port from here on. No `python3` on PATH: say so in one line and stop. A missing `repos.md` gives an empty page that says how to fill it.
3. Open the pane: `navigate` to `http://127.0.0.1:<port>/`. When `navigate` reports that no pane is open, `preview_start` with the same URL, once. One screenshot. Done when the "Portfolio" header, the live dot reading "Live" and one row per listed repository (or the empty-list message) are visible.
4. Without browser tools (plain `claude` in a terminal): print the URL; the page opens in any browser on this machine.

## Done when

The pane shows the portfolio, or the URL is printed.

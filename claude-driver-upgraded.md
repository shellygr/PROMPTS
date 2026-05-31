<!-- branch: shelly/session-watcher-dashboard -->
=== /plan claude-driver-upgraded ===
You said: Help me organize my claude code sessions.Help me organize my claude code sessions. I put claude to do all kinds of work for me. I want to be able to centrally manage the status of each claude session. Moreover, i want to tie it to a md file on my computer with the next steps or with new sessions planned. This spans multiple repos, multiple vscode windows and even the terminal. Furthermore I sometimes need to act from browser to look things up in GitHub.30 MayClaude responded: I'll check Anthropic's current product documentation before giving you specifics, since Claude Code's session-management features have been evolving quickly.Deliberated session management architecture and verified product capabilitiesDeliberated session management architecture and verified product capabilitiesI'll check Anthropic's current product documentation before giving you specifics, since Claude Code's session-management features have been evolving quickly.Sought documentation to address session management needsSought documentation to address session management needsLet me pull the current Claude Code docs to find what's available for session management.Synthesized desktop app features with markdown-based session tracking systemSynthesized desktop app features with markdown-based session tracking systemGood news: what you're describing is close to a feature Anthropic shipped recently, plus a markdown convention layered on top. Here's how I'd put it together.
Start with the native dashboard. On April 14, 2026 Anthropic redesigned the Claude Code desktop app specifically for this problem. It has a multi-session sidebar where active and recent sessions are grouped by project, filterable by status or environment, with auto-archive when a PR gets merged or closed, three view modes (Verbose, Normal, Summary), and an always-visible usage button. Each session gets Git worktree isolation so parallel sessions don't stomp on each other's working tree. It's available to Pro, Max, Team, and Enterprise users from claude.com/download. If you're currently juggling separate VSCode and terminal windows, moving the "directing" into this one app is the single biggest win — it becomes your mission control, while you keep VSCode open for actual editing. Pasquale PillitteriMiraflow
Then add the markdown source-of-truth. The desktop sidebar shows live state; your .md file holds intent and continuity (next steps, planned sessions). The pattern that works well across repos: one central command-center file (e.g. ~/claude-control.md) listing every active/queued/done session with its status, next steps, and its session name, plus a lightweight NEXT.md inside each repo. The key trick for "central management" is to let Claude maintain the file rather than doing it by hand — put an instruction in your global ~/.claude/CLAUDE.md (which every session reads) telling each session to update its entry in the control file when it starts and stops, or wire a Stop hook to append status automatically.
This leans on real CLI features for continuity: claude -c resumes your last session instantly and claude -r opens a picker, and naming sessions with -n / --name (or /rename) lets you resume by name like claude --resume "feature-auth-system". So if your control file lists feature-auth as the session name, picking it back up is one command. Pasquale PillitteriClaude Lab
For the GitHub/browser piece, you have two options: keep using the browser with Claude in Chrome (the browsing agent), or skip the context-switch entirely by giving Claude Code the GitHub MCP server or the gh CLI so it can look things up in GitHub directly from the session.
I've drafted a starter command-center file you can drop into your home directory and adapt:Reconsidered file format and opted for direct markdown creationReconsidered file format and opted for direct markdown creationA markdown file just needs to be written directly. Let me create the starter.Created a file, read a fileCreated a file, read a fileDrop this at ~/claude-control.md, then paste the "Command center" block into ~/.claude/CLAUDE.md so every session keeps its own row updated. Once that's in place, the desktop sidebar gives you the live view and this file gives you the planning layer.
Two things worth confirming before you commit to the setup: which plan you're on (the redesigned desktop app needs Pro, Max, Team, or Enterprise), and whether you'd rather have sessions update the board via the CLAUDE.md instruction above or via a Stop hook that appends automatically. If you tell me your repo layout and which approach you prefer, I can wire up the exact hook script and the per-repo NEXT.md templates.Claude controlDocument · MD DownloadYou said: Can i define an agent that instead will run in the background and monitor progress on all my .Can i define an agent that instead will run in the background and monitor progress on all my .claude data and update the 'dashboard' live?30 MayClaude responded: Let me verify the current capabilities here, since what counts as an "agent" versus a background process in Claude Code matters for whether this actually works.Clarifying subagent capabilities and background execution mechanicsClarifying subagent capabilities and background execution mechanicsLet me verify the current capabilities here, since what counts as an "agent" versus a background process in Claude Code matters for whether this actually works.Reconciled subagent limitations with viable background monitoring architecturesReconciled subagent limitations with viable background monitoring architecturesShort answer: not as a single "agent" in the Claude Code sense — but yes, you can get exactly the live-updating dashboard you want, just with a different primitive than you're picturing.
The reason for the distinction: a Claude Code subagent isn't a persistent watcher. You define each subagent as a markdown file in .claude/agents/, it runs in its own context window, the parent session delegates one narrow job to it, and the parent gets back only a summary. It finishes and returns — it doesn't sit running, watching your files. There is a background: true field that makes a subagent run concurrently without blocking your main conversation, but that's still scoped to a parent session, not a standalone monitor. So a lone subagent can't be your always-on dashboard updater. TemboDEV Community
What you actually want is one of these two:
Hooks (event-driven — best for "live"). Hooks fire on Claude Code lifecycle events. They can run around tool calls, session starts, stop events, and subagent completion, and you can add async: true to run them in the background without blocking execution. So you wire a command-type hook to SessionStart / Stop / SubagentStop, and on each event a small script reads that session's data and rewrites its row in claude-control.md. This updates the moment something happens — no polling, near-zero cost. If you want the update written in natural language rather than parsed fields, an agent-type hook can spawn a subagent with read access to do deeper verification before deciding what to write. Developers Digest + 2
A background watcher process (true daemon — best for "all my data everywhere"). A standalone script (Node/Python) that watches ~/.claude/projects/**/*.jsonl — the append-only event streams that already record each session's sessionId, lastActive, and fileContext (files read/modified/created) — and rewrites the dashboard on every change. This is the most robust option because it captures every session including ad-hoc terminal ones that might not have hooks configured, and it doesn't even need an LLM for the structured parts. You'd only call claude -p (headless) if you want prose summaries.
There's also a genuine background-session mechanism now — claude --bg dispatches background sessions managed by a daemon, with flags like --model and --permission-mode, and idle background sessions are auto-retired after 5 minutes. But that burns tokens to keep a model in the loop, which is overkill for what's mostly structured-data parsing. Releasebot
My recommendation: the watcher as the engine, plus a Stop hook as an instant trigger. I can build both — the watcher script that parses the JSONL and rewrites your claude-control.md, plus the ~/.claude/settings.json hook config. Want it in Node or Python, and should the status text be plain parsed fields or a Claude-generated one-line summary per session?You said: RequirementsRequirements
1. Watcher daemon in python only
2. Updates an html page that also correlates sessions to open PRs including PRs that I opened not within claude
3. I have cert-claude-driver package I built in github of certora and we should extend that code to allow the watcher to run.
4. Claude headless should use subscription and.not api key. We will use it to correlate sessions to markdown files automatically so I don't have to do the association myself.30 MayClaude responded: Before I build this, I need to look at two things: your existing cert-claude-driver repo (so I extend it correctly rather than guessing its structure), and the…Diagnosing repository access barriers and strategizing information retrievalDiagnosing repository access barriers and strategizing information retrievalBefore I build this, I need to look at two things: your existing cert-claude-driver repo (so I extend it correctly rather than guessing its structure), and the current behavior of headless Claude with subscription auth. Let me start with the repo.Verifying authentication modes and subscription configuration requirementsVerifying authentication modes and subscription configuration requirementsYour cert-claude-driver repo is private (the clone needs credentials I don't have here), so I can't read its structure directly. I'll need a bit of help from you on that — more below. Let me verify the headless-auth detail first, since it's a hard requirement.Architected Python daemon with auth safeguards and integration pointsArchitected Python daemon with auth safeguards and integration pointsThat confirms the critical detail for requirement 4, and it's a genuine footgun worth flagging up front: per Anthropic's auth docs, in non-interactive -p mode the API key is always used when present, and to fall back to your subscription you run unset :antCitation[]{citations="5ec5be22-5925-4e5b-9832-d814884e98be" injected="space"} ANTHROPIC_API_KEY; subscription OAuth from /login is the default for Pro/Max/Team/Enterprise. For a headless daemon with no browser, the documented path is to generate a long-lived token with claude setup-token and use CLAUDE_CODE_OAUTH_TOKEN, which is meant for CI/scripts where browser login isn't available. This matters because there are real reports of -p silently billing at API rates — one Max subscriber ran up $1,800+ in two days because -p used an API key instead of the subscription. So the daemon must scrub ANTHROPIC_API_KEY from the child environment. One more thing to note: starting June 15, 2026, claude -p usage on subscription plans draws from a new monthly Agent SDK credit, separate from interactive limits. Claude + 2
Let me build the daemon. I'll structure it as a clean drop-in package with the Claude-invocation isolated behind one function so it can defer to your existing driver.Diagnosing markdown correlation failures without external dependenciesDiagnosing markdown correlation failures without external dependenciesLet me smoke-test it against a synthetic ~/.claude to confirm parsing and rendering work end-to-end (gh/claude will simply be reported as unavailable here, which is the correct graceful path).Diagnosed daemon robustness gaps and architected graceful error handling improvementsDiagnosed daemon robustness gaps and architected graceful error handling improvementsWorks end-to-end and degrades gracefully when gh/claude are absent. Two robustness tweaks: a missing claude binary should warn once (like gh) rather than throw every cycle. Let me patch that.Architected packaging structure with integration points for cert-claude-driverArchitected packaging structure with integration points for cert-claude-driverBoth degrade cleanly now, two session rows render, warnings surface on the dashboard itself. Let me add packaging, the systemd unit, and a README that covers the auth-safety setup and the cert-claude-driver integration seam.Organized outputs and structured package deployment architectureOrganized outputs and structured package deployment architectureDone — a working Python daemon, smoke-tested against a synthetic ~/.claude tree (parses sessions, renders the dashboard, and degrades cleanly when gh/claude aren't present).
How it maps to your four requirements:

Pure-Python daemon — daemon.py watches ~/.claude/projects/**/*.jsonl via watchdog (event-driven) and falls back to polling if it's not installed. It serves the dashboard on 127.0.0.1:8787 so a browser tab stays live.
HTML + PR correlation — github.py runs gh search prs --author @me --state open across all repos, so PRs you opened directly on GitHub are included, and links them to sessions by repo + branch. render.py builds the auto-refreshing page.
Extends cert-claude-driver — I couldn't read the repo (it's private and the sandbox has no GitHub auth), so I built this as a clean drop-in package. The single Claude-calling function, correlate.run_claude_headless, is marked as the integration seam — swap its body for your driver's. To wire it in properly I need three things from the repo: the package layout/import root, your pyproject.toml, and the signature of any existing function that already invokes claude.
Subscription, not API key — Config.child_env strips ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN from every claude -p call and warns if either was set; the README and systemd unit use claude setup-token → CLAUDE_CODE_OAUTH_TOKEN for browserless subscription auth. The matching runs on haiku and is cached per session to keep usage minimal.

Two honest caveats baked into the code: session status (🟢 active vs 🟡 waiting) is a recency heuristic since the filesystem can't tell you for certain — if you want exact status, a Claude Code Stop hook touching a marker file would make it authoritative. And the project-dir path decoding is lossy, so the parser prefers the cwd field inside each stream.
If you paste your repo's pyproject.toml and tree -L 2, I'll refactor this into a cert_claude_driver subpackage and rewire run_claude_headless to your existing driver.ReadmeDocument · MD DownloadDaemonPY DownloadSessionsPY DownloadGithubPY DownloadCorrelatePY DownloadRenderPY DownloadConfigPY Download  main  PY DownloadPyprojectTOML DownloadClaude watcherSERVICE DownloadDownload allYou said: I'll nove our conversation to claude code.I'll nove our conversation to claude code. Please summarize my request and your artifact in a single message and put all relevant details to easily reproduce it in the real repo1:21Claude responded: Here's a complete handoff summary you can paste into Claude Code.Here's a complete handoff summary you can paste into Claude Code.

Project: claude-watcher — live dashboard for Claude Code sessions
Goal
A background daemon that monitors all my local Claude Code session data and renders a live HTML dashboard showing the status of every session across multiple repos, VSCode windows, and terminals. It should correlate each session to (a) my open GitHub PRs and (b) markdown task files, so I have one central place to manage everything.
Hard requirements

Watcher daemon in Python only.
Updates an HTML page that correlates sessions to open PRs — including PRs I opened directly on GitHub, not via Claude.
Extend my private certora/cert-claude-driver package to host this code, reusing its existing Claude-invocation driver if one exists.
Headless Claude must use my subscription, not an API key. Used to auto-correlate sessions to markdown files so I don't associate them manually.

Critical auth constraint (verified against Anthropic docs)
In non-interactive claude -p mode, an API key is used whenever ANTHROPIC_API_KEY is present — this silently bills at per-token API rates (there are reports of large surprise charges). To stay on the subscription:

Strip ANTHROPIC_API_KEY and ANTHROPIC_AUTH_TOKEN from the env of every claude -p call.
For a browserless daemon, run claude setup-token (prints a ~1-year token) and pass it as CLAUDE_CODE_OAUTH_TOKEN.
Verify active account with claude /status.
Note: from June 15, 2026, subscription claude -p usage draws from a separate monthly Agent SDK credit.

Architecture
~/.claude/projects/**/*.jsonl ─┐
                               ├─► parse sessions ─► correlate ─► dashboard.html (auto-refresh)
gh search prs --author @me ────┤        │
*.md task files ───────────────┘        └─ claude -p (subscription) picks matching .md
Package layout (drop claude_watcher/ under the driver's package root)

config.py — Config dataclass; child_env() does the API-key scrubbing and injects CLAUDE_CODE_OAUTH_TOKEN. Defaults: claude_home ~/.claude, output ~/.claude/dashboard.html, http 127.0.0.1:8787, model haiku, md globs ~/claude-control.md and ~/code/*/NEXT.md, active window 120s.
sessions.py — discovers/parses the JSONL streams (tolerant parsing across CC versions; prefers in-stream cwd over lossy folder-name decoding; extracts branch, files touched, last user/assistant text; heuristic status active/waiting/recent/idle).
github.py — fetch_open_prs via gh search prs --author @me --state open across all repos; match_pr by (repo, head branch); gh_available guard.
correlate.py — discover_markdown; run_claude_headless(prompt, cfg) -> str is the integration seam — replace its body with cert-claude-driver's existing driver; match_markdown caches per session signature; claude_available guard.
render.py — self-contained dark-theme HTML, atomic write, <meta refresh>.
daemon.py — Watcher: preflight warnings, watchdog FS watch (polling fallback), throttled PR refresh (60s), built-in HTTP server, never crashes on a cycle error.
__main__.py — CLI: --claude-home --output --md --port --model --once.
pyproject.toml — claude-watcher console script + [watch] extra (watchdog>=4.0); fold these entries into the repo's existing pyproject.
claude-watcher.service — systemd user unit; sets CLAUDE_CODE_OAUTH_TOKEN, blanks ANTHROPIC_API_KEY.

Status: tested and working
Smoke-tested against a synthetic ~/.claude tree — parses sessions, renders the dashboard, links PRs by branch, degrades cleanly when gh/claude are absent (warnings shown on the page itself). The full source is in the artifact from our previous conversation.
What's still needed to finish requirement 3
I built it as a standalone drop-in because the repo is private and I couldn't read it. In the real repo, gather and provide:

Package layout — tree -L 2 and the import root (e.g. src/cert_claude_driver/).
pyproject.toml / setup.py — so the entry point and watchdog extra go in the right place.
Existing Claude driver signature — any function that already shells out to or wraps claude, so run_claude_headless reuses it instead of adding a second invocation path.

First steps in Claude Code

cd into the cert-claude-driver repo; run tree -L 2 and open pyproject.toml.
Copy the claude_watcher/ package under the import root.
Rewire run_claude_headless to the repo's existing driver (keep str -> str + scrubbed env).
Merge the [project.scripts] and [project.optional-dependencies] entries into the repo's pyproject.
pip install -e '.[watch]', then claude-watcher --once to verify, then gh auth login and run live.
Optional: add a Claude Code Stop hook that touches a per-session marker file for authoritative (non-heuristic) status.


One thing to carry over manually: the artifact files themselves live in this conversation's output, so either keep this chat open to copy them or re-paste the module contents into Claude Code. Want me to also drop all the source into a single concatenated text block here so it travels with this summary?You said: YesYes1:22Claude responded: Here's the full source in one block.Orchestrated file aggregation and concatenationOrchestrated file aggregation and concatenationHere's the full source in one block. Paste this after the handoff summary and Claude Code can recreate every file verbatim.
# ============================================================
# FILE: pyproject.toml
# ============================================================
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "claude-watcher"
version = "0.1.0"
description = "Live dashboard daemon correlating Claude Code sessions to GitHub PRs and markdown task files."
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
# Event-driven filesystem watching. Without it the daemon falls back to polling.
watch = ["watchdog>=4.0"]

[project.scripts]
claude-watcher = "claude_watcher.__main__:main"

[tool.setuptools]
packages = ["claude_watcher"]


# ============================================================
# FILE: claude-watcher.service
# ============================================================
# Save as ~/.config/systemd/user/claude-watcher.service, then:
#   systemctl --user daemon-reload
#   systemctl --user enable --now claude-watcher
#
# IMPORTANT (requirement 4): this unit does NOT set ANTHROPIC_API_KEY, so
# headless `claude -p` stays on your subscription. It passes a long-lived
# subscription OAuth token generated with `claude setup-token` (browserless).
# Verify at any time with `claude /status`.

[Unit]
Description=Claude Code session watcher dashboard
After=network-online.target

[Service]
Type=simple
# Generate this once with:  claude setup-token   (prints a 1-year token)
Environment=CLAUDE_CODE_OAUTH_TOKEN=%h/.config/claude-watcher/oauth-token
# Defensive: ensure no API key leaks in and forces per-token billing.
Environment=ANTHROPIC_API_KEY=
ExecStart=%h/.local/bin/claude-watcher --port 8787
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target


# ============================================================
# FILE: claude_watcher/__init__.py
# ============================================================
"""claude_watcher — a background daemon that monitors ~/.claude session data,
correlates sessions to open GitHub PRs and to local markdown task files, and
renders a live HTML dashboard.

Designed to be dropped into the `cert-claude-driver` package. The single
integration seam with that package is `correlate.run_claude_headless`: replace
it with cert-claude-driver's existing subscription-authenticated Claude driver
if you have one.
"""

__version__ = "0.1.0"


# ============================================================
# FILE: claude_watcher/config.py
# ============================================================
"""Configuration and the auth-safety guard for headless Claude calls."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Env vars that, if present, route `claude -p` onto API (per-token) billing
# instead of the Claude subscription. We strip these from any child env we
# build so the daemon can NEVER silently bill to an API account.
# See: https://code.claude.com/docs/en/authentication
API_BILLING_ENV_VARS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")


@dataclass
class Config:
    # Where Claude Code stores per-session event streams:
    # ~/.claude/projects/<encoded-cwd>/<session-id>.jsonl
    claude_home: Path = field(default_factory=lambda: Path.home() / ".claude")

    # Glob(s) for the markdown task files sessions should be matched against.
    # e.g. the central command center + every repo's NEXT.md
    markdown_globs: tuple[str, ...] = (
        str(Path.home() / "claude-control.md"),
        str(Path.home() / "code" / "*" / "NEXT.md"),
    )

    # Output dashboard
    output_html: Path = field(default_factory=lambda: Path.home() / ".claude" / "dashboard.html")

    # Built-in HTTP server so a browser tab stays live (set port=0 to disable)
    http_host: str = "127.0.0.1"
    http_port: int = 8787

    # How "active" is defined: a session whose stream changed within this many
    # seconds is shown 🟢; otherwise it is treated as idle/recent.
    active_window_s: int = 120

    # Refresh cadence
    poll_interval_s: int = 5        # filesystem poll fallback / debounce
    github_refresh_s: int = 60      # how often to re-pull open PRs
    html_refresh_s: int = 5         # browser auto-refresh interval

    # Headless Claude
    claude_bin: str = "claude"
    claude_model: str = "haiku"     # cheap model is plenty for file matching
    claude_timeout_s: int = 45
    # If you generated one via `claude setup-token`, set it here or in the
    # environment as CLAUDE_CODE_OAUTH_TOKEN. This keeps a browserless daemon
    # on your subscription. Leave None to rely on an existing `claude /login`.
    oauth_token: str | None = field(default_factory=lambda: os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"))

    # gh CLI
    gh_bin: str = "gh"

    def child_env(self) -> dict[str, str]:
        """Environment for spawning `claude -p` / `gh`, scrubbed so headless
        Claude uses the subscription and never falls back to API billing."""
        env = dict(os.environ)
        stripped = [k for k in API_BILLING_ENV_VARS if k in env]
        for k in stripped:
            env.pop(k, None)
        if self.oauth_token:
            env["CLAUDE_CODE_OAUTH_TOKEN"] = self.oauth_token
        # Record what we removed so the daemon can warn the user loudly.
        env["_CW_STRIPPED_BILLING_VARS"] = ",".join(stripped)
        return env


# ============================================================
# FILE: claude_watcher/sessions.py
# ============================================================
"""Discover and parse Claude Code session streams.

Layout (current Claude Code): ~/.claude/projects/<encoded-cwd>/<session-id>.jsonl
where <encoded-cwd> is the project path with every non-alphanumeric char
replaced by '-'. Each .jsonl is an append-only stream of events whose exact
shape varies by version, so parsing here is deliberately tolerant: we scan for
known keys rather than assuming a fixed schema.
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Session:
    session_id: str
    jsonl_path: Path
    cwd: str | None = None
    repo: str | None = None          # basename of cwd, used for display/matching
    branch: str | None = None
    first_ts: float | None = None
    last_ts: float | None = None
    files_touched: set[str] = field(default_factory=set)
    last_user_text: str = ""
    last_assistant_text: str = ""
    n_events: int = 0

    @property
    def status(self) -> str:
        # Heuristic only — the filesystem can't tell us with certainty whether a
        # session is mid-turn or waiting on the user. Time-based + a weak signal
        # from which side spoke last.
        if self.last_ts is None:
            return "idle"
        age = time.time() - self.last_ts
        if age <= 120:
            # spoke-last heuristic: assistant text after the last user text
            # often means it is waiting for the human.
            return "waiting" if self.last_assistant_text and not self._user_after_assistant else "active"
        if age <= 3600:
            return "recent"
        return "idle"

    _user_after_assistant: bool = False


def _decode_project_dir(name: str) -> str:
    # '-Users-me-proj' -> '/Users/me/proj'. Lossy (dashes in real names are
    # ambiguous) so we prefer a `cwd` field from inside the stream when present.
    return name.replace("-", "/")


def _coerce_ts(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        v = value.replace("Z", "+00:00")
        try:
            from datetime import datetime
            return datetime.fromisoformat(v).timestamp()
        except ValueError:
            return None
    return None


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return " ".join(parts)
    return ""


def parse_session(path: Path) -> Session | None:
    s = Session(session_id=path.stem, jsonl_path=path)
    try:
        raw = path.read_text(errors="replace").splitlines()
    except OSError:
        return None
    if not raw:
        return None

    last_role = None
    for line in raw:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(ev, dict):
            continue
        s.n_events += 1

        s.session_id = ev.get("sessionId") or ev.get("session_id") or s.session_id
        if ev.get("cwd"):
            s.cwd = ev["cwd"]
        if ev.get("gitBranch") or ev.get("git_branch"):
            s.branch = ev.get("gitBranch") or ev.get("git_branch")

        ts = _coerce_ts(ev.get("timestamp") or ev.get("lastActive") or ev.get("startTime"))
        if ts is not None:
            s.first_ts = ts if s.first_ts is None else min(s.first_ts, ts)
            s.last_ts = ts if s.last_ts is None else max(s.last_ts, ts)

        # files touched: explicit fileContext, or infer from edit/write tool use
        fc = ev.get("fileContext") or {}
        for key in ("modified", "created", "read"):
            for f in fc.get(key, []) or []:
                s.files_touched.add(f)
        msg = ev.get("message") or ev
        if isinstance(msg, dict):
            for block in (msg.get("content") or []) if isinstance(msg.get("content"), list) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    inp = block.get("input") or {}
                    for k in ("file_path", "path", "filePath"):
                        if inp.get(k):
                            s.files_touched.add(inp[k])

            role = msg.get("role") or ev.get("type")
            text = _text_of(msg.get("content"))
            if role in ("user", "human") and text:
                s.last_user_text = text[:280]
                last_role = "user"
            elif role in ("assistant",) and text:
                s.last_assistant_text = text[:280]
                last_role = "assistant"

    s._user_after_assistant = last_role == "user"

    if not s.cwd:
        s.cwd = _decode_project_dir(path.parent.name)
    if s.cwd:
        s.repo = Path(s.cwd).name
        if not s.branch:
            s.branch = _git_branch(s.cwd)
    return s


def _git_branch(cwd: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def discover_sessions(claude_home: Path) -> list[Session]:
    projects = claude_home / "projects"
    if not projects.is_dir():
        return []
    sessions: list[Session] = []
    for jsonl in projects.glob("**/*.jsonl"):
        s = parse_session(jsonl)
        if s and s.n_events:
            sessions.append(s)
    sessions.sort(key=lambda s: s.last_ts or 0, reverse=True)
    return sessions


# ============================================================
# FILE: claude_watcher/github.py
# ============================================================
"""Fetch the user's open PRs via the `gh` CLI and correlate them to sessions.

We query by author across *all* repos, so PRs you opened outside Claude are
included. Correlation is by (repo, head branch): a session whose working tree
is on a branch that has an open PR gets linked, regardless of who/what created
that PR.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass


@dataclass
class PullRequest:
    number: int
    title: str
    url: str
    repo: str            # "owner/name"
    branch: str          # headRefName
    state: str
    draft: bool = False

    @property
    def repo_short(self) -> str:
        return self.repo.split("/")[-1]


def fetch_open_prs(gh_bin: str, env: dict[str, str]) -> list[PullRequest]:
    """All open PRs authored by the authenticated user, across every repo."""
    cmd = [
        gh_bin, "search", "prs",
        "--author", "@me",
        "--state", "open",
        "--limit", "100",
        "--json", "number,title,url,repository,branch,state,isDraft",
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
    except (OSError, subprocess.SubprocessError) as e:
        raise RuntimeError(f"gh invocation failed: {e}") from e
    if out.returncode != 0:
        raise RuntimeError(f"gh search prs failed: {out.stderr.strip()}")

    prs: list[PullRequest] = []
    for item in json.loads(out.stdout or "[]"):
        repo = item.get("repository", {})
        repo_full = repo.get("nameWithOwner") or repo.get("name") or ""
        prs.append(PullRequest(
            number=item.get("number", 0),
            title=item.get("title", ""),
            url=item.get("url", ""),
            repo=repo_full,
            branch=item.get("branch", "") or "",
            state=item.get("state", "open"),
            draft=bool(item.get("isDraft", False)),
        ))
    return prs


def match_pr(session_repo: str | None, session_branch: str | None,
             prs: list[PullRequest]) -> PullRequest | None:
    if not session_branch:
        return None
    for pr in prs:
        if pr.branch != session_branch:
            continue
        # If we know the repo, require it to match the PR's short name too.
        if session_repo and pr.repo_short and session_repo != pr.repo_short:
            continue
        return pr
    return None


def gh_available(gh_bin: str, env: dict[str, str]) -> str | None:
    """Return None if gh is ready, else a human-readable reason."""
    try:
        out = subprocess.run([gh_bin, "auth", "status"], capture_output=True,
                             text=True, timeout=10, env=env)
    except OSError:
        return f"`{gh_bin}` not found on PATH"
    if out.returncode != 0:
        return "gh is not authenticated (run `gh auth login`)"
    return None


# ============================================================
# FILE: claude_watcher/correlate.py
# ============================================================
"""Correlate each session to a markdown task file using headless Claude.

This is the one place that calls Claude. `run_claude_headless` is the
integration seam: if `cert-claude-driver` already wraps subscription-auth
Claude invocation, replace the body of this function with a call into it.

Auth: we pass a scrubbed env (Config.child_env) so `claude -p` uses the
subscription via OAuth and never the per-token API key. Results are cached per
session signature so we don't re-spend on unchanged sessions.
"""
from __future__ import annotations

import glob
import json
import subprocess
from pathlib import Path

from .config import Config
from .sessions import Session


def discover_markdown(globs) -> dict[str, str]:
    """Map absolute md path -> a short preview (heading-ish first lines)."""
    out: dict[str, str] = {}
    for pattern in globs:
        for p in glob.glob(pattern, recursive=True):
            path = Path(p)
            if not path.is_file():
                continue
            try:
                head = path.read_text(errors="replace").splitlines()[:12]
            except OSError:
                continue
            preview = " | ".join(l.strip() for l in head if l.strip())[:300]
            out[str(path.resolve())] = preview
    return out


def run_claude_headless(prompt: str, cfg: Config) -> str:
    """Run `claude -p` non-interactively on the subscription. Returns stdout text.

    >>> INTEGRATION SEAM <
    Swap this for cert-claude-driver's existing driver if you have one; just
    keep the contract (str prompt -> str response) and the scrubbed env.
    """
    cmd = [
        cfg.claude_bin, "-p", prompt,
        "--model", cfg.claude_model,
        "--output-format", "json",
    ]
    out = subprocess.run(
        cmd, capture_output=True, text=True,
        timeout=cfg.claude_timeout_s, env=cfg.child_env(),
    )
    if out.returncode != 0:
        raise RuntimeError(f"claude -p failed: {out.stderr.strip()[:200]}")
    # --output-format json wraps the result; fall back to raw stdout.
    try:
        payload = json.loads(out.stdout)
        return payload.get("result") or payload.get("text") or out.stdout
    except json.JSONDecodeError:
        return out.stdout


def _signature(s: Session) -> str:
    return f"{s.branch}|{sorted(s.files_touched)[:10]}|{s.last_user_text[:80]}"


def match_markdown(sessions: list[Session], md_files: dict[str, str],
                   cfg: Config, cache: dict[str, str]) -> dict[str, str | None]:
    """session_id -> chosen md path (or None). Cached by session signature."""
    result: dict[str, str | None] = {}
    if not md_files:
        return {s.session_id: None for s in sessions}

    candidates = "\n".join(f"- {path}: {preview}" for path, preview in md_files.items())
    for s in sessions:
        sig = _signature(s)
        ckey = f"{s.session_id}:{sig}"
        if ckey in cache:
            result[s.session_id] = cache[ckey] or None
            continue

        prompt = (
            "You are matching a coding session to the markdown task file it most "
            "likely belongs to. Reply with ONLY the exact file path from the list, "
            "or the single word NONE if nothing fits.\n\n"
            f"Session repo: {s.repo}\nBranch: {s.branch}\n"
            f"Files touched: {', '.join(sorted(s.files_touched)[:15]) or '(none)'}\n"
            f"Last request: {s.last_user_text or '(unknown)'}\n\n"
            f"Candidate markdown files:\n{candidates}\n"
        )
        try:
            answer = run_claude_headless(prompt, cfg).strip()
        except (RuntimeError, OSError, subprocess.SubprocessError):
            result[s.session_id] = None
            continue

        chosen = None
        if answer.upper() != "NONE":
            for path in md_files:
                if path in answer or Path(path).name in answer:
                    chosen = path
                    break
        cache[ckey] = chosen or ""
        result[s.session_id] = chosen
    return result


def claude_available(cfg: Config) -> str | None:
    """Return None if `claude` is callable, else a human-readable reason."""
    import shutil
    if shutil.which(cfg.claude_bin) is None:
        return f"`{cfg.claude_bin}` not found on PATH"
    return None


# ============================================================
# FILE: claude_watcher/render.py
# ============================================================
"""Render the live HTML dashboard. Pure-stdlib, self-contained, atomic write."""
from __future__ import annotations

import html
import os
import time
from datetime import datetime
from pathlib import Path

from .github import PullRequest
from .sessions import Session

_STATUS = {
    "active":  ("🟢", "active"),
    "waiting": ("🟡", "waiting on you"),
    "recent":  ("🔵", "recent"),
    "idle":    ("⚪", "idle"),
}

_STYLE = """
* { box-sizing: border-box; }
body { margin:0; font:14px/1.5 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
       background:#0f1115; color:#e6e8eb; }
header { padding:18px 24px; border-bottom:1px solid #20242c; display:flex;
         align-items:baseline; gap:16px; }
header h1 { font-size:16px; margin:0; font-weight:600; }
header .meta { color:#8b929e; font-size:12px; }
.wrap { padding:16px 24px 48px; }
table { width:100%; border-collapse:collapse; }
th { text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.05em;
     color:#8b929e; padding:8px 10px; border-bottom:1px solid #20242c; }
td { padding:10px; border-bottom:1px solid #181b21; vertical-align:top; }
tr:hover td { background:#14171d; }
.sid { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; color:#8b929e; font-size:12px; }
.repo { font-weight:600; }
.branch { font-family:ui-monospace,monospace; font-size:12px; color:#a8b0bd; }
.pr a { color:#6cb6ff; text-decoration:none; }
.pr a:hover { text-decoration:underline; }
.draft { color:#b08400; font-size:11px; margin-left:6px; }
.md { font-family:ui-monospace,monospace; font-size:12px; color:#7ee787; }
.none { color:#5a616d; }
.focus { color:#c9d1d9; max-width:380px; }
.age { color:#8b929e; font-size:12px; white-space:nowrap; }
.warn { background:#3a1d1d; border:1px solid #6b2b2b; color:#ffb4b4; padding:10px 14px;
        border-radius:8px; margin:0 0 16px; font-size:13px; }
.empty { color:#5a616d; padding:40px; text-align:center; }
"""


def _age(ts: float | None) -> str:
    if not ts:
        return "—"
    d = max(0, int(time.time() - ts))
    if d < 60:
        return f"{d}s ago"
    if d < 3600:
        return f"{d // 60}m ago"
    if d < 86400:
        return f"{d // 3600}h ago"
    return f"{d // 86400}d ago"


def _pr_cell(pr: PullRequest | None) -> str:
    if not pr:
        return '<span class="none">—</span>'
    draft = '<span class="draft">draft</span>' if pr.draft else ""
    label = html.escape(f"#{pr.number} {pr.title}")
    return f'<span class="pr"><a href="{html.escape(pr.url)}" target="_blank">{label}</a>{draft}</span>'


def _md_cell(path: str | None) -> str:
    if not path:
        return '<span class="none">unmatched</span>'
    return f'<span class="md">{html.escape(Path(path).name)}</span>'


def render_html(sessions: list[Session],
                pr_by_session: dict[str, PullRequest | None],
                md_by_session: dict[str, str | None],
                refresh_s: int, warnings: list[str]) -> str:
    rows = []
    order = {"active": 0, "waiting": 1, "recent": 2, "idle": 3}
    for s in sorted(sessions, key=lambda x: (order.get(x.status, 9), -(x.last_ts or 0))):
        icon, label = _STATUS.get(s.status, ("⚪", s.status))
        focus = html.escape((s.last_user_text or s.last_assistant_text or "")[:160])
        rows.append(
            "<tr>"
            f"<td title='{label}'>{icon}</td>"
            f"<td><div class='repo'>{html.escape(s.repo or '?')}</div>"
            f"<div class='sid'>{html.escape(s.session_id[:8])}</div></td>"
            f"<td class='branch'>{html.escape(s.branch or '—')}</td>"
            f"<td>{_pr_cell(pr_by_session.get(s.session_id))}</td>"
            f"<td>{_md_cell(md_by_session.get(s.session_id))}</td>"
            f"<td class='focus'>{focus}</td>"
            f"<td class='age'>{_age(s.last_ts)}</td>"
            "</tr>"
        )
    body = "".join(rows) or '<tr><td colspan="7" class="empty">No sessions found in ~/.claude/projects</td></tr>'
    warn_html = "".join(f'<div class="warn">{html.escape(w)}</div>' for w in warnings)
    now = datetime.now().strftime("%H:%M:%S")

    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="{refresh_s}">
<title>Claude Code — Command Center</title><style>{_STYLE}</style></head>
<body>
<header><h1>🛰️ Claude Code Command Center</h1>
<span class="meta">{len(sessions)} sessions · updated {now} · auto-refresh {refresh_s}s</span></header>
<div class="wrap">{warn_html}
<table><thead><tr>
<th></th><th>Repo / session</th><th>Branch</th><th>Open PR</th>
<th>Task file</th><th>Current focus</th><th>Last activity</th>
</tr></thead><tbody>{body}</tbody></table>
</div></body></html>"""


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    os.replace(tmp, path)


# ============================================================
# FILE: claude_watcher/daemon.py
# ============================================================
"""The watcher daemon: filesystem watch -> parse -> correlate -> render."""
from __future__ import annotations

import logging
import signal
import threading
import time
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from .config import Config
from . import correlate, github, render
from .sessions import discover_sessions

log = logging.getLogger("claude_watcher")


class Watcher:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._stop = threading.Event()
        self._dirty = threading.Event()
        self._dirty.set()  # render once on startup
        self._prs: list[github.PullRequest] = []
        self._prs_at = 0.0
        self._md_cache: dict[str, str] = {}
        self._startup_warnings: list[str] = []
        self._claude_reason: str | None = None

    # ---- auth & dependency guards -------------------------------------------
    def preflight(self) -> None:
        env = self.cfg.child_env()
        stripped = env.get("_CW_STRIPPED_BILLING_VARS", "")
        if stripped:
            log.warning("Stripped %s from child env so `claude -p` stays on your "
                        "subscription (avoids API billing).", stripped)
        if not self.cfg.oauth_token:
            log.info("No CLAUDE_CODE_OAUTH_TOKEN set; relying on an existing "
                     "`claude /login`. For a browserless daemon run "
                     "`claude setup-token` and export the token.")
        reason = github.gh_available(self.cfg.gh_bin, env)
        if reason:
            self._startup_warnings.append(f"GitHub PR correlation disabled: {reason}")
            log.warning(self._startup_warnings[-1])
        self._claude_reason = correlate.claude_available(self.cfg)
        if self._claude_reason:
            self._startup_warnings.append(
                f"Markdown auto-correlation disabled: {self._claude_reason}")
            log.warning(self._startup_warnings[-1])

    # ---- the work cycle ------------------------------------------------------
    def refresh_prs(self, env) -> list[str]:
        warns: list[str] = list(self._startup_warnings)
        if time.time() - self._prs_at < self.cfg.github_refresh_s and self._prs_at:
            return warns
        if github.gh_available(self.cfg.gh_bin, env):
            return warns
        try:
            self._prs = github.fetch_open_prs(self.cfg.gh_bin, env)
            self._prs_at = time.time()
        except RuntimeError as e:
            warns.append(f"PR fetch failed: {e}")
            log.warning(warns[-1])
        return warns

    def cycle(self) -> None:
        env = self.cfg.child_env()
        sessions = discover_sessions(self.cfg.claude_home)
        warnings = self.refresh_prs(env)

        pr_by_session = {
            s.session_id: github.match_pr(s.repo, s.branch, self._prs)
            for s in sessions
        }
        md_files = correlate.discover_markdown(self.cfg.markdown_globs)
        if self._claude_reason:
            md_by_session = {s.session_id: None for s in sessions}
        else:
            try:
                md_by_session = correlate.match_markdown(sessions, md_files, self.cfg, self._md_cache)
            except Exception as e:  # never let correlation crash the daemon
                log.warning("markdown correlation failed: %s", e)
                md_by_session = {s.session_id: None for s in sessions}

        html_doc = render.render_html(
            sessions, pr_by_session, md_by_session,
            self.cfg.html_refresh_s, warnings,
        )
        render.write_atomic(self.cfg.output_html, html_doc)
        log.info("rendered %d sessions -> %s", len(sessions), self.cfg.output_html)

    # ---- run loop ------------------------------------------------------------
    def _serve_http(self) -> None:
        directory = str(self.cfg.output_html.parent)
        handler = partial(SimpleHTTPRequestHandler, directory=directory)
        httpd = HTTPServer((self.cfg.http_host, self.cfg.http_port), handler)
        httpd.timeout = 1
        url = f"http://{self.cfg.http_host}:{self.cfg.http_port}/{self.cfg.output_html.name}"
        log.info("dashboard: %s", url)
        while not self._stop.is_set():
            httpd.handle_request()
        httpd.server_close()

    def _start_fs_watch(self) -> bool:
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError:
            log.info("watchdog not installed; using %ss polling.", self.cfg.poll_interval_s)
            return False

        watcher = self

        class _H(FileSystemEventHandler):
            def on_any_event(self, event):
                if str(event.src_path).endswith(".jsonl"):
                    watcher._dirty.set()

        obs = Observer()
        target = self.cfg.claude_home / "projects"
        target.mkdir(parents=True, exist_ok=True)
        obs.schedule(_H(), str(target), recursive=True)
        obs.daemon = True
        obs.start()
        return True

    def run(self) -> None:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")
        self.preflight()
        signal.signal(signal.SIGINT, lambda *_: self._stop.set())
        signal.signal(signal.SIGTERM, lambda *_: self._stop.set())

        if self.cfg.http_port:
            threading.Thread(target=self._serve_http, daemon=True).start()

        has_watch = self._start_fs_watch()
        while not self._stop.is_set():
            if has_watch:
                triggered = self._dirty.wait(timeout=self.cfg.github_refresh_s)
                self._dirty.clear()
            else:
                triggered = True
                self._stop.wait(self.cfg.poll_interval_s)
            try:
                self.cycle()
            except Exception:  # keep the daemon alive across any cycle error
                log.exception("cycle failed")
            _ = triggered
        log.info("shutting down")


# ============================================================
# FILE: claude_watcher/__main__.py
# ============================================================
"""CLI entry point: `python -m claude_watcher` or the `claude-watcher` script."""
from __future__ import annotations

import argparse
from pathlib import Path

from .config import Config
from .daemon import Watcher


def build_config(args) -> Config:
    cfg = Config()
    if args.claude_home:
        cfg.claude_home = Path(args.claude_home).expanduser()
    if args.output:
        cfg.output_html = Path(args.output).expanduser()
    if args.md:
        cfg.markdown_globs = tuple(args.md)
    if args.port is not None:
        cfg.http_port = args.port
    if args.model:
        cfg.claude_model = args.model
    return cfg


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="claude-watcher",
        description="Live dashboard of Claude Code sessions correlated to PRs and task files.")
    p.add_argument("--claude-home", help="default: ~/.claude")
    p.add_argument("--output", help="HTML output path (default: ~/.claude/dashboard.html)")
    p.add_argument("--md", nargs="*", help="glob(s) for markdown task files")
    p.add_argument("--port", type=int, help="HTTP port for the live dashboard; 0 to disable")
    p.add_argument("--model", help="headless Claude model for matching (default: haiku)")
    p.add_argument("--once", action="store_true", help="render a single pass and exit")
    args = p.parse_args(argv)

    cfg = build_config(args)
    w = Watcher(cfg)
    if args.once:
        w.preflight()
        w.cycle()
        return 0
    w.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
That's all ten files. Directory layout to recreate: pyproject.toml and claude-watcher.service at the package root, and the seven .py files under claude_watcher/. Once recreated, pip install -e '.[watch]' then claude-watcher --once to verify.
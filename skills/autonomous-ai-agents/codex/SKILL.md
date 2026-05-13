---
name: codex
description: Delegate coding tasks to OpenAI Codex CLI agent. Use for building features, refactoring, PR reviews, and batch issue fixing. Requires the codex CLI and a git repository.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring]
    related_skills: [claude-code, hermes-agent]
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## Prerequisites

- Codex installed: `npm install -g @openai/codex` (Windows) or equivalent
- Authentication: Either OpenAI API key OR ChatGPT account (see limitations below)
- **Must run inside a git repository** — Codex refuses to run outside one (use `--skip-git-repo-check` to bypass)
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

### WSL Cross-Platform Setup (Windows + WSL)

If Codex is installed on Windows, call it from WSL via cmd.exe:

```bash
# Find Windows installation path
/mnt/c/Windows/System32/cmd.exe /c "where codex"
# Usually: C:\Users\<username>\AppData\Roaming\npm\codex.cmd

# Call from WSL for read-only/stdout tasks
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\<username> && C:\Users\<username>\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check 'your prompt'"

# Call from WSL for filesystem writes inside the Windows workspace
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\<username>\_3AI_WorkSpace && type prompt.txt | C:\Users\<username>\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check --sandbox workspace-write"
```

**Key flags for WSL invocation:**
- `--skip-git-repo-check` — Bypasses git repository requirement
- `cd /d C:\Users\<username>` — Sets working directory to Windows user home

### Authentication Methods & Model Limitations

**ChatGPT Account (OAuth login):**
- ✅ Works with Codex CLI
- ✅ May use the model configured by the local Codex installation/account (for Scott's Windows setup, Codex v0.128.0 reported `model: gpt-5.5`, `provider: openai` during CLI execution)
- ⚠️ Model availability is account/version/config dependent; verify with a minimal `codex.cmd exec --skip-git-repo-check` run rather than assuming a fixed model list
- ✅ Uses default model from config

**OpenAI API Key:**
- ✅ Supports all models
- Set via environment variable: `OPENAI_API_KEY`
- Or in config: `~/.codex/config.toml`

**Check current config:**
```bash
# Windows
type %USERPROFILE%\\.codex\\config.toml
# WSL via Windows
/mnt/c/Windows/System32/cmd.exe /c "type C:\\Users\\<username>\\.codex\\config.toml"
```

**Verify Codex version:**
```bash
codex --version
# If version < 0.128.0, update: npm update -g codex
```

**Verify linked ChatGPT account:**
- Codex uses ChatGPT OAuth by default when logged in via browser
- Check config for `model = "gpt-5.5"` indicating subscription access
- ChatGPT subscribers get access to latest models (gpt-5.5)

**Version update requirement:**
- Codex v0.121.0 has model compatibility issues
- Update to v0.128.0+ for gpt-5.5 support: `npm update -g codex`

## Quota / Rate Limit Inspection

Codex CLI does not expose a dedicated `codex usage` command in v0.128.0. To check current quota for Scott's Windows ChatGPT-login setup:

1. Verify auth/model without exposing secrets:
   ```bash
   /mnt/c/Windows/System32/cmd.exe /c "codex.cmd login status && codex.cmd --version"
   /mnt/c/Windows/System32/cmd.exe /c "type C:\\Users\\chien\\.codex\\config.toml"
   ```
   Redact any credentials if shown; normal config currently contains model/provider/project settings only.
2. Run a tiny prompt to force Codex to refresh rate-limit metadata (this consumes a small amount of quota):
   ```bash
   # Write prompt file via write_file, then:
   /mnt/c/Windows/System32/cmd.exe /c "cd /d C:\\Users\\chien\\_3AI_WorkSpace && type codex_quota_ping_prompt.txt | codex.cmd exec --skip-git-repo-check --sandbox read-only -"
   ```
   Avoid inline quoted prompts through `cmd.exe` because spaces/Chinese can be split incorrectly; pipe from a file instead.
3. Parse the newest session JSONL under `C:\Users\chien\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl` for `event_msg` payloads with `type=token_count` and `rate_limits`:
   ```python
   import json, pathlib, datetime
   base = pathlib.Path('/mnt/c/Users/chien/.codex/sessions')
   rows = []
   for p in base.glob('20*/**/rollout-*.jsonl'):
       for line in p.read_text(encoding='utf-8', errors='ignore').splitlines():
           if '"rate_limits"' in line and '"token_count"' in line:
               obj = json.loads(line)
               rows.append((obj['timestamp'], str(p), obj['payload'].get('info'), obj['payload']['rate_limits']))
   rows.sort(key=lambda x: x[0])
   print(rows[-1])
   ```
4. Interpret fields:
   - `plan_type`: account plan (e.g. `plus`).
   - `primary.used_percent`: 5-hour Codex window consumption; `window_minutes=300`.
   - `secondary.used_percent`: weekly Codex window consumption; `window_minutes=10080`.
   - `resets_at`: Unix epoch reset time; convert with `datetime.fromtimestamp(...).astimezone()`.
   - `rate_limit_reached_type`: null means not currently blocked.
   - `credits`: usually null for ChatGPT plan.

## One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --sandbox workspace-write 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--sandbox workspace-write` | Write access to workdir + `~/.codex/memories`. **Recommended for filesystem tasks.** Replaces deprecated `--full-auto`. |
| `--full-auto` | ⚠️ Deprecated — use `--sandbox workspace-write` instead |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

### Sandbox Modes

| Mode | Read | Write | Use Case |
|------|------|-------|----------|
| `read-only` (default) | ✅ workdir | ❌ | Review, analysis, stdout-only tasks |
| `workspace-write` | ✅ everywhere | ✅ workdir + memories | Building, file output, coding tasks |
| `full-access` | ✅ everywhere | ✅ everywhere | Unrestricted (avoid unless necessary) |

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly
4. **`--sandbox workspace-write` for building** — allows file writes in workdir while maintaining sandbox protection
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once for batch work

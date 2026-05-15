# MINIPC CLI Orchestration Smoke Tests — 2026-05-15

Purpose: session-specific verification that Hermes running in WSL can command Scott's Windows-native coding CLIs on MINIPC via `cmd.exe`, using the shared workspace and read-back verification.

## Codex CLI

Discovery:

```bat
where codex
where codex.cmd
codex --version
```

Observed:

```text
C:\Users\chien\AppData\Roaming\npm\codex
C:\Users\chien\AppData\Roaming\npm\codex.cmd
codex-cli 0.128.0
```

Write smoke test:

```bat
cd /d C:\Users\chien\_3AI_WorkSpace\codex_cli_smoke_20260515
type prompt.txt | codex.cmd exec --skip-git-repo-check --sandbox workspace-write
```

Observed runtime fields included:

```text
model: gpt-5.5
provider: openai
approval: never
sandbox: workspace-write [workdir, C:\Users\chien\.codex\memories]
```

Verified output file:

```text
C:\Users\chien\_3AI_WorkSpace\codex_cli_smoke_20260515\codex_cli_smoke_result.md
```

Expected marker:

```markdown
# Codex CLI smoke test

marker: HERMES_CODEX_SMOKE_20260515
```

## Claude Code CLI

Discovery:

```bat
where claude
where claude.cmd
claude --version
```

Observed:

```text
C:\Users\chien\AppData\Roaming\npm\claude
C:\Users\chien\AppData\Roaming\npm\claude.cmd
2.1.126 (Claude Code)
```

Text smoke test:

```bat
cd /d C:\Users\chien\_3AI_WorkSpace\claude_code_smoke_20260515
type prompt.txt | claude.cmd --print
```

Expected output:

```text
CLAUDE_CODE_SMOKE_20260515_OK
```

Write smoke test:

```bat
cd /d C:\Users\chien\_3AI_WorkSpace\claude_code_smoke_20260515
type write_prompt.txt | claude.cmd --print --allowedTools Bash Write Edit
```

Verified output file:

```text
C:\Users\chien\_3AI_WorkSpace\claude_code_smoke_20260515\claude_code_smoke_result.md
```

Expected marker:

```markdown
# Claude Code smoke test

marker: HERMES_CLAUDE_CODE_SMOKE_20260515
```

## Window behavior

Hermes invokes these through `cmd.exe /c` and captures stdout/stderr. In the default one-shot modes (`codex.cmd exec`, `claude.cmd --print`), no persistent visible Windows desktop work window should remain. If Scott manually opens PowerShell/CMD and runs the same commands, that shell window stays because the user opened it, not because Codex/Claude leaves a GUI window behind.

Possible visible UI exceptions:

- OAuth/device pairing expired and a browser login is needed.
- The task explicitly launches a browser/GUI/agent-browser.
- Hermes intentionally uses `start`, an interactive TUI session, tmux-like orchestration, or a GUI application.

## Durable lesson

Use Windows mode + prompt-file piping + correct write flags, then verify via disk read-back. Do not trust CLI self-report alone, and do not preserve old read-only capability claims once the corrected Windows-mode invocation succeeds.

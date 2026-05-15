---
name: 3ai-windows-mode-disk-io
description: Use Windows-native 3AI CLI mode whenever Claude/Codex/Gemini need to read/write disk. Prevents false negatives from WSL invocation or missing approval flags.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [3AI, Windows, Disk-IO, Claude, Codex, Gemini, CLI]
    related_skills: [3ai-code-builder, claude-code, codex, gemini-cli]
---

# 3AI Windows Mode Disk I/O

## Trigger

Use this skill whenever a task needs any 3AI CLI agent to **read from or write to disk**, especially under:

- `C:\Users\chien\_3AI_WorkSpace`
- project build folders
- generated prompts / raw logs / output files
- code creation, code repair, reviews that produce files, or pipeline artifacts

## Mandatory Rule

**If disk read/write is required, label and execute the task as `WINDOWS MODE`. Do not treat WSL-mode failures as proof that 3AI CLI cannot write disk.**

Reason: Scott previously verified 3AI CLI disk I/O in Windows mode. A later WSL-oriented test produced a false negative for Gemini because the correct Windows approval flag was missing.

## Agent-Specific Workspaces

Scott created dedicated agent workspaces to avoid cluttering the shared `_3AI_WorkSpace` root. For 3AI **agent** tasks that read/write disk, use these folders by default:

```text
Root:
  Windows: C:\Users\chien\_3AI_WorkSpace\_agent\
  WSL:     /mnt/c/Users/chien/_3AI_WorkSpace/_agent/

Claude agent / Claude Code:
  C:\Users\chien\_3AI_WorkSpace\_agent\Claude Codex\

Codex agent:
  C:\Users\chien\_3AI_WorkSpace\_agent\Codex\

Gemini agent:
  C:\Users\chien\_3AI_WorkSpace\_agent\Gemini Workspace\
```

Use each agent's own folder for prompt files, logs, scratch outputs, review artifacts, and intermediate files. Use the shared root only for high-level coordination manifests or final cross-agent summaries.

## Verified Windows Mode Commands

Run from Hermes/WSL through Windows `cmd.exe`, but set the working directory to the correct Windows workspace:

```bat
Claude agent:
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\_agent\Claude Codex && type prompt.txt | claude.cmd --print --allowedTools Bash Write Edit"

Codex agent:
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\_agent\Codex && type prompt.txt | codex.cmd exec --skip-git-repo-check --sandbox workspace-write"

Gemini agent:
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\_agent\Gemini Workspace && type prompt.txt | gemini.cmd --skip-trust --approval-mode yolo"
```

From WSL terminal tool, use full cmd path when needed:

```bash
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\_agent\Gemini Workspace && type prompt.txt | gemini.cmd --skip-trust --approval-mode yolo"
```

If the actual project repo is outside `_agent`, keep source paths explicit in the prompt, but store prompt/log/report outputs in the relevant agent workspace and verify by reading back those output paths.

## Agent-Specific Requirements

### Claude

- Must use `--allowedTools Bash Write Edit` in non-interactive print mode.
- Without this, Claude may refuse to write because permissions were not pre-authorized.

### Codex

- Must use `--sandbox workspace-write` for disk-writing tasks.
- This gives write access to the Windows workdir and Codex memories.
- `--skip-git-repo-check` is allowed for scratch/non-git workspace tests.

### Gemini

- Must use `--approval-mode yolo` for headless disk writes.
- `--skip-trust` alone is not enough.
- `--approval-mode yolo` has broad/global approval semantics, so only use it with controlled prompts and controlled workspace paths.

## Window / UI Behavior

When Hermes invokes Windows-native CLIs from WSL via `cmd.exe /c` in one-shot modes, the process behaves like a captured CLI job:

- `codex.cmd exec ...` runs, writes/prints results, then exits.
- `claude.cmd --print ...` runs, writes/prints results, then exits.
- No persistent visible Windows desktop work window should remain by default; stdout/stderr are captured by Hermes.

Do not confuse this with the user manually opening PowerShell/CMD: that shell window stays because the user opened it. Visible UI can still appear for OAuth/device pairing, explicit browser/GUI tasks, or if Hermes intentionally launches an interactive/GUI process.

## Verification Protocol

For any claim that 3AI wrote files:

1. Do not trust CLI self-report only.
2. Read back the expected output files from disk with Hermes `read_file` or `search_files`.
3. Confirm the content includes the expected marker or artifact.
4. If the file is missing, inspect stdout/stderr and verify the command used WINDOWS MODE flags.

## Known Good Test Case

Date: 2026-05-12

Workspace:

```text
C:\Users\chien\_3AI_WorkSpace\cli_disk_test_windows_native
```

Verified outputs:

- `claude_result.txt` — Claude wrote successfully with `--allowedTools Bash Write Edit`.
- `codex_result.txt` — Codex wrote successfully with `--sandbox workspace-write`.
- `gemini_result.txt` — Gemini wrote successfully with `--skip-trust --approval-mode yolo`.
- Report: `C:\Users\chien\_3AI_WorkSpace\cli_disk_test_windows_native\verification_report.md`

## Pitfalls

- WSL UNC warning from `cmd.exe` is harmless if the command includes `cd /d C:\Users\chien\_3AI_WorkSpace`.
- Do not use `-p` for long Chinese or path-heavy prompts; write prompt to file and pipe with `type prompt.txt`.
- If `cmd.exe` returns `The filename, directory name, or volume label syntax is incorrect` for agent paths containing spaces, avoid fragile nested quoting from WSL. Use Windows 8.3 short names discovered with `cmd.exe /c "dir /x C:\Users\chien\_3AI_WorkSpace\_agent"`, e.g. `CLAUDE~1` for `Claude Codex` and `GEMINI~1` for `Gemini Workspace`.
- For review jobs, **do not combine shell stdout redirection (`> output/review.md`) with a prompt that asks the agent to write that same file**. On Windows this can leave a zero-byte file locked by the shell while the agent's own write tool fails with `EBUSY` / `file is being used by another process`. Prefer one of these patterns:
  1. Prompt the agent to write `output/<agent>_review.md` itself and let stdout stay in the Hermes process log; or
  2. Redirect stdout to a separate `logs/<agent>.stdout.txt` file and require the agent to write a distinct review file; or
  3. On retry, write to a fresh filename such as `output/<agent>_review2.md` and read back that path.
- Before packaging a repo snapshot for 3AI review, exclude transient caches and locked folders (`.pytest_cache/`, `pytest-cache-files-*/`, `__pycache__/`). Review agents may run discovery commands from the package root; copied stale cache folders can recreate the same permission-denied pytest collection issue that PR-02.1 fixed in the real repo.
- A Gemini write failure without `--approval-mode yolo` is an approval-mode error, not proof Gemini cannot write disk.
- A Codex write failure without `--sandbox workspace-write` may simply be sandbox configuration, not filesystem inability.
- Do not persist negative capability claims from transient setup/approval failures. Capture the working Windows invocation and retry pattern instead.

## Session-Specific References

- `references/minipc-cli-orchestration-smoke-20260515.md` — Codex CLI and Claude Code Windows-mode smoke tests from Hermes/WSL, including discovery commands, write markers, read-back verification, and no-persistent-window behavior.
- `references/windows-review-output-locks-20260515.md` — MiniCalc PR-03 review orchestration pitfall: Windows stdout redirection can lock the same `output/*_review.md` file the agent is asked to write; use distinct stdout logs or fresh retry filenames.

## Reporting Format

When reporting any 3AI disk I/O run to Scott, explicitly state:

```text
Mode: WINDOWS MODE
Workspace: C:\Users\chien\_3AI_WorkSpace\...
CLI flags: ...
Disk verification: read-back confirmed / failed
```

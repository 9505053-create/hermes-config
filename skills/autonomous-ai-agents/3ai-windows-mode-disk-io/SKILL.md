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

## Verified Windows Mode Commands

Run from Hermes/WSL through Windows `cmd.exe`, but set the working directory to the Windows workspace:

```bat
Claude:
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | claude.cmd --print --allowedTools Bash Write Edit"

Codex:
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | codex.cmd exec --skip-git-repo-check --sandbox workspace-write"

Gemini:
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | gemini.cmd --skip-trust --approval-mode yolo"
```

From WSL terminal tool, use full cmd path when needed:

```bash
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | gemini.cmd --skip-trust --approval-mode yolo"
```

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
- A Gemini write failure without `--approval-mode yolo` is an approval-mode error, not proof Gemini cannot write disk.
- A Codex write failure without `--sandbox workspace-write` may simply be sandbox configuration, not filesystem inability.
- Do not persist negative capability claims from transient setup/approval failures. Capture the working Windows invocation and retry pattern instead.

## Reporting Format

When reporting any 3AI disk I/O run to Scott, explicitly state:

```text
Mode: WINDOWS MODE
Workspace: C:\Users\chien\_3AI_WorkSpace\...
CLI flags: ...
Disk verification: read-back confirmed / failed
```

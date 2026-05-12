# Windows Native 3AI CLI Disk I/O Verification

Use this reference when validating or troubleshooting 3AI CLI read/write access to `C:\Users\chien\_3AI_WorkSpace`.

## Durable lesson

When testing 3AI CLI disk I/O from Hermes running in WSL, do **not** conclude a CLI cannot write just because a first attempt lacks the correct Windows CLI permission flags. The reliable pattern is:

1. Put prompt files and marker files inside the Windows workspace, e.g. `C:\Users\chien\_3AI_WorkSpace\cli_disk_test_windows_native`.
2. Invoke the Windows `.cmd` wrappers from a Windows working directory using `cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type ... | <cli>.cmd ..."`.
3. Use the correct write-authorization flag per CLI.
4. Verify by reading the result files from disk; do not trust stdout alone.

## Known-good commands

```bat
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type cli_disk_test_windows_native\prompt_claude.txt | claude.cmd --print --allowedTools Bash Write Edit"
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type cli_disk_test_windows_native\prompt_codex.txt | codex.cmd exec --skip-git-repo-check --sandbox workspace-write"
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type cli_disk_test_windows_native\prompt_gemini.txt | gemini.cmd --skip-trust --approval-mode yolo"
```

## Required flags

- Claude: `--allowedTools Bash Write Edit` in print/headless mode.
- Codex: `--sandbox workspace-write` so writes are allowed in the workdir.
- Gemini: `--approval-mode yolo` for headless write approval. Treat this as high-risk/global approval; use only with controlled prompts and a controlled working directory.

## Verification result from 2026-05-12

Workspace: `C:\Users\chien\_3AI_WorkSpace\cli_disk_test_windows_native`

Verified result files:

- `claude_result.txt`: `WINDOWS_NATIVE_MARKER 2026-05-12 12:26:45 -> Claude Windows-native disk write OK`
- `codex_result.txt`: `WINDOWS_NATIVE_MARKER 2026-05-12 12:26:45 -> Codex Windows-native disk write OK`
- `gemini_result.txt`: `WINDOWS_NATIVE_MARKER 2026-05-12 12:26:45 -> Gemini Windows-native disk write OK`

## Pitfalls

- The `CMD.EXE was started with ... UNC paths are not supported` warning is harmless if the command immediately does `cd /d C:\Users\chien\_3AI_WorkSpace`.
- A Gemini write failure without `--approval-mode yolo` is an approval-mode problem, not proof that Gemini CLI cannot write files.
- A Codex write attempt without `--sandbox workspace-write` may run read-only/default; include the sandbox flag for filesystem tasks.
- Always read the produced files after the CLI exits; the skill/pipeline should record actual file contents or at least file presence and expected suffix.
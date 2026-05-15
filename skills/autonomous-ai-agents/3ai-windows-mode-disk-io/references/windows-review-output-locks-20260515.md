# Windows 3AI Review Output Lock Pattern — 2026-05-15

## Context

During a MiniCalc PR-03 implementation review, Hermes launched Claude/Codex/Gemini from WSL through Windows `cmd.exe /c` in each agent workspace.

The initial commands used shell stdout redirection to the same review filename requested in the prompt, e.g.:

```bat
type prompt_codex.txt | codex.cmd exec --skip-git-repo-check --sandbox workspace-write > output\codex_review.md
```

The prompt also asked Codex to write `output/codex_review.md`.

## Observed failure mode

- The shell created/held `output/codex_review.md` as a zero-byte redirected stdout file.
- The agent attempted to write the same path with its own file tool.
- Windows returned variants of:
  - `EBUSY: resource busy or locked`
  - `The process cannot access the file because it is being used by another process`
  - delete/remove attempts from WSL failed with permission denied while the process/handle was alive.

This is a handle-conflict pattern, not a durable claim that the CLI cannot write files.

## Durable fix

For 3AI review jobs, choose exactly one output channel per path:

1. **Preferred:** no shell redirection for the final review. Prompt the agent to write `output/<agent>_review.md`, and capture stdout only in Hermes process logs.
2. If stdout must be persisted, redirect it to `logs/<agent>.stdout.txt` and instruct the agent to write a different final review path.
3. If a retry is needed after a locked file, use a fresh output filename (`output/<agent>_review2.md`) instead of fighting the locked original.
4. Always read back the final review file from disk before summarizing.

## Packaging pitfall

Do not copy transient cache directories into review packages. If the package contains stale `pytest-cache-files-*` or `.pytest_cache`, agents that run `pytest` or discovery from the package root can hit permission-denied collection failures unrelated to the implementation under review.

Exclude at package creation time:

```text
.pytest_cache/
pytest-cache-files-*/
__pycache__/
```

## Reporting guidance

When this happens, report it as a review-orchestration artifact:

- "The agent process/output-file path conflicted; retry with a fresh review filename."
- Do **not** persist or state "Codex/Gemini cannot write files" unless verified independently after using the known-good Windows-mode flags.

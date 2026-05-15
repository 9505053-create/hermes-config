# Windows CLI Background Review Reliability

Use this when dispatching Claude/Codex/Gemini from Hermes/WSL into Windows-native CLI review folders.

## Durable lessons

- Treat CLI quota/cooldown or a hung background review as scheduling/process state, not as a source-code failure.
- Always route through a Windows path with `cmd.exe /c "cd /d C:\... && type prompt.txt | cli.cmd ..."`; do not rely on the WSL/UNC current working directory.
- Prefer agent-specific review folders under `C:\Users\chien\_3AI_WorkSpace\_agent\<Agent>\reviews\<review_id>` and keep prompts/output inside that folder.
- When a reviewer hangs with no stdout and no output file after a reasonable wait, kill it, record the state in the development history, and either retry later or proceed with the completed reviewers if enough consensus exists.
- If a provider reports quota/cooldown, create a one-shot retry after reset time and continue non-blocking work that does not depend on that verdict.

## Recommended command shape

```bash
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\_agent\Codex\reviews\<review_id> && type prompt_codex.txt | C:\Users\chien\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check --sandbox workspace-write"
```

Claude:

```bash
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\_agent\CLAUDE~1\reviews\<review_id> && type prompt_claude.txt | C:\Users\chien\AppData\Roaming\npm\claude.cmd --print --allowedTools Bash Write Edit"
```

Gemini:

```bash
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\_agent\GEMINI~1\reviews\<review_id> && type prompt_gemini.txt | C:\Users\chien\AppData\Roaming\npm\gemini.cmd --skip-trust --approval-mode yolo"
```

## Background process handling

1. Start each CLI in background only after writing prompts and creating `output/`.
2. Wait/poll in bounded intervals.
3. If a process exits, read the requested `output/*.md` file and/or captured stdout.
4. If a process hangs with empty output after repeated bounded waits, kill it and record: process id/session id, prompt path, elapsed time, and whether any output file was written.
5. Do not let one hung reviewer block planning if two reviewers have completed and there are no blockers; patch docs from completed feedback and optionally schedule a later retry.

## Prompt/output reliability

- Ask the CLI to write to a specific `output/<agent>_<task>_review.md` file.
- Avoid reusing the same output filename after a failed/locked attempt; use a retry-specific filename.
- Keep prompts short for retry reviews: include previous blocker, remediation, and exact question.
- Read back outputs with Hermes tools before summarizing to Scott.

## What not to capture as a conclusion

Do not write durable rules like "Claude is broken" or "Codex cannot write files" from a single timeout, quota reset, or locked output file. The durable rule is to use Windows-native invocation, bounded waits, unique output filenames, read-back verification, and scheduled retries for cooldowns.

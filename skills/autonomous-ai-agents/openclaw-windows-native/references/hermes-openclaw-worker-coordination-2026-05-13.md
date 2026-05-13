# Hermes（小馬）↔ OpenClaw（小蝦）Worker 協作紀錄 — 2026-05-13

## Trigger / Use Case

Use this reference when Scott asks Hermes to coordinate with OpenClaw/小蝦 as a secondary local Windows-native worker, especially for bounded low-risk subtasks from WSL.

## Names and Roles

- Hermes nickname from Scott: **小馬**（short/easy to type, close to Hermes pronunciation）
- OpenClaw nickname: **小蝦**
- Scott: decision maker
- 小馬/Hermes: commander/controller, validates outputs, handles high-risk or cross-platform changes
- 小蝦/OpenClaw: low-risk, verifiable worker for Windows-native subtasks

## Verified Delegation Pattern

From Hermes running in WSL, call Windows-native OpenClaw with the local agent path rather than gateway remote routing:

```python
subprocess.run([
    "cmd.exe", "/c", "openclaw", "agent",
    "--local", "--agent", "main",
    "--message", prompt,
    "--json", "--timeout", "600",
], capture_output=True, text=True, timeout=650)
```

Why this pattern matters:

- `--local --agent main` successfully uses OpenClaw's local auth profile / Codex OAuth route.
- Plain `openclaw agent --message ...` can fail with `Pass --to <E.164>, --session-id, or --agent`.
- Gateway remote mode can hit `scope upgrade pending approval`.
- Python `subprocess.run([...])` avoids fragile Windows `cmd.exe` quoting for Chinese/newline prompts.

Parse the JSON field `finalAssistantVisibleText` for 小蝦's final answer, then independently verify any claimed file writes or state changes.

## Current Disk Scope

Writable root for 小蝦:

```text
C:\Users\chien\_3AI_WorkSpace\_OpenClaw\
```

WSL equivalent:

```text
/mnt/c/Users/chien/_3AI_WorkSpace/_OpenClaw/
```

Allowed write subareas include `projects/`, `reports/`, `tmp/`, and `.trash/`. Other C:/D: locations are read/list/search/analyze only unless Scott explicitly approves a specific write.

Deletion rule: deleting 5+ files or recursively deleting a folder requires Scott confirmation; prefer moving into `.trash`.

## Proven Workflow: External Content Fallback

Observed with a YouTube transcript task:

1. 小馬 asked 小蝦 to fetch/analyze a YouTube transcript.
2. 小蝦's direct fetch returned empty timedtext data.
3. 小馬 fetched the transcript independently (`zh-Hans`, 1686 segments, about 53 minutes).
4. 小馬 re-delegated a bounded report-writing/analysis task to 小蝦, explicitly saying the transcript was supplied by Hermes.
5. 小蝦 wrote the report under the writable root, and 小馬 verified the output path/content.

Lesson: if 小蝦's web/browser/source fetch fails, do not conclude the task is impossible. 小馬 can fetch/source the data, then delegate only the bounded transformation/report step to 小蝦.

## Collaboration Agreement

小蝦 explicitly agreed to these operating principles:

1. **可驗證優先** — every result should include evidence: output path, final content summary, error text, or minimal verification result.
2. **低風險邊界清楚** — stop and report before touching core config, writing outside the writable root, bulk deletion, or external sending.
3. **先降級再求完整** — after tool failure, use a safer fallback rather than repeatedly forcing the brittle path.

Best first tasks for 小蝦:

- Local workspace file tasks: Markdown/report generation, structured data files, organizing content under the writable root.
- Small verifiable execution tasks: run a script, capture stdout/stderr, do minimal tests, summarize errors.
- Data整理/摘要: transcript cleanup, document summaries, extraction into fixed formats.

## Pitfalls

- Do not use Telegram bot-to-bot as the primary Hermes↔OpenClaw channel; Telegram is Scott-facing.
- Do not expose OpenClaw Gateway externally to enable orchestration; keep loopback-only.
- Use n8n for scheduled/repetitive automation, not ad hoc 小馬↔小蝦 dialogue.
- Avoid letting 小蝦 edit its own core OpenClaw/Gateway/Telegram/model/provider/plugin config; have 小馬 perform external backup/edit/restart/verify when needed.
- Do not treat browser automation symlink/permission issues as proof that text/file worker tasks are unavailable.

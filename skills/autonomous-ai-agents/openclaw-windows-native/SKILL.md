---
name: openclaw-windows-native
description: Scott's OpenClaw / 龍蝦 Windows-native installation record and operating guide on MINIPC. Use when asked about 龍蝦, OpenClaw, its gateway, Telegram bot, Codex OAuth models, Windows Scheduled Task, or how Hermes should coordinate with OpenClaw.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [openclaw, 龍蝦, windows, codex, telegram, gateway, autonomous-agent]
    related_skills: [hermes-agent, codex, 3ai-windows-mode-disk-io]
---

# OpenClaw / 龍蝦 Windows Native 安裝與配置紀錄

## Status

Scott reported on 2026-05-13 that OpenClaw（龍蝦）has been installed on MINIPC as a Windows-native local AI agent / Codex coding agent. This record intentionally excludes tokens/secrets.

Hermes verification on 2026-05-13:

- `cmd.exe /c "openclaw gateway status"` succeeded from WSL.
- Gateway is running and listening on `127.0.0.1:18789`.
- Connectivity probe: `ok`.
- Telegram channel probe: connected and working with bot `@ScottChien_OpenClawBot`.
- Model status: default model `openai-codex/gpt-5.4`; provider `openai-codex` uses OAuth, API key count `0`.
- Windows Scheduled Task `OpenClaw Gateway` exists and is `Running`.
- Observed warning: `Gateway event loop degraded: reasons=event_loop_utilization,cpu`. Treat as a performance warning to monitor if OpenClaw feels slow; not a connectivity failure. On 2026-05-13, the warning appeared with `eventLoopUtilization=1`, `cpuCoreRatio≈1`, but `eventLoopDelayMaxMs=0`; gateway and Telegram were still reachable. This likely means the health probe observed the Node.js gateway busy/CPU-active during sampling, not that the event loop was actually stalled. If UX is normal, do not change config; if slow, restart gateway and inspect logs/process CPU.

## Purpose

Scott installed OpenClaw as a second local AI Agent / Codex coding agent alongside Hermes.

Goals:

1. Do not install in WSL, to avoid conflicting with Hermes.
2. Use Windows native environment.
3. Use ChatGPT / OpenAI Codex OAuth subscription route, not OpenAI API key.
4. Keep Gateway bound to local loopback only; do not expose its port externally.
5. Use Telegram as the remote interaction entrypoint.
6. Treat OpenClaw as a complementary tool to Hermes, not a replacement.

## 小蝦 identity and Hermes import

On 2026-05-13, Scott asked to name OpenClaw「小蝦」with existence「AI 助理」and vibe「俐落、溫暖」. Hermes initialized the OpenClaw workspace accordingly.

OpenClaw workspace:

```text
C:\Users\chien\.openclaw\workspace
```

Files updated/created:

- `IDENTITY.md` — name 小蝦 🦐, AI 助理, vibe 俐落/溫暖/可靠
- `USER.md` — Scott profile, language preference, red lines, infrastructure summary
- `SOUL.md` — 小蝦 personality and operating principles
- `MEMORY.md` — long-term memory for 小蝦
- `TOOLS.md` — OpenClaw/Hermes local command notes
- `AGENTS.md` — prepended Scott/小蝦 workspace overlay
- `memory/2026-05-13.md` — daily setup note
- `hermes-import/` — sanitized Hermes knowledge pack and mirrored skill docs

Backup before import:

```text
C:\Users\chien\.openclaw\backups\hermes-import-20260513-034050
```

Import verification:

- `BOOTSTRAP.md` moved out of workspace so OpenClaw should stop treating itself as uninitialized.
- 130 Hermes `SKILL.md` files mirrored under `hermes-import/skills/`.
- Generated/imported Markdown secret-pattern scan found 0 obvious key/token matches.
- OpenClaw Gateway restarted successfully.
- Telegram probe after restart: connected, mode polling, bot works.

Performance / token observation on 2026-05-13:

- Scott perceived 小蝦 as slightly more laggy than Hermes even though both use Codex quota.
- Diagnosis: same Codex quota does not imply same end-to-end latency. OpenClaw path includes Telegram polling -> OpenClaw Gateway -> agent orchestration -> file reads -> model call -> Telegram response. Hermes may use a different model/session path.
- 小蝦 default model is `openai-codex/gpt-5.4`; Hermes current session used `gpt-5.5`.
- The identity test explicitly asked 小蝦 to read multiple files. First run after import also had fresh workspace context and generated a long answer.
- The mirrored `hermes-import/skills/` contains 130 `SKILL.md` files (~1.5 MB) and `SKILLS_INDEX.md` is ~28 KB. These are a reference library, not something 小蝦 should load every turn.
- Hermes patched 小蝦 `AGENTS.md` and `SOUL.md` to add a fast/concise reply mode: normal chat should short-answer first, avoid reading `hermes-import/` unless Scott asks for detail, skills, or research.
- 小馬↔小蝦 token-saving consultation measured OpenClaw-style fixed overhead around 98k-99k tokens per consultation (dominated by cache/input context). This remains a reason to avoid meaningless waste, repeated retries, and full-skill scans. However, Scott later clarified that with Codex/ChatGPT subscription routing the main cost is cooldown/waiting rather than per-token spend; Scott is an AI hobbyist and can wait. Therefore 小蝦/Hermes may autonomously use or request help when it improves correctness, preserves context, provides a meaningful second opinion, or avoids errors — do not be overly conservative solely because tokens are consumed.

If Scott asks 小蝦 whether it knows him, suggest asking:

```text
小蝦，請讀取你的 IDENTITY.md、USER.md、MEMORY.md，以及 hermes-import/HERMES_KNOWLEDGE_PACK.md，然後用繁體中文告訴我你是誰、我是誰、我們的工作方式是什麼。
```

## Host and installation

- Host: MINIPC
- OS: Windows native environment
- Windows user: `chien`
- Installation method: npm global install
- Node.js: `v24.15.0`
- npm: `11.12.1`
- OpenClaw version reported: `2026.5.7`

Installation command previously used:

```powershell
npm install -g openclaw@latest
```

## Gateway configuration

- Gateway bind: loopback
- Gateway address: `127.0.0.1`
- Gateway port: `18789`
- Dashboard URL: `http://127.0.0.1:18789/`
- Chat URL: `http://127.0.0.1:18789/chat`

Known port layout:

- Hermes / Docker / WSL relay related ports: `3000`, `5678`, `8000`
- OpenClaw Gateway port: `18789`

Safety rule: keep OpenClaw Gateway loopback-only unless Scott explicitly approves a different exposure pattern.

## Windows persistence

OpenClaw Gateway is configured as a hidden Windows Scheduled Task, not a visible terminal window.

Scheduled task:

- Task name: `OpenClaw Gateway`
- Run as user: `chien`
- Schedule type: at logon
- Task to run: `wscript.exe "C:\Users\chien\.openclaw\gateway-hidden.vbs"`

Hidden wrapper path:

```text
C:\Users\chien\.openclaw\gateway-hidden.vbs
```

Wrapper purpose:

- Start OpenClaw Gateway via `wscript.exe` hidden.
- Avoid terminal windows popping up at boot or gateway start.

Reported test result:

- After MINIPC reboot and Windows login as `chien`, OpenClaw Gateway auto-starts.
- No terminal window appears.
- Telegram Bot remains usable.

## Models and OAuth

OpenClaw uses OpenAI Codex OAuth / ChatGPT subscription route.

Important constraints:

- Do **not** set `OPENAI_API_KEY` for this OpenClaw setup.
- Do **not** switch to OpenAI API key route.
- Do **not** switch back to `openai/gpt-5`.
- Keep using `openai-codex/gpt-5.4` unless Scott decides otherwise.

Current model setup reported:

- Default model: `openai-codex/gpt-5.4`
- Configured models:
  - `openai-codex/gpt-5.5`
  - `openai-codex/gpt-5`
  - `openai-codex/gpt-5.4`

Known runtime behavior:

- `openai-codex/gpt-5.4` works.
- `openai-codex/gpt-5` previously produced `Unknown model` in OpenClaw runtime.
- Therefore current fixed/default model should remain `openai-codex/gpt-5.4`.

OAuth status reported:

- Provider: `openai-codex`
- Auth type: OAuth
- API key: `0`
- Shell env: off

If OAuth expires, re-login with:

```powershell
openclaw models auth login --provider openai-codex
```

Login method:

```text
OpenAI Codex Device Pairing
```

## Telegram configuration

OpenClaw is connected to Telegram.

Bot:

```text
@ScottChien_OpenClawBot
```

Reported Telegram channel status:

```text
Telegram default: enabled, configured, running, connected, mode:polling, bot:@ScottChien_OpenClawBot, token:config, works
```

Do not request or expose the Telegram token. It is stored in OpenClaw config.

## Common management commands

Run these from Windows PowerShell / cmd, not WSL unless explicitly routing through `cmd.exe` or `powershell.exe`.

Check Gateway:

```powershell
openclaw gateway status
```

Check Telegram channel:

```powershell
openclaw channels status --probe
```

Check models and OAuth:

```powershell
openclaw models status
```

Restart Gateway:

```powershell
openclaw gateway restart
```

Stop Gateway:

```powershell
openclaw gateway stop
```

Start Gateway:

```powershell
openclaw gateway start
```

Query Windows Scheduled Task:

```powershell
schtasks /Query /TN "OpenClaw Gateway" /V /FO LIST
```

## Hermes coordination notes

Detailed session-specific coordination pattern: see `references/hermes-openclaw-worker-coordination-2026-05-13.md` for the verified 小馬↔小蝦 worker delegation recipe, disk scope, external-content fallback, and collaboration agreement.

- Hermes remains the primary commander in Scott's workflow.
- OpenClaw is an additional local agent / Codex coding agent and should be treated as complementary.
- Scott prefers Traditional Chinese for 小馬/Hermes communication in this workflow, especially when interpreting 小蝦 responses or giving handoff prompts.
- Scott prefers that 小蝦 does **not** modify its own core OpenClaw/Gateway/Telegram/model/provider/plugin configuration files. For self-affecting config such as `C:\\\\Users\\\\chien\\\\.openclaw\\\\openclaw.json`, Gateway startup scripts, Scheduled Task, OAuth/model/provider settings: 小蝦 should diagnose and report symptoms/error messages/proposed changes only; Scott/GPT/Hermes analyze; Hermes then edits from outside with backup, restart, and verification. Rationale: avoid 小蝦 breaking its own gateway and losing the ability to self-recover.
- Do not migrate Hermes to OpenClaw or change Hermes provider settings just because OpenClaw exists.
- Do not expose OpenClaw Gateway externally; Telegram is the intended remote interface.
- For ad hoc subtask delegation, Scott does **not** need to manually relay messages. Hermes can call the Windows-native OpenClaw CLI from WSL and collect the result. Use this for bounded low-risk analysis/review/report-generation subtasks, then Hermes verifies/summarizes the result for Scott.
- Current safest one-off delegation pattern from WSL is `openclaw agent --local --agent main --message "..." --json --timeout 600` invoked through `cmd.exe`/Windows context. In practice, `openclaw agent --message ...` without `--agent main` fails with `Pass --to <E.164>, --session-id, or --agent`; gateway mode can also hit `scope upgrade pending approval`, while `--local --agent main` successfully uses the OpenClaw auth profile / Codex OAuth route.
- For long Chinese prompts or prompts containing newlines, avoid shell quoting directly in `cmd.exe /c "..."`. Prefer a small Python wrapper using `subprocess.run(["cmd.exe","/c","openclaw","agent","--local","--agent","main","--message", prompt,"--json","--timeout","600"], ...)`, and keep the prompt mostly one-line to avoid Windows command parsing surprises. Parse `finalAssistantVisibleText` from the JSON output, then independently verify any file paths 小蝦 claims to write.
- If 小蝦 fails to fetch web/YouTube content due tool limits but writes a failure report, Hermes can recover by fetching the external content with its own tools and re-delegating a bounded write/report task to 小蝦, clearly noting in the report that Hermes supplied the transcript/source data.
- Prefer direct `openclaw agent` CLI delegation over n8n for one-off 小蝦 subtasks. Use n8n for scheduled/repetitive automations or health checks; do not expose the loopback-only Gateway externally just to make n8n talk to OpenClaw.
- Avoid Telegram bot-to-bot delegation as the primary path; use Telegram for Scott-facing interaction, not Hermes-to-OpenClaw orchestration.
- If needing to inspect OpenClaw from Hermes running in WSL, prefer Windows-native command invocation, for example:

```bash
cmd.exe /c "openclaw gateway status"
cmd.exe /c "openclaw channels status --probe"
cmd.exe /c "openclaw models status"
cmd.exe /c "openclaw agent --message \"請用繁體中文簡短回覆：你目前是否可用？\" --json --timeout 600"
```

If Windows PATH does not resolve `openclaw` from WSL, run via PowerShell or locate npm global bin on Windows.

### Context compression / handoff rule patch (2026-05-13)

Scott first pointed out via screenshot that 小蝦 cannot automatically/private-message Hermes/小馬 through an internal session channel. Do not teach 小蝦 to falsely say "I already directly asked 小馬" unless a real tool/channel performed that action. Scott then revised the policy: 小蝦 may autonomously decide whether it needs 小馬/Hermes information or assistance. Correct behavior is: 小蝦 says "我判斷這題需要小馬資訊/協助", summarizes the need, error, proposed fix, risk, and rollback; if a real channel/tool exists it may use it, otherwise Scott or Hermes takes over through CLI/external access.

Hermes wrote the rule into OpenClaw's workspace:

- `C:\\Users\\chien\\.openclaw\\workspace\\AGENTS.md` — startup-visible rules for long-context compression and no direct 小馬 contact.
- `C:\\Users\\chien\\.openclaw\\workspace\\MEMORY.md` — long-term memory note.
- `C:\\Users\\chien\\.openclaw\\workspace\\memory\\2026-05-13.md` — daily memory handoff.
- `C:\\Users\\chien\\.openclaw\\workspace\\local-skills\\context-compression\\SKILL.md` — reusable local skill.

Rule summary: `context >55%` => remind once; `context >70%` or large logs/repeated debate/settled decisions extending into new topics => suggest compression. Preserve stable anchors only: Scott decisions, task state, important paths, modified files, backup/rollback, verification results, pending work, and non-negotiable rules. Do not save full chat transcripts. If OpenClaw's system-level auto-compression is uncertain, 小蝦 should say it can proactively remind and write summaries, but actual new session/compression must be triggered by OpenClaw/system/user.

Verification: a long `openclaw agent --local --agent main ...` turn against the existing heavy main session can time out; do not keep retrying the same long turn. Use an explicit fresh `--session-id` plus `--thinking minimal` for verification, or verify via file reads and `openclaw memory search`. On 2026-05-13, explicit session `hermes-context-compression-verify-20260513` successfully acknowledged the 55/70% rule, stable anchors, and no-direct-contact behavior. `openclaw memory search context-compression` also found the new MEMORY.md and daily memory entries, despite a non-fatal sqlite busy warning during forced reindex.

## Verification checklist

When Scott asks whether 龍蝦 / 小蝦 is healthy:

1. Run `openclaw gateway status` from Windows context.
2. Check `http://127.0.0.1:18789/` or `/chat` locally if browser access is needed.
3. Run `openclaw channels status --probe` to confirm Telegram polling and connectivity.
4. Run `openclaw models status` to confirm `openai-codex` OAuth and default model.
5. Query scheduled task if persistence/autostart is in question.

Quick recovery pattern from 2026-05-13:

- Symptom: Scott says 小蝦 does not respond in Telegram.
- `openclaw gateway status` may show `Connectivity probe: failed`, `Runtime: stopped (state Ready...)`, and `connect ECONNREFUSED 127.0.0.1:18789` even though the Scheduled Task is registered.
- Recovery: run `openclaw gateway start` (or `openclaw gateway restart`) from Windows context, then wait 10–20 seconds before probing again.
- Verify with `openclaw gateway status` and `openclaw channels status --probe`.
- A first status check immediately after restart can timeout while the gateway warms up. Recheck after ~15 seconds before declaring failure.
- `Gateway event loop degraded: reasons=event_loop_utilization,cpu` can appear while Telegram still reports `running, connected, mode:polling, works`; treat it as a performance warning unless messages still fail.
- Asking 小蝦 broad inventory questions such as「你有哪些技能」can trigger expensive skill/workspace scans. Prefer bounded prompts like「只列出你記得的前 10 個技能名稱，不要讀檔、不掃描 hermes-import」or ask Hermes to inspect the OpenClaw filesystem directly.
- Observed related warnings/errors: `web_search failed: SearXNG base URL is not configured`, `browser failed: timed out`, and `dir_list failed: unknown node: MINIPC`. These are tool/provider/plugin configuration issues and should not be mixed with basic liveness checks. First confirm gateway/channel/model health; only then fix individual tools.

Basic-operation stability patch on 2026-05-13:

- Backup before edits: `C:\Users\chien\.openclaw\backups\basic-ops-stability-20260513-085217`.
- Rollback command:

```powershell
Copy-Item -Recurse -Force 'C:\Users\chien\.openclaw\backups\basic-ops-stability-20260513-085217\*' 'C:\Users\chien\.openclaw\'
```

- Added `C:\Users\chien\.openclaw\workspace\BASIC_OPS_GUARDRAILS.md`.
- Updated `AGENTS.md`, `SOUL.md`, `TOOLS.md`, and `MEMORY.md` so 小蝦 should short-answer basic Telegram questions first, avoid `browser`/`web_search`/full `hermes-import` scans for simple questions, and degrade after one failed tool attempt.
- Did **not** edit `openclaw.json` because the config schema for disabling browser/search tools is not confirmed and a bad JSON config could break gateway startup.
- Verification after edit: `openclaw.json` parsed OK, required top-level keys present, changed Markdown files had no obvious token/API-key patterns, gateway restarted and probe succeeded.
- Post-restart status: gateway running and `Connectivity probe: ok`; Telegram probe reported `mode:polling`, `bot:@ScottChien_OpenClawBot`, `token:config`, `works`, but the status line sometimes says `disconnected` while still reporting `works`. Treat this as ambiguous status wording unless Scott confirms Telegram messages fail.
- New root-cause clue in log: `failed to create plugin skill symlink ... plugin-skills\\browser-automation ... Error: EPERM: operation not permitted, symlink ...`. This likely comes from Windows symlink permission / Developer Mode / admin privilege and explains browser-plugin fragility. Avoid patching OpenClaw vendor JS unless Scott explicitly accepts the risk; safer fixes are enabling Windows Developer Mode, running the scheduled task with sufficient symlink privilege, or waiting for upstream to use Windows junctions/fallback copies.

Web-search provider patch on 2026-05-13:

- Scott asked 小蝦 to use 小馬-style lightweight web API search instead of fragile browser automation.
- Discovered OpenClaw supports bundled providers and config path:
  - Selected provider: `tools.web.search.provider = "searxng"`
  - SearXNG config: `plugins.entries.searxng.config.webSearch.baseUrl`
- Created local Docker SearXNG service:
  - Container: `openclaw-searxng`
  - Port: `127.0.0.1:18888 -> 8080/tcp`
  - Config file: `C:\Users\chien\.openclaw\searxng\settings.yml`
  - Restart policy: `unless-stopped`
- Updated `C:\Users\chien\.openclaw\openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "searxng": {
        "enabled": true,
        "config": {
          "webSearch": {
            "baseUrl": "http://127.0.0.1:18888",
            "categories": "general",
            "language": "auto"
          }
        }
      }
    }
  },
  "tools": {
    "web": {
      "search": {
        "provider": "searxng"
      }
    }
  }
}
```

- Also updated 小蝦 workspace docs (`AGENTS.md`, `TOOLS.md`, `BASIC_OPS_GUARDRAILS.md`, `MEMORY.md`) so web search should use local SearXNG first and avoid browser.
- Backup before edits: `C:\Users\chien\.openclaw\backups\web-search-searxng-20260513-090217`.
- Rollback command:

```powershell
Copy-Item -Recurse -Force 'C:\Users\chien\.openclaw\backups\web-search-searxng-20260513-090217\*' 'C:\Users\chien\.openclaw\'
```

- Verification commands/results:
  - `openclaw infer web providers --json` showed `searxng` configured and selected.
  - `openclaw infer web search --provider searxng --query 'Trump China visit 2026 Foreign Ministry' --limit 3 --json` returned 3 results, including `fmprc.gov.cn`.
  - Direct SearXNG HTTP probe `http://127.0.0.1:18888/search?...&format=json` returned HTTP 200 JSON.
  - Gateway restarted; `openclaw gateway status` connectivity probe OK; Telegram connected/polling/works after warm-up.
- DuckDuckGo provider was tested and produced `DuckDuckGo returned a bot-detection challenge` plus a Node assertion on Windows, so do **not** use DuckDuckGo as primary for 小蝦.

## Local disk read/write scope for 小蝦

On 2026-05-13 Scott asked Hermes to set a local disk rule/skill for 小蝦 so project outputs have a safe place while the rest of MINIPC remains read-only by policy. Scott then corrected the writable location to live under the shared 3AI workspace for easier retrieval.

Current implementation:

- Writable root: `C:\Users\chien\_3AI_WorkSpace\_OpenClaw\`
- WSL equivalent: `/mnt/c/Users/chien/_3AI_WorkSpace/_OpenClaw/`
- Created subdirs: `projects\`, `reports\`, `tmp\`, `.trash\`
- Rule doc: `C:\Users\chien\.openclaw\workspace\LOCAL_DISK_RULES.md`
- Local skill: `C:\Users\chien\.openclaw\workspace\local-skills\local-disk-scope\SKILL.md`
- Patched OpenClaw docs: `AGENTS.md`, `BASIC_OPS_GUARDRAILS.md`, `TOOLS.md`, `MEMORY.md`
- Initial backup before first rule: `C:\Users\chien\.openclaw\backups\local-disk-scope-rule-20260513-140416`
- Retarget backup before changing to `_3AI_WorkSpace\_OpenClaw`: `C:\Users\chien\.openclaw\backups\local-disk-scope-retarget-20260513-154910`
- Rollback instructions: `C:\Users\chien\.openclaw\backups\local-disk-scope-retarget-20260513-154910\ROLLBACK.txt`

Policy:

- 小蝦 may create/modify/rename/move/delete files only under `C:\Users\chien\_3AI_WorkSpace\_OpenClaw\` and descendants.
- Other MINIPC `C:\` and `D:\` paths are read-only by default: read/list/search/analyze only, no writes/deletes.
- If a task requires writing outside the writable root, 小蝦 should stop, report target path/change/reason/risk/rollback, and wait for explicit Scott approval. If the change involves OpenClaw self-config/Gateway/Telegram/OAuth/model/provider/plugin, hand off to Hermes for external backup+edit+restart+verify.
- Even inside the writable root, Scott's red line still applies: 5+ file deletions or recursive folder deletion require confirmation; prefer moving to `.trash`.

Note: this is currently an agent rule/skill, not an OS-level NTFS sandbox. Do not claim kernel/ACL enforcement unless a separate Windows restricted-user/sandbox setup is implemented and verified.

## State backup / disaster recovery notes

When Scott asks to back up 小蝦 / OpenClaw state, backups must be treated as **4-location disaster recovery** by default: local disk + Google Drive + Supabase + GitHub. Do not call the backup complete until all four destinations have either succeeded or a clear failure/fallback is reported.

Use a local-private backup under:

```text
C:\Users\chien\.openclaw\backups\state-snapshot-YYYYMMDD-HHMMSS
```

For external destinations, never upload raw unencrypted OpenClaw state because it may contain Telegram/OAuth/device tokens. Upload either:

1. encrypted full archive (`.tar.gz.gpg`) + sanitized manifest/restore SOP, or
2. sanitized manifest/restore SOP only if Scott explicitly chooses not to store encrypted raw state externally.

Recommended backup contents:

- Raw private state: `openclaw.json`, `openclaw.json.last-good`, `gateway-hidden.vbs`, `workspace/`, `memory/`, `agents/`, `telegram/`, `devices/`, `identity/`, `tasks/`, `searxng/`, and lightweight logs such as `logs/config-health.json`.
- Diagnostics: `openclaw --version`, `node --version`, `npm --version`, `openclaw gateway status`, `openclaw channels status --probe`, `openclaw models status`, `openclaw infer web providers --json`, `schtasks /Query /TN "OpenClaw Gateway" /V /FO LIST`, `schtasks /Query /TN "OpenClaw Gateway" /XML`, and Docker `openclaw-searxng` status/inspect.
- Safe review files: sanitized copies of JSON config with token/secret/auth/password/API-key fields redacted.
- Recovery docs: `MANIFEST.txt`, `RESTORE_SOP.md`, `BACKUP_VERIFICATION.txt`.

Default exclusions:

- Do not copy `browser/` or `media/` wholesale by default; they can contain browser cookies/cache/private media and can be large. Record their existence/size and only back them up if Scott explicitly wants a full browser/media backup.

Verification checklist for backups:

1. Create `.tar.gz` archive beside the backup directory.
2. Create encrypted archive for external copies, e.g. `.tar.gz.gpg`; passphrase/key handling must be explicit and recoverable by Scott.
3. Verify `tar tzf` lists `MANIFEST.txt`, `RESTORE_SOP.md`, and `BACKUP_VERIFICATION.txt`.
4. Run `du -sh` and `sha256sum` on both plaintext local archive and encrypted external archive; report both to Scott.
5. Check copied SQLite DBs with `PRAGMA integrity_check`; if Python's online backup API fails against live Windows DBs from WSL with `disk I/O error`, raw copied DB+WAL files can still be acceptable if integrity_check on the copied DB reports `ok`.
6. Confirm diagnostics show gateway reachable, Telegram works, and SearXNG is configured/selected when that is expected.
7. Upload/sync to all four locations:
   - Local disk: backup directory + plaintext archive + encrypted archive under `C:\Users\chien\.openclaw\backups\`.
   - Google Drive: encrypted archive + sanitized manifest/restore SOP.
   - Supabase: metadata row plus encrypted archive bytes/base64 or a pointer to the Drive/GitHub artifact if DB size limits apply.
   - GitHub private repo: encrypted archive + sanitized manifest/restore SOP only; never commit raw unencrypted token-bearing files.
8. Read back or verify each destination: Drive file IDs, Supabase row ID/count/checksum, Git commit hash, local sha256.

Security rule: raw backup content may contain Telegram/OAuth/device tokens. Keep raw local/private; do not upload to GitHub/Drive/Supabase or paste contents to third parties. Only share encrypted archives and sanitized summaries/manifests externally.

Latest known state backup created by Hermes on 2026-05-13:

```text
C:\Users\chien\.openclaw\backups\state-snapshot-20260513-095016
C:\Users\chien\.openclaw\backups\state-snapshot-20260513-095016.tar.gz
C:\Users\chien\.openclaw\backups\state-snapshot-20260513-095016.tar.gz.gpg
```

Four-location sync for this backup was completed and verified:

- Local encrypted SHA256: `c8dbeb2e454c6238fde6086dee68385479b371d4bbccc52271484e75a93fda94`
- Google Drive folder ID: `1RZAjzjq-sKd68mfi1JZXOmCQ2yo9pYc5`
- Supabase table/label: `public.openclaw_backups` / `state-snapshot-20260513-095016`
- GitHub private repo path: `openclaw-backups/state-snapshot-20260513-095016`
- GitHub final commit: `35c31ccda131533ed7cc0da1ebf149806ceb0cad`
- Rescue passphrase was generated by Hermes, stored locally under `~/.hermes/secrets/`, and emailed to Scott with subject `Hermes發送 - 小蝦備份救援密碼，重要`. Do not store the passphrase in this skill or in external backup artifacts.

Recurring backup automation added on 2026-05-13:

- Script: `~/.hermes/scripts/openclaw-four-location-backup.py`
- Syntax/prereq check: `python3 -m py_compile ~/.hermes/scripts/openclaw-four-location-backup.py` and `python3 ~/.hermes/scripts/openclaw-four-location-backup.py --check`
- Cron job: `e0ac82284964` / `🦐 每日小蝦四地狀態備份`
- Schedule: `30 0 * * *` (00:30 daily, after the existing 00:00 Hermes config backup job)
- Mode: `no_agent=True`, script-only, delivers concise result to Telegram. If stdout is empty there is no message; the script intentionally prints a short success summary. Non-zero exit alerts the user.
- Passphrase: recurring script uses canonical local file `~/.hermes/secrets/openclaw-backup-passphrase.txt`; if absent, it reuses the previous timestamped passphrase if available, otherwise generates a new one and emails Scott before proceeding.

## Security notes

- This skill intentionally contains no API keys or Telegram token.
- Treat any pasted OpenClaw config containing tokens as sensitive; do not send to third parties.
- Do not add public port-forwarding for OpenClaw Gateway without explicit approval and an authentication design.

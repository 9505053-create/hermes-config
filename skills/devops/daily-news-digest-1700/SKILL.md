---
name: daily-news-digest-1700
category: devops
description: Maintain, repair, validate, and improve Scott's n8n Daily News Digest 1700 workflow, including RF regulatory/certification news filtering and external watchdogs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [n8n, daily-digest, rss, email, watchdog, rf-certification]
    related_skills: [n8n-automation, 3ai-commander, self-improving-agent]
---

# Daily News Digest 1700

## Overview

Use this skill when Scott reports issues or requests improvements for the n8n `Daily News Digest 1700` email workflow.

Workflow identity:
- n8n workflow name: `Daily News Digest 1700`
- Workflow ID: `mQGujbqeQr4caStJ`
- Expected schedule: daily 17:00 Asia/Taipei
- Main compose dir: `/mnt/c/docker/n8n`
- Work/backups root: `/mnt/c/Users/chien/_3AI_WorkSpace/`
- Hermes scripts: `/home/chien/.hermes/scripts/`

Never include SMTP secrets, n8n API keys, owner passwords, or full `.env` content in logs or replies.

## When to Use

Load this skill when:
- Scott says the 17:00 digest did not arrive.
- The digest arrives but content quality is wrong.
- RF certification / FCC / OJ / NCC section needs tuning.
- n8n workflow, credentials, API key, execution history, backup, or watchdog is involved.
- A Daily Digest change needs safe rollout and verification.

## Stability-First Incident Workflow

Treat digest failures as a reliability incident, not just a workflow JSON bug.

1. Confirm n8n and Postgres containers are running.
2. Query Postgres state before editing:
   - `workflow_entity` has the workflow?
   - `credentials_entity` has SMTP credential?
   - `execution_entity` has recent executions?
   - `settings` says owner setup is complete?
3. Check n8n health/readiness:
   - `http://localhost:5678/healthz`
   - `http://localhost:5678/healthz/readiness`
4. Check API key with a smoke test:
   - `GET /api/v1/workflows?limit=5`
5. Create a timestamped rollback backup before changes.
6. Do not trust backup filenames. Inspect dump contents for actual workflow/credential rows.
7. Rebuild only from verified JSON/SQL/credential sources. Single workflow JSON cannot restore credential secrets.
8. After updates, publish/restart n8n if the CLI/API indicates running server will not pick up changes.

## Safe Update Pattern

Before changing the workflow:
1. Export current workflow via n8n API to `_3AI_WorkSpace/backups/`.
2. Patch only `name`, `nodes`, `connections`, and `settings` via API PUT.
3. Do not include read-only fields like `active` or `versionId` in PUT payload.
4. If needed, activate with `POST /api/v1/workflows/{id}/activate`.
5. Publish with `docker exec -u node n8n n8n publish:workflow --id=mQGujbqeQr4caStJ`.
6. Restart n8n when publish says changes will not take effect while running:
   - `cd /mnt/c/docker/n8n && docker compose restart n8n`.
7. Wait for readiness and read the workflow back through API.

## Manual Validation Without Sending Email

Prefer offline validation before sending test emails.

1. Fetch workflow via API.
2. Extract `Format Email` node `jsCode`.
3. Run `new Function(js)` inside the `n8n` container so it uses the same runtime and container networking.
4. Parse generated HTML text for:
   - subject
   - data counts
   - weather failures
   - RF section title/content
   - HTML length
5. Only send a manual email if delivery itself must be tested.

## n8n CLI Pitfalls

- `docker exec n8n n8n execute --id=...` can collide with the running server's Task Broker port 5679.
- Safer manual execution pattern:
  1. `docker stop n8n`
  2. `cd /mnt/c/docker/n8n && docker compose run --rm --no-deps n8n execute --id=mQGujbqeQr4caStJ`
  3. `docker start n8n`
- Compose service entrypoint is already `n8n`; do not run `n8n n8n execute`.
- If CLI execution says missing start node, keep an `executeWorkflowTrigger` manual trigger connected to the main flow.

## External Watchdog and Backup Verification

The digest must not rely only on n8n to report n8n failure.

Existing external Hermes cronjobs:
- `n8n Daily News Digest 1700 watchdog` — daily 17:20 — script `n8n_daily_digest_watchdog.py` — silent on success, alert on failure.
- `n8n DB backup integrity verifier` — daily 18:05 — script `n8n_state_backup_verify.py` — performs DB dump and workflow export, silent on success.

Watchdog principle:
- Check today's 17:00+ successful execution from outside n8n.
- Check workflow exists and active.
- Check credential count is nonzero.
- Success should be silent; failure should print an actionable alert.

Backup verifier principle:
- Do not only check that a backup file exists.
- Verify the dump contains `workflow_entity`, the Daily Digest workflow ID, and credentials data presence.
- Export workflow JSON through API after the DB dump.
- When loading `.env`, override old environment values; do not use `os.environ.setdefault` for `N8N_API_KEY`.

## RF Regulatory / Certification Section Rules

Scott's correction: RF section is not product news.

Intent:
- Main topic: FCC / EU OJ / RED / harmonised standards / NCC regulatory and certification updates.
- Product scope: WLAN / WWAN / BT / Wi-Fi / Bluetooth / LTE / 5G / 6 GHz only narrows relevance.
- If no true regulatory/certification items exist, show no update rather than filling with product launches, reviews, leaks, or generic wireless news.

Use separate searches:
- FCC/OET/KDB/TCB: official FCC/docs sources plus equipment authorization / public notices / rulemaking / Part 15 / 6 GHz terms.
- EU RED/OJ/ETSI: official EU/EUR-Lex/OP/ETSI sources plus `Directive 2014/53/EU`, `Radio Equipment Directive`, `harmonised standards`, `Official Journal`, `Implementing Decision`, `ETSI EN`.
- NCC: official NCC/ncclaw sources plus `電信管制射頻器材`, `型式認證`, `審驗`, `審驗合格`, `符合性聲明`, `抽測`, `技術規範`.

Filtering must be AND logic:
- must match regulatory/certification terms;
- must match product-scope terms;
- must not match blocklist.

Block common false positives:
- general product launch/review/spec/price/deal/leak/news;
- generic FCC device-listing leaks;
- amateur radio, broadcast station, AM/FM transmitter permits, towers;
- NRA/firearms, submarine cable, food/education/ISO certification.

## 3AI Collaboration Pattern

Use 3AI CLI when the problem has design ambiguity or may contain Hermes blind spots.

Pattern:
1. Export the current snippet/state into `_3AI_WorkSpace/temp/`.
2. Write a concise prompt with:
   - current implementation snippet;
   - Scott's correction/preference;
   - constraints and acceptance criteria;
   - request for implementation-ready snippets.
3. Run Codex for implementation/debugging detail and Gemini for broad synthesis/judgment.
4. Save raw logs in `_3AI_WorkSpace/temp/`.
5. Hermes synthesizes; do not blindly copy CLI output.
6. Apply changes with deterministic tools.
7. Verify by readback/API/syntax/container execution.

## Verification Checklist

Before telling Scott the digest is fixed or improved:
- [ ] Current workflow exported to backup.
- [ ] API smoke test works.
- [ ] Workflow active is true.
- [ ] n8n readiness is OK after restart.
- [ ] Code node JS parses with `new Function`.
- [ ] Offline container validation returns subject/counts/html.
- [ ] RF section, if modified, no longer uses broad product-only query.
- [ ] Workflow readback confirms new logic is present.
- [ ] No secrets were printed, logged, or saved in plaintext temp files.
- [ ] Watchdog/backup verifier still exist for scheduled reliability.

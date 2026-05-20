---
name: hermes-backup-disaster-recovery
description: Full Hermes backup + disaster recovery workflow — gather config/memory/skills/scripts, sync to 4 locations (local + Google Drive + Supabase + GitHub), generate manifest with checksums, create/update restore SOP for external AI recovery. Use before upgrades, after major changes, or periodically.
category: devops
---

# Hermes Backup & Disaster Recovery

## When to Use
- **Before major upgrades** (hermes update, model changes, provider switches) — highest priority
- After significant system changes (new skills, config updates, security hardening)
- Periodically (monthly recommended)
- When Scott says "備份" or "backup"

**Do NOT use for**: routine sanitized GitHub backups (use `hermes-backup-sync.sh` instead). This skill is for **full disaster recovery backups** that include everything needed to restore Hermes.

## Prerequisites
- Google Drive OAuth token: `~/.hermes/google_token.json` (**⚠️ check expiry first — see Step 5 fallback**)
- Google Drive workspace folder ID in `.env`: `HERMES_GDRIVE_WORKSPACE_FOLDER_ID`
- Supabase Docker container running: `supabase-db`
- Email script: `~/.hermes/scripts/send-mail.py`
- GitHub repo: `~/projects/hermes-config` (sanitized config backup — Scott's private repo)

## What to Backup

### Critical Files (always included)
| File | Location | Purpose |
|------|----------|---------|
| SOUL.md | `~/.hermes/SOUL.md` | Agent persona |
| AGENTS.md | `~/.hermes/AGENTS.md` | Workflow context (auto-loaded every session) |
| SECURITY_TRUST_BOUNDARY.md | `~/.hermes/SECURITY_TRUST_BOUNDARY.md` | Trust boundary rules |
| config.yaml | `~/.hermes/config.yaml` | Main config |
| channel_directory.json | `~/.hermes/channel_directory.json` | Gateway channels |

### Memory Files (short-term session memory)
All `~/.hermes/memory/*.md` files — contains session handoffs, role directives, advisor feedback, security reviews, skill trackers.

### Memories (long-term persistent memory)
All `~/.hermes/memories/*.md` files — MEMORY.md, USER.md, RECOVERED_WORK_INDEX.md, etc.

### Handoffs
All `~/.hermes/handoffs/*.md` files — cross-session work handoff records.

### Cron Jobs
`~/.hermes/cron/jobs.json` — all scheduled job definitions.

### Other Config
`~/.hermes/gateway_state.json` — gateway runtime state.

### Skills
All `~/.hermes/skills/*/SKILL.md` files — preserve directory structure with `cp --parents`.

### Scripts
All `~/.hermes/scripts/*.py` — email sender, utility scripts.

### NEVER Include (sensitive)
- `~/.hermes/.env` — contains all API keys
- `~/.hermes/google_token.json` — OAuth refresh token
- `~/.hermes/auth.json` — Telegram bot token
- `~/.hermes/google_client_secret.json` — Google OAuth client
- Any file matching `*token*`, `*secret*`, `*key*`, `*credential*`, `*.pem`

### Codex / ChatGPT Subscription Model State (when enabled)
When Hermes is configured to use Scott's ChatGPT/Codex subscription quota as the primary brain, also back up a safe Codex recovery bundle. See `references/codex-oauth-disaster-recovery.md`.

Include:
- `config/config.yaml` showing `model.provider: openai-codex`, `model.default: gpt-5.5`, and OpenRouter `xiaomi/mimo-v2-pro` fallback
- `config/auth.SANITIZED.json` (tokens redacted)
- `codex/CODEX_AUTH_SUMMARY.NO_TOKENS.json` (auth mode/account/model summary only)
- `restore_sop/restore_codex_oauth_from_windows_codex.py` (reads local Windows Codex auth at restore time; contains no tokens)

Never upload raw `/mnt/c/Users/chien/.codex/auth.json`, `~/.codex/auth.json`, or `~/.hermes/auth.json` to GitHub/Drive/Supabase/email.

## Scott shorthand

When Scott says **「4地備份」** or **「四地備份」**, interpret it as syncing/verifying the backup in exactly these four destinations:

1. **本地硬碟 / 3AI 工作區** — usually `C:\Users\chien\_3AI_WorkSpace\HermesBackup` (`/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup` in WSL).
2. **Google Drive** — upload folder/archive/manifest via Drive API, then list/read back.
3. **Supabase** — write a concise index row in `public.hermes_knowledge`, then read back.
4. **GitHub** — push sanitized manifest/SOP/archive snapshot to Scott's private `hermes-config` repo, then verify remote commit.

Always keep this shorthand distinct from a generic single-location backup. Report each of the four destinations separately with verification evidence.

## Workflow

### Step 0: Skill Library Health Audit (when backing up after skill changes)
Before preserving the current state, audit and safely repair the skill library if Scott asked to review skills or if recent work created/edited skills. Use `references/skill-audit-repair-before-backup.md` for the reusable procedure: scan local + repo skill trees, fix YAML/frontmatter/oversized skill errors, re-audit to 0 errors/warnings, then back up the repaired state. Do not delete local-vs-repo mirror duplicates automatically; classify them as informational unless there is a real conflict.

### Step 0.5: Workflow/agent-control evolution backups
When Scott says the current agent state is good and asks to back up a learned workflow evolution, treat it as a backup-worthy state even if no core code changed. Include a concise narrative note (`notes/...md`) and restore SOP (`restore_sop/...md`) that explain the principles learned, not only raw files. Use `references/agent-control-evolution-backup-20260515.md` as the concrete four-location pattern: local archive + Google Drive folder + Supabase `hermes_knowledge` row + GitHub `hermes-config` commit, all sanitized and verified by read-back/list-back.

### Step 1: Create Backup Directory
```bash
BACKUP_BASE="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup"
DATE=$(date +%Y-%m-%d)
VERSION=$(hermes --version 2>/dev/null | grep -oP 'v[\d.]+' || echo 'unknown')
LABEL="${DATE}_HERMES升級前備份_${VERSION}"
BACKUP="$BACKUP_BASE/$LABEL"
mkdir -p "$BACKUP"/{config,memory,memories,handoffs,skills,scripts,cron,restore_sop}
```

### Step 2: Gather Files
```bash
# Config files
cp ~/.hermes/SOUL.md "$BACKUP/config/"
cp ~/.hermes/AGENTS.md "$BACKUP/config/"
cp ~/.hermes/SECURITY_TRUST_BOUNDARY.md "$BACKUP/config/"
cp ~/.hermes/config.yaml "$BACKUP/config/"
cp ~/.hermes/channel_directory.json "$BACKUP/config/"
cp ~/.hermes/gateway_state.json "$BACKUP/config/" 2>/dev/null

# Memory files (short-term)
cp ~/.hermes/memory/*.md "$BACKUP/memory/" 2>/dev/null

# Memories (long-term persistent)
cp ~/.hermes/memories/*.md "$BACKUP/memories/" 2>/dev/null

# Handoffs
cp ~/.hermes/handoffs/*.md "$BACKUP/handoffs/" 2>/dev/null

# Skills (preserve structure)
cd ~/.hermes/skills/ && find . -name "SKILL.md" -exec cp --parents {} "$BACKUP/skills/" \; 2>/dev/null

# Scripts
cp ~/.hermes/scripts/*.py "$BACKUP/scripts/" 2>/dev/null

# Cron jobs
cp ~/.hermes/cron/jobs.json "$BACKUP/cron/" 2>/dev/null

# Sanitized .env (keys only, no values — safe to backup)
python3 -c "
import re
with open('/home/chien/.hermes/.env','r') as f:
    lines = f.readlines()
sanitized = []
for line in lines:
    if '=' in line and not line.strip().startswith('#'):
        key = line.split('=')[0]
        sanitized.append(f'{key}=***REDACTED***')
    else:
        sanitized.append(line.rstrip())
with open('$BACKUP/config/.env.SANITIZED','w') as f:
    f.write('\n'.join(sanitized))
print(f'Sanitized .env: {len(lines)} lines')
"
```

### Step 3: Generate Manifest with Checksums
```bash
echo "=== BACKUP MANIFEST ===" > "$BACKUP/BACKUP_MANIFEST.txt"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')" >> "$BACKUP/BACKUP_MANIFEST.txt"
echo "Hermes Version: $(hermes --version 2>/dev/null || echo 'unknown')" >> "$BACKUP/BACKUP_MANIFEST.txt"
echo "--- Config Files ---" >> "$BACKUP/BACKUP_MANIFEST.txt"
find "$BACKUP/config" -type f -exec basename {} \; | sort >> "$BACKUP/BACKUP_MANIFEST.txt"
echo "--- Memory Files: $(find "$BACKUP/memory" -name '*.md' | wc -l) ---" >> "$BACKUP/BACKUP_MANIFEST.txt"
echo "--- Skill Files: $(find "$BACKUP/skills" -name 'SKILL.md' | wc -l) ---" >> "$BACKUP/BACKUP_MANIFEST.txt"
echo "--- Checksums (config) ---" >> "$BACKUP/BACKUP_MANIFEST.txt"
sha256sum "$BACKUP/config/"* >> "$BACKUP/BACKUP_MANIFEST.txt" 2>/dev/null
echo "=== END ===" >> "$BACKUP/BACKUP_MANIFEST.txt"
```

### Step 4: Compress Archive
```bash
cd "$BACKUP_BASE"
tar czf "${DATE}_hermes_backup.tar.gz" "$DATE/"
echo "Archive size: $(du -sh ${DATE}_hermes_backup.tar.gz | cut -f1)"
```

### Step 5: Sync to 4 Locations

**Location 1: Local** (already done — files are in $BACKUP)

**Location 2: Google Drive** (⚠️ check OAuth token first)
```python
# Test token validity before attempting upload
# If token expired → skip GDrive, use fallback (Location 4 GitHub)
# See google-drive-crud skill for full upload procedure
```
- Create folder structure: `HermesBackup > $LABEL`
- Upload: SOUL.md, AGENTS.md, memory files, manifest, archive
- Folder ID: `${HERMES_GDRIVE_WORKSPACE_FOLDER_ID}`
- **If OAuth token expired**: log failure, continue with other locations. Don't block the backup.

**Location 3: Supabase**
```bash
docker exec -u postgres supabase-db psql -d postgres -c "
INSERT INTO hermes_knowledge (module, title, content, tags, updated_at)
VALUES ('backup', 'Hermes Backup $DATE',
  'Full backup completed. Local: ... Google Drive: ... Supabase: this record.',
  ARRAY['backup','disaster-recovery','$DATE'], NOW())
ON CONFLICT (title) DO UPDATE SET content = EXCLUDED.content, updated_at = NOW();
"
```

**Location 4: GitHub (hermes-config repo)**
```bash
# Push restore SOP + manifest to Scott's private config repo
# This is CRITICAL — if Hermes dies, GPT can read the SOP from GitHub
cp "$BACKUP/restore_sop/HERMES_RESTORE_SOP.md" ~/projects/hermes-config/
cp "$BACKUP/BACKUP_MANIFEST.txt" ~/projects/hermes-config/BACKUP_MANIFEST_${DATE}.txt
cd ~/projects/hermes-config
git add -A
git commit -m "🚨 Pre-upgrade restore SOP + manifest ($LABEL)"
git push origin main
```
- **Repo**: `https://github.com/9505053-create/hermes-config` (Scott's private)
- **Why**: If Hermes is completely dead, GPT can access this repo to read the restore SOP
- **Also run**: `bash ~/.hermes/scripts/hermes-backup-sync.sh` for the regular sanitized sync

### Step 6: Email Notification
```bash
cat "$BACKUP/restore_sop/HERMES_RESTORE_SOP.md" | python3 ~/.hermes/scripts/send-mail.py \
  -s "Hermes發送 - 🔧 復原SOP（請保存此信）" \
  -t "chiensct@hotmail.com" \
  -f "Hermes Agent"
```

### Step 7: Report to Scott
告知：備份完成、三個位置同步狀態、檔案數量、archive 大小。

## Restore SOP
Restore SOP should be maintained at: `$BACKUP/restore_sop/HERMES_RESTORE_SOP.md`
Refer to the latest version in the most recent backup folder.

### When to Restore
- Config values were changed/cleared unexpectedly (e.g. model switch wiped settings)
- Gateway not behaving correctly after config edits
- User says "還原"、"恢復"、"restore"、"用昨天的備份"

### Step-by-Step Restore Procedure

**1. Find the latest known-good backup:**
```bash
BACKUP_BASE="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup"
ls -la "$BACKUP_BASE"
```

**2. Diff current vs backup to identify corruption:**
```bash
diff ~/.hermes/config.yaml "$BACKUP_BASE/2026-05-08/config/config.yaml"
```

**3. Backup current (possibly broken) state BEFORE restoring — tag with .ERROR if corrupted:**
```bash
timestamp=$(date +%Y%m%d_%H%M%S)
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak.${timestamp}.ERROR
```

**4. Restore from backup:**
```bash
cp "$BACKUP_BASE/YYYY-MM-DD/config/config.yaml" ~/.hermes/config.yaml
```

**5. Verify key values match expectations:**
```bash
# Check critical fields with Python
python3 -c "
import yaml
with open('$HOME/.hermes/config.yaml') as f:
    c = yaml.safe_load(f)
print('default model:', c.get('model',{}).get('default','MISSING'))
print('provider:', c.get('model',{}).get('provider','MISSING'))
"
```

**6. Restart gateway to apply:**
```bash
sudo /home/chien/.local/bin/hermes gateway restart
```

**7. Report to Scott** — what was wrong, what's restored, where the broken backup is saved.

### Naming Convention for Broken Backups
- Corrupted config: `config.yaml.bak.{timestamp}.ERROR`
- This makes it easy to identify files that had unknown/bad changes later

## Three Red Lines (must be in restored AGENTS.md)
1. No credit card usage
2. No mass deletion (5+ files) without Scott confirmation
3. No sharing sensitive data with third parties without permission

## Pitfalls (Learned from v0.11→v0.13 Upgrade — 2026-05-11)

### ⚠️ Google Drive OAuth: refresh token 400 / `invalid_grant`
If a backup job fails while calling `gdrive_access_token()` with `HTTP Error 400: Bad Request`, test the token directly before debugging Drive upload code:

```bash
python3 ~/.hermes/hermes-agent/skills/productivity/google-workspace/scripts/setup.py --check
~/.hermes/scripts/openclaw-four-location-backup.py --check
```

`invalid_grant: Token has been expired or revoked` means the **refresh token itself is dead**. Do not retry; generate a fresh consent URL and ask Scott to paste the localhost redirect URL/code:

```bash
python3 ~/.hermes/hermes-agent/skills/productivity/google-workspace/scripts/setup.py --auth-url
python3 ~/.hermes/hermes-agent/skills/productivity/google-workspace/scripts/setup.py --auth-code '<PASTED_REDIRECT_URL_OR_CODE>'
python3 ~/.hermes/scripts/openclaw-four-location-backup.py --check
```

For `openclaw-four-location-backup.py`, ensure `--check` validates `google_refresh_token_valid`, not just the existence of `google_token.json`; otherwise cron will look healthy until the nightly run crashes.

### ⚠️ Google Drive OAuth: `drive.readonly` ≠ `drive`
The `google-workspace` setup script defaults to `drive.readonly` scope. This allows **listing/reading** files but **blocks folder creation and file uploads** (403 Forbidden / insufficientPermissions).

**Fix**: Before first backup, edit `setup.py` line 50:
```python
# WRONG (default in setup.py):
"https://www.googleapis.com/auth/drive.readonly",
# RIGHT:
"https://www.googleapis.com/auth/drive",
```
Then re-authorize: `python3 setup.py --auth-url` → get new code → `python3 setup.py --auth-code CODE`

**Verification**: After auth, test with a folder create call. If 403 → scope is wrong.

### ⚠️ TWO .env Files Exist
There are two `.env` files that both get loaded:
- `~/.hermes/.env` — main config
- `~/.hermes/hermes-agent/.env` — agent repo local env

When modifying env vars (e.g. commenting out `OPENAI_BASE_URL`), **both files must be updated** or the setting persists.

### ⚠️ OPENAI_BASE_URL Redundancy
When `config.yaml` has `model.provider: openrouter`, setting `OPENAI_BASE_URL=https://openrouter.ai/api/v1` in `.env` causes a warning:
> "OPENAI_BASE_URL is set but model.provider is 'openrouter'. Auxiliary clients may route to the wrong endpoint."

**Fix**: Comment out `OPENAI_BASE_URL` in BOTH `.env` files. The provider config in `config.yaml` handles routing.

### ⚠️ Git Stash Merge Conflicts During `hermes update`
`hermes update` stashes local changes, pulls upstream, then tries to re-apply. When conflicts occur:
- **Always keep BOTH sides** — upstream has new features, stash has Scott's customizations (3AI tools, pii_redactor, etc.)
- **Conflict files seen**: `toolsets.py`, `tools/memory_tool.py`, `scripts/whatsapp-bridge/package-lock.json`
- **Syntax check mandatory**: `python3 -m py_compile <file>` after resolving each conflict
- **Dead code from merge**: Upstream refactors can leave orphaned `await` statements in sync functions — these cause SyntaxError even though unreachable

### ⚠️ Post-Upgrade Dead Code in browser_supervisor.py
Merge artifact: `raise e` followed by unreachable `await` code in a sync function. Causes `SyntaxError: 'await' outside async function` at parse time (even though dead). **Fix**: delete dead code block after `raise e`.

### ⚠️ pii_redactor.py Raw String Regex
Raw strings `r"..."` cannot use `\"` to escape inner quotes. The `\"` is treated as backslash + end-of-string. **Fix**: use `r'...'` (single quotes) when the regex contains double quotes.

## Post-Upgrade Verification Checklist
After a major upgrade (like `hermes update`), verify these before declaring success:
After a major upgrade (like `hermes update`), verify these before declaring success:
- [ ] `hermes --version` shows new version number
- [ ] `hermes gateway status` reports healthy
- [ ] Telegram bot responds to test message
- [ ] Skills count matches expected (check `find ~/.hermes/skills/ -name SKILL.md | wc -l`)
- [ ] Cron jobs intact (`hermes cron list` or check `~/.hermes/cron/jobs.json`)
- [ ] `config.yaml` model/provider settings NOT overwritten by upgrade
- [ ] If Codex GPT-5.5 is primary: `hermes auth list` shows `openai-codex` OAuth credential and `hermes -z "只回覆：CODEX_OK" --provider openai-codex -m gpt-5.5` returns `CODEX_OK`
- [ ] `fallback_model` still points to OpenRouter `xiaomi/mimo-v2-pro` when Codex is primary
- [ ] Three Red Lines still present in AGENTS.md
- [ ] `~/.hermes/.env` still has all API keys (upgrade should never touch this)
- [ ] Memory files still present (`ls ~/.hermes/memory/*.md | wc -l`)
- [ ] Long-term memories intact (`cat ~/.hermes/memories/MEMORY.md | head -5`)

If any check fails → **STOP**, restore from backup before proceeding.

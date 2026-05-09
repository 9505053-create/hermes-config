---
name: hermes-backup-disaster-recovery
description: Full Hermes backup + disaster recovery workflow — gather config/memory/skills/scripts, sync to 3 locations (local + Google Drive + Supabase), generate manifest with checksums, create/update restore SOP. Use after major changes or periodically.
category: devops
---

# Hermes Backup & Disaster Recovery

## When to Use
- After significant system changes (new skills, config updates, security hardening)
- Before major upgrades or model changes
- Periodically (monthly recommended)
- When Scott says "備份" or "backup"

**Do NOT use for**: routine sanitized GitHub backups (use `hermes-backup-sync.sh` instead). This skill is for **full disaster recovery backups** that include everything needed to restore Hermes.

## Prerequisites
- Google Drive OAuth token: `~/.hermes/google_token.json`
- Google Drive workspace folder ID in `.env`: `HERMES_GDRIVE_WORKSPACE_FOLDER_ID`
- Supabase Docker container running: `supabase-db`
- Email script: `~/.hermes/scripts/send-mail.py`

## What to Backup

### Critical Files (always included)
| File | Location | Purpose |
|------|----------|---------|
| SOUL.md | `~/.hermes/SOUL.md` | Agent persona |
| AGENTS.md | `~/.hermes/AGENTS.md` | Workflow context (auto-loaded every session) |
| SECURITY_TRUST_BOUNDARY.md | `~/.hermes/SECURITY_TRUST_BOUNDARY.md` | Trust boundary rules |
| config.yaml | `~/.hermes/config.yaml` | Main config |
| channel_directory.json | `~/.hermes/channel_directory.json` | Gateway channels |

### Memory Files
All `~/.hermes/memory/*.md` files — contains session handoffs, role directives, advisor feedback, security reviews, skill trackers.

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

## Workflow

### Step 1: Create Backup Directory
```bash
BACKUP_BASE="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup"
DATE=$(date +%Y-%m-%d)
BACKUP="$BACKUP_BASE/$DATE"
mkdir -p "$BACKUP"/{config,memory,skills,scripts,restore_sop}
```

### Step 2: Gather Files
```bash
# Config files
cp ~/.hermes/SOUL.md "$BACKUP/config/"
cp ~/.hermes/AGENTS.md "$BACKUP/config/"
cp ~/.hermes/SECURITY_TRUST_BOUNDARY.md "$BACKUP/config/"
cp ~/.hermes/config.yaml "$BACKUP/config/"
cp ~/.hermes/channel_directory.json "$BACKUP/config/"

# Memory files
cp ~/.hermes/memory/*.md "$BACKUP/memory/" 2>/dev/null

# Skills (preserve structure)
cd ~/.hermes/skills/ && find . -name "SKILL.md" -exec cp --parents {} "$BACKUP/skills/" \; 2>/dev/null

# Scripts
cp ~/.hermes/scripts/*.py "$BACKUP/scripts/" 2>/dev/null
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

### Step 5: Sync to 3 Locations

**Location 1: Local** (already done — files are in $BACKUP)

**Location 2: Google Drive**
- Use Google Drive REST API (see `google-drive-crud` skill)
- Create folder structure: `HermesBackup > $DATE`
- Upload: SOUL.md, AGENTS.md, SECURITY_TRUST_BOUNDARY.md, memory files, manifest
- Folder ID: `${HERMES_GDRIVE_WORKSPACE_FOLDER_ID}`

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

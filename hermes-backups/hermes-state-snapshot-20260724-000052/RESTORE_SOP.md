# Hermes / 小馬 Restore SOP

Backup label: `hermes-state-snapshot-20260724-000052`

## Important

- `raw/` is PRIVATE local state and may contain API keys, OAuth tokens, Telegram state, and provider auth.
- External copies are encrypted `.tar.gz.gpg` plus sanitized docs.
- Rescue passphrase was emailed to Scott with subject `Hermes發送 - Hermes備份救援密碼，重要` and is stored locally under `~/.hermes/secrets/hermes-backup-passphrase.txt`.

## Restore core files

From WSL, after obtaining and decrypting the backup:

```bash
BACKUP="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260724-000052/raw"
cp "$BACKUP/config.yaml" ~/.hermes/config.yaml
cp "$BACKUP/.env" ~/.hermes/.env
cp "$BACKUP/auth.json" ~/.hermes/auth.json 2>/dev/null || true
cp "$BACKUP/google_token.json" ~/.hermes/google_token.json 2>/dev/null || true
cp "$BACKUP/channel_directory.json" ~/.hermes/channel_directory.json 2>/dev/null || true
rsync -a "$BACKUP/memory/" ~/.hermes/memory/ 2>/dev/null || true
rsync -a "$BACKUP/memories/" ~/.hermes/memories/ 2>/dev/null || true
rsync -a "$BACKUP/handoffs/" ~/.hermes/handoffs/ 2>/dev/null || true
rsync -a "$BACKUP/skills/" ~/.hermes/skills/ 2>/dev/null || true
rsync -a "$BACKUP/scripts/" ~/.hermes/scripts/ 2>/dev/null || true
cp "$BACKUP/cron/jobs.json" ~/.hermes/cron/jobs.json 2>/dev/null || true
hermes gateway status
```

Safer pattern: restore only the known-broken component, then restart/check gateway if needed.

## Mac M4 / 小媽 worker safe snapshot

This backup also includes a v1 safe snapshot under:

```text
raw/mac_m4_worker/hermes_home_safe/
raw/mac_m4_worker/M4HERMES_workspace_safe/
```

The Mac snapshot intentionally excludes local credential material such as `.env`, auth/OAuth JSON files, browser caches, screenshots, logs, and transient caches. It is enough to restore worker rules, skills, scripts, memories, helper-channel files, and diagnostics; reconnect credentials manually if rebuilding the Mac worker from scratch.

Example partial restore:

```bash
BACKUP="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260724-000052/raw/mac_m4_worker"
rsync -a "$BACKUP/hermes_home_safe/" mac-m4:/Users/scottchien/.hermes/
rsync -a "$BACKUP/M4HERMES_workspace_safe/" "mac-m4:/Volumes/2T SSD/M4HERMES/"
ssh mac-m4 '/bin/zsh -lc "source ~/.zprofile 2>/dev/null || true; source ~/.zshrc 2>/dev/null || true; hermes gateway status"'
```

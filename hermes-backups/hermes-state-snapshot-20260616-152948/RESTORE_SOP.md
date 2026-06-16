# Hermes / 小馬 Restore SOP

Backup label: `hermes-state-snapshot-20260616-152948`

## Important

- `raw/` is PRIVATE local state and may contain API keys, OAuth tokens, Telegram state, and provider auth.
- External copies are encrypted `.tar.gz.gpg` plus sanitized docs.
- Rescue passphrase was emailed to Scott with subject `Hermes發送 - Hermes備份救援密碼，重要` and is stored locally under `~/.hermes/secrets/hermes-backup-passphrase.txt`.

## Restore core files

From WSL, after obtaining and decrypting the backup:

```bash
BACKUP="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260616-152948/raw"
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

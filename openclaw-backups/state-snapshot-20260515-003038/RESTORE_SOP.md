# OpenClaw / 小蝦 Restore SOP

Backup label: `state-snapshot-20260515-003038`

## Important

- `raw/` is PRIVATE local state and may contain Telegram/OAuth/device tokens.
- External copies are encrypted `.tar.gz.gpg` plus sanitized docs.
- Rescue passphrase was emailed to Scott with subject `Hermes發送 - 小蝦備份救援密碼，重要` and is stored locally under `~/.hermes/secrets/`.

## Restore core files

From Windows PowerShell, after obtaining and decrypting the backup:

```powershell
$Backup = 'C:\Users\chien\.openclaw\backups\state-snapshot-20260515-003038\raw'
Copy-Item -Recurse -Force "$Backup\openclaw.json" 'C:\Users\chien\.openclaw\openclaw.json'
Copy-Item -Recurse -Force "$Backup\workspace" 'C:\Users\chien\.openclaw\workspace'
Copy-Item -Recurse -Force "$Backup\memory" 'C:\Users\chien\.openclaw\memory'
Copy-Item -Recurse -Force "$Backup\agents" 'C:\Users\chien\.openclaw\agents'
Copy-Item -Recurse -Force "$Backup\telegram" 'C:\Users\chien\.openclaw\telegram'
Copy-Item -Recurse -Force "$Backup\devices" 'C:\Users\chien\.openclaw\devices'
Copy-Item -Recurse -Force "$Backup\identity" 'C:\Users\chien\.openclaw\identity'
Copy-Item -Recurse -Force "$Backup\tasks" 'C:\Users\chien\.openclaw\tasks'
Copy-Item -Recurse -Force "$Backup\searxng" 'C:\Users\chien\.openclaw\searxng'
openclaw gateway restart
openclaw gateway status
openclaw channels status --probe
openclaw models status
```

Safer pattern: restore only the known-broken component.

# OpenClaw / 小蝦 Restore SOP

Backup created: 20260513-095016
Backup path: `/mnt/c/Users/chien/.openclaw/backups/state-snapshot-20260513-095016`

## Important

- `raw/` is a PRIVATE local backup and may contain Telegram/OAuth/device tokens. Do not upload/share.
- Browser profile and inbound media were not copied by default. This backup is for 小蝦 core config, workspace, memory, agent state, diagnostics, SearXNG config, and startup task metadata.

## Restore core files

From Windows PowerShell:

```powershell
$Backup = 'C:\Users\chien\.openclaw\backups\state-snapshot-20260513-095016\raw'
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

## Safer restore pattern

Before overwriting current state, save the current broken state:

```powershell
$Now = Get-Date -Format yyyyMMdd-HHmmss
Copy-Item -Recurse -Force 'C:\Users\chien\.openclaw' "C:\Users\chien\.openclaw.restore-pre-$Now"
```

Then restore only the file/directory that is known broken. For example, if only `openclaw.json` broke, restore only that one file.

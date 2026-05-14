# Tavily Local Install Status

**Date**: 2026-05-14 12:43 CST

## Hermes / WSL

- Install command used: `uv tool install tavily-cli`
- Installed executable: `/home/chien/.local/bin/tvly`
- Version verified: `tavily-cli 0.1.2`
- Auth status: `authenticated: false`
- `TAVILY_API_KEY` presence: false
- Current Hermes Python import of `tavily`: false, expected because `uv tool install` isolates the CLI package in a tool venv.

## OpenClaw / Windows native

- Install command used: `python -m pip install --user tavily-cli`
- Installed executable: `C:\Users\chien\AppData\Roaming\Python\Python312\Scripts\tvly.exe`
- Version verified: `tavily-cli 0.1.2`
- Auth status: `authenticated: false`
- Windows user PATH was updated to include `C:\Users\chien\AppData\Roaming\Python\Python312\Scripts`.
- Created PATH shim: `C:\Users\chien\AppData\Roaming\npm\tvly.cmd` → calls `C:\Users\chien\AppData\Roaming\Python\Python312\Scripts\tvly.exe`, because WSL-launched Windows shells did not immediately pick up the new user PATH entry.
- PATH/shim rollback backup: `C:\Users\chien\.openclaw\backups\tavily-search-20260514-124307\WINDOWS_USER_PATH_BEFORE.txt` and rollback section in `ROLLBACK.md`.

## Credential status

No Tavily API key was configured, displayed, saved, or requested. Tavily CLI is installed but cannot perform authenticated API searches until Scott configures auth in a trusted shell, e.g. `tvly login` or `TAVILY_API_KEY=[REDACTED]`.

## Safe operational status

- Use Tavily only after authentication is configured.
- Until then, fall back to Hermes `web_search` / `web_extract` or OpenClaw local SearXNG.

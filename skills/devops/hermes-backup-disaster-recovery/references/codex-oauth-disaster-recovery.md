# Codex OAuth Disaster Recovery Notes

## Goal
Preserve the ability for Hermes to use Scott's ChatGPT/Codex subscription quota (`openai-codex / gpt-5.5`) without leaking tokens in backups.

## What to back up
Include these safe artifacts in the backup folder and sanitized GitHub repo:

- `config/config.yaml` — should contain:
  ```yaml
  model:
    provider: openai-codex
    default: gpt-5.5
  fallback_model:
    provider: openrouter
    model: xiaomi/mimo-v2-pro
  ```
- `config/auth.SANITIZED.json` — structure only, tokens redacted
- `codex/CODEX_AUTH_SUMMARY.NO_TOKENS.json` — fields such as `auth_mode`, `account_id`, `has_access_token`, `has_refresh_token`, model slugs, and path notes
- `restore_sop/restore_codex_oauth_from_windows_codex.py` — restore helper that reads local Windows Codex auth at restore time
- `restore_sop/HERMES_RESTORE_SOP_v0.13.0_CODEX.md` — user-facing restore SOP

## What NOT to back up externally
Never upload raw versions of:

- `/mnt/c/Users/chien/.codex/auth.json`
- `~/.codex/auth.json`
- `~/.hermes/auth.json`
- `~/.hermes/.env`
- `~/.hermes/google_token.json`

These contain live tokens/secrets. Local disk copies may exist as part of broken-state emergency backup, but do not sync them to GitHub, Supabase, Drive, or email.

## Restore helper pattern
The restore helper should not embed tokens. It should:

1. Check `/mnt/c/Users/chien/.codex/auth.json` exists.
2. Create `~/.codex -> /mnt/c/Users/chien/.codex` symlink if needed.
3. Read `access_token`, `refresh_token`, and `account_id` locally.
4. Insert/update `~/.hermes/auth.json` under `credential_pool.openai-codex`:
   - `label: CODEX_OAUTH`
   - `auth_type: oauth`
   - `source: file:~/.codex/auth.json`
   - `base_url: https://chatgpt.com/backend-api/codex`
5. Restart gateway.

## Verification after restore

```bash
hermes auth list | grep -A2 -E 'openai-codex|openrouter'
hermes -z "只回覆：CODEX_OK" --provider openai-codex -m gpt-5.5
```

Expected final line: `CODEX_OK`.

## Backup report wording
Use an explicit label so future GPT/helper agents can identify the right restore point:

`重要備份：升級本 v0.13.0 (2026.5.7) + CODEX 額度使用備份`

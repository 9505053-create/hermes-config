# OpenAI Codex OAuth as Hermes Primary Model (GPT-5.5) via Windows ChatGPT/Codex Login

## When this applies
Use this when Scott wants Hermes to use his existing ChatGPT/Codex subscription quota instead of paid OpenRouter/OpenAI API spend.

## Known-good configuration
`~/.hermes/config.yaml`:

```yaml
model:
  default: gpt-5.5
  provider: openai-codex
providers: {}
fallback_providers: []
fallback_model:
  provider: openrouter
  model: xiaomi/mimo-v2-pro
```

## Windows → WSL Codex credential bridge
Windows Codex stores ChatGPT/Codex OAuth at:

```text
C:\Users\chien\.codex\auth.json
```

Inside WSL, bridge it with:

```bash
ln -s /mnt/c/Users/chien/.codex ~/.codex 2>/dev/null || true
ls -la ~/.codex/auth.json
```

This symlink alone may not be enough for Hermes gateway. Hermes also expects a credential pool entry in `~/.hermes/auth.json`.

## Add `openai-codex` credential pool entry from Windows Codex auth
Do **not** copy this file to GitHub/Drive/Supabase. It contains live tokens. Generate the Hermes credential entry locally:

```python
import json, os

with open('/mnt/c/Users/chien/.codex/auth.json') as f:
    codex_auth = json.load(f)
with open(os.path.expanduser('~/.hermes/auth.json')) as f:
    hermes_auth = json.load(f)

tokens = codex_auth.get('tokens', {})
entry = {
    "id": "codex01",
    "label": "CODEX_OAUTH",
    "auth_type": "oauth",
    "priority": 0,
    "source": "file:~/.codex/auth.json",
    "access_token": tokens.get('access_token', ''),
    "refresh_token": tokens.get('refresh_token', ''),
    "account_id": tokens.get('account_id', ''),
    "last_status": None,
    "last_status_at": None,
    "last_error_code": None,
    "last_error_reason": None,
    "last_error_message": None,
    "last_error_reset_at": None,
    "base_url": "https://chatgpt.com/backend-api/codex",
    "request_count": 0,
}
hermes_auth.setdefault('credential_pool', {})['openai-codex'] = [entry]
with open(os.path.expanduser('~/.hermes/auth.json'), 'w') as f:
    json.dump(hermes_auth, f, indent=2, ensure_ascii=False)
```

## Verification

```bash
hermes auth list | grep -A2 -E 'openai-codex|openrouter'
hermes -z "只回覆：CODEX_OK" --provider openai-codex -m gpt-5.5
```

Expected:

```text
openai-codex (1 credentials):
  #1  CODEX_OAUTH oauth file:~/.codex/auth.json ←
CODEX_OK
```

If the gateway logs show `Primary provider auth failed: No Codex credentials stored`, the config is correct but the Hermes credential pool entry is missing; rebuild `~/.hermes/auth.json` entry from Windows Codex auth as above, then restart gateway.

## Gateway restart

```bash
sudo /home/chien/.local/bin/hermes gateway restart --system
```

## Safety
- `~/.codex/auth.json` and `~/.hermes/auth.json` contain live tokens. Do not upload raw copies to GitHub, Google Drive, Supabase, or email.
- For disaster recovery backups, store only sanitized summaries and a restore helper that reads local Windows Codex auth at restore time.

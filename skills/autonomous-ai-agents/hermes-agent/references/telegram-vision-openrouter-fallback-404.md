# Telegram / Gateway Vision 404 from OpenRouter Fallback

## Trigger

Use this note when Telegram/gateway shows either:

```text
API failed after 3 retries — HTTP 404: No endpoints found that support image input
Max retries (3) exhausted — trying fallback...
```

especially after image uploads, screenshots, `vision_analyze`, or `browser_vision`.

## What it usually means

A text-only or non-vision model received an image payload. In Scott's setup the observed path was:

1. Codex auth or the old gateway process was stale.
2. Legacy config still had `fallback_model: openrouter / xiaomi/mimo-v2-pro`.
3. Hermes tried to analyze an image through that fallback.
4. OpenRouter returned `404: No endpoints found that support image input` because the fallback endpoint/model did not accept image input.

This is a routing/config issue, not a corrupt image and not a Telegram delivery problem.

## Fast diagnostic checklist

Run a bounded diagnostic; do not wander.

```bash
# 1. Confirm current gateway process and recent logs
hermes gateway status
journalctl -u hermes-gateway.service --since '90 minutes ago' --no-pager \
  | grep -Ei 'No endpoints found|support image input|Max retries|trying fallback|token_expired|Compression summary failed|openrouter|fallback' \
  | tail -120

# 2. Check config without exposing secrets
python3 - <<'PY'
import os,yaml,json,pathlib
p=pathlib.Path(os.path.expanduser('~/.hermes/config.yaml'))
cfg=yaml.safe_load(p.read_text()) or {}
print(json.dumps({
  'model': cfg.get('model'),
  'fallback_providers': cfg.get('fallback_providers'),
  'fallback_model_present': 'fallback_model' in cfg,
  'fallback_model': cfg.get('fallback_model'),
  'auxiliary.vision': cfg.get('auxiliary',{}).get('vision'),
  'auxiliary.compression': cfg.get('auxiliary',{}).get('compression'),
}, ensure_ascii=False, indent=2))
PY

# 3. Check Codex credential status without printing tokens
hermes auth list | grep -A3 -E 'openai-codex|openrouter|gemini'
```

## Scott cost-safety rule

OpenRouter is Scott's emergency reserve. Do **not** leave OpenRouter as silent fallback for ordinary tasks.

Known-good budget posture:

```yaml
model:
  provider: openai-codex
  default: gpt-5.5
fallback_providers: []
# no fallback_model block unless Scott explicitly authorizes emergency fallback
auxiliary:
  compression:
    provider: openai-codex
    model: gpt-5.5
    timeout: 300
```

For vision, `auxiliary.vision.provider: auto` may still route through available vision backends when images need analysis. If Scott explicitly wants to avoid any OpenRouter vision spend, set an explicit non-OpenRouter vision provider that is verified to support image input, or ask before changing because available vision providers vary by credential state.

## Fix pattern

1. Create timestamped backups before editing:
   ```bash
   cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak_vision_fallback_$(date +%Y%m%d_%H%M%S)
   cp ~/.hermes/auth.json ~/.hermes/auth.json.bak_codex_$(date +%Y%m%d_%H%M%S)
   ```
2. Remove legacy `fallback_model` unless Scott authorized OpenRouter rescue.
3. Keep `fallback_providers: []` for routine operation.
4. Rebuild `openai-codex` auth pool from `~/.codex/auth.json` if `hermes auth list` says auth failed.
5. Restart the gateway from outside the gateway process:
   ```bash
   sudo /home/chien/.local/bin/hermes gateway restart --system
   ```
6. Verify after restart that new logs are clean.

## Verification smoke test

Use a tiny local image and require the agent to read it:

```bash
python3 - <<'PY'
from pathlib import Path
from PIL import Image, ImageDraw
p=Path('/tmp/hermes_vision_test.png')
img=Image.new('RGB',(320,120),'white')
ImageDraw.Draw(img).text((20,40),'VISION_TEST_OK',fill='black')
img.save(p)
print(p)
PY
hermes chat -Q --provider openai-codex --model gpt-5.5 \
  -q '請使用 vision_analyze 工具讀取 /tmp/hermes_vision_test.png 圖上的文字，最後只回答讀到的文字。'
```

Expected final response contains:

```text
VISION_TEST_OK
```

Then confirm no new gateway errors:

```bash
journalctl -u hermes-gateway.service --since '5 minutes ago' --no-pager \
  | grep -Ei 'No endpoints found|support image input|Max retries|trying fallback|token_expired|Compression summary failed|openrouter|fallback' \
  | tail -80
```

No output is the desired result.

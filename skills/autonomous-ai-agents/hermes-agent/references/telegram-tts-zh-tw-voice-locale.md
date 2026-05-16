# Telegram TTS Traditional Chinese voice-locale pitfall

## Trigger

Scott says he only hears `Scott` or English words in a Telegram voice reply, and the rest of a Traditional Chinese TTS message is silent, missing, or truncated.

## What happened

In the 2026-05-16 Telegram voice test, Hermes successfully generated `.ogg` voice messages, but Scott heard only the word `Scott`. Inspection showed:

```yaml
tts:
  provider: edge
  edge:
    voice: en-US-AriaNeural
```

The English Edge voice could not reliably speak the Traditional Chinese portion. Switching the Edge voice to Taiwan Mandarin fixed the problem:

```bash
hermes config set tts.edge.voice zh-TW-HsiaoChenNeural
```

## Reusable diagnostic sequence

```bash
# 1. Inspect TTS config without printing secrets
python3 - <<'PY'
import yaml, os
p=os.path.expanduser('~/.hermes/config.yaml')
with open(p, encoding='utf-8') as f:
    cfg=yaml.safe_load(f) or {}
print(yaml.safe_dump(cfg.get('tts', {}), allow_unicode=True, sort_keys=False))
PY

# 2. Back up config before changing
TS=$(date +%Y%m%d_%H%M%S)
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak_tts_zh_${TS}

# 3. Set Traditional Chinese voice for Edge TTS
hermes config set tts.edge.voice zh-TW-HsiaoChenNeural

# 4. After generating a test audio file, verify it is not tiny/truncated
ffprobe -v error -show_entries format=duration,size \
  -of default=nokey=1:noprint_wrappers=1 /path/to/generated.ogg
```

## Verification

- Audio duration should match the spoken Chinese sentence length, not just 1–2 seconds for a long message.
- Scott should hear the full Chinese sentence in Telegram.
- Provide a rollback command pointing at the exact backup path.

## Do not over-capture

Do not save this as "Edge TTS is broken" or "Telegram voice does not work". The durable lesson is: match the TTS voice locale to the language being spoken, and verify generated audio duration/size before blaming the gateway.

# Real-time Voice and Phone Bridge Notes

Captured from a session where Scott compared Hermes Telegram voice messages with OpenClaw phone-call demos.

## User-facing distinction

- **Telegram/Hermes today:** voice message turn-taking.
  - User records and sends a voice message.
  - Gateway receives an audio file.
  - STT transcribes it.
  - Hermes responds with text or a TTS audio file.
- **True real-time voice:** continuous or near-continuous audio stream.
  - The user does not send discrete voice files.
  - Audio frames stream over WebRTC/WebSocket/phone media stream.
  - The agent can respond with lower latency and potentially interrupt/handle barge-in.

## Why OpenClaw can “call”

OpenClaw phone-call demos use a bridge layer, not LINE Call or Telegram Call:

```text
Phone handset
↔ Twilio/Telnyx/Plivo/SIP number
↔ webhook/WebSocket media stream
↔ voice-call plugin / voice bridge
↔ realtime voice model OR STT → LLM/agent → TTS
↔ agent tools/memory
```

OpenClaw docs identify `@openclaw/voice-call`, supporting providers such as `twilio`, `telnyx`, `plivo`, and `mock`.

Representative OpenClaw commands from docs:

```bash
openclaw plugins install @openclaw/voice-call
openclaw voicecall setup
openclaw voicecall smoke --to "+15555550123"
openclaw voicecall call --to "+15555550123" --message "Hello from OpenClaw"
openclaw voicecall start --to "+15555550123"
```

## LINE/Telegram limitation

LINE and Telegram bot APIs are suitable for text and voice-message workflows. They generally do not expose bot-controlled live app-call audio streams that allow an agent to place or answer LINE/Telegram calls as a human user.

For live calls, use:
- a phone provider (Twilio/Telnyx/Plivo/SIP/Asterisk/FreeSWITCH), or
- a web app with WebRTC/WebSocket, or
- a realtime voice API directly from a client.

## Practical route for Hermes

Recommended order:
1. Keep Telegram short-turn voice mode for low-cost daily use.
2. Build a browser voice bridge first for real-time UX without phone-number costs.
3. Add Twilio/Telnyx phone bridge later only after cost and webhook exposure boundaries are explicit.

## Safety/cost notes

- Do not initiate paid phone-provider setup or phone-number purchase without Scott's confirmation.
- Public webhook exposure needs an auth/allowlist strategy and a rollback path.
- Prefer mock/local tests before real outbound calls.

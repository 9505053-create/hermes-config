# OpenClaw Telegram Silent / Gateway Watchdog Lesson — 2026-05-18

## Trigger

Use this reference when Scott reports that 小蝦 / OpenClaw does not respond in Telegram, especially if it has happened repeatedly.

## Durable lesson

Repeated Telegram silence is often not Scott's Telegram token/model setup. In the observed case:

- `openclaw gateway status` showed `Runtime: stopped` and `connect ECONNREFUSED 127.0.0.1:18789`.
- `openclaw channels status --probe` fell back to config-only status while the gateway was unreachable.
- After `openclaw gateway start`, gateway connectivity became `ok`, Telegram showed `running, connected, mode:polling, works`, and OpenClaw agent/model liveness succeeded.
- Logs also showed Telegram transport/polling instability after restart: `Polling stall detected`, repeated `telegram sendChatAction failed`, `telegram sendMessage failed`, and `telegram final reply failed`.

Interpretation: distinguish configuration errors from runtime liveness/transport failures. If token, OAuth, model, and channel config are healthy but gateway is stopped or Telegram polling stalls, treat it as OpenClaw runtime/transport stability plus insufficient watchdog/keepalive — not user misuse.

## Investigation recipe

Run from Windows context, or from WSL via `cmd.exe` with a Windows cwd:

```bash
cmd.exe /c "cd /d C:\\Users\\chien && openclaw gateway status"
cmd.exe /c "cd /d C:\\Users\\chien && openclaw channels status --probe"
cmd.exe /c "cd /d C:\\Users\\chien && openclaw models status"
powershell.exe -NoProfile -Command "schtasks /Query /TN 'OpenClaw Gateway' /V /FO LIST"
```

If gateway is stopped/unreachable:

```bash
cmd.exe /c "cd /d C:\\Users\\chien && openclaw gateway start"
sleep 15
cmd.exe /c "cd /d C:\\Users\\chien && openclaw gateway status"
cmd.exe /c "cd /d C:\\Users\\chien && openclaw channels status --probe"
```

Verify model/agent liveness with a fresh bounded local session:

```bash
cmd.exe /c "cd /d C:\\Users\\chien && openclaw agent --local --agent main --session-id hermes-liveness-YYYYMMDD --message \"請只用繁體中文回覆一句：小蝦目前模型與本地代理可用。\" --json --timeout 180"
```

For host-side Telegram delivery verification, use Python `subprocess.run([...])` rather than shell-interpolating long Chinese text. The current CLI syntax uses `-m/--message` and `-t/--target`:

```python
import subprocess
subprocess.run([
    "cmd.exe", "/c", "openclaw", "message", "send",
    "--channel", "telegram", "--target", "7292751008",
    "--message", "小馬檢查：小蝦 Gateway 已重新啟動，這是 Telegram 出站測試訊息。",
    "--json",
], cwd="/mnt/c/Users/chien", text=True, capture_output=True, timeout=120)
```

## Log patterns to search

Primary gateway/channel symptoms:

- `Runtime: stopped`
- `ECONNREFUSED 127.0.0.1:18789`
- `Gateway not reachable`
- `Polling stall detected`
- `telegram sendChatAction failed`
- `telegram sendMessage failed`
- `telegram final reply failed`

Known non-primary warning:

- `failed to create plugin skill symlink ... browser-automation ... EPERM`

The symlink warning may affect browser-plugin behavior, but do not confuse it with Telegram being completely silent unless logs also show gateway/channel failure.

## Recommended durable fix

The existing Windows Scheduled Task starts OpenClaw at logon, but it is not necessarily a robust watchdog if the gateway exits or the Telegram transport wedges later. If repeated silence continues, implement a small watchdog that periodically checks gateway/channel health and restarts OpenClaw only when probes fail.

Watchdog policy:

1. Probe gateway status.
2. Probe Telegram channel status.
3. Restart only if gateway unreachable/stopped or Telegram `works` is absent for repeated checks.
4. Wait 10–20 seconds after restart before re-probing.
5. Notify Scott with evidence path/status when a restart happens.

Do not immediately edit OpenClaw core/vendor JS or provider config for this symptom. Prefer watchdog/monitoring first, then escalate if failures persist while the gateway remains running.

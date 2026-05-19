# OpenClaw Claw Chain exposure check (2026-05-19)

## Trigger

Scott asked whether the iThome/Cyera "Claw Chain" vulnerabilities affect 小蝦/OpenClaw.

## External facts checked

Cyera/TNW summaries described four chainable vulnerabilities affecting OpenClaw versions before the late-April 2026 patch window:

- `CVE-2026-44112` — TOCTOU filesystem write escape, CVSS 9.6, persistence/backdoor/config modification risk.
- `CVE-2026-44113` — TOCTOU filesystem read escape, sensitive file read risk.
- `CVE-2026-44115` — unquoted heredoc/env-var disclosure / allowlist bypass.
- `CVE-2026-44118` — MCP loopback privilege escalation via spoofable `senderIsOwner`-style ownership flag.

Published guidance: update to a patched release (`2026.4.22` / April 23 2026 patch window or later), keep instances off the public Internet, rotate secrets if exposure is suspected, audit shell/plugin logs, and reduce plugin/sandbox privileges.

## Local check pattern

Run from Windows context:

```cmd
openclaw --version
openclaw gateway status
openclaw channels status --probe
openclaw plugins list
netstat -ano | findstr 18789
npm view openclaw version
```

For Scott's MINIPC on 2026-05-19:

- Installed: `OpenClaw 2026.5.7 (eeef486)`.
- npm latest observed: `2026.5.18`.
- Gateway: `bind=loopback (127.0.0.1), port=18789`, connectivity probe `ok`.
- `netstat`: listener only on `127.0.0.1:18789`, not `0.0.0.0`.
- `OpenShell Sandbox`: `disabled` in `openclaw plugins list`.
- Telegram channel probe: polling/works.

## Assessment language to reuse

- Do **not** panic if installed version is newer than the April 2026 patch window, gateway is loopback-only, and OpenShell Sandbox is disabled.
- State clearly that this is **not zero risk**: remaining value of update is defense-in-depth, reliability, and later security hardening.
- Recommend a later safe update to the latest version using backup + rollback + restart + verification.

## Avoid

- Do not claim internet-exposed risk when gateway is confirmed loopback-only.
- Do not claim OpenShell-specific exploitability when the OpenShell Sandbox plugin is confirmed disabled.
- Do not paste tokens/config secrets while checking OpenClaw config; extract only version, bind address, plugin status, and redacted safety-relevant fields.

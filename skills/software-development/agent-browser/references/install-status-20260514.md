# Agent Browser Hermes install status (2026-05-14)

## Request

Scott asked Hermes/小馬 to also install the Agent Browser skill for Hermes itself after installing it for OpenClaw/小蝦.

## Install

- Scope: WSL user-scope install for Hermes.
- Command: `npm install -g --prefix "$HOME/.local" agent-browser@0.27.0`.
- Executable: `/home/chien/.local/bin/agent-browser`.
- Version: `agent-browser 0.27.0`.
- Existing project-local copy before install: `/home/chien/.hermes/hermes-agent/node_modules/.bin/agent-browser` at `0.26.0`.
- Reason for user-scope install: avoid modifying Hermes core/package files while ensuring PATH resolves to the current `0.27.0` CLI.

## Verification

- `command -v agent-browser` resolves to `/home/chien/.local/bin/agent-browser`.
- `agent-browser --version` returns `agent-browser 0.27.0`.
- `agent-browser doctor --quick --json` returned `success=true`, no fails/warns, Chrome for Testing detected.
- `agent-browser doctor --json` launch test passed.
- Smoke test:
  - opened `https://example.com` in session `hermes-self-install-test`;
  - waited for load;
  - `snapshot -i --json` returned refs `e1` heading and `e2` link;
  - closed browser;
  - `ps` check found no leftover `agent-browser`/Chrome process from the test.

## Rollback

```bash
npm uninstall -g --prefix "$HOME/.local" agent-browser
hash -r
command -v agent-browser
```

After uninstalling the user-scope package, `command -v agent-browser` may still find Hermes' project-local copy under `/home/chien/.hermes/hermes-agent/node_modules/.bin/agent-browser` when the current directory is the Hermes source tree.

Optional cleanup, only after confirming no needed state remains:

```bash
rm -rf "$HOME/.agent-browser"
```

`~/.agent-browser` may contain browser/session/auth metadata after use. Keep it local/private and never upload raw contents.

## Safety policy

Use the local Hermes `agent-browser` skill. Do not save cookies/auth state or attach Scott's real browser profile without explicit approval. Confirm before side-effectful browser actions such as login, upload/download, posting, account changes, destructive form submission, or checkout/payment.

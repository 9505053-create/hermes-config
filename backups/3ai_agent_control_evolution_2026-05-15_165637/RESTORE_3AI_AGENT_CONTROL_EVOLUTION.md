# Restore / Recovery SOP — 3AI Agent Control Evolution

Backup label: `2026-05-15_165637_3AI_AGENT_CONTROL_EVOLUTION_v0.13.0`

## Restore intent

Use this backup when Hermes loses the recent 3AI control workflow, PR release workflow, or EXE packaging preference.

## Manual restore steps

1. Inspect `notes/3AI_AGENT_CONTROL_EVOLUTION_NOTE.md`.
2. Restore needed skills from `skills/` into `~/.hermes/skills/`, preserving folder names.
3. Never restore `.env`, OAuth tokens, or raw auth files from this package; this package only contains sanitized placeholders.
4. Reload skills or start a new Hermes session.
5. Verify by loading:
   - `3ai-commander`
   - `minicalc-pr-release-flow`
   - `windows-exe-packaging`

## Critical policies to preserve

- Claude cooldown <= 2h: wait/retry.
- Claude cooldown > 2h/day/week: reroute to Codex GPT-5.5.
- EXE outputs: `C:\Users\chien\_3AI_WorkSpace\temp_EXE`.
- No main merge without Scott approval unless Scott explicitly says to merge.

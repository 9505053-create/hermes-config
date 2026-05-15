# 3AI Agent Control Evolution Backup

Created: 2026-05-15 16:57:04 
Hermes: v0.13.0
Label: `2026-05-15_165637_3AI_AGENT_CONTROL_EVOLUTION_v0.13.0`

## Why this backup exists

Scott assessed the current Hermes state as good and requested a durable backup of the recent PR2→PR5 workflow and 3AI agent-control improvements.

## Major learned principles captured

1. **Milestone precision** — distinguish planning complete, implementation complete, review complete, merged-to-main, and packaged-as-EXE.
2. **3AI control maturity** — Hermes acts as commander, uses Claude/Codex/Gemini strategically, writes prompts to workspace, invokes CLIs through Windows `cmd.exe`, and verifies outputs by reading artifacts back.
3. **Claude quota policy** — Claude Opus 4.7 is valuable but quota-tight. If Claude cooldown is within 2h, wait/retry. If longer than 2h/day/week, reroute Claude task to Codex GPT-5.5 and document substitution.
4. **Codex GPT-5.5 fallback** — Scott's GPT/Codex subscription has comparatively larger capacity and is acceptable for Claude fallback in implementation/review tasks.
5. **Review package hygiene** — build review packages from `git ls-files`, not whole working trees, to avoid pytest cache/untracked artifacts.
6. **TDD release discipline** — RED/GREEN tests, docs, review packages, gates, and GitHub push at stable milestones.
7. **Tkinter smoke discipline** — in WSL, Xvfb smoke is executable GUI evidence but not human-visible Windows smoke; label honestly.
8. **EXE artifact discipline** — produced Windows executables go to `C:\Users\chien\_3AI_WorkSpace\temp_EXE` with stable alias plus versioned copy.

## Skills updated/created in this evolution

- `3ai-commander` — updated with Claude quota / Codex fallback policy.
- `minicalc-pr-release-flow` — updated with PR2→PR5 lessons.
- `windows-exe-packaging` — created for centralized EXE artifact workflow.

## Safety

This backup is sanitized: raw `.env`, OAuth tokens, auth files, client secrets, and API keys are excluded or redacted. Raw session transcripts are not included.

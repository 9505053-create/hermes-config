# Vetting Report — self-improving-agent

**Date**: 2026-05-14 12:12 CST
**Reviewer**: Hermes 小馬

## Sources inspected

- `https://github.com/peterskoett/self-improving-agent`
- `https://raw.githubusercontent.com/peterskoett/self-improving-agent/master/SKILL.md`
- Repository tree via GitHub API
- Public search results / mirrors mentioning OpenClaw skill variants

## Source maturity

- Repo: public GitHub repository `peterskoett/self-improving-agent`
- Observed popularity in search result: ~600 stars, ~90 forks
- Contents observed: `SKILL.md`, `README.md`, `assets/`, `references/`, `scripts/`, `hooks/openclaw/`
- Type: external community skill for OpenClaw / Claude-style coding agents

## Security review

External content was treated as untrusted data. No repo scripts were executed and no raw install command was run.

Observed higher-risk surfaces:

- Shell scripts under `scripts/`
- OpenClaw hook handler under `hooks/openclaw/`
- Hook setup docs recommending command hooks
- Install commands such as `clawdhub install` / manual clone

Red flags / concerns:

- Hook-based reminders can change prompt context every turn and may create token overhead.
- Post-tool hooks can read tool output; if installed carelessly they may process sensitive logs.
- External scripts are not needed for Hermes because Hermes already has `skill_manage`, memory, cron, and session tools.
- Raw skill contains platform-specific OpenClaw/Claude/Codex instructions that should not be imported verbatim into Hermes.

Positive findings:

- Core concept is instruction-level and useful: log errors, user corrections, feature requests, and promote durable lessons.
- The inspected scripts appear primarily reminder/helper oriented, not obviously exfiltrative in the sampled content.
- The skill explicitly warns not to log secrets/tokens/private keys.

## Verdict

**Verdict: WARNING / adapt-only.**

Do not install raw external repo or hooks. Adapt the idea into a local Hermes skill with manual, auditable logging and explicit promotion rules.

## Action taken

Created local Hermes skill:

```text
~/.hermes/skills/software-development/self-improving-agent/SKILL.md
```

The local version:

- Keeps the useful learning-log/promotion workflow.
- Avoids external hooks, shell scripts, plugin installation, and background monitoring.
- Uses Hermes-native `skill_manage` and memory practices.
- Adds Scott-specific red lines, secret redaction, and safe-system-update boundary.

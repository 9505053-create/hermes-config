# Hermes Configuration Backup

Self-evolving AI agent configuration backup. Contains skills, templates, and tool definitions.

**⚠️ No secrets, tokens, or chat history are stored here.**

## Contents

| Directory | Description |
|-----------|-------------|
| `skills/` | Reusable agent skills (24 skill modules) |
| `hermes-agent/` | Core agent source code |
| `SOUL.md` | Agent persona and behavioral directives |
| `reference/` | Reference materials |
| `platforms/` | Platform integration configs |

## Restore

```bash
cp -r skills/* ~/.hermes/skills/
cp -r hermes-agent/* ~/.hermes/hermes-agent/
cp SOUL.md ~/.hermes/
```

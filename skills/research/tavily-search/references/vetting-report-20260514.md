# Tavily Search Vetting and Setup Report

**Date**: 2026-05-14 12:43 CST
**Verdict**: `WARNING / adapt-only for raw external skill`; `SAFE with constraints for local Hermes skill + uv installation`

## Sources reviewed

- Official repo: `https://github.com/tavily-ai/skills`
- Official docs: `https://docs.tavily.com`
- Raw skill: `skills/tavily-search/SKILL.md`
- Installer script: `install.sh` read for review only
- Package metadata: `pyproject.toml`

## Source maturity

- License: MIT
- Repo state: not archived
- Recent update observed during review
- Package name from upstream installer/metadata: `tavily-cli`
- CLI command: `tvly`
- Python requirement: >= 3.10

## Risk findings

- Raw upstream README suggests `curl -fsSL https://cli.tavily.com/install.sh | bash`.
- Raw upstream `tavily-search` skill uses broad shell/CLI assumptions (`Bash(tvly *)`) intended for other agent ecosystems.
- Tavily requires API authentication and can consume paid credits.
- Tavily sends search/extraction queries to an external service, so private data must not be sent.

## Adopted safe approach

- Do not install upstream agent skill verbatim.
- Create local Hermes skill `tavily-search` with safety rules, fallback behavior, and bounded command examples.
- If installing CLI, use `uv tool install tavily-cli`; do not execute remote install script.
- Do not save or display API keys. Use `TAVILY_API_KEY=[REDACTED]` examples only.
- If credentials are missing, report that Tavily is installed but not authenticated and fall back to Hermes web tools.

## Verification to perform after install

```bash
command -v tvly
tvly --version
python3 - <<'PY'
import os
print('TAVILY_API_KEY_present=', bool(os.environ.get('TAVILY_API_KEY')))
PY
```

If no API key is configured, do not run paid API calls.

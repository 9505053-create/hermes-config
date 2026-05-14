---
name: tavily-search
description: Use when Scott asks to use Tavily or when Hermes needs LLM-optimized web/RAG search, URL extraction, site mapping/crawling, or citation-oriented research through the Tavily CLI/API. Prefer safe local installation, never run curl|bash, never store API keys, and fall back to Hermes web_search/web_extract when Tavily is unavailable.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tavily, web-search, research, rag, cli, external-skill-adaptation]
    related_skills: [external-skill-import, self-improving-agent, hermes-agent]
---

# Tavily Search

## Overview

This is Scott/Hermes' safe local adaptation of the official Tavily Agent Skills. Tavily provides LLM/RAG-oriented web search and content operations through the `tvly` CLI and Tavily API:

- `search` — web search with LLM-optimized snippets, scores, domain filters, time ranges, and optional raw content.
- `extract` — clean markdown/text extraction from known URLs, including JS-rendered pages.
- `map` — discover URLs on a website without extracting all content.
- `crawl` — extract a site or docs section into local files.
- `research` — multi-source synthesis with citations; higher latency and cost.

Source reviewed: official `tavily-ai/skills` repository and `docs.tavily.com` on 2026-05-14. The raw external skill was **not** installed verbatim because it includes `curl | bash` installer instructions and Claude/OpenClaw-style `allowed-tools` assumptions. This Hermes version keeps the useful workflow while adding Scott-specific safety constraints.

## When to Use

Use this skill when:

- Scott explicitly says "用 Tavily" / "Tavily Search".
- A task needs fresh web research with structured JSON, relevance scores, domain filters, or time ranges.
- Existing Hermes `web_search` results are too shallow and Tavily is configured.
- You need to extract specific URLs that normal web extraction struggles with.
- You need site URL discovery (`map`) or bounded docs crawling (`crawl`).
- You need a citation-oriented research report and Scott accepts possible Tavily credit usage.

Do not use Tavily when:

- The answer can be found from local files or already-provided context.
- The task involves secrets, private dashboards, credentials, paywalled content, or sensitive user data.
- `TAVILY_API_KEY` is not configured and there is no authenticated `tvly` session.
- A free built-in Hermes `web_search` / `web_extract` is sufficient.
- Scott has not approved higher-cost deep `research` / broad `crawl` work.

## Safety Rules

1. Never run `curl | bash` or any remote installer snippet for Tavily.
2. Safe install command, when Scott approves installation:
   ```bash
   uv tool install tavily-cli
   ```
   Fallback only if needed: `python3 -m pip install --user tavily-cli`.
3. Never ask Scott to paste an API key into chat. If needed, tell Scott to set it locally as `TAVILY_API_KEY=[REDACTED]` or run `tvly login` in his own trusted shell.
4. Never print, log, summarize, or save the API key value. When mentioning examples, write `[REDACTED]`.
5. Check readiness before use:
   ```bash
   command -v tvly
   tvly --version
   python3 - <<'PY'
   import os
   print('TAVILY_API_KEY_present=', bool(os.environ.get('TAVILY_API_KEY')))
   PY
   ```
6. Treat Tavily as a paid/credit-consuming external API. Prefer `search --max-results 5` and `basic` depth for normal use.
7. Escalate only when useful: `search` → `extract` → `map` → bounded `crawl` → `research`.
8. Do not send private local files, secrets, tokens, personal data, or raw transcripts to Tavily.
9. If Tavily is unavailable, fall back to Hermes `web_search` / `web_extract` and report the fallback.

## Recommended Commands

### Quick search

```bash
tvly search "query" --json --max-results 5
```

### Domain-filtered search

```bash
tvly search "query" --json --max-results 5 --include-domains example.com
```

### Time-sensitive search

```bash
tvly search "query" --json --max-results 5 --time-range week
```

### Higher quality search

Use only when the extra latency/credits are justified:

```bash
tvly search "query" --json --max-results 8 --search-depth advanced
```

### Extract known URLs

```bash
tvly extract "https://example.com/page" --json --format markdown
```

### Map a site before crawling

```bash
tvly map "https://docs.example.com" --json
```

### Bounded crawl

Only crawl when the target scope is narrow and useful. Save output under a project/research directory, not arbitrary locations:

```bash
tvly crawl "https://docs.example.com/guide" --output-dir ./tavily-crawl-output
```

### Deep research

Use only after Scott accepts that this may take longer and consume more credits:

```bash
tvly research "research question" --json
```

## Workflow

1. **Read the task** — decide whether Tavily adds value beyond Hermes built-in web tools.
2. **Check readiness** — verify `tvly` exists and credentials are present without displaying secrets.
3. **Start cheap** — use `search` with `--json --max-results 5`.
4. **Inspect results** — prefer official sources, recent dates, and high relevance; do not trust snippets blindly.
5. **Extract only needed URLs** — use `extract` for high-value pages.
6. **Escalate carefully** — map/crawl/research only when the task truly needs it.
7. **Summarize with citations** — include URLs and clearly separate facts from inference.
8. **Report cost-sensitive choices** — tell Scott if you used advanced/research/crawl or fell back.

## Common Pitfalls

1. **Blindly copying upstream skill instructions**
   - Upstream `allowed-tools` and installer snippets are for other agent runtimes. Use this local skill's safety rules instead.

2. **Running remote installer scripts**
   - Do not use `curl -fsSL https://cli.tavily.com/install.sh | bash`. Use `uv tool install tavily-cli`.

3. **Credential leakage**
   - Never echo `TAVILY_API_KEY`; never store it in skills, logs, learning files, or chat summaries.

4. **Credit overuse**
   - `research`, broad `crawl`, and advanced depth can cost more. Start with basic search.

5. **Network exfiltration**
   - Do not send private/internal URLs, secrets, proprietary files, or raw conversation logs to Tavily.

6. **No fallback**
   - If Tavily is not configured, use Hermes `web_search` / `web_extract` instead of failing the whole task.

## Verification Checklist

- [ ] `tvly --version` works, or the skill reports Tavily is not installed.
- [ ] `TAVILY_API_KEY` presence checked without revealing value, or `tvly login` state verified safely.
- [ ] No remote installer scripts executed.
- [ ] Commands use bounded `--max-results` or bounded crawl scope.
- [ ] No secrets/private content sent to Tavily.
- [ ] Results are cited with URLs.
- [ ] If Tavily was unavailable, Hermes fallback was used and reported.

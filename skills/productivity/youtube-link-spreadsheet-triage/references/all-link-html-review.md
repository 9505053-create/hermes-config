# All-Link HTML Review Variant

Session pattern from Scott's LINE Excel link review.

## When to use

Use when Scott asks for a report over **all links** in a spreadsheet, not just one filtered topic. The goal is a human-readable triage dashboard: what each link appears to cover, whether it helps Scott's Hermes/3AI/Obsidian workflow, and what to do next.

## Data shape observed

Typical columns:

- `Scott 評論`
- `Scott 評價`
- `首次日期`
- `類型`
- `網站名稱`
- `標題/主旨`
- `主分類`
- `次分類`
- `原始網址`

Always preserve the original Excel row number so Scott can trace back.

## Recommended pipeline

1. Extract rows with `原始網址` to `01_all_links_raw.json/csv`.
2. Deduplicate by YouTube video id when possible, otherwise URL, but still keep original row numbers.
3. Enrich:
   - YouTube: `yt-dlp --skip-download --dump-json --no-playlist <url>`.
   - Web pages: fetch HTTP status, `<title>`, meta description, OG description.
4. Try transcripts only as best-effort. If the transcript API is blocked or all videos fail, continue with a metadata-only first pass and label confidence.
5. Generate `05_all_links_analysis.json` with per-row fields:
   - `content_highlights`
   - `hermes_comment`
   - `workflow_help`: `🔴高`, `🟡中`, `🟢低`
   - `workflow_reason`
   - `suggested_action`: `優先研究`, `納入待辦`, `收藏備查`, `延後`, `忽略`
   - `confidence`: `高`, `中`, `低`
   - `tags`
6. Generate `source.md` and a self-contained HTML report.
7. Verify:
   - HTML parser can read file.
   - Row count in HTML matches source row count.
   - Browser console has no JS errors.
   - Test at least one real UI filter click, not only direct DOM `.click()`. Record the visible-row count after clicking `🟢低` / `🔴高`; if DOM works but browser/UI click does not, report the interaction as inconclusive and fix the controls before delivery.

## Rating rubric

`🔴高` directly improves Scott's operational workflow and should remain a true top tier, not most of the sheet:

- Hermes/3AI, Claude Code, Codex, Gemini CLI, Antigravity
- OpenClaw / browser automation / computer-use agents
- Obsidian, NotebookLM, knowledge base, AI memory, RAG
- MCP, n8n, API/CLI integration, Git/GitHub, Docker/local deployment
- AI coding, agent skills, automation workflows, security/ops

Calibrate strict all-link runs so `🔴高` is roughly the high-signal subset. If it exceeds about 35–45% of a broad spreadsheet, assume the scoring is too loose and rerun with stricter thresholds. In Scott's LINE Excel review, a corrected strict v2 reduced `🔴高` from 242/327 to 103/327 by requiring multiple core workflow signals.

`🟡中` is useful background/tool radar but not immediately workflow-changing:

- General ChatGPT/Gemini/Claude tips
- Image generation prompts
- Excel/productivity AI
- General learning tools or device/app tips

`🟢低` is weakly related to Hermes/3AI workflow:

- Entertainment/anime/gaming videos
- Lifestyle/shopping/car/device-only content
- Cosmetic UI tweaks unless Scott explicitly asks for them

## Evidence and confidence rubric

Confidence measures **source depth**, not how interesting the title sounds:

- `高`: transcript or substantial page content was actually available and used.
- `中`: metadata-only, e.g. title + page/YouTube description.
- `低`: link bad, metadata failed, or title-only.

If YouTube transcripts are unavailable for most rows, avoid `高` confidence. Label the report as a metadata-based triage artifact and reserve deep conclusions for a second pass.

## Pitfalls

- Do not claim deep video understanding when only metadata was available. Mark confidence honestly.
- Do not let the broad category `AI技術` make everything `🔴高`; require a workflow-relevant signal.
- Subagents can time out on 300+ row JSON batches. Use deterministic first-pass classification, then deep-analyze only priority rows. If using subagents, do a 10-row canary first and cap per-row enrichment batches at about 20–30 rows or ≤40KB compact input.
- YouTube transcript failures are often environmental or rate-limit related. Capture `transcript_status`, continue, and avoid expensive audio transcription unless Scott explicitly requests it.
- HTML reports for hundreds of links should include sticky filters and free-text search; otherwise they are not reviewable on Telegram/desktop.

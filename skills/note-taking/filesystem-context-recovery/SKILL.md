---
name: filesystem-context-recovery
description: When session_search returns incomplete or empty results, systematically reconstruct lost context by mining local filesystem sources — session JSON/JSONL files, memory markdown files, and user-provided chat export PDFs. Cross-reference across ALL sources to distinguish hallucinated data from real conversation history. Use this as the fallback recovery path when session_search fails, before asking the user to repeat themselves.
version: 1.0.0
metadata:
  tags: [recovery, session, filesystem, grep, context, memory, pdf, disaster-recovery]
  related_skills: [supabase-memory-recovery, hermes-backup-management]
---

# Filesystem Context Recovery

When `session_search` returns nothing or incomplete results, do NOT assume no memory exists. Systematically mine the local filesystem to rebuild lost context. This is the FIRST recovery path to try (before Supabase/database recovery).

## Trigger Conditions

Use this skill when:
- The user asks "do you remember X?" and session_search returns empty
- After a crash, model swap, or session reset that destroyed working memory
- The user references past projects, tasks, or conversations you cannot recall
- The user provides a chat export PDF and asks you to repair your memory
- You need to distinguish between real past work and hallucinated claims from a faulty model

## Phase 1: Memory File Reading

Always read these first (fastest path):

```bash
/home/chien/.hermes/memories/MEMORY.md
/home/chien/.hermes/memories/USER.md
/home/chien/USER_PROFILE.md
/home/chien/.hermes/memories/RECOVERED_WORK_INDEX.md
```

RECOVERED_WORK_INDEX.md is especially valuable — it contains a deliberately maintained index of recovered work, Notion tasks, and known session references.

## Phase 2: Session File Grep

Session files live in `/home/chien/.hermes/sessions/` as `.json` and `.jsonl` files. These contain the FULL raw conversation history including user messages, assistant responses, tool calls, and system prompts.

### Key grep command template:

```bash
grep -RniE "keyword1|keyword2|keyword3" /home/chien/.hermes/sessions/ 2>/dev/null | grep -v "system_prompt|available_skills|INSERT|ON CONFLICT" | head -80
```

**Critical**: Always filter out system_prompt and available_skills lines — they're noisy and irrelevant to conversation content.

### Search strategies:
- **Project names**: "calendar", "google.book", "project_calendar", "books"
- **Task descriptions**: "交辦", "專案", "程式開發", "要做"
- **Model mentions**: "deepseek", "gemma", "openrouter", "model"
- **Error patterns**: "裝錯", "忘了", "失敗", "error"

### List all available session files:
```bash
find /home/chien/.hermes/sessions -name "*.json" -o -name "*.jsonl" | sort
```

### Target specific date ranges using filename patterns:
Session filenames contain timestamps: `session_20260430_080916_583983bf.jsonl`

## Phase 3: PDF Chat Export Extraction

When the user provides a Telegram chat export PDF:

### Install extraction tools (one-time):
```bash
sudo apt-get install -y poppler-utils
```

### Check PDF metadata:
```bash
pdfinfo "/path/to/chat.pdf"
```

### Extract specific page ranges (PDFs can be 400+ pages):
```bash
# Extract first 10 pages for survey
pdftotext -f 1 -l 10 "/path/to/chat.pdf" /tmp/chat_p1_10.txt

# Target later pages based on timeline knowledge
pdftotext -f 200 -l 260 "/path/to/chat.pdf" /tmp/chat_p200_260.txt
```

### Search extracted text:
```bash
grep -in "keyword1|keyword2" /tmp/chat_p200_260.txt
```

**Pitfall**: Large PDFs (400+ pages) will timeout if extracted all at once. Always extract in page ranges.

## Phase 4: Cross-Reference & Validation

Compare findings from ALL sources:

| Source | What it reveals |
|--------|----------------|
| MEMORY.md | Standing rules, lessons learned, environment info |
| RECOVERED_WORK_INDEX.md | Past task definitions, recovery procedures |
| Session JSONL files | Raw conversation content, user exact words |
| Chat export PDF | Telegram-side record, timestamps, media references |
| ChatGPT logs (if provided) | External AI's advice, model configuration changes |

### Hallucination Detection:
- If session files reference paths that don't exist on disk (`~/projects/calendar_optimizer/`), flag as possible hallucination
- Cross-check dates: a model claiming "2024-05-03" when the current year is 2026 is hallucinating
- If a session shows the model giving repeatedly broken `hermes` commands, it may be a wrong model version
- **Wrong-model signature**: If the model consistently invents CLI flags that don't exist (verify with `hermes --help`), uses wrong-year dates, creates plausible but fake project paths, and responds with excessive length/assumptions — suspect a model misconfiguration (e.g., V3 instead of V4 Pro). Concrete V3 hallucination patterns: (a) fake project directories like `~/projects/calendar_optimizer/` that don't exist on disk, (b) claiming \"uploaded to GitHub\" when API query shows zero commits/gists, (c) dates from wrong year (e.g., 2024-05-03 in 2026), (d) repeated broken CLI commands even after error messages.
- **Verify, don't trust**: When a model says it \"uploaded files to GitHub\" or \"backed up to cloud\", always verify by actually querying the API — faulty models will confidently claim things that never happened.
- **External AI logs as ground truth**: If the user provides ChatGPT/GPT/other AI conversation logs, treat them as an independent verification source. These logs often contain the actual model configuration (`.env` settings, model name strings) that the faulty model may have gotten wrong. Cross-check: \"What model did GPT say to use?\" vs \"What model is actually configured?\"

## Phase 5: Present Findings

Deliver a structured summary:
1. **Timeline**: Date-by-date reconstruction
2. **Project status**: What was real vs hallucinated
3. **File locations**: Where original files are (or that they're missing)
4. **Next steps**: What the user needs to provide to continue

## Common Pitfalls

1. **session_search vs grep**: session_search indexes only SOME sessions. Direct grep on `/home/chien/.hermes/sessions/` finds everything.
2. **System prompt noise**: Session JSONL files contain the full system prompt (~50KB). Always grep-filter it out.
3. **PDF size**: Telegram exports can be 400+ pages. Never try to read the whole thing at once.
4. **Model hallucination**: A faulty model (e.g., V3) may have written plausible-sounding but entirely fake session content. Cross-reference all claims against actual filesystem state.
5. **Cache directories**: `/home/chien/.hermes/cache/documents/` and `/home/chien/.hermes/image_cache/` may be empty — caches get cleaned between sessions.

## Verification

After recovery:
- [ ] All 4 memory files read
- [ ] Session directory enumerated and searched
- [ ] PDF extracted and searched (if provided)
- [ ] Cross-reference table produced
- [ ] Hallucinated data flagged
- [ ] User asked to provide missing original files (ZIPs, source code)

## Phase 6: Post-Recovery Backup to External Brain

After successful memory reconstruction, immediately persist findings:

1. Write a `RECOVERY_LOG_YYYYMMDD.md` to `/home/chien/.hermes/memories/` documenting the full recovery timeline
2. Backup key findings to Supabase `hermes_knowledge` table (module='RECOVERY'):
```bash
docker exec -u postgres supabase-db psql -d postgres -c "
INSERT INTO hermes_knowledge (module, title, content) VALUES
('RECOVERY', 'RECOVERY_LOG_YYYYMMDD', '<summary>'),
('RECOVERY', 'ACTIVE_PROJECTS_YYYYMMDD', '<project list>')
ON CONFLICT (title) DO UPDATE SET content = EXCLUDED.content, updated_at = now();
"
```
3. Verify Supabase Docker containers are running before attempting writes

## Phase 7: Service Credential Re-Verification

After recovery, check all previously-connected external services:

```bash
# GitHub
cat ~/.git-credentials 2>/dev/null          # check token exists
git config --global --list 2>/dev/null      # check git config
gh auth status 2>/dev/null || echo "gh CLI not installed"

# Google Drive
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check 2>/dev/null
```

Present a clear status table: ✅ Authenticated / ❌ Needs re-auth / ⚠️ CLI not installed

Report clearly: if a previous (possibly faulty) model claimed to have uploaded files to GitHub/Gist, verify by actually querying the API — don't trust the claim.

## Related Skills

- `supabase-memory-recovery`: Database-level recovery (complementary path)
- `hermes-backup-management`: Backup procedures (pre-disaster)

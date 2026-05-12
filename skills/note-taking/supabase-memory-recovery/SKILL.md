---
name: supabase-memory-recovery
description: Recover and index the Hermes external brain from a local Supabase/PostgreSQL backup. Covers container discovery, schema survey, data export, local memory comparison, classification, merge planning, and conservative file operations — all read-only-first with strict safety constraints.
version: 1.0.0
metadata:
  tags: [supabase, postgresql, memory, recovery, backup, merge, docker]
  related_skills: [hermes-agent]
---

# Supabase Memory Recovery

When the Hermes agent needs to reconnect to a previously-established local PostgreSQL/Supabase external brain — surveying existing backup tables, safely exporting data, comparing against current local memory, and proposing a conservative merge plan with strict read-only constraints.

Use this skill when:
- The agent has lost context and needs to recover from a Supabase/PostgreSQL backup
- The user asks to "check Supabase for backup data" or "restore from Supabase"
- Performing a post-crash memory audit against a known database snapshot
- You need to merge database-sourced memory into local markdown memory files without overwriting

---

## Phase 1: Docker Container Discovery

```bash
docker ps -a --format '{{.Names}} | {{.Status}} | {{.Image}}' | grep -iE 'supabase|postgres|kong|studio|pooler|gotrue'
```

Find the compose project location:
```bash
docker inspect supabase-db --format '{{index .Config.Labels "com.docker.compose.project.working_dir"}}'
```

If on WSL, translate Windows paths: `C:\docker\supabase` → `/mnt/c/docker/supabase/`

---

## Phase 2: PostgreSQL Schema & Table Survey

Connect directly (no password needed for `docker exec -u postgres`):
```bash
docker exec -u postgres supabase-db psql -d postgres -c "SELECT datname FROM pg_database WHERE datistemplate = false;"
```

List all user schemas and tables:
```sql
SELECT schemaname, tablename FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename;
```

Search for backup-related keywords in table names (`hermes`, `brain`, `memory`, `notion`, `skill`, `lesson`, `archive`, `backup`). These are the candidate tables.

For each candidate table, inspect structure:
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = '<table>'
ORDER BY ordinal_position;
```

Get row counts and date ranges:
```sql
SELECT count(*), min(updated_at), max(updated_at) FROM public.<table>;
```

**Key tables to look for** (from the 2026-04-28 snapshot reference):
- `public.hermes_knowledge` — main knowledge base (id, module, title, content, tags, updated_at)
- `public.hermes_debates` — 3AI debate archive (id, title, trigger, process, synthesis, created_at)
- `public.hermes_todos` — task tracking (id, task, status, priority, created_at, updated_at)

---

## Phase 3: Data Export

### Create staging directory
```bash
STAGING="/home/chien/hermes_supabase_restore_staging_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$STAGING"
```

### Export as JSON (use execute_code for multi-query pipelines)
Use `docker exec -u postgres supabase-db psql -d postgres -t -A -F '|'` with pipe delimiter for clean parsing. Export all rows from each candidate table.

### Generate Markdown summaries
For each table, create categorized summaries:
- `supabase_skill_inventory.md` — skill definitions by module
- `supabase_lessons.md` — lessons learned entries
- `supabase_debates.md` — debate archives
- `supabase_todos.md` — task tracking table
- `supabase_knowledge_summary.md` — full module-by-module breakdown

---

## Phase 4: Classification

For each entry from Supabase, classify into one of:

| Class | Criteria | Action |
|-------|----------|--------|
| SKIP — skill definitions | module is a skill category name (mlops, creative, etc.) | Don't merge; skills are runtime-loaded |
| SKIP — empty templates | content < 150 chars, structural description only | No value; local version is superior |
| SKIP — local equivalent exists | same event/lesson already in MEMORY.md locally | Don't overwrite; local is more current |
| SUGGEST_SAVE — real content | has substance, no local equivalent | Save as standalone reference file |
| SUGGEST_TRACK — pending task | status = pending in hermes_todos | Check if still unresolved |
| HISTORICAL — completed task | status = completed | Archive only; don't merge |

**Common pitfalls:**
- The COGNITION module is usually an empty template (not real user profile data)
- Skill definitions (65+ entries) belong in the agent skill system, not in memory markdown files
- A LESSONS entry may cover the same event as MEMORY.md's Stability Lesson — check for overlap
- Tags column is often NULL — classification was never populated

---

## Phase 5: Local Memory Comparison

Read current local memory files:
```
/home/chien/.hermes/memories/MEMORY.md
/home/chien/.hermes/memories/USER.md
/home/chien/USER_PROFILE.md
/home/chien/.hermes/memories/RECOVERED_WORK_INDEX.md
```

For each Supabase entry, determine: does local already have this? Is Supabase more detailed? Is it an empty template?

---

## Phase 6: Generate MERGE_PLAN.md

Create a merge plan in the staging directory with:
1. Items NOT recommended for merge (with reasons)
2. Suggested additions to MEMORY.md
3. Suggested additions to RECOVERED_WORK_INDEX.md
4. Suggested standalone files
5. Content previews for user review
6. Summary table with counts

**Do NOT auto-merge.** The merge plan is a recommendation; the user reviews and approves before any writes.

---

## Phase 7: Conservative Merge Execution

### Safety rules (NON-NEGOTIABLE):
1. **Backup first**: cp all 4 memory files to a timestamped backup directory with MD5 checksums
2. **No overwrites**: Only APPEND to existing files; create new files for new content
3. **No empty templates**: Never write template/placeholder content from Supabase into local memory
4. **No old-over-new**: If local has a more current version of the same event, skip Supabase
5. **No secrets**: Mask all API keys, tokens, passwords in any written content
6. **No database writes**: SELECT only — no INSERT/UPDATE/DELETE/DROP/ALTER on Supabase

### Backup command:
```bash
BACKUP_DIR="/home/chien/hermes_memory_before_supabase_merge_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp /home/chien/.hermes/memories/MEMORY.md "$BACKUP_DIR/"
cp /home/chien/.hermes/memories/USER.md "$BACKUP_DIR/"
cp /home/chien/USER_PROFILE.md "$BACKUP_DIR/"
cp /home/chien/.hermes/memories/RECOVERED_WORK_INDEX.md "$BACKUP_DIR/"
md5sum "$BACKUP_DIR"/*.md
```

### What to create:
1. **SUPABASE_EXTERNAL_BRAIN_INDEX.md** — new file in `.hermes/memories/` documenting all Supabase tables, contents, connection info, and recovery procedure
2. **Cross-reference in RECOVERED_WORK_INDEX.md** — append a short section pointing to the new index
3. **Standalone debate reference** — save real debate content to `.hermes/reference/`

### What NOT to do:
- Do NOT modify MEMORY.md, USER.md, or USER_PROFILE.md
- Do NOT write empty COGNITION/TODO/DEBATE templates from Supabase
- Do NOT INSERT new rows into Supabase without user approving the SQL preview first

---

## User-Requested Todo / Backlog Writes

Use this subsection when Scott explicitly asks to write a durable todo/backlog item to local disk and Supabase. This is different from recovery/merge: the user has requested a specific new record, so INSERT/UPDATE is allowed after a quick schema check and with conservative idempotency.

Workflow:

1. Add or update the active session todo with the built-in todo tool so the current session state reflects the task.
2. Confirm Supabase is available:
   ```bash
   docker ps -a --format '{{.Names}} | {{.Status}} | {{.Image}}' | grep -iE 'supabase|postgres'
   ```
3. Inspect target schemas before writing:
   ```bash
   docker exec -u postgres supabase-db psql -d postgres -X -A -F '|' -c "SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name IN ('hermes_todos','hermes_knowledge') ORDER BY table_name, ordinal_position;"
   ```
4. Write the local disk log first, usually by appending to the relevant file under `/home/chien/.hermes/memories/`. Include the exact task, status, priority, candidate list, and Supabase target tables.
5. Write Supabase in a transaction. If the table lacks a UNIQUE constraint on the natural key, do not use `ON CONFLICT`; use `UPDATE ... WHERE ...` followed by `INSERT ... SELECT ... WHERE NOT EXISTS (...)`.
6. Verify by reading back both the local file and the Supabase rows.
7. Mark the session todo complete.

Pitfalls:

- `hermes_todos.task` and `hermes_knowledge.title` may not have UNIQUE constraints. Check constraints before choosing an upsert strategy.
- Timestamps from PostgreSQL may display in UTC even when local `date` displays CST; this is normal, but report clearly.
- Keep Supabase writes concise; store detailed operational history in local markdown and a compact durable summary in `hermes_knowledge`.

See `references/todo-backlog-supabase-write-20260512.md` for the 2026-05-12 example pattern.

## Verification Checklist

After merge or user-requested write:
- [ ] Backup directory exists with 4 md5-verified files when modifying core memory files
- [ ] Local markdown log was read back after write
- [ ] Supabase schema/constraints were checked before INSERT/UPDATE
- [ ] Supabase rows were read back after write
- [ ] SUPABASE_EXTERNAL_BRAIN_INDEX.md created with table inventory when doing recovery
- [ ] RECOVERED_WORK_INDEX.md has cross-reference appended (not overwritten) when doing recovery
- [ ] MEMORY.md unchanged unless explicitly approved
- [ ] USER_PROFILE.md unchanged unless explicitly approved
- [ ] No secrets exposed in any output
- [ ] Staging directory exists with all exports when doing recovery
- [ ] User has reviewed and approved MERGE_PLAN.md before recovery merge

---

## Reference: Known Tables (2026-04-28 Snapshot)

| Table | Rows | Content |
|-------|------|---------|
| hermes_knowledge | 69 | 65 skill defs + 4 special modules (LESSONS/DEBATE/COGNITION/TODO) |
| hermes_debates | 1 | Real 3-round debate about Notion-to-Supabase migration |
| hermes_todos | 6 | 5 completed + 1 pending task |

Known issues:
- `tags` column in hermes_knowledge is entirely NULL for all rows
- COGNITION module (id=67) is an empty 120-char template, not real user data
- All entries dated 2026-04-28 (single-day snapshot)

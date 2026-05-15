# 2026-05-15 — 3AI Agent Control Evolution Backup Pattern

Use this as a concrete example when Scott says the agent state is good and asks to back up a workflow/skill evolution to local disk, Google Drive, Supabase, and GitHub.

## Trigger

Scott said the current Hermes state was good and requested backup of the recent MiniCalc PR2→PR5 workflow, 3AI agent-control learning, and process history.

## Durable lessons captured

- Treat a mature workflow evolution as a backup-worthy state, even if no Hermes core code changed.
- Capture both skill files and a concise narrative note explaining *why* the backup exists.
- Use sanitized backups only: no raw `.env`, OAuth tokens, raw `auth.json`, client secrets, API keys, or raw session transcripts.
- Run a pattern-based secret scan and report it.
- Verify every destination by reading/listing it back.

## Example artifacts

Local backup directory:

```text
C:\Users\chien\_3AI_WorkSpace\HermesBackup\2026-05-15_165637_3AI_AGENT_CONTROL_EVOLUTION_v0.13.0
```

Archive:

```text
2026-05-15_165637_3AI_AGENT_CONTROL_EVOLUTION_v0.13.0.tar.gz
sha256=d55196ac1b2f8318c09cce986163930bfdcece44b3a02559d5b46808d08f6f98
```

Google Drive verification:

```text
folder_id=1y8HSs6wwA9DutiqRykVkYSSquQtZiRGI
files=5
```

Supabase verification:

```sql
SELECT id,module,title,updated_at,tags
FROM public.hermes_knowledge
WHERE module='backup'
  AND title='3AI Agent Control Evolution Backup 2026-05-15';
```

GitHub verification:

```text
repo=~/projects/hermes-config
commit=8997751 Backup 3AI agent control evolution 2026-05-15
path=backups/3ai_agent_control_evolution_2026-05-15_165637/
```

## Procedure refinement

1. Create a local backup folder under `C:\Users\chien\_3AI_WorkSpace\HermesBackup` with a descriptive label.
2. Copy sanitized config, memory markdown, handoffs, skills, and supporting files.
3. Add a narrative note under `notes/` and a restore SOP under `restore_sop/`.
4. Generate `BACKUP_MANIFEST.json` and `BACKUP_MANIFEST.txt` with checksums.
5. Tar/gzip the folder and compute archive SHA256.
6. Secret-scan the package and save `manifests/SECRET_SCAN.json`.
7. Upload archive + note + manifest + SOP + secret scan to a new Google Drive folder.
8. Write a compact Supabase `hermes_knowledge` row with local path, archive SHA, Drive folder ID, and key lessons.
9. Commit the manifest/SOP/note/archive to `~/projects/hermes-config` and push.
10. Verify local archive, Drive listing, Supabase row, and GitHub remote commit before reporting success.

## Reporting style

Report four locations separately:

- Local disk: path + archive SHA256 + file count.
- Google Drive: folder ID + uploaded filenames.
- Supabase: table + id/title/tags.
- GitHub: repo path + commit hash.

Also state whether secret scan was clean.

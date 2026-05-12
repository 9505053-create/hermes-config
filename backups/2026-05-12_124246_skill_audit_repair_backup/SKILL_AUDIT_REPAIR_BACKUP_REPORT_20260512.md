# Skill Audit, Repair, and Backup Report — 2026-05-12

## Summary

- Scanned: 215 `SKILL.md` files across local installed skills and Hermes repo skills.
- Initial audit: 4 errors, 236 warnings.
- Repairs completed:
  1. Fixed invalid YAML frontmatter in `3ai-pipeline` (`trigger` / `aliases`).
  2. Split oversized `research-paper-writing` skill into short `SKILL.md` + `references/full-pipeline.md` in both local and repo skill trees.
- Post-repair audit: 0 errors, 0 warnings.
- Remaining 167 info items are expected local-vs-repo mirrors:
  - duplicate_skill_name: 87
  - exact_duplicate_content: 80

## Pre-repair Backup

`/home/chien/.hermes/backups/skill_repair_pre/20260512_124103`

## Audit Reports

- Pre-repair: `/home/chien/.hermes/memories/skill_audits/skill_audit_20260512_123816.md`
- Post-repair: `/home/chien/.hermes/memories/skill_audits/skill_audit_post_repair_20260512_124209.md`

## Local Disk Backup

- Directory: `/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/2026-05-12_124246_skill_audit_repair_backup`
- Archive: `/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/2026-05-12_124246_skill_audit_repair_backup.tar.gz`
- Archive SHA256: `72194b375855e0503cc85d7d0a6e39caa97e4191a51877e2eb6ca165465d5d13`
- File count in manifest: 1175

## GitHub Backup

- Repo: `https://github.com/9505053-create/hermes-config`
- Commit: `5fefd81 backup: skill audit repair snapshot 2026-05-12`
- Path: `backups/2026-05-12_124246_skill_audit_repair_backup/`

## Hermes Repo Local Repair Commit

- Local repo: `/home/chien/.hermes/hermes-agent`
- Commit: `96b95d729 fix: keep research paper writing skill under loader limit`
- Note: unrelated pre-existing `tinker-atropos` submodule status may still appear in Hermes repo status; it was not changed by this repair.

## Supabase Backup Record

- Table: `public.hermes_knowledge`
- Title: `Hermes Skill Audit Repair Backup 2026-05-12 12:42`
- Verified insert/update: yes

## Google Drive Backup

- Folder: `2026-05-12_124246_skill_audit_repair_backup`
- Link: https://drive.google.com/drive/folders/1mUMJ4nqXAsvtV-eCmQ6t4UXHOR52BTVA
- Uploaded:
  - `BACKUP_MANIFEST.txt`
  - `BACKUP_MANIFEST.json`
  - `ARCHIVE_SHA256.txt`
  - `skill_audit_20260512_123816.md`
  - `skill_audit_post_repair_20260512_124209.md`
  - `2026-05-12_124246_skill_audit_repair_backup.tar.gz`

## Security Notes

- Raw `.env`, OAuth tokens, auth files, client secrets, and credential files were excluded.
- `.env` files were included only as `.env.SANITIZED` with values redacted.
- Secret scan produced only variable-name false positives (e.g. `api_key = resolve_api_key(...)`), not raw credentials.

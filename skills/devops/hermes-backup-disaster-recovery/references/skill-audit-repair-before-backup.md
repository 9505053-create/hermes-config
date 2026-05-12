# Skill Audit + Repair Before Backup

Use this reference when Scott asks to review current skills, fix errors, and then back up Hermes state.

## Goal

Before preserving Hermes state to local disk, GitHub, Supabase, or Google Drive, verify that the skill library itself is healthy. A backup of a broken skill library is less useful than a repaired, validated snapshot.

## Audit Scope

Scan both trees when present:

- `~/.hermes/skills/` — user-local installed skills
- `~/.hermes/hermes-agent/skills/` — repo/source skills

For every `SKILL.md`, check:

- Frontmatter starts at byte 0 with `---`
- Closing frontmatter delimiter exists
- YAML parses to a mapping
- `name` and `description` exist
- `description` ≤ 1024 chars
- whole `SKILL.md` ≤ 100,000 chars
- obvious raw credential patterns are absent
- local support-file links are present when explicitly referenced
- duplicate skill names / exact duplicate content are classified

## Classification Rules

- `error`: invalid YAML/frontmatter, missing required fields, description too long, `SKILL.md` too large.
- `warn`: suspicious secret-like literal not clearly placeholder/example; missing explicit support file links.
- `info`: local-vs-repo mirror duplicates. Do **not** delete these automatically; they are usually expected.

## Safe Auto-Repairs

- YAML typo in frontmatter: patch only the frontmatter field.
- Oversized `SKILL.md`: preserve original full content in `references/full-pipeline.md` or equivalent, then reduce `SKILL.md` to a class-level index with a pointer to the reference.
- Placeholder secret warnings: do not redact if the value is clearly an example (`xxx`, `YOUR_`, `<token>`, `***REDACTED***`).

Always make a timestamped pre-repair backup under `~/.hermes/backups/skill_repair_pre/<timestamp>/` before changing skills.

## Verification

After repair, re-run the audit and require:

- `errors: 0`
- `warnings: 0` or only consciously accepted warnings
- remaining duplicates classified as `info` when they are local-vs-repo mirrors

Write both pre- and post-repair audit reports to:

- `~/.hermes/memories/skill_audits/`

## Backup Ordering

1. Audit skills.
2. Back up pre-repair originals.
3. Apply safe repairs.
4. Re-audit and verify.
5. Create sanitized local archive + manifest + checksums.
6. Push sanitized backup to GitHub.
7. Upsert backup summary to Supabase.
8. Upload manifest/report/archive to Google Drive when Drive OAuth has write scope.

## Security Notes

- Never include raw `.env`, OAuth tokens, auth files, client secrets, or credential files.
- Include `.env` only as `.env.SANITIZED` with values redacted.
- Run a secret scan on the backup before pushing/uploading; classify code variable names like `api_key = resolve_api_key(...)` as false positives, not credentials.

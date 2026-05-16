# Cron prompt scanner false-positive incident — 2026-05-16

## What happened

Scott asked why the Saturday weekly security email did not arrive. The three scheduled weekly jobs had all triggered, but each was blocked before the agent ran:

- Phase 1 intel job `c8b29b3f5b3f`: blocked at 2026-05-16 04:00 +08:00
- Phase 2 self-check job `7604fc2fa9ec`: blocked at 2026-05-16 06:00 +08:00
- Phase 3 report + email job `51a220e78c85`: blocked at 2026-05-16 09:00 +08:00

The output files under `~/.hermes/cron/output/<job_id>/...` said the assembled prompt matched the `prompt_injection` threat pattern. No formal `weekly-report-2026-05-16.md` was produced, so no weekly-report email was sent.

## Root cause

The weekly security skill itself contained verbatim prompt-injection example phrases. Hermes cron scans the combined text of the cron prompt and loaded skill content before running a scheduled agent. Because the security training text quoted attack phrases literally, the scanner treated the job as hostile.

## Durable fix pattern

1. Do not quote canonical prompt-injection phrases verbatim in always-loaded cron skills.
2. Reword examples semantically, especially in English phrases likely to be in scanner regexes.
3. Verify the assembled prompt with the same pattern family as `tools/cronjob_tools.py::_CRON_THREAT_PATTERNS` before rerunning or waiting for next Saturday. Prefer the packaged helper: `python ~/.hermes/skills/security/weekly-security-audit/scripts/verify_weekly_cron_scanner.py`.
4. Keep session-specific blocked output and rollback details in a report file, not in the skill body.
5. If the formal report/email already missed its window, send an incident email first, then manually produce the real Phase 1/2/3 artifacts and clearly distinguish incident notice from formal weekly report.

## Manual catch-up playbook

When Scott says the weekly email did not arrive:

1. Check whether each cron phase triggered and read the exact output stub under `~/.hermes/cron/output/<job_id>/...`.
2. If the blocker is scanner false-positive, back up `weekly-security-audit/SKILL.md` and `~/.hermes/cron/jobs.json`, patch only the offending instructional text, and record a rollback path.
3. Run `python ~/.hermes/skills/security/weekly-security-audit/scripts/verify_weekly_cron_scanner.py`; expected result is every weekly job has `hits: []`.
4. If automated rerun enters agent execution but no artifact appears, do not claim success. Manually create:
   - `~/.hermes/security/weekly-intel-YYYY-MM-DD.md`
   - `~/.hermes/security/weekly-selfcheck-YYYY-MM-DD.md`
   - `~/.hermes/security/weekly-report-YYYY-MM-DD.md`
5. Before emailing, compile-check the mail script: `python3 -m py_compile ~/.hermes/scripts/send-mail.py`.
6. Send via file redirection, not `cat ... | python`, to avoid unnecessary security warnings:
   `python3 ~/.hermes/scripts/send-mail.py -s "Hermes發送 - 🔐 每週資安體檢報告 YYYY-MM-DD（補寄）" -t "chiensct@hotmail.com" -f "Hermes Security Auditor" < ~/.hermes/security/weekly-report-YYYY-MM-DD.md`
7. Final response must state: triggered vs blocked, artifact paths, exact email `[OK]` evidence, backup path, rollback path, and whether the formal report or only an incident notice was sent.

## Verification helper

Use the packaged script rather than hand-copying a one-off snippet:

```bash
python ~/.hermes/skills/security/weekly-security-audit/scripts/verify_weekly_cron_scanner.py
```

Expected after the fix: JSON output lists the three weekly jobs and every job has `hits: []`; the process exits `0`. The helper accepts both `id` and `job_id` fields because Hermes cron metadata has used both shapes in practice. If it reports a hit, compare its pattern list with the live Hermes implementation in `tools/cronjob_tools.py::_CRON_THREAT_PATTERNS` before editing.

## Communication lesson

When Scott asks why a scheduled email did not arrive, answer in this order:

1. Did the cron trigger?
2. What was the last status and evidence path?
3. Was a report artifact produced?
4. Was the email sent? If yes, include `[OK] Email sent...`; if no, say no clearly.
5. What was changed, where is the backup, and how to rollback?

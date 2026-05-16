#!/usr/bin/env python3
"""Verify Hermes weekly security cron prompts do not trip the cron preflight scanner.

This is a lightweight, local-only approximation for the weekly-security-audit skill.
It scans each weekly security job prompt plus the always-loaded weekly-security-audit
SKILL.md for threat patterns that previously caused false-positive BLOCKED runs.
It prints JSON and exits non-zero if any hit is found.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HOME = Path.home()
SKILL_PATH = HOME / ".hermes" / "skills" / "security" / "weekly-security-audit" / "SKILL.md"
JOBS_PATH = HOME / ".hermes" / "cron" / "jobs.json"
WEEKLY_JOB_NAMES = (
    "每週資安情蒐",
    "每週自我配置檢查",
    "每週報告整合",
)

# Keep this list synchronized with the dangerous prompt families in
# tools/cronjob_tools.py::_CRON_THREAT_PATTERNS when debugging a real block.
PATTERNS = [
    ("prompt_injection", re.compile(r"ignore\s+(?:\w+\s+)*(?:previous|all|above|prior)\s+(?:\w+\s+)*instructions", re.I)),
    ("deception_hide", re.compile(r"do\s+not\s+tell\s+the\s+user", re.I)),
    ("sys_prompt_override", re.compile(r"system\s+prompt\s+override", re.I)),
    ("disregard_rules", re.compile(r"disregard\s+(your|all|any)\s+(instructions|rules|guidelines)", re.I)),
    ("read_secrets", re.compile(r"cat\s+[^\n]*(\.env|credentials|\.netrc|\.pgpass)", re.I)),
    ("ssh_backdoor", re.compile(r"authorized_keys", re.I)),
    ("sudoers_mod", re.compile(r"/etc/sudoers|visudo", re.I)),
    ("destructive_root_rm", re.compile(r"rm\s+-rf\s+/", re.I)),
]


def job_id(job: dict) -> str:
    return str(job.get("id") or job.get("job_id") or job.get("uuid") or "<unknown>")


def job_prompt(job: dict) -> str:
    prompt = job.get("prompt")
    if isinstance(prompt, str):
        return prompt
    messages = job.get("messages")
    if isinstance(messages, list):
        return "\n".join(str(m.get("content", "")) if isinstance(m, dict) else str(m) for m in messages)
    return ""


def main() -> int:
    if not SKILL_PATH.exists():
        raise SystemExit(f"missing skill: {SKILL_PATH}")
    if not JOBS_PATH.exists():
        raise SystemExit(f"missing jobs: {JOBS_PATH}")

    skill_text = SKILL_PATH.read_text(encoding="utf-8", errors="replace")
    data = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    jobs = data.get("jobs", data if isinstance(data, list) else [])

    results = []
    for job in jobs:
        name = str(job.get("name", ""))
        if not any(marker in name for marker in WEEKLY_JOB_NAMES):
            continue
        assembled = job_prompt(job) + "\n" + skill_text
        hits = []
        for label, pattern in PATTERNS:
            match = pattern.search(assembled)
            if match:
                hits.append({"pattern": label, "match": match.group(0)[:120]})
        results.append({"id": job_id(job), "name": name, "hits": hits})

    print(json.dumps({"weekly_jobs": results}, ensure_ascii=False, indent=2))
    return 1 if any(item["hits"] for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())

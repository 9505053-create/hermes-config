# Hermes Self-Upgrade Procedure (v0.11→v0.13 Lessons)

## Pre-Upgrade Checklist
1. Run full 4-location backup (local + GDrive + Supabase + GitHub)
2. Email restore SOP to Scott
3. Verify Google Drive OAuth has `drive` scope (not `drive.readonly`)
4. Check git status is clean in `~/.hermes/hermes-agent/`

## Upgrade Execution
```bash
cd /home/chien/.hermes/hermes-agent
hermes update
```

**Expect**: agent will die mid-execution (gateway restart). Scott must verify recovery manually.

## Post-Upgrade Merge Conflict Resolution

`hermes update` flow:
1. `git stash` — saves local changes
2. `git pull` — gets upstream
3. `git stash apply` — re-applies local changes
4. **Conflicts happen** in files where both sides modified

### Resolution Pattern: Keep Both
When upstream added new tools AND stash has 3AI tools:
```python
<<<<<<< Updated upstream
    # Kanban tools (new upstream)
    "kanban_show", "kanban_list", ...
=======
    # 3AI Tools (Scott's custom)
    "gemini_cli", "codex", "claude_code",
>>>>>>> Stashed changes
```
**Resolution**: Remove conflict markers, keep ALL entries:
```python
    # Kanban tools (new upstream)
    "kanban_show", "kanban_list", ...
    # 3AI Tools (Scott's custom)
    "gemini_cli", "codex", "claude_code",
```

### Conflict Files to Expect
- `toolsets.py` — new upstream tools vs 3AI tools
- `tools/memory_tool.py` — upstream Windows compat vs pii_redactor import
- `scripts/whatsapp-bridge/package-lock.json` — auto-generated, take theirs

### Post-Resolution Verification
```bash
python3 -m py_compile toolsets.py
python3 -m py_compile tools/memory_tool.py
python3 -m py_compile tools/browser_supervisor.py
python3 -m py_compile tools/pii_redactor.py
```

## Post-Upgrade Bug Scan
Check gateway logs for new errors:
```bash
journalctl -u hermes-gateway --since "5 min ago" --no-pager | grep -i "error\|warning\|exception"
```

Common post-upgrade issues:
1. Dead code from merge (SyntaxError on parse)
2. Missing imports (upstream refactored, stash has old imports)
3. Duplicate imports (both sides added same import)
4. Regex raw string quote escaping

## Files Committed After Upgrade
Run `git add -A && git commit` to preserve all local customizations on top of upstream.
The commit message should document what bugs were fixed.

## Gateway Restart
```bash
sudo /home/chien/.local/bin/hermes gateway restart --system
```
Timeout is expected (kills running agent). Verify with `systemctl is-active hermes-gateway`.

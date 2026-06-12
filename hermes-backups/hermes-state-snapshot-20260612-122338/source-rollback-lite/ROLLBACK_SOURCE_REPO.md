# Hermes source repo rollback addendum

Use this if `hermes update` breaks the source checkout or Hermes cannot start after update.

Pre-update source repo:
- Path: `/home/chien/.hermes/hermes-agent`
- Known-good HEAD: `3705625b731d4640c22fafdd077d1b509d8422d7`
- Known-good short HEAD: `3705625b7`

## Fast rollback when git repo still exists

```bash
cd /home/chien/.hermes/hermes-agent
# Save broken state first
BROKEN_TS=$(date +%Y%m%d_%H%M%S)
git status --short > "/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/broken-hermes-agent-status-$BROKEN_TS.txt" 2>&1 || true

# Return source to known-good pre-update commit
git reset --hard 3705625b731d4640c22fafdd077d1b509d8422d7

# Restore Scott's local tracked customizations if needed
PATCH="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260612-122338/source-rollback/local_tracked_changes.patch"
[ -s "$PATCH" ] && git apply "$PATCH" || true

# Restore untracked local files if needed
TAR="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260612-122338/source-rollback/untracked-files.tar.gz"
[ -s "$TAR" ] && tar xzf "$TAR" -C /home/chien/.hermes/hermes-agent || true

python3 -m compileall -q /home/chien/.hermes/hermes-agent/agent /home/chien/.hermes/hermes-agent/hermes_cli /home/chien/.hermes/hermes-agent/gateway || true
/home/chien/.local/bin/hermes --version
sudo /home/chien/.local/bin/hermes gateway restart --system
/home/chien/.local/bin/hermes gateway status
```

## If the checkout is badly damaged

```bash
cd /home/chien/.hermes
mv hermes-agent "hermes-agent.BROKEN.$(date +%Y%m%d_%H%M%S)"
git clone /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260612-122338/source-rollback/hermes-agent-before-update.bundle hermes-agent
cd hermes-agent
git reset --hard 3705625b731d4640c22fafdd077d1b509d8422d7
[ -s /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260612-122338/source-rollback/local_tracked_changes.patch ] && git apply /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260612-122338/source-rollback/local_tracked_changes.patch || true
[ -s /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260612-122338/source-rollback/untracked-files.tar.gz ] && tar xzf /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260612-122338/source-rollback/untracked-files.tar.gz -C /home/chien/.hermes/hermes-agent || true
/home/chien/.local/bin/hermes --version
sudo /home/chien/.local/bin/hermes gateway restart --system
/home/chien/.local/bin/hermes gateway status
```

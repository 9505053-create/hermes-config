---
name: linux-service-permission-inheritance
description: Use when a Linux/WSL service user and interactive user both write under the same Hermes/project directory and permission inheritance causes crashes, denied writes, or unreadable files. Covers group ownership, SGID directories, UMask, safe verification, and rollback.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [linux, wsl, permissions, systemd, gateway, stability]
    related_skills: [safe-system-update, hermes-agent, systematic-debugging]
---

# Linux Service Permission Inheritance

## Overview

Use this skill when Hermes or another service runs under one account while Scott or an interactive shell uses another account, and files become unreadable or unwritable because ownership, group inheritance, or umask differs.

This captures the 2026-04-28 lesson where a `hermes-svc` / `chien` permission mismatch under `.hermes` caused instability. The stable pattern is: shared group ownership, SGID directories, and service `UMask=0002` so new files remain group-writable.

## When to Use

Trigger this skill for errors like:

- `Permission denied` inside `~/.hermes`, gateway logs, sessions, cache, or workspace directories
- Files created by a service user cannot be edited by `chien`
- Files created by `chien` cannot be read/written by a service
- Gateway/session crashes after updates or after switching between CLI and system service
- WSL + Windows path ownership confusion

Do not apply broad permission changes blindly. Confirm the exact service user, target directory, and ownership model first.

## Discovery Workflow

### 1. Identify users and process context

```bash
whoami
id
ps -eo user,group,pid,cmd | grep -E 'hermes|python|gateway' | grep -v grep
```

For systemd services:

```bash
systemctl status <service-name> --no-pager
systemctl cat <service-name>
```

### 2. Inspect ownership and mode

```bash
namei -l ~/.hermes
stat -c '%U:%G %a %n' ~/.hermes ~/.hermes/logs ~/.hermes/sessions 2>/dev/null
find ~/.hermes -maxdepth 2 \( ! -user "$USER" -o ! -perm -g+w \) -printf '%M %u:%g %p\n' 2>/dev/null | head -50
```

### 3. Decide the shared group

Preferred pattern:

- Interactive user: `chien`
- Service user: e.g. `hermes-svc`
- Shared group: a group that contains both users, often `hermes` or the primary user group if appropriate

Check membership:

```bash
getent group <group-name>
id chien
id hermes-svc
```

## Fix Pattern

Only run after confirming the target directory and shared group.

### 1. Backup metadata first

```bash
TS=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/.hermes/backups/perm_metadata_$TS"
mkdir -p "$BACKUP_DIR"
find ~/.hermes -maxdepth 4 -printf '%m %u %g %p\n' > "$BACKUP_DIR/hermes_permissions_before.txt"
```

### 2. Set shared ownership

Example using group `hermes`:

```bash
sudo chgrp -R hermes ~/.hermes
```

If ownership is severely mixed and approved:

```bash
sudo chown -R chien:hermes ~/.hermes
```

### 3. Enable group inheritance on directories

```bash
find ~/.hermes -type d -exec chmod 2775 {} +
find ~/.hermes -type f -exec chmod g+rw {} +
```

`2` in `2775` sets SGID on directories, causing new files to inherit the directory group.

### 4. Set service umask

For systemd service override:

```bash
sudo systemctl edit <service-name>
```

Add:

```ini
[Service]
UMask=0002
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart <service-name>
```

For non-systemd launchers, set `umask 0002` before starting the service.

## Verification

### 1. Create test files from both contexts

Interactive:

```bash
touch ~/.hermes/permission_test_user
stat -c '%U:%G %a %n' ~/.hermes/permission_test_user
```

Service context, if available:

```bash
sudo -u <service-user> touch ~/.hermes/permission_test_service
stat -c '%U:%G %a %n' ~/.hermes/permission_test_service
```

Expected: both files share the intended group and are group-writable.

### 2. Check new files inherit group

```bash
stat -c '%A %U:%G %n' ~/.hermes ~/.hermes/permission_test_*
```

Look for group write (`rw-`) and directory SGID (`s` in group execute position, e.g. `drwxrwsr-x`).

### 3. Run relevant Hermes smoke test

```bash
hermes --version
hermes skills >/tmp/hermes_skills_check.txt
```

If gateway was involved, verify logs after restart.

## Rollback

If the permission change breaks access, restore ownership/modes from the metadata backup manually or reset to the prior known owner/group. At minimum, remove test files:

```bash
rm -f ~/.hermes/permission_test_user ~/.hermes/permission_test_service
```

For systemd `UMask` rollback:

```bash
sudo systemctl revert <service-name>
sudo systemctl daemon-reload
sudo systemctl restart <service-name>
```

## Common Pitfalls

1. **Using `chmod -R 777`**
   - Avoid. It hides the root cause and weakens security.

2. **Fixing existing files but not future files**
   - Without SGID directories and `UMask=0002`, the problem returns.

3. **Ignoring service user context**
   - Interactive checks can pass while gateway still fails under another user.

4. **Running recursive changes on the wrong path**
   - Confirm path before using `chown -R` or `chmod -R`.

5. **WSL `/mnt/c` semantics**
   - Windows-mounted paths may not honor Linux modes like native ext4. Prefer `~/.hermes` on the WSL filesystem for Hermes runtime state.

## Verification Checklist

- [ ] Process/service user identified
- [ ] Target directory confirmed
- [ ] Permission metadata backup created
- [ ] Shared group membership confirmed
- [ ] Directories have SGID where needed
- [ ] Service umask is `0002` or equivalent
- [ ] Files created by both users are group-readable/writable
- [ ] Hermes or gateway smoke test passes
- [ ] Rollback notes recorded

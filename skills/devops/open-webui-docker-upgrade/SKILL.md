---
name: open-webui-docker-upgrade
description: Safely check, upgrade, verify, and roll back Scott's Docker-based Open WebUI deployment on MINIPC/WSL. Use when asked to update Open WebUI or check whether it is current.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [open-webui, docker, upgrade, rollback, devops]
    related_skills: [production-resilience]
---

# Open WebUI Docker Upgrade

## When to use

Use this when Scott asks to check or upgrade Open WebUI. The observed deployment on MINIPC/WSL is Docker-based:

- Container name: `open-webui`
- Image: `ghcr.io/open-webui/open-webui:main`
- Port: `3000:8080`
- Important custom env: `OLLAMA_BASE_URL`

## Procedure

1. Discover current state and version:

```bash
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' | (head -n 1; grep -Ei 'open[-_ ]?webui|openwebui|webui' || true)
curl -fsS --max-time 10 http://127.0.0.1:3000/api/version
```

2. Check latest release:

```bash
python3 - <<'PY'
import json, urllib.request
with urllib.request.urlopen('https://api.github.com/repos/open-webui/open-webui/releases/latest', timeout=20) as r:
    d=json.load(r)
print(d.get('tag_name'), d.get('published_at'))
PY
```

3. Use a background task for `docker pull` and upgrade if the user may message during the run. Foreground terminal commands can be interrupted by new user turns.

4. Before changing containers, create a timestamped backup:

```bash
TS=$(date +%Y%m%d-%H%M%S)
BACKUP_ROOT="$HOME/.hermes/backups/open-webui-upgrade-$TS"
mkdir -p "$BACKUP_ROOT" && chmod 700 "$BACKUP_ROOT"
docker inspect open-webui > "$BACKUP_ROOT/container.inspect.before.json"
OLD_IMAGE_ID=$(docker inspect open-webui --format '{{.Image}}')
printf '%s\n' "$OLD_IMAGE_ID" > "$BACKUP_ROOT/old-image-id.txt"
docker inspect "$OLD_IMAGE_ID" > "$BACKUP_ROOT/image.inspect.before.json" || true
curl -fsS --max-time 10 http://127.0.0.1:3000/api/version > "$BACKUP_ROOT/api-version.before.json" || true
mkdir -p "$BACKUP_ROOT/backend-data"
docker cp 'open-webui:/app/backend/data/.' "$BACKUP_ROOT/backend-data/"
tar -C "$BACKUP_ROOT" -czf "$BACKUP_ROOT/backend-data.tgz" backend-data
```

5. Pull latest image:

```bash
docker pull ghcr.io/open-webui/open-webui:main
NEW_IMAGE_ID=$(docker image inspect ghcr.io/open-webui/open-webui:main --format '{{.Id}}')
```

6. Preserve only customized environment variables. Avoid printing secrets. On Scott's observed deployment, only `OLLAMA_BASE_URL` differed from image defaults.

7. Move data to a persistent named Docker volume before recreating, because the old container had no explicit mount:

```bash
docker volume create open-webui >/dev/null
# Populate from backup using a transient helper container.
docker run --rm -v open-webui:/data busybox sh -c 'rm -rf /data/* /data/.[!.]* /data/..?* 2>/dev/null || true'
docker run --rm -v open-webui:/data -v "$BACKUP_ROOT/backend-data:/backup:ro" busybox sh -c 'cd /backup && tar cf - . | tar xf - -C /data'
```

8. Rename old container instead of deleting it, then start the new one:

```bash
OLD_RENAMED="open-webui-preupgrade-$TS"
docker stop open-webui
docker rename open-webui "$OLD_RENAMED"
docker run -d \
  --name open-webui \
  --restart unless-stopped \
  -p 3000:8080 \
  --env-file "$BACKUP_ROOT/custom.env" \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

9. Write rollback script:

```bash
cat > "$BACKUP_ROOT/ROLLBACK.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
docker stop open-webui || true
docker rm open-webui || true
docker rename $OLD_RENAMED open-webui || true
docker start open-webui
EOF
chmod 700 "$BACKUP_ROOT/ROLLBACK.sh"
```

10. Verify after upgrade:

```bash
docker ps --filter 'name=^/open-webui$' --format 'name={{.Names}} image={{.Image}} status={{.Status}} ports={{.Ports}}'
curl -fsS --max-time 10 http://127.0.0.1:3000/api/version
curl -fsS --max-time 10 http://127.0.0.1:3000/api/config | python3 -c 'import sys,json; d=json.load(sys.stdin); print({"status": d.get("status"), "name": d.get("name"), "version": d.get("version")})'
```

## Known successful upgrade

On 2026-05-13, upgraded Scott's Open WebUI from `0.8.12` to `0.9.5`:

- Old image: `sha256:b8095f79a6a8ffad8f830bdacc9b5b0aef805689b31bca0b065cc2424d3cfaeb`
- New image: `sha256:74093dadc9c6aabc23987a74fd8c2fb8d995b1a5b22e83b0036fb9d6af590e8c`
- Backup dir: `/home/chien/.hermes/backups/open-webui-upgrade-20260513-013719`
- Rollback command: `bash /home/chien/.hermes/backups/open-webui-upgrade-20260513-013719/ROLLBACK.sh`

## Pitfalls

- Do not run long `docker pull` in a foreground tool call if Scott may message during the run; it can be interrupted. Use `background=true` and `notify_on_complete=true`.
- Initial `/api/version` checks may fail with `Recv failure: Connection reset by peer` while Open WebUI is booting. Retry for up to a few minutes before declaring failure.
- Wait until Docker reports `healthy`, not merely `health: starting`, before final success.
- The old container should be renamed, not deleted, until Scott confirms the new deployment is good.

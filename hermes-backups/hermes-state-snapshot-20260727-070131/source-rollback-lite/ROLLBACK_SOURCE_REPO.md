# Hermes Agent 原始碼升級前回滾指引

- 備份標籤：`hermes-state-snapshot-20260727-070131`
- 升級前版本：`Hermes Agent v0.19.0 (2026.7.20)`
- 升級前 HEAD：`86fb046383fe9d3b72e89c211191fd404f00676d`
- 升級前分支：`main`
- 本地保護分支：`backup/pre-update-20260727_0714`
- 原始碼目錄：`/home/chien/.hermes/hermes-agent`
- 回滾資料夾：`/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260727-070131/source-rollback`

## 快速回滾（原 checkout 還可用）

```bash
cd /home/chien/.hermes/hermes-agent
BROKEN_TS=$(date +%Y%m%d_%H%M%S)
git status --short > "/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/broken-hermes-agent-status-$BROKEN_TS.txt" 2>&1 || true
git reset --hard 86fb046383fe9d3b72e89c211191fd404f00676d
PATCH="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260727-070131/source-rollback/local_tracked_changes.patch"
[ -s "$PATCH" ] && git apply "$PATCH" || true
TAR="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260727-070131/source-rollback/untracked-files.tar.gz"
[ -s "$TAR" ] && tar xzf "$TAR" -C /home/chien/.hermes/hermes-agent || true
python3 -m compileall -q agent hermes_cli gateway tools cron plugins
/home/chien/.local/bin/hermes --version
sudo /home/chien/.local/bin/hermes gateway restart --system
/home/chien/.local/bin/hermes gateway status
```

## checkout 嚴重受損時由 bundle 重建

```bash
cd /home/chien/.hermes
mv hermes-agent "hermes-agent.BROKEN.$(date +%Y%m%d_%H%M%S)"
git clone /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260727-070131/source-rollback/hermes-agent-before-update.bundle hermes-agent
cd hermes-agent
git reset --hard 86fb046383fe9d3b72e89c211191fd404f00676d
[ -s /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260727-070131/source-rollback/local_tracked_changes.patch ] && git apply /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260727-070131/source-rollback/local_tracked_changes.patch || true
[ -s /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260727-070131/source-rollback/untracked-files.tar.gz ] && tar xzf /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260727-070131/source-rollback/untracked-files.tar.gz -C /home/chien/.hermes/hermes-agent || true
/home/chien/.local/bin/hermes --version
sudo /home/chien/.local/bin/hermes gateway restart --system
/home/chien/.local/bin/hermes gateway status
```

## 驗證

```bash
/home/chien/.local/bin/hermes --version
/home/chien/.local/bin/hermes config check
/home/chien/.local/bin/hermes cron list
/home/chien/.local/bin/hermes gateway status
systemctl is-active hermes-gateway.service
journalctl -u hermes-gateway.service -n 80 --no-pager
```

## 安全注意

- 復原期間不要再執行另一輪升級。
- 不要把 `.env`、`auth.json`、OAuth 資料或備份解密密碼貼給第三方。
- 完整 bundle 僅保存在本地完整備份；外部目的地只保存 lite 回滾資料與索引。

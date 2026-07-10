# Hermes 例行更新前 Source Rollback Addendum

Backup label: `hermes-state-snapshot-20260710-131408`  
建立日期：2026-07-10  
範圍：MINIPC 小馬 + Mac M4 小媽

## 更新前版本與 HEAD

| 主機 | Hermes | Source HEAD | Branch | 模型設定（非敏感） |
|---|---|---|---|---|
| MINIPC | `v0.18.0 / 2026.7.1` | `cd124ad1fae574dcdab8124924f84201d65277da` | `main` | `openai-codex / gpt-5.6-sol` |
| Mac M4 | `v0.18.0 / 2026.7.1` | `19d4174454624a1ca91bc47b8f2a7ae8c3b4b5d3` | `main` | `opencode-go / deepseek-v4-flash` |

## 保存內容

- MINIPC：tracked binary patch、untracked tar、完整 git bundle、status/remotes、SHA256。
- Mac：tracked binary patch、untracked tar、完整 git bundle、status/remotes、SHA256。
- MINIPC 路徑：`C:\Users\chien\_3AI_WorkSpace\HermesBackup\hermes-state-snapshot-20260710-131408\source-rollback-minipc`
- Mac 本機路徑：`/Users/scottchien/hermes_artifacts/hermes-state-snapshot-20260710-131408/source-rollback-mac`
- Mac 的第二份副本：`C:\Users\chien\_3AI_WorkSpace\HermesBackup\hermes-state-snapshot-20260710-131408\source-rollback-mac`

## MINIPC 快速回復

```bash
cd /home/chien/.hermes/hermes-agent
BROKEN_TS=$(date +%Y%m%d_%H%M%S)
git status --short > "/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/broken-minipc-status-$BROKEN_TS.txt" 2>&1 || true
git reset --hard cd124ad1fae574dcdab8124924f84201d65277da
PATCH="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260710-131408/source-rollback-minipc/local_tracked_changes.patch"
[ -s "$PATCH" ] && git apply "$PATCH" || true
TAR="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260710-131408/source-rollback-minipc/untracked-files.tar.gz"
[ -s "$TAR" ] && tar xzf "$TAR" -C /home/chien/.hermes/hermes-agent || true
python3 -m compileall -q agent hermes_cli gateway
/home/chien/.local/bin/hermes --version
sudo /home/chien/.local/bin/hermes gateway restart --system
/home/chien/.local/bin/hermes gateway status
```

## MINIPC checkout 損壞時從 bundle 重建

```bash
cd /home/chien/.hermes
mv hermes-agent "hermes-agent.BROKEN.$(date +%Y%m%d_%H%M%S)"
git clone "/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260710-131408/source-rollback-minipc/hermes-agent-before-update.bundle" hermes-agent
cd hermes-agent
git reset --hard cd124ad1fae574dcdab8124924f84201d65277da
```

之後依「MINIPC 快速回復」套用 patch 與 untracked tar，再重啟 gateway。

## Mac 快速回復

```zsh
ssh mac-m4
cd ~/.hermes/hermes-agent
BROKEN_TS=$(date +%Y%m%d_%H%M%S)
git status --short > "$HOME/hermes_artifacts/broken-mac-status-$BROKEN_TS.txt" 2>&1 || true
git reset --hard 19d4174454624a1ca91bc47b8f2a7ae8c3b4b5d3
D="$HOME/hermes_artifacts/hermes-state-snapshot-20260710-131408/source-rollback-mac"
[ -s "$D/local_tracked_changes.patch" ] && git apply "$D/local_tracked_changes.patch" || true
[ -s "$D/untracked-files.tar.gz" ] && tar xzf "$D/untracked-files.tar.gz" -C "$HOME/.hermes/hermes-agent" || true
python3 -m compileall -q agent hermes_cli gateway
/Users/scottchien/.local/bin/hermes --version
/Users/scottchien/.local/bin/hermes gateway restart
/Users/scottchien/.local/bin/hermes gateway status
```

## Mac checkout 損壞時從 bundle 重建

```zsh
cd ~/.hermes
mv hermes-agent "hermes-agent.BROKEN.$(date +%Y%m%d_%H%M%S)"
git clone "$HOME/hermes_artifacts/hermes-state-snapshot-20260710-131408/source-rollback-mac/hermes-agent-before-update.bundle" hermes-agent
cd hermes-agent
git reset --hard 19d4174454624a1ca91bc47b8f2a7ae8c3b4b5d3
```

## 安全提醒

- 不要刪除整個 `~/.hermes`。
- 不要把 `.env`、`auth.json`、OAuth token 或備份解密密碼貼給第三方。
- 救援期間不要再次執行更新。
- 回復後先驗證版本、gateway、cron 與指定模型，再恢復日常工作。

# Hermes / 小馬升級前四地備份清單與救援 SOP

Scott，

這封信是給你與小蝦在「Hermes 更新後開不起來 / Telegram 沒回應」時使用的救援文件。

建立時間：2026-06-12 12:23-12:35 CST
備份標籤：`hermes-state-snapshot-20260612-122338`
升級前 Hermes 版本：`Hermes Agent v0.16.0 (2026.6.5)`
升級前 source HEAD：`3705625b731d4640c22fafdd077d1b509d8422d7`（短版 `3705625b7`）

安全提醒：
- raw 本地備份含 `.env`、OAuth、auth token，請勿轉寄給第三方。
- 外部三地保存的是加密 `.tar.gz.gpg` 與 sanitized 文件。
- 這封信沒有放解密密碼。救援密碼在先前主旨 `Hermes發送 - Hermes備份救援密碼，重要` 的郵件，或本機 `~/.hermes/secrets/hermes-backup-passphrase.txt`。

---

## 一、四地備份完成狀態

### 1. 本地硬碟 / 3AI 工作區

Windows 路徑：
`C:\Users\chien\_3AI_WorkSpace\HermesBackup\hermes-state-snapshot-20260612-122338\`

主要加密封包：
`C:\Users\chien\_3AI_WorkSpace\HermesBackup\hermes-state-snapshot-20260612-122338.tar.gz.gpg`

主封包 SHA256：
`7c08beeb81070d3d856d9c6206caa9a6271b8f5bb4cfef5f2c07d8428df4f794`

### 2. Google Drive

Google Drive folder ID：
`17XHA19ZKyYvckXHnXOLq8pvP8FDOu08N`

已上傳主備份封包、manifest、restore SOP、verification、sanitized config 等。後續又補上 source rollback lite addendum。

Source rollback lite Google Drive file ID：
`17f_hnBiI-kZMXHC36uSijRlWaXt4ervn`

### 3. Supabase

資料表：`public.hermes_backups`

備份 row label：
`hermes-state-snapshot-20260612-122338`

已寫入：主封包 base64、manifest、restore SOP、verification、Google Drive folder、GitHub path、source rollback lite metadata。

### 4. GitHub 私有備份 repo

Repo path：
`hermes-backups/hermes-state-snapshot-20260612-122338`

目前 remote main commit：
`41612afb63939245c97ba59b7302a36a604addc9`

Source rollback lite GitHub path：
`hermes-backups/hermes-state-snapshot-20260612-122338/source-rollback-lite`

---

## 二、本地備份檔案清單

主要檔案：
- `MANIFEST.txt`：完整清單與檔案 SHA256
- `RESTORE_SOP.md`：原始 restore SOP
- `BACKUP_VERIFICATION.txt`：備份檢查摘要
- `FOUR_LOCATION_SYNC_VERIFICATION.txt`：四地同步驗證
- `ARCHIVE_SHA256.txt`：主封包 sha256
- `GOOGLE_DRIVE_UPLOAD.json`：Drive 上傳結果
- `SUPABASE_WRITE.txt`：Supabase 寫入結果
- `GITHUB_COMMIT.txt`：GitHub commit 記錄
- `DECRYPT_VERIFY.txt`：加密封包可解密驗證
- `EMAIL_BACKUP_LIST_AND_RESTORE_SOP.md`：本信內容

本地 raw 私密資料：
- `raw/config.yaml`
- `raw/.env`
- `raw/auth.json`
- `raw/google_token.json`
- `raw/google_client_secret.json`
- `raw/channel_directory.json`
- `raw/gateway_state.json`
- `raw/memory/`
- `raw/memories/`
- `raw/handoffs/`
- `raw/skills/`
- `raw/scripts/`
- `raw/cron/jobs.json`
- `raw/sessions_index.json`

Sanitized 外部可讀摘要：
- `sanitized/config.yaml.SANITIZED`
- `sanitized/.env.SANITIZED`
- `sanitized/auth.json.SANITIZED.json`
- `sanitized/google_token.json.SANITIZED.json`
- `sanitized/channel_directory.json.SANITIZED.json`
- `sanitized/gateway_state.json.SANITIZED.json`

Source rollback addendum：
- `source-rollback/PREUPDATE_HEAD.txt`
- `source-rollback/GIT_STATUS_SHORT.txt`
- `source-rollback/local_tracked_changes.patch`
- `source-rollback/untracked-files.tar.gz`
- `source-rollback/hermes-agent-before-update.bundle`（本地完整 source bundle，約 257 MB）
- `source-rollback/ROLLBACK_SOURCE_REPO.md`
- `source-rollback-lite/`（輕量版，已同步到 Drive / GitHub / Supabase metadata）

外層封包：
- `hermes-state-snapshot-20260612-122338.tar.gz`：17 MB
- `hermes-state-snapshot-20260612-122338.tar.gz.gpg`：17 MB
- `hermes-state-snapshot-20260612-122338_source-rollback.tar.gz.gpg`：243 MB，本地 source bundle
- `hermes-state-snapshot-20260612-122338_source-rollback-lite.tar.gz.gpg`：29 KB，已同步外部

Source rollback lite encrypted SHA256：
`9b7886ce22c7db35622dc16f86877f0c1a6422fc5c659781eb811a3c042cf491`

---

## 三、若更新後小馬開不起來：小蝦救援 SOP

### 情境 A：Telegram 沒回應，但 Windows / WSL 還能開

請先在 Windows Terminal 打開 WSL，執行：

```bash
/home/chien/.local/bin/hermes --version || true
/home/chien/.local/bin/hermes gateway status || true
journalctl -u hermes-gateway.service -n 80 --no-pager || true
```

如果只是 gateway 沒起來，先嘗試：

```bash
sudo /home/chien/.local/bin/hermes gateway restart --system
/home/chien/.local/bin/hermes gateway status
```

如果仍然失敗，進入 source rollback。

### 情境 B：更新後 source code 壞掉，快速退回升級前版本

```bash
cd /home/chien/.hermes/hermes-agent

BROKEN_TS=$(date +%Y%m%d_%H%M%S)
git status --short > "/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/broken-hermes-agent-status-$BROKEN_TS.txt" 2>&1 || true

# 退回更新前已知可用 commit
git reset --hard 3705625b731d4640c22fafdd077d1b509d8422d7

# 還原 Scott 本地 tracked customizations（若 patch 能套用）
PATCH="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260612-122338/source-rollback/local_tracked_changes.patch"
[ -s "$PATCH" ] && git apply "$PATCH" || true

# 還原更新前 untracked local files（若存在）
TAR="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260612-122338/source-rollback/untracked-files.tar.gz"
[ -s "$TAR" ] && tar xzf "$TAR" -C /home/chien/.hermes/hermes-agent || true

# 基本語法檢查
python3 -m compileall -q /home/chien/.hermes/hermes-agent/agent /home/chien/.hermes/hermes-agent/hermes_cli /home/chien/.hermes/hermes-agent/gateway || true

# 重啟 gateway
/home/chien/.local/bin/hermes --version
sudo /home/chien/.local/bin/hermes gateway restart --system
/home/chien/.local/bin/hermes gateway status
```

### 情境 C：config / auth 被更新弄壞，還原核心設定

注意：這會還原 `.env`、`auth.json` 等敏感檔。只在確認設定被破壞時執行。

```bash
BACKUP="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/hermes-state-snapshot-20260612-122338/raw"
ERR_TS=$(date +%Y%m%d_%H%M%S)

mkdir -p /home/chien/.hermes/restore-preimage-$ERR_TS
cp /home/chien/.hermes/config.yaml /home/chien/.hermes/restore-preimage-$ERR_TS/config.yaml 2>/dev/null || true
cp /home/chien/.hermes/.env /home/chien/.hermes/restore-preimage-$ERR_TS/.env 2>/dev/null || true
cp /home/chien/.hermes/auth.json /home/chien/.hermes/restore-preimage-$ERR_TS/auth.json 2>/dev/null || true

cp "$BACKUP/config.yaml" /home/chien/.hermes/config.yaml
cp "$BACKUP/.env" /home/chien/.hermes/.env
cp "$BACKUP/auth.json" /home/chien/.hermes/auth.json 2>/dev/null || true
cp "$BACKUP/channel_directory.json" /home/chien/.hermes/channel_directory.json 2>/dev/null || true
cp "$BACKUP/gateway_state.json" /home/chien/.hermes/gateway_state.json 2>/dev/null || true
cp "$BACKUP/cron/jobs.json" /home/chien/.hermes/cron/jobs.json 2>/dev/null || true
rsync -a "$BACKUP/memory/" /home/chien/.hermes/memory/ 2>/dev/null || true
rsync -a "$BACKUP/memories/" /home/chien/.hermes/memories/ 2>/dev/null || true
rsync -a "$BACKUP/handoffs/" /home/chien/.hermes/handoffs/ 2>/dev/null || true
rsync -a "$BACKUP/skills/" /home/chien/.hermes/skills/ 2>/dev/null || true
rsync -a "$BACKUP/scripts/" /home/chien/.hermes/scripts/ 2>/dev/null || true

sudo /home/chien/.local/bin/hermes gateway restart --system
/home/chien/.local/bin/hermes gateway status
```

### 情境 D：整個 `~/.hermes/hermes-agent` checkout 損毀

若 git repo 已經壞到不能 reset，可用本地 bundle 重建：

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

### 情境 E：本地備份資料夾也找不到，只剩 Google Drive / GitHub / Supabase

1. 從 Google Drive folder `17XHA19ZKyYvckXHnXOLq8pvP8FDOu08N` 或 GitHub private repo `hermes-backups/hermes-state-snapshot-20260612-122338` 下載：
   - `hermes-state-snapshot-20260612-122338.tar.gz.gpg`
   - `MANIFEST.txt`
   - `RESTORE_SOP.md`

2. 取得救援解密密碼：
   - 先找 Scott 信箱中主旨 `Hermes發送 - Hermes備份救援密碼，重要`
   - 或若 WSL 檔案還在，讀 `/home/chien/.hermes/secrets/hermes-backup-passphrase.txt`

3. 解密與展開：

```bash
mkdir -p /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/recovered
cd /mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/recovered

gpg --batch --yes --pinentry-mode loopback --passphrase '在這裡貼上救援密碼' \
  --output hermes-state-snapshot-20260612-122338.tar.gz \
  --decrypt hermes-state-snapshot-20260612-122338.tar.gz.gpg

tar xzf hermes-state-snapshot-20260612-122338.tar.gz
```

4. 之後照「情境 C」還原核心設定。

---

## 四、復原後驗證

請小蝦務必做完以下檢查再告訴 Scott 完成：

```bash
/home/chien/.local/bin/hermes --version
/home/chien/.local/bin/hermes gateway status
/home/chien/.local/bin/hermes cron list | head -80
/home/chien/.local/bin/hermes chat -q '只回覆：CODEX_OK' --provider openai-codex -m gpt-5.5 -Q
journalctl -u hermes-gateway.service -n 80 --no-pager | tail -80
```

成功標準：
- `hermes --version` 能執行。
- gateway 狀態 healthy / running。
- cron list 能列出 job。
- Codex smoke test 回覆 `CODEX_OK`。
- Telegram 重新傳訊息給小馬有回應。

---

## 五、救援時不要做的事

- 不要刪除 `~/.hermes` 整個資料夾。
- 不要大量刪除 5 個以上檔案；需要先問 Scott。
- 不要把 `.env`、`auth.json`、`google_token.json` 貼到第三方 AI 或公開網頁。
- 不要在復原中再次執行 `hermes update`，先恢復可開機狀態再說。

---

結論：四地備份已完成；另外已補 source rollback addendum。若升級後小馬失聯，小蝦照本信的情境 A → B → C → D 順序救援即可。

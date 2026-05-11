# 🚨 HERMES 還原 SOP — v0.13.0 + Codex GPT-5.5 額度使用備份

**備份標籤**：重要備份：升級本 v0.13.0 (2026.5.7) + CODEX 額度使用備份  
**備份日期**：2026-05-11  
**主要模型**：`openai-codex / gpt-5.5`（使用 Scott 的 ChatGPT/Codex 登入額度）  
**備用模型**：`openrouter / xiaomi/mimo-v2-pro`

---

## 0. 四地備份位置

| 位置 | 路徑 / 說明 |
|---|---|
| 硬碟 | `C:\Users\chien\_3AI_WorkSpace\HermesBackup\2026-05-11_重要備份_HERMES_v0.13.0_CODEX額度使用備份\` |
| Google Drive | `Hermes workspace / 2026-05-11_重要備份_HERMES_v0.13.0_CODEX額度使用備份` |
| Supabase | `hermes_knowledge`，title: `重要備份 HERMES v0.13.0 + CODEX額度使用 2026-05-11` |
| GitHub | `9505053-create/hermes-config`，檔案：`HERMES_RESTORE_SOP_v0.13.0_CODEX.md`、`BACKUP_MANIFEST_2026-05-11_CODEX.txt` |

> 安全註記：備份包不包含 token/API key 原文；含 `auth.SANITIZED.json` 與 `CODEX_AUTH_SUMMARY.NO_TOKENS.json`。Codex token 還原時由本機 Windows 的 `C:\Users\chien\.codex\auth.json` 讀取。

---

## 1. 還原前先備份壞狀態

```bash
BAD=~/hermes_bad_state_$(date +%Y%m%d_%H%M%S)
mkdir -p "$BAD"
cp -r ~/.hermes/config.yaml ~/.hermes/auth.json ~/.hermes/SOUL.md ~/.hermes/AGENTS.md "$BAD/" 2>/dev/null || true
cp -r ~/.hermes/memory ~/.hermes/memories ~/.hermes/skills ~/.hermes/cron "$BAD/" 2>/dev/null || true
echo "壞狀態備份在: $BAD"
```

---

## 2. 從硬碟備份還原核心檔案

```bash
BACKUP="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/2026-05-11_重要備份_HERMES_v0.13.0_CODEX額度使用備份"

# P0 核心設定
cp "$BACKUP/config/config.yaml" ~/.hermes/config.yaml
cp "$BACKUP/config/SOUL.md" ~/.hermes/SOUL.md
cp "$BACKUP/config/AGENTS.md" ~/.hermes/AGENTS.md
cp "$BACKUP/config/SECURITY_TRUST_BOUNDARY.md" ~/.hermes/SECURITY_TRUST_BOUNDARY.md
cp "$BACKUP/config/channel_directory.json" ~/.hermes/channel_directory.json 2>/dev/null || true

# P1 記憶、技能、排程
mkdir -p ~/.hermes/memory ~/.hermes/memories ~/.hermes/handoffs ~/.hermes/skills ~/.hermes/scripts ~/.hermes/cron
cp "$BACKUP/memory/"*.md ~/.hermes/memory/ 2>/dev/null || true
cp "$BACKUP/memories/"*.md ~/.hermes/memories/ 2>/dev/null || true
cp "$BACKUP/handoffs/"*.md ~/.hermes/handoffs/ 2>/dev/null || true
cp -r "$BACKUP/skills/"* ~/.hermes/skills/ 2>/dev/null || true
cp "$BACKUP/scripts/"* ~/.hermes/scripts/ 2>/dev/null || true
cp "$BACKUP/cron/jobs.json" ~/.hermes/cron/jobs.json 2>/dev/null || true
```

---

## 3. 還原 Codex GPT-5.5 額度使用設定

### 3.1 確認 Windows Codex 已登入

在 Windows 應存在：

```text
C:\Users\chien\.codex\auth.json
```

WSL 中確認：

```bash
ls -la /mnt/c/Users/chien/.codex/auth.json
```

如果不存在，先在 Windows 重新登入 Codex / ChatGPT，再回來執行下一步。

### 3.2 建立 WSL symlink + 重建 Hermes Codex OAuth pool

```bash
BACKUP="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/2026-05-11_重要備份_HERMES_v0.13.0_CODEX額度使用備份"
python3 "$BACKUP/restore_sop/restore_codex_oauth_from_windows_codex.py"
```

這支腳本會：
1. 確認 `/mnt/c/Users/chien/.codex/auth.json` 存在
2. 建立 `~/.codex -> /mnt/c/Users/chien/.codex` symlink（如果不存在）
3. 從 Windows Codex auth 讀取 token
4. 寫入 `~/.hermes/auth.json` 的 `credential_pool.openai-codex`

### 3.3 確認模型設定

```bash
python3 - <<'PY'
import yaml, json
c=yaml.safe_load(open('/home/chien/.hermes/config.yaml'))
print(json.dumps({'model': c.get('model'), 'fallback_model': c.get('fallback_model')}, indent=2, ensure_ascii=False))
PY

hermes auth list | grep -A2 -E 'openai-codex|openrouter'
```

預期：

```yaml
model:
  provider: openai-codex
  default: gpt-5.5
fallback_model:
  provider: openrouter
  model: xiaomi/mimo-v2-pro
```

---

## 4. 重啟 Gateway 並測試

```bash
sudo /home/chien/.local/bin/hermes gateway restart --system
systemctl is-active hermes-gateway

# 測試 Codex GPT-5.5
hermes -z "只回覆：CODEX_OK" --provider openai-codex -m gpt-5.5
```

若回覆 `CODEX_OK`，代表 GPT-5.5 主模型恢復。

---

## 5. 如果 Codex 失敗，暫時切回 OpenRouter 備援

```bash
python3 - <<'PY'
import yaml
p='/home/chien/.hermes/config.yaml'
c=yaml.safe_load(open(p))
c['model']={'provider':'openrouter','default':'xiaomi/mimo-v2-pro'}
c['fallback_model']={'provider':'openai-codex','model':'gpt-5.5'}
open(p,'w').write(yaml.safe_dump(c, allow_unicode=True, sort_keys=False))
PY
sudo /home/chien/.local/bin/hermes gateway restart --system
```

---

## 6. 必須確認的安全紅線

還原後確認 `~/.hermes/AGENTS.md` 包含：

1. 不得使用 Scott 信用卡資訊消費
2. 大量刪除檔案（5+ 檔案或遞迴刪除資料夾）前必須與 Scott 確認
3. Scott 敏感資料（信用卡卡號、API Key、個資）不得未經允許提供給第三方

```bash
grep -n "三大紅線" ~/.hermes/AGENTS.md
```

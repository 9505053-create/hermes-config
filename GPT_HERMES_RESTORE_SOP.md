# 🚨 HERMES 緊急復原 SOP — 給 GPT 的操作手冊

> **情境**：Hermes 升級後掛掉，Scott 請你（GPT）協助復原。
> **備份日期**：2026-05-11
> **備份版本**：v0.11.0 (2026.4.23)
> **備份位置**：`C:\Users\chien\_3AI_WorkSpace\HermesBackup\2026-05-11_HERMES升級前備份_v0.11.0\`

---

## ⚠️ 復原前必讀

1. **先備份當前壞掉的狀態**，別直接覆蓋
2. **不動敏感檔案**（.env、auth.json、token）— 這些在升級後應該自行保留
3. **按順序復原**，每步驗證後再下一步
4. **Hermes 安裝目錄**：`~/.hermes/`（WSL: `/home/chien/.hermes/`）
5. **Hermes 程式碼**：`~/.hermes/hermes-agent/`（這是 git repo）

---

## 📁 檔案復原優先級（按重要性排序）

### 🔴 P0 — 沒有這些 Hermes 不知道「自己是誰」

| 檔案 | 備份位置 | 目標位置 | 說明 |
|------|----------|----------|------|
| `config.yaml` | `config/config.yaml` | `~/.hermes/config.yaml` | **核心設定檔** — model、provider、toolsets、gateway 全在這 |
| `SOUL.md` | `config/SOUL.md` | `~/.hermes/SOUL.md` | **人格定義** — Hermes 的行為準則、Stability Doctrine |
| `AGENTS.md` | `config/AGENTS.md` | `~/.hermes/AGENTS.md` | **工作流上下文** — Scott 工作流、3AI 呼叫模式、紅線規則 |

### 🟡 P1 — 沒有這些記憶和技能消失

| 檔案 | 備份位置 | 目標位置 | 說明 |
|------|----------|----------|------|
| `memory/*.md` | `memory/` (36 files) | `~/.hermes/memory/` | **對話記憶** — 教訓、顧問回饋、排程指令 |
| `memories/MEMORY.md` | `memories/MEMORY.md` | `~/.hermes/memories/MEMORY.md` | **長期記憶核心** |
| `memories/USER.md` | `memories/USER.md` | `~/.hermes/memories/USER.md` | **用戶偏好與關係記憶** |
| `skills/*/SKILL.md` | `skills/` (98 skills) | `~/.hermes/skills/` | **全部技能定義** — 恢復時保持目錄結構 |
| `SECURITY_TRUST_BOUNDARY.md` | `config/SECURITY_TRUST_BOUNDARY.md` | `~/.hermes/SECURITY_TRUST_BOUNDARY.md` | **安全邊界** |

### 🟢 P2 — 復原後再補就行

| 檔案 | 備份位置 | 目標位置 | 說明 |
|------|----------|----------|------|
| `channel_directory.json` | `config/channel_directory.json` | `~/.hermes/channel_directory.json` | Telegram 頻道對應 |
| `handoffs/*.md` | `handoffs/` | `~/.hermes/handoffs/` | 工作交接紀錄 |
| `scripts/*.py` | `scripts/` | `~/.hermes/scripts/` | 自訂腳本（email、backup） |
| `cron/jobs.json` | `cron/jobs.json` | `~/.hermes/cron/jobs.json` | 定時任務定義 |

### ⛔ 不要動的檔案（升級應保留）
- `~/.hermes/.env` — 所有 API keys
- `~/.hermes/auth.json` — Telegram bot token
- `~/.hermes/google_token.json` — Google OAuth
- `~/.hermes/google_client_secret.json` — Google OAuth client
- `~/.hermes/state.db` — 內部狀態資料庫

---

## 🔧 復原步驟

### Step 0: 診斷現狀
```bash
# 在 WSL 中執行
hermes --version
hermes gateway status
# 如果 hermes 命令不存在，先修安裝：
pip install hermes-agent  # 或參考安裝文件
```

### Step 1: 備份當前（壞的）狀態
```bash
cd ~
BAD_STATE_DIR=~/hermes_bad_state_$(date +%Y%m%d_%H%M%S)
mkdir -p "$BAD_STATE_DIR"
cp -r ~/.hermes/config.yaml "$BAD_STATE_DIR/" 2>/dev/null
cp -r ~/.hermes/SOUL.md "$BAD_STATE_DIR/" 2>/dev/null
cp -r ~/.hermes/AGENTS.md "$BAD_STATE_DIR/" 2>/dev/null
cp -r ~/.hermes/memory "$BAD_STATE_DIR/" 2>/dev/null
cp -r ~/.hermes/memories "$BAD_STATE_DIR/" 2>/dev/null
cp -r ~/.hermes/skills "$BAD_STATE_DIR/" 2>/dev/null
echo "壞狀態備份在: $BAD_STATE_DIR"
```

### Step 2: 復原 P0 核心檔案
```bash
BACKUP="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/2026-05-11_HERMES升級前備份_v0.11.0"

# config.yaml — 最關鍵！
cp "$BACKUP/config/config.yaml" ~/.hermes/config.yaml
chmod 644 ~/.hermes/config.yaml

# SOUL.md — 人格
cp "$BACKUP/config/SOUL.md" ~/.hermes/SOUL.md
chmod 600 ~/.hermes/SOUL.md

# AGENTS.md — 工作流
cp "$BACKUP/config/AGENTS.md" ~/.hermes/AGENTS.md
chmod 644 ~/.hermes/AGENTS.md
```

### Step 3: 驗證 config.yaml 關鍵值
```bash
python3 -c "
import yaml
with open('/home/chien/.hermes/config.yaml') as f:
    c = yaml.safe_load(f)
print('Model default:', c.get('model',{}).get('default','⚠️ MISSING'))
print('Provider:', c.get('model',{}).get('provider','⚠️ MISSING'))
print('Gateway port:', c.get('gateway',{}).get('port','⚠️ MISSING'))
print('Telegram channel:', c.get('channels',{}).get('telegram',{}).get('home_channel','⚠️ MISSING'))
"
```

### Step 4: 復原 P1 記憶與技能
```bash
BACKUP="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/2026-05-11_HERMES升級前備份_v0.11.0"

# 記憶檔案
mkdir -p ~/.hermes/memory ~/.hermes/memories ~/.hermes/handoffs
cp "$BACKUP/memory/"*.md ~/.hermes/memory/
cp "$BACKUP/memories/"*.md ~/.hermes/memories/
cp "$BACKUP/handoffs/"*.md ~/.hermes/handoffs/

# 安全邊界
cp "$BACKUP/config/SECURITY_TRUST_BOUNDARY.md" ~/.hermes/

# 技能（完整目錄結構）
cp -r "$BACKUP/skills/"* ~/.hermes/skills/

# 腳本
mkdir -p ~/.hermes/scripts
cp "$BACKUP/scripts/"*.py ~/.hermes/scripts/
chmod +x ~/.hermes/scripts/*.py 2>/dev/null

# Cron 排程
mkdir -p ~/.hermes/cron
cp "$BACKUP/cron/jobs.json" ~/.hermes/cron/

echo "復原完成！驗證："
echo "Memory files: $(ls ~/.hermes/memory/*.md 2>/dev/null | wc -l)"
echo "Memories: $(ls ~/.hermes/memories/*.md 2>/dev/null | wc -l)"
echo "Skills: $(find ~/.hermes/skills/ -name SKILL.md | wc -l)"
```

### Step 5: 復原 channel_directory（Telegram 連線）
```bash
BACKUP="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/2026-05-11_HERMES升級前備份_v0.11.0"
cp "$BACKUP/config/channel_directory.json" ~/.hermes/channel_directory.json
```

### Step 6: 重啟 Gateway
```bash
hermes gateway restart
# 或手動：
sudo /home/chien/.local/bin/hermes gateway restart
```

### Step 7: 驗證復原成功
```bash
# 檢查版本
hermes --version

# 檢查 gateway
hermes gateway status

# 檢查 Telegram 連線
# → 發一則訊息給 Hermes bot，看有沒有回應

# 檢查技能載入
hermes skills list 2>/dev/null || echo "skills list 命令不可用，手動檢查目錄"

# 檢查記憶
cat ~/.hermes/memories/MEMORY.md | head -5
```

---

## 🔍 備份完整性驗證

```bash
BACKUP="/mnt/c/Users/chien/_3AI_WorkSpace/HermesBackup/2026-05-11_HERMES升級前備份_v0.11.0"

echo "=== 備份完整性檢查 ==="
echo "Config: $(ls $BACKUP/config/*.md $BACKUP/config/*.yaml $BACKUP/config/*.json 2>/dev/null | wc -l) 檔案"
echo "Memory: $(ls $BACKUP/memory/*.md 2>/dev/null | wc -l) 檔案"
echo "Memories: $(ls $BACKUP/memories/*.md 2>/dev/null | wc -l) 檔案"
echo "Skills: $(find $BACKUP/skills/ -name SKILL.md | wc -l) 個技能"
echo "Scripts: $(ls $BACKUP/scripts/*.py 2>/dev/null | wc -l) 檔案"
echo ""
echo "=== 關鍵檔案 checksum ==="
sha256sum $BACKUP/config/config.yaml $BACKUP/config/SOUL.md $BACKUP/config/AGENTS.md
```

---

## 🧠 Scott 工作流背景（GPT 必知）

- **Scott 是決策者**，你（GPT）是顧問團成員
- **Hermes 是指揮官**，負責控場、派工、整理
- **三大紅線**：不碰信用卡、大量刪除要問 Scott、敏感資料不外洩
- **Telegram 是主要溝通渠道**，郵件通知：chiensct@hotmail.com
- **共享空間**：`C:\Users\chien\_3AI_WorkSpace\`
- **Hermes 使用 OpenRouter** 作為主要 LLM provider

---

## 📞 聯絡 Scott

如果復原過程遇到問題：
1. **Telegram**：直接傳訊息給 Scott
2. **郵件**：chiensct@hotmail.com
3. **共享空間留言**：在 `_3AI_WorkSpace` 放一個 `RESTORE_STATUS.md`

---

## 📦 四地備份位置

| # | 位置 | 路徑 | 狀態 |
|---|------|------|------|
| 1 | 硬碟 (本地) | `C:\Users\chien\_3AI_WorkSpace\HermesBackup\2026-05-11_HERMES升級前備份_v0.11.0\` | ✅ |
| 2 | Google Drive | `HermesBackup/2026-05-11_HERMES升級前備份_v0.11.0/` | 待確認 |
| 3 | Supabase | `hermes_knowledge` 表 — module='backup' | 待確認 |
| 4 | GitHub | hermes-agent repo — tag: `pre-upgrade-v0.11.0` | 待確認 |

---

*此 SOP 由 Hermes v0.11.0 於 2026-05-11 自動生成，標示為「HERMES升級前備份」。*

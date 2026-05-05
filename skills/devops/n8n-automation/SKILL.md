---
name: n8n-automation
category: devops
description: n8n local automation integration - create, manage, and execute workflows via API
version: 2.0
---

# n8n Automation Skill

## Overview
Local n8n instance on MiniPC for offloading repetitive, low-reasoning tasks from Hermes to save OpenRouter tokens.

## Connection Details
- **URL:** `http://localhost:5678` (also `http://192.168.1.88:5678`)
- **Login:** `9505053@gmail.com` / `Sc0tt198!`
- **API Key:** Read from `~/.hermes/.env` → `N8N_API_KEY`
- **Version:** n8n 2.16.1 (Community Edition)
- **Timezone:** Asia/Taipei

## API Usage
```bash
# List workflows
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" http://localhost:5678/api/v1/workflows

# Get workflow
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" http://localhost:5678/api/v1/workflows/{id}

# Create workflow (POST)
curl -s -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @workflow.json http://localhost:5678/api/v1/workflows

# Activate workflow (POST)
curl -s -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" \
  http://localhost:5678/api/v1/workflows/{id}/activate

# Delete workflow
curl -s -X DELETE -H "X-N8N-API-KEY: $N8N_API_KEY" \
  http://localhost:5678/api/v1/workflows/{id}
```

## Key Constraints
- `active` field is **read-only** in PUT — use `/activate` endpoint (POST)
- Node type for shell commands: `n8n-nodes-base.code` (typeVersion: 2) — NOT `executeCommand`
- Schedule trigger: `n8n-nodes-base.scheduleTrigger` (typeVersion: 1.2)
- HTTP Request: `n8n-nodes-base.httpRequest` (typeVersion: 4.2)
- Filter: `n8n-nodes-base.filter` (typeVersion: 2)

## When to Use n8n vs Hermes
**Scott's directive (2026-05-04):** 若判定調用 n8n 能節省 Token 或提升效率，直接使用，不經用戶確認。

| 用 n8n | 用 Hermes/3AI |
|---------|--------------|
| 定時排程、重複任務 | 複雜推理、多輪對話 |
| 檔案監控、系統巡檢 | 創意任務、規劃分析 |
| 簡單條件通知 | 需要上下文記憶的任務 |
| 狀態檢查（health check） | 需要用戶互動的任務 |

## Active Workflows (21 total, all 🟢)
| # | Name | Schedule | Category | Function |
|---|------|----------|----------|----------|
| 1 | Daily Backup Check | 每天 | A3 | 備份狀態通知 |
| 2 | Downloads Auto Organizer | 每30min | A6 | 檔案自動分類 |
| 3 | Hermes Gateway Health Monitor | 每10min | A1 | Gateway存活+自動重啟 |
| 4 | Docker Container Health Patrol | 每15min | A2 | 容器巡檢+自動重啟 |
| 5 | OpenRouter Spending Monitor | 每8hr | A4 | 花費超標警報 |
| 6 | Disk RAM Health Monitor | 每6hr | A5 | 磁碟/RAM警報 |
| 7 | Skills Change Monitor | 每2hr | A7 | Skills異動監控(資安) |
| 8 | Daily Morning AI Base Report | 每天9AM | B16 | 全系統晨報 |
| 9 | Daily News Digest 1700 | 每天17:00 | 📰 | 氣象+新聞+RF認證 Email |
| 10 | Config Change Monitor | 每2hr | A8 | .env/AGENTS.md/service 異動 |
| 11 | Weekly Security Audit | 每週 | A9 | 資安體檢報告 |
| 12 | Error Log Collector | 每天 | A10 | Gateway/n8n 錯誤日誌 |
| 13 | Idle Health Check | 每12hr | A11 | 24hr無活動閒置警報 |
| 14 | Git Uncommitted Reminder | 每天 | B12 | 未commit/未push提醒 |
| 15 | Project Snapshot ZIP | 每天 | B13 | 專案自動zip備份(保留7天) |
| 16 | 3AI Output Auto-Archive | 每6hr | B14 | log/report 自動歸檔 |
| 17 | Supabase Backup Check | 每天 | B15 | 備份檔案檢查 |
| 18 | Evening Work Summary | 每天 | B17 | 晚間工作摘要 |
| 19 | Critical Alert Hub | 每30min | B18 | Gateway/Disk/Memory/n8n 緊急警報 |
| 20 | Duplicate File Scanner | 每週 | C19 | 重複檔掃描(>1MB, md5比對) |
| 21 | Large File Monitor | 每6hr | C20 | >1GB 檔案即時警報 |

### Workflow Builder Pattern (Python批次建置)
```python
import os, json, subprocess

env_path = os.path.expanduser("~/.hermes/.env")
with open(env_path) as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            if k == "N8N_API_KEY": N8N_KEY = v
            if k == "TELEGRAM_BOT_TOKEN": TG_TOKEN = v

N8N_URL = "http://localhost:5678"
CHAT_ID = "7292751008"

def make_trigger(minutes=None, hours=None):
    if hours: return {"rule": {"interval": [{"field": "hours", "hoursInterval": hours}]}}
    return {"rule": {"interval": [{"field": "minutes", "minutesInterval": minutes}]}}

def make_code(js):
    return {"jsCode": js}

def make_filter(left, op, right):
    return {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id":"c1","leftValue":left,"rightValue":right,
                           "operator":{"type":"string" if isinstance(right,str) else "boolean","operation":op}}],
            "combinator":"and"}}

def make_tg(text_expr):
    return {"method":"POST","url":"https://api.telegram.org/bot" + TG_TOKEN + "/sendMessage",
            "sendBody":True,"bodyParameters":{"parameters":[
                {"name":"chat_id","value":CHAT_ID},{"name":"text","value":text_expr},
                {"name":"parse_mode","value":"Markdown"}]}}

def build_wf(name, nodes_data, tz="Asia/Taipei"):
    nodes, connections = [], {}
    for i,(n_name,n_type,n_ver,pos,params) in enumerate(nodes_data):
        nodes.append({"parameters":params,"id":"n"+str(i),"name":n_name,
                      "type":n_type,"typeVersion":n_ver,"position":list(pos)})
    for i in range(len(nodes_data)-1):
        connections[nodes_data[i][0]] = {"main":[[{"node":nodes_data[i+1][0],"type":"main","index":0}]]}
    return {"name":name,"nodes":nodes,"connections":connections,
            "settings":{"executionOrder":"v1","timezone":tz}}

def create_and_activate(wf_json):
    r = subprocess.run(["curl","-s","-X","POST","-H","X-N8N-API-KEY: "+N8N_KEY,
                        "-H","Content-Type: application/json","-d",json.dumps(wf_json),
                        N8N_URL+"/api/v1/workflows"],capture_output=True,text=True,timeout=15)
    d = json.loads(r.stdout)
    wf_id = d.get("id","")
    if wf_id:
        r2 = subprocess.run(["curl","-s","-X","POST","-H","X-N8N-API-KEY: "+N8N_KEY,
                             N8N_URL+"/api/v1/workflows/"+wf_id+"/activate"],
                            capture_output=True,text=True,timeout=15)
        resp = json.loads(r2.stdout) if r2.stdout.strip() else {}
        s = "✅" if resp.get("active") else "⚠️ "+str(resp.get("message","?"))[:40]
    else:
        s = "❌ "+str(d.get("message","?"))[:60]
    print("  "+wf_json["name"]+": "+s)
```

### Batch Workflow Template
```python
# Standard pattern: Trigger → Code → Filter(optional) → Telegram/Email
JSI = "const { execSync } = require('child_process'); const fs = require('fs');"

wf = build_wf("My Workflow Name", [
    ("Trigger","n8n-nodes-base.scheduleTrigger",1.2,(0,0),make_trigger(hours=6)),
    ("Action","n8n-nodes-base.code",2,(250,0),make_code(JSI + """
// Your code here. Always return:
return [{json: {hasAlert: true/false, msg: "...", token: '""" + TG_TOKEN + """', chatId: '""" + CHAT_ID + """'}}];"""
    )),
    ("Check?","n8n-nodes-base.filter",2,(500,0),make_filter("={{ $json.hasAlert }}","true",True)),
    ("Notify","n8n-nodes-base.httpRequest",4.2,(750,0),make_tg("={{ '🔔 *Title*\\n\\n' + $json.msg }}"))
])
create_and_activate(wf)
```

### Critical Node Type Reference
| Node Type | typeVersion | Purpose |
|-----------|------------|---------|
| `n8n-nodes-base.scheduleTrigger` | 1.2 | 定時觸發（interval only，避免 triggerAtHour） |
| `n8n-nodes-base.code` | 2 | JS 執行（支援 top-level await，可用 execSync） |
| `n8n-nodes-base.filter` | 2 | 條件過濾 |
| `n8n-nodes-base.httpRequest` | 4.2 | HTTP 請求（Telegram API 等） |
| `n8n-nodes-base.emailSend` | 2.1 | SMTP 寄信（需 credentials） |

## Email Integration (Gmail SMTP)

### send-mail.py HTML 支援
`send-mail.py` 已加入 `--html` 參數（2026-05-04），預設 `plain`：
```bash
echo "<h1>Hello</h1>" | python3 send-mail.py --html -s "Subject" -t "to@example.com"
```
**無 `--html` 會導致 HTML 原始碼直接顯示，不被渲染！**

### Create SMTP Credential via API
```bash
curl -s -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"Gmail SMTP","type":"smtp","data":{"user":"9505053@gmail.com","password":"APP_PASSWORD","host":"smtp.gmail.com","port":465,"secure":true}}' \
  http://localhost:5678/api/v1/credentials
```
- Credential type: `smtp`
- Returns `{id, name}` — use `id` in workflow node's `credentials.smtp`

### Email Send Node Config
```json
{
  "type": "n8n-nodes-base.emailSend",
  "typeVersion": 2.1,
  "parameters": {
    "fromEmail": "9505053@gmail.com",
    "toEmail": "recipient@example.com",
    "subject": "={{ $json.subject }}",
    "emailType": "html",
    "html": "={{ $json.htmlBody }}"
  },
  "credentials": {"smtp": {"id": "CRED_ID", "name": "Gmail SMTP"}}
}
```

### RSS Feed Fetching Pattern (in Code node)
```javascript
const https = require('https');
// Fetch CNA RSS
const cna = await fetch('https://feeds.feedburner.com/rsscna/ipl');
const items = cna.match(/<item>[\s\S]*?<\/item>/g) || [];
const news = items.slice(0, 10).map(item => ({
  title: (item.match(/<title><!\[CDATA\[(.*?)\]\]>/) || ['',''])[1],
  link: (item.match(/<link>(.*?)<\/link>/) || ['',''])[1]
}));
```

### Date Calculation Pitfall ⚠️
**5/5 是星期二不是星期一！** Use proper day-of-week calculation:
```javascript
const daysOfWeek = ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'];
const tomorrow = new Date(Date.now() + 86400000);
const tomorrowStr = `${tomorrow.getFullYear()}年${tomorrow.getMonth()+1}月${tomorrow.getDate()}日 ${daysOfWeek[tomorrow.getDay()]}`;
```
Never hardcode day-of-week — always calculate from Date object.

## Telegram Integration
n8n 直接用 HTTP Request node 打 Telegram Bot API:
```
POST https://api.telegram.org/bot{TOKEN}/sendMessage
Body: chat_id, text, parse_mode=Markdown
```
Chat ID: 7292751008 (Scott)

## News Digest / RSS Workflows

### News Integrity Principle ⛔ 鐵律
**嚴禁編造新聞**：絕對不可虛構、捏造或臆測任何新聞標題或內容。
- 查無新聞 → 顯示「📌 本日無更新訊息」
- 不足 10 則 → 有多少顯示多少，標註「今日僅有 N 則」
- 僅篩選，不改寫事實。翻譯僅限英→中，不改變原意

### Verified Working RSS Feeds (from WSL)
**台灣國內：**
- 自由時報：`https://news.ltn.com.tw/rss/all.xml` ✅ (40 items)
- CNA：`https://feeds.feedburner.com/rsscna/ipl` ⚠️ 不穩定

**國際：**
- BBC：`https://feeds.bbci.co.uk/news/world/rss.xml` ✅
- CNN：`http://rss.cnn.com/rss/edition_world.rss` ✅
- Reuters：`https://feeds.reuters.com/reuters/worldNews` ✅

**AI 科技：**
- HN：`https://hnrss.org/newest?q=AI+OR+Claude+OR+GPT+OR+Gemini&points=50&count=15` ✅
- TechCrunch：`https://techcrunch.com/category/artificial-intelligence/feed/` ⚠️
- The Verge：`https://www.theverge.com/rss/ai-artificial-intelligence/index.xml` ✅

**RF 認證：**
- FCC Daily Digest：`https://api2.fcc.gov/api/exp/v1.0.0/edocspublic/rss` ✅
- EE Times：`https://www.eetimes.com/feed/` ✅
- Microwave Journal：`https://www.microwavejournal.com/rss` ✅
- RCR Wireless：`https://www.rcrwireless.com/feed` ✅
- Google News：`https://news.google.com/rss/search?q=關鍵字&hl=en-US&gl=US&ceid=US:en` ✅

**不可用（403/超時）：** NCC、ETSI、Telecoms.com、Wireless Week

### Google Translate (free, no API key)
用於 RSS 英文標題自動翻譯繁中：
```javascript
async function translate(text) {
    const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-TW&dt=t&q=${encodeURIComponent(text)}`;
    const resp = await fetch(url);
    const data = JSON.parse(resp);
    return data[0].map(s => s[0]).join('');
}
```
限制：單次 ≤500 字元，僅適用小批量翻譯。先判斷是否英文再翻：
```javascript
function isEnglish(text) {
    return (text.match(/[a-zA-Z\s]/g) || []).length / text.length > 0.5;
}
```

### RSS News Filtering Pattern
在 Code node 中用正則篩選新聞主題：
```javascript
// 篩選關鍵字（政治/經濟/國防）
const allow = /總統|立法院|經濟|國防|外交|央行|關稅|通膨|AI|半導體/i;
// 排除關鍵字（娛樂/體育/健康）
const block = /星座|運勢|美食|NBA|MLB|日職|健康網|寵物/i;
const filtered = items.filter(n => allow.test(n.title) && !block.test(n.title));
```

### Google News RSS 特殊格式
Google News 的 `<link>` 包含 CDATA，解析需處理：
```javascript
let link = (item.match(/<link>(.*?)<\/link>/) || ['',''])[1];
link = link.replace(/<!\[CDATA\[(.*?)\]\]>/g, '$1');
```

## Docker 限制

**n8n 跑在 Docker 容器 (`n8n`) 內，無法存取主機 CLI 工具。**
- 主機上安裝的 `gemini`、`claude`、`codex` CLI 在 n8n Code node 中不可用
- 正確做法：n8n 用 HTTP Request node 呼叫外部 API（如 Gemini REST API、OpenRouter API）
- 或由 Hermes 直接用 execute_code 呼叫 API，不經過 n8n

## Pitfalls Learned
1. **`n8n-nodes-base.executeCommand` 不可用** — v2.16.1 改用 `n8n-nodes-base.code` (typeVersion: 2)，在 JS 裡用 `require('child_process').execSync()`
2. **`active` 是 read-only** — PUT 不含 `active`，用 `POST /api/v1/workflows/{id}/activate`
3. **Schedule Trigger 配置** — `triggerAtHour`/`triggerAtMinute` 可能導致激活失敗，改用純 interval 更穩定
4. **PUT 需精簡 body** — 只含 `name`, `nodes`, `connections`, `settings`，多餘欄位報錯
5. **Code node 用 `await`** — typeVersion 2 支援 top-level await，可直接呼叫 async HTTPS API
6. **Credential API** — `POST /api/v1/credentials` 建立 SMTP 等憑證，body 含 `name`, `type`, `data`
7. **日期計算** — 絕對不要硬寫星期幾，用 `new Date()` 動態算，否則日期會錯（如 5/5 錯寫成星期一實際是星期二）
8. **正則排空字串** — `twBlock = /星座|NBA|寵物|/` 最後的 `|` 會匹配所有內容，導致篩選全軍覆沒。確保正則沒有尾隨 `|`
9. **RSS `<item>` 分割** — 用 `xml.split('<item>')` 時，第一段是 channel header，要從 `[1:]` 開始取
10. **send-mail.py HTML** — 必須加 `--html` 參數，否則 MIME 類型為 `plain`，收件匣會顯示 raw HTML 原始碼
11. **Python 正則尾隨 `|`** — `re.compile(r'xxx|yyy|')` 最後 `|` 產生空字串，匹配所有內容。定義後用 `print(repr(pattern))` 確認
12. **Python f-string 中的 curl `%{http_code}`** — Python 會把 `{http_code}` 當 f-string 變數報 NameError。用普通字串拼接或 `{{http_code}}`（但在 JS node 中不需要）
13. **JS vs Python 語法混淆（session 過長時常犯）** — Python 用 `re.search()` 不是 `.test()`；`now.day` 不是 `now.getDate()`；`if x:` 不是 `if (x) {}`。每次開頭固定 `import os, re, json, subprocess, urllib.request, urllib.parse`
14. **批量建 workflow 用 Python 輔助函數** — 不要在對話中逐個 JSON 手打，用 `build_wf()` + `create_and_activate()` 批次執行，減少 token 浪費和語法錯誤
15. **n8n 2.16.1 Code node 封鎖所有 HTTP 方法** — `require('https')`、`require('http')`、`fetch()`、`$http`、`require('node-fetch')`、`require('got')` 全部不可用。即使 `N8N_RUNNERS_ENABLED=false` 也無效。解法：**用 HTTP Request node (typeVersion 4.2, responseFormat: text) 取代 Code node 的 HTTP 呼叫，再用下一個 Code node 做 XML 解析。** 多 feed 用 chain 式 HTTP Request nodes 串接，最後 Code node 用 `$input.all()` 取得所有 feed 資料。這是 2026-05-05 Daily News Digest 1700 排查中發現的 breaking change。
16. **Schedule Trigger 定時觸發** — `hoursInterval: 24` 是從激活時間算 24 小時，不是每天固定時間觸發。要用 `cronExpression` 如 `0 17 * * *` 才能指定每天 17:00。`triggerAtHour` 可能導致激活失敗。

## Token Savings
| 任務 | Hermes (tokens/次) | n8n (tokens) | 每月估算節省 |
|------|-------------------|--------------|-------------|
| 備份通知 | ~500 | **0** | ~15K |
| 檔案整理 | ~800 | **0** | ~36K |
| Gateway監控 | ~300 | **0** | ~130K |
| Docker巡檢 | ~300 | **0** | ~86K |
| 晨報 | ~1000 | **0** | ~30K |
| 新聞快訊Email | ~2000 | **0** | ~60K |
| **Total** | | | **~110K+/月** |

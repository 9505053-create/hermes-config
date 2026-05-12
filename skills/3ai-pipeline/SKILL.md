---
name: 3ai-pipeline
description: "3AI 純搬運管線 — 用 ~! 觸發，Hermes 零思考，Gemini→Claude→Codex 依次淬鍊問題"
category: autonomous-ai-agents
trigger: "~!"
aliases: ["!~"]
---

# 3AI Pipeline — 純搬運模式

## 核心原則
**Hermes 在此技能中完全不思考、不分析、不總結。** 只做：
1. 寫 prompt 檔
2. 管道呼叫 CLI
3. 收集 stdout
4. 組裝貼回 Telegram

## 觸發條件
使用者訊息以 `~!` 或 `!~` 開頭。

## 流程架構

```
Scott 提問 (!~ ...)
  │
  ▼
┌─────────────────────────────────┐
│  Gemini CLI（情報員）            │
│  - 判斷是否需要網路資料          │
│  - 需要 → Google grounding 搜尋  │
│  - 超時（>180s）→ 自動 fallback  │
│    → 用本地知識回覆（無網路）    │
│  - 整理客觀資訊 + 來源摘要       │
│  - 只做情報，不做結論            │
└────────────┬────────────────────┘
             │ stdout
             ▼
┌─────────────────────────────────┐
│  Claude CLI（批判員）            │
│  - 理解 Gemini 資料              │
│  - 找漏洞、缺漏、不合理處        │
│  - 發表分析 + 補充忽略面向       │
└────────────┬────────────────────┘
             │ stdout
             ▼
┌─────────────────────────────────┐
│  Codex CLI（技術審核員）         │
│  - 判斷是否為技術/邏輯/架構題    │
│  - 是 → 驗證技術合理性 + 總結    │
│  - 否 → 跳過，直接傳 Claude 結果 │
└────────────┬────────────────────┘
             │ stdout
             ▼
┌─────────────────────────────────┐
│  Hermes（搬運工）                │
│  - 組裝最終結果                  │
│  - 格式化貼回 Telegram           │
│  - 不做任何修改/總結             │
└─────────────────────────────────┘
```

## 執行方式

### 步驟 1：解析問題
從使用者訊息中移除 `~!` 或 `!~` 前綴，剩餘內容即為原始問題。

### 步驟 2：執行管線腳本
將問題傳入 `pipeline.py` 腳本，腳本自動完成全部流程。

```bash
cd /home/chien/.hermes/skills/3ai-pipeline && python3 pipeline.py "使用者的問題"
```

### 步驟 3：傳送結果
腳本輸出最終組裝好的 Markdown，Hermes 直接貼回 Telegram。

## CLI 呼叫順序與指令

### Gemini（第一棒）
```bash
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt_gemini.txt | C:\Users\chien\AppData\Roaming\npm\gemini.cmd --skip-trust"
```

### Claude（第二棒）
```bash
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt_claude.txt | C:\Users\chien\AppData\Roaming\npm\claude.cmd --print"
```

### Codex（第三棒，條件執行）
```bash
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt_codex.txt | C:\Users\chien\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check"
```

## Prompt 模板

### Gemini Prompt（prompt_gemini.txt）
```
你是情報搜集員。針對以下問題，判斷是否需要網路資料。

若需要，請使用你的搜尋能力查找最新資訊。
若不需要，直接整理你已知的客觀資訊。

【規則】
- 只做情報搜集，不做結論或建議
- 標註資料來源
- 如果不確定，明確說「此處資訊可能不完整」
- 用繁體中文回答

【問題】
{QUESTION}
```

### Gemini Fallback Prompt（prompt_gemini_fallback.txt）
網路搜尋超時後自動啟用，禁止觸發網路搜尋，純靠本地知識回答。
```
你是情報搜集員。以下問題的網路搜尋目前無法使用，請完全依賴你的訓練資料回答。

【重要】
- 禁止使用網路搜尋功能
- 僅根據你已知的知識整理客觀資訊
- 明確標註「以下為本地知識，未經網路查證」
- 如果你的知識不足以回答，誠實說明哪些部分不確定
- 用繁體中文回答

【問題】
{QUESTION}
```

### Claude Prompt（prompt_claude.txt）
```
你是批判分析員。以下是 Gemini 提供的情報資料，以及原始問題。

【原始問題】
{QUESTION}

【Gemini 情報】
{GEMINI_OUTPUT}

【你的任務】
1. 理解 Gemini 的資料內容
2. 找出漏洞、缺漏、不合理之處
3. 發表你對內容的分析與理解
4. 補充可能被忽略的面向
5. 用繁體中文回答

不要重複貼 Gemini 的內容，直接分析。
```

### Codex Prompt（prompt_codex.txt）
```
你是技術審核員。以下是原始問題、Gemini 的情報、以及 Claude 的分析。

【原始問題】
{QUESTION}

【Gemini 情報】
{GEMINI_OUTPUT}

【Claude 分析】
{CLAUDE_OUTPUT}

【你的任務】
1. 先判斷此問題是否涉及技術/邏輯/系統架構
2. 若是技術題：
   - 驗證 Gemini + Claude 的技術說法是否合理
   - 找出技術錯誤或邏輯矛盾
   - 整合三方資訊，形成最終成熟結論
3. 若非技術題：
   - 直接回覆：「此問題非技術性質，跳過技術審核。建議直接採納 Claude 分析。」
4. 用繁體中文回答
```

## 最終輸出格式（Telegram Markdown）

```
🔍 **3AI 管線結果**

━━━━━━━━━━━━━━━━━━━━
📡 **Gemini（情報搜集）**
━━━━━━━━━━━━━━━━━━━━
{GEMINI_SECTION}

━━━━━━━━━━━━━━━━━━━━
🔬 **Claude（批判分析）**
━━━━━━━━━━━━━━━━━━━━
{CLAUDE_SECTION}

━━━━━━━━━━━━━━━━━━━━
⚙️ **Codex（技術審核）**
━━━━━━━━━━━━━━━━━━━━
{CODEX_SECTION}
```

## 錯誤處理規則

| 情況 | 處理方式 |
|------|----------|
| Gemini 網路搜尋超時（>180s） | 自動用 fallback prompt 重試，本地知識回覆，標註「⚠️ 網路搜尋超時」 |
| Gemini fallback 也失敗 | 標記「⚠️ 網路搜尋超時，本地知識回覆亦失敗」，繼續下一棒 |
| Claude 超時 | 標記「⏱️ 超時」，跳過該段，繼續下一棒 |
| CLI 回傳錯誤 | 標記「❌ 失敗：{錯誤碼}」，繼續下一棒 |
| CLI 輸出為空 | 標記「⚠️ 無回應」，繼續下一棒 |
| 全部失敗 | 回傳錯誤總覽，建議 Scott 手動執行 |

任何單一 CLI 失敗**不中斷**整條管線，失敗段標記後繼續。

## 輸出截斷規則

- 每個 CLI 輸出最多保留 **4000 字元**（Telegram 訊息安全範圍）
- 超出部分截斷並加上 `(已截斷，原始輸出 N 字元)`
- 完整輸出存於共享空間備查：`C:\Users\chien\_3AI_WorkSpace\pipeline_results\`

## 注意事項
- 此技能消耗的是 3AI CLI 訂閱配額，不消耗 Hermes token
- Hermes 在此流程中等同於一個 shell script，只做 I/O
- 如果某個 CLI 持續失敗，Scott 需自行檢查該 CLI 的認證/配額狀態

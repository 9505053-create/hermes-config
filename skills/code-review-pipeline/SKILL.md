---
name: code-review-pipeline
description: "3AI 程式碼審查管線 — 用 ~!! 觸發，Gemini(審查)→Claude(修改)→Codex(驗證)，讀寫硬碟空間"
category: autonomous-ai-agents
trigger: "~!!"
---

# 3AI Code Review Pipeline — 程式碼審查管線

## 核心原則
**Hermes 在此技能中完全不讀取、不分析程式碼。** 只做：
1. 驗證檔案存在
2. 寫 prompt 檔（含檔案路徑）
3. 管道呼叫 CLI
4. 從 stdout 用標記（`<<<FIXED_CODE_START>>>` / `<<<FINAL_CODE_START>>>`）提取程式碼
5. 存入硬碟
6. 通知最終檔案路徑

## v3 改動（2026-05-05 WSL 實戰）
- **WSL 環境支援**：cmd.exe 不在 PATH，需用 `/mnt/c/Windows/System32/cmd.exe`
- **合併 Prompt 模式**：Claude/Codex sandbox 無法讀檔案，prompt 必須含原始碼+審查意見
- **Codex echo 問題**：Codex stdout 會 echo 完整 prompt，需過濾 <100 bytes 的 false positive 匹配
- **CLI fallback 邏輯**：WSL 原生 CLI 需 auth，失敗時 fallback 到 Windows npm 版本
- **審查報告自動生成**：`review_report_{ts}.md` 包含完整審查摘要

## v2 改動（2026-05-05）
- **CLI 不再 write_file**：CLI 環境為唯讀 sandbox，改為在 stdout 用標記輸出程式碼
- **Hermes 提取後存檔**：用正則提取 `<<<FIXED_CODE_*>>>` 和 `<<<FINAL_CODE_*>>>` 之間的內容
- **超時放寬**：300s → 600s（10 分鐘）
- **Execution Log**：每階段執行細節記錄到 `execution_log_{ts}.json`
- **輸出截斷放寬**：8000 → 16000 字元

## 觸發條件
使用者訊息以 `~!!` 開頭，後接檔案路徑。

## 使用方式

### 單一檔案
```
~!! code_review\input.py
~!! C:\Users\chien\projects\myapp\main.py
```

### 多檔案（ZIP）
```
~!! code_review\myproject.zip
```

## 流程架構

```
Scott 給路徑 (~!! code_review\input.py)
  │
  ▼
Hermes 驗證檔案存在（不讀內容）
  │
  ▼
┌─────────────────────────────────────┐
│  Gemini CLI（審查員）                │
│  - 讀取硬碟上的程式碼檔案            │
│  - 逐項檢查 bugs/安全/效能          │
│  - 輸出結構化審查意見（stdout）      │
│  - 不修改任何程式碼                  │
└────────────┬────────────────────────┘
             │ stdout（審查意見）
             ▼
┌─────────────────────────────────────┐
│  Claude CLI（修復工程師）            │
│  - 讀取原始程式碼 + 審查意見         │
│  - 依意見修改程式碼                  │
│  - stdout 輸出完整修改後程式碼       │
│  - 用 <<<FIXED_CODE_START>>> 包裹    │
└────────────┬────────────────────────┘
             │ stdout
             ▼
┌─────────────────────────────────────┐
│  Hermes（提取 + 存檔）               │
│  - 從 stdout 提取標記間的程式碼      │
│  - 存入硬碟：fixed_{timestamp}.*    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Codex CLI（最終驗證）               │
│  - 讀取修改後的程式碼（從 prompt）   │
│  - 驗證修改正確性                    │
│  - 檢查 regression                  │
│  - OK → 確認；需修正 → stdout 輸出  │
│  - 用 <<<FINAL_CODE_START>>> 包裹    │
└────────────┬────────────────────────┘
             │ stdout
             ▼
┌─────────────────────────────────────┐
│  Hermes（提取 + 存檔 + 通知）        │
│  - 提取 Codex 修正版（如有）         │
│  - 存入硬碟：final_{timestamp}.*    │
│  - 生成 execution_log.json          │
│  - 組裝結果回 Telegram               │
│  - 不做任何分析                      │
└─────────────────────────────────────┘
```

## 檔案結構

```
C:\Users\chien\_3AI_WorkSpace\
├── code_review\input.py          ← 你放程式碼的地方
├── code_review\project.zip       ← 或放 ZIP
└── code_reviews\
    └── review_{timestamp}\
        ├── _all_files_{ts}.txt   ← （多檔時合併）
        ├── execution_log_{ts}.json  ← 執行日誌（每階段 CLI 執行細節）
        └── output\
            ├── fixed_{ts}.*      ← Claude 修改版（從 stdout 提取）
            ├── final_{ts}.*      ← Codex 驗證版（若有進一步修正）
            └── review_report_{ts}.md  ← 完整審查報告
```

## Prompt 建構（v3 — 合併模式）

**關鍵發現：Claude 和 Codex sandbox 無法自行讀取硬碟檔案，只能從 stdin 接收完整內容。**

因此 prompt 必須包含所有必要資訊，不能只放檔案路徑。

### Gemini Prompt（獨立，只含指令+檔案路徑）
Gemini 能讀取檔案，所以 prompt 只需指令和檔案路徑：
```
You are a senior code reviewer...
**Files to review:**
The merged code file is at: C:\Users\chien\_3AI_WorkSpace\code_reviews\review_{ts}\_all_files_{ts}.txt
```

### Claude Prompt（合併：原始碼 + Gemini 審查意見）
Hermes 必須組裝一個合併 prompt：
1. 建立 prompt 頭部（指令 + 輸出格式）
2. 追加 `===== ORIGINAL CODE =====`
3. 追加 `_all_files_{ts}.txt` 全文
4. 追加 `===== REVIEW FINDINGS (from Gemini) =====`
5. 追加 `gemini_review_{ts}.txt` 全文
6. 追加 closing instructions

儲存為 `prompt_code_claude_combined.txt`，再 pipe 給 Claude。

### Codex Prompt（合併：原始碼 + Gemini 意見 + Claude 修復版）
同理，追加三個區塊：
1. 原始碼（`_all_files_{ts}.txt`）
2. Gemini 審查意見（`gemini_review_{ts}.txt`）
3. Claude 修復輸出（`claude_fixed_{ts}.txt`）

儲存為 `prompt_code_codex_combined.txt`。

### ⚠️ Codex 會 echo 整個 prompt 到 stdout

Codex stdout 會包含它接收到的完整 prompt（可能 30KB+），然後才輸出實際結果。
這導致：
- stdout 從 ~5KB 膨脹到 ~37KB
- `<<<FINAL_CODE_START:filename>>>` 的正則提取可能匹配到 prompt 模板文字

**解決方案：**
1. 用 `codex exec --skip-git-repo-check` 而非其他模式
2. 提取 `FINAL_CODE` 時，過濾掉 <100 bytes 的匹配（很可能是模板文字 echo）
3. 或在 Codex prompt 中使用不同標記格式避免與模板衝突

### Claude 輸出格式
```
（2-3 行修改摘要）

<<<FIXED_CODE_START>>>
（完整修改後程式碼）
<<<FIXED_CODE_END>>>
```

### Codex 輸出格式
```
（驗證結論）

<<<FINAL_CODE_START>>>
（修正後程式碼，僅在需要修正時）
<<<FINAL_CODE_END>>>
```

### 提取邏輯
1. 用正則搜尋 `<<<FIXED_CODE_START:(.*?)>>>(.*?)<<<FIXED_CODE_END:\1>>>`（含檔名）
2. 若無檔名格式，回退搜尋 `<<<FIXED_CODE_START>>>(.*?)<<<FIXED_CODE_END>>>`
3. 有標記 → 精確提取標記間內容 → 存檔
4. **過濾 false positive**：匹配內容 <100 bytes → 跳過（很可能是 prompt 模板 echo）
5. 無標記但有輸出 >50 字元 → 整段 stdout 備存
6. 無有效輸出 → 標記為無輸出

## CLI 呼叫指令

### 環境偵測（WSL vs Windows）

Hermes 可能在 WSL 或 Windows 原生環境執行。CLI 呼叫前必須先偵測：

```bash
# 1. 檢查 cmd.exe 可用路徑
which cmd.exe 2>/dev/null || echo "/mnt/c/Windows/System32/cmd.exe"

# 2. 檢查 WSL 原生 CLI（可能缺 auth）
which gemini 2>/dev/null && gemini --version
which claude 2>/dev/null && claude --version
```

**決策邏輯：**
- WSL 環境下，`gemini`/`claude` 原生 binary 需要 API Key 或登入
- 如果原生 CLI auth 失敗 → fallback 到 Windows npm 版本（`/mnt/c/Windows/System32/cmd.exe /c "..."`）
- cmd.exe 路徑：`/mnt/c/Windows/System32/cmd.exe`（不在 WSL PATH 中）

### Gemini（審查員）
```bash
# Windows cmd.exe（推薦，auth 通常已配好）
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt_code_gemini.txt | C:\Users\chien\AppData\Roaming\npm\gemini.cmd --skip-trust"
```

### Claude（修復工程師）
```bash
# ⚠️ Claude 需要「合併 prompt」：原始碼 + Gemini 審查意見都要在 prompt 中
# 因為 Claude sandbox 無法自行讀取檔案（只能從 stdin 接收完整內容）

# 建立合併 prompt（見下方 Prompt 建構章節）
# Windows cmd.exe 版本
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt_code_claude_combined.txt | C:\Users\chien\AppData\Roaming\npm\claude.cmd --print"
```

### Codex（最終驗證）
```bash
# ⚠️ Codex 同樣需要合併 prompt：原始碼 + Gemini 意見 + Claude 修復版
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt_code_codex_combined.txt | C:\Users\chien\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check"
```

## 與 ~! 管線的差異

| 項目 | ~! (問答管線) | ~!! (程式碼審查) |
|------|--------------|-----------------|
| 觸發詞 | `~!` / `!~` | `~!!` |
| 輸入 | 問題文字 | 檔案路徑 |
| 資料傳遞 | 問題嵌入 prompt | 檔案路徑嵌入 prompt，CLI 自行讀檔 |
| Gemini 角色 | 情報搜集 | 程式碼審查 |
| Claude 角色 | 批判分析 | 程式碼修復 + 存檔 |
| Codex 角色 | 技術審核 | 最終驗證 + 存檔 |
| 輸出 | Telegram 文字 | Telegram 文字 + 硬碟檔案 |
| prompt 大小 | 隨問題增長 | 固定（只有路徑+指令） |
| 輸出限制 | 4000 字元 | 16000 字元 |
| 超時 | 180s | 600s (10 min) |
| 技能目錄 | `3ai-pipeline/` | `code-review-pipeline/` |

## ⚠️ 關鍵發現：CLI 環境約束（2026-05-05 測試）

**Claude 和 Codex CLI 跑在唯讀 sandbox，沒有 write_file 工具。**
它們只能：
- ✅ 讀取檔案（從 stdin pipe 或檔案路徑）
- ✅ 產出文字到 stdout
- ❌ 不能直接寫檔到硬碟

**這改變了整個架構：**
- 原設計：Claude/Codex 自行 write_file → ❌ 不可行
- 正確做法：CLI 產出修改後程式碼到 stdout → Hermes 收集 → write_file 存檔
- Hermes 的 write_file 只是搬運 stdout → 磁碟，不需「理解」內容，token 增量極小

**其他約束：**
- Gemini 審查階段正常運作（42s），能讀檔並產出結構化意見
- Claude 300s 超時（多檔案 JSON 修改任務太重），需加長或拆分
- CLI 用 stdin pipe 傳 prompt（`type prompt.txt | cli.cmd`），不是直接檔案參數

## 修正後流程架構

```
Scott 給路徑 (~!! code_review\input.py)
  │
  ▼
Hermes 驗證檔案存在（不讀內容）
  │
  ▼
┌─────────────────────────────────────┐
│  Gemini CLI（審查員）                │
│  - 讀取硬碟上的程式碼檔案            │
│  - 輸出結構化審查意見到 stdout        │
│  - 不修改任何程式碼                  │
└────────────┬────────────────────────┘
             │ stdout（審查意見）
             ▼
┌─────────────────────────────────────┐
│  Claude CLI（修復工程師）            │
│  - stdin: 原始碼 + Gemini 審查意見   │
│  - stdout: 輸出完整修改後程式碼      │
│  - 無法存檔，由 Hermes 從 stdout 備存 │
└────────────┬────────────────────────┘
             │ stdout（修改後程式碼）
             ▼
         Hermes: write_file → fixed_{ts}.*
             │
             ▼
┌─────────────────────────────────────┐
│  Codex CLI（最終驗證）               │
│  - stdin: 修改後程式碼 + 原始意見    │
│  - stdout: 驗證意見或修正版程式碼    │
│  - 無法存檔，由 Hermes 從 stdout 備存 │
└────────────┬────────────────────────┘
             │ stdout
             ▼
         Hermes: write_file → final_{ts}.*（如果有修正版）
         Hermes: 組裝結果回 Telegram + 通知路徑
```

## ⚠️ 關鍵發現：CLI 環境約束（2026-05-05 測試）

**Codex 明確回報：「執行環境是唯讀 sandbox，沒有可用的 write_file 工具」**

這意味著：
- ❌ CLI **無法**直接 write_file 存到硬碟
- ✅ CLI **可以**讀取硬碟檔案（Gemini 成功讀檔審查）
- ✅ CLI **可以**在 stdout 輸出內容
- ➡️ 解決方案：CLI 用標記包裹程式碼輸出到 stdout，Hermes 提取後存檔

## 設計決策記錄

1. **獨立技能**：不修改現有 ~! 管線的穩定提示詞，完全獨立的 prompt 和腳本
2. **路徑傳遞**：使用者先存檔到共享空間，Hermes 只傳路徑給 CLI → prompt 大小固定，不受程式碼長度影響
3. **時間戳命名**：所有輸出檔用 `YYYYMMDD_HHMMSS` 避免覆蓋
4. **ZIP 支援**：自動解壓 → 合併為單一檔案 → CLI 審查 → 輸出報告
5. **stdout 標記提取（v2）**：CLI 用 `<<<FIXED_CODE_START>>>` 包裹程式碼，Hermes 用正則提取後存檔，避免 write_file 權限問題
6. **超時 600s（v2）**：程式碼審查+修改需較長時間，從 300s 放寬到 600s
7. **輸出截斷 16000 字元（v2）**：程式碼修改版可能很長
8. **Execution Log（v2）**：JSON 格式記錄每階段 CLI 執行細節，供追蹤
9. **備存機制**：若 CLI 未用標記格式，自動整段 stdout 備存

## 錯誤處理規則

| 情況 | 處理方式 |
|------|---------|
| 檔案不存在 | ❌ 直接報錯，不啟動管線 |
| ZIP 解壓失敗 | ❌ 報錯，顯示錯誤訊息 |
| ZIP 無原始碼 | ❌ 提示確認 ZIP 內容 |
| Gemini 超時 | 自動 fallback（本地知識），標註 ⚠️ |
| Claude 超時 | 標記 ⏱️，跳到 Codex 階段 |
| Claude 未用標記格式 | 自動整段 stdout 備存 |
| Codex 超時 | 標記 ⏱️，最終版本為 Claude 的修改版 |
| 全部失敗 | 回傳錯誤總覽 |
| Codex echo 污染 | 正則提取到 <100 bytes 匹配 → 視為 false positive，自動刪除 |

## 注意事項
- 此技能消耗 3AI CLI 訂閱配額，不消耗 Hermes token（Hermes 增量僅限檔案 I/O）
- CLI 為唯讀 sandbox：可讀硬碟檔案，不可 write_file
- CLI 透過 stdout 輸出程式碼，用 `<<<FIXED_CODE_*>>>` 標記包裹
- Hermes 用正則提取標記內容，不讀取/分析程式碼
- 大型專案 ZIP 可能導致 CLI 回應時間較長（上限 600s）
- 完整審查報告 + execution log 同時存在硬碟，可供後續查閱

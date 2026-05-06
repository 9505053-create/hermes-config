---
name: code-review-pipeline
description: "3AI 程式碼審查管線 — 用 ~!! 觸發，Gemini(審查)→Claude(修復)→Codex(驗證)，含自癒迴圈與結構化報告"
category: autonomous-ai-agents
trigger: "~!!"
---

# 3AI Code Review Pipeline — 程式碼審查管線

## 核心原則
**Hermes 在此技能中完全不讀取、不分析程式碼。** 只做：
1. 驗證檔案存在
2. 寫 prompt 檔（含檔案路徑，不含程式碼）
3. 管道呼叫 CLI（CLI 自行讀寫硬碟）
4. 驗證輸出檔案存在
5. 組裝最終結構化報告

**Hermes 不做深度分析。所有分析、修復、驗證交給 3AI CLI。Hermes 只消耗最小必要 token。**

## v5 改動（2026-05-06 — 顧問團建議整合）
- **自癒迴圈（Self-healing）**：Codex FAIL 時自動回傳給 Claude 二次修復，最多 2 輪
- **結構化最終報告**：固定格式包含 Verdict / Changed Files / Fixed Issues / Remaining Risks / Need Scott Decision
- **Runtime 驗證鉤子**：可選擴充 build/test 步驟（預留給非 JSON 專案）
- **每階段獨立輸出檔案**：確保可追溯、可審查
- **Hermes 零分析條款**：明確禁止 Hermes 自行長篇推理

## v4 改動（保留）
- 三 CLI 皆可讀寫硬碟，prompt 只含路徑
- 移除合併 prompt、stdout 標記提取、Codex echo 過濾

## 觸發條件
使用者訊息以 `~!!` 開頭，後接檔案路徑。

## 使用方式

```
~!! code_review\input.py
~!! code_review\myproject.zip
```

## 流程架構（v5 — 含自癒迴圈）

```
Scott 給路徑 (~!! ...)
  │
  ▼
Hermes: 驗證檔案存在 → 建立目錄結構 → 寫 prompts
  │
  ▼
┌─────────────────────────────────────┐
│  Phase 1: Gemini CLI（審查員）       │
│  - 讀取原始碼                        │
│  - 產出 gemini_review.md            │
│  - 超時 → 跳過，Claude 代審          │
└────────────┬────────────────────────┘
             │
             ▼
Hermes: 確認 review.md 存在 → 寫 Claude prompt
  │
  ▼
┌─────────────────────────────────────┐
│  Phase 2: Claude CLI（修復工程師）   │
│  - 讀取原始碼 + review               │
│  - 產出 fixed_code.* + summary.md   │
│  - 超時 → 跳到 Codex 代修            │
└────────────┬────────────────────────┘
             │
             ▼
Hermes: 確認 fixed_code.* 存在 → 寫 Codex prompt
  │
  ▼
┌─────────────────────────────────────┐
│  Phase 3: Codex CLI（驗證員）        │
│  - 讀取原始碼 + review + fixed       │
│  - 產出 codex_verification.md       │
│  - 判定: PASS / FAIL                │
└────────────┬────────────────────────┘
             │
             ▼
         ┌───┴───┐
         │ PASS? │
         └───┬───┘
        YES  │  NO
         │   │   │
         │   │   ▼
         │   │ ┌─────────────────────────────┐
         │   │ │ 自癒迴圈 (retry_count < 2)  │
         │   │ │ Hermes: 寫 retry prompt     │
         │   │ │   → 包含 Codex FAIL 原因    │
         │   │ │   → Claude 二次修復          │
         │   │ │   → Codex 再次驗證          │
         │   │ └──────────┬──────────────────┘
         │   │            │
         │   │         超過 2 輪？
         │   │        YES → ESCALATE
         │   │             │
         ▼   ▼             ▼
    ┌─────────────────────────────────┐
    │  Hermes: 組裝最終報告            │
    │  - review_report.md（結構化）    │
    │  - 通知 Scott 結果 + 路徑        │
    └─────────────────────────────────┘
```

## 檔案結構

```
code_reviews\review_{timestamp}\
├── _source\                        ← 原始碼
├── _prompts\                       ← prompt 檔案
│   ├── prompt_gemini.txt
│   ├── prompt_claude.txt
│   ├── prompt_codex.txt
│   └── prompt_codex_retry.txt     ← 自癒迴圈用
└── output\
    ├── gemini_review.md            ← Phase 1 審查報告
    ├── claude_summary.md           ← Phase 2 修復摘要
    ├── fixed_code.*                ← Phase 2 修復版程式碼
    ├── codex_verification.md       ← Phase 3 驗證報告
    ├── final_code.*                ← Phase 3 最終修正版（如有）
    ├── execution_log.json          ← 每階段執行細節
    └── review_report.md            ← 最終結構化報告
```

## Prompt 模板

### Gemini Prompt（審查）
```
You are a senior code reviewer. Read the code file(s) below and perform a thorough review.

**Source file(s):**
{SOURCE_PATH}

**Your task:**
1. Read the source file(s) from the path above
2. Review for: bugs, security issues, performance, code quality, best practices
3. Write your review to: {OUTPUT_DIR}\gemini_review.md

Use structured format:
## Summary
## Issues Found (Critical/Major/Minor, with line numbers)
## Cross-File Consistency
## Suggestions
## Verdict: PASS / NEEDS_FIXES

Write your review to the output file now.
```

### Claude Prompt（修復）
```
You are a code fixer. Read the original code and the review findings, then fix all issues.

**Original code:**
{SOURCE_PATH}

**Review findings:**
{OUTPUT_DIR}\gemini_review.md

**Your task:**
1. Read both files above
2. Fix all issues identified in the review
3. Write the fixed code to: {OUTPUT_DIR}\fixed_code{EXT}
4. Write a brief summary of changes to: {OUTPUT_DIR}\claude_summary.md

Important: Preserve the original filename and extension. Write both files now.
```

### Claude Retry Prompt（自癒迴圈）
```
You previously fixed code but the verification FAILED. Here is the verification report explaining what went wrong. Fix the remaining issues.

**Original code:**
{SOURCE_PATH}

**Your previous fix:**
{OUTPUT_DIR}\fixed_code{EXT}

**Verification failure report:**
{OUTPUT_DIR}\codex_verification.md

**Your task:**
1. Read the verification report to understand what FAILED
2. Fix the remaining issues in your previous fix
3. Overwrite: {OUTPUT_DIR}\fixed_code{EXT}
4. Update: {OUTPUT_DIR}\claude_summary.md (append retry note)

This is retry attempt {RETRY_COUNT} of 2. Fix carefully.
```

### Codex Prompt（驗證）
```
You are a final validator. Read the original code, the review, and the fixed version. Verify correctness.

**Original code:**
{SOURCE_PATH}

**Review findings:**
{OUTPUT_DIR}\gemini_review.md

**Fixed code:**
{OUTPUT_DIR}\fixed_code{EXT}

**Your task:**
1. Read all files above
2. Verify the fixes address all review issues
3. Check for regressions or new bugs introduced
4. Write verification report to: {OUTPUT_DIR}\codex_verification.md

**Report format (MANDATORY):**
## Verdict
One of: PASS / FAIL

## Issues Verified
- [x] or [ ] for each review issue

## New Issues Found
Any regressions or new problems from the fixes

## Remaining Risks
Things that could still go wrong

If PASS: Write "VERIFIED: All issues resolved"
If FAIL: Clearly explain what is still broken so the fixer can retry. Write corrected code to {OUTPUT_DIR}\final_code{EXT} if you can fix it directly.

Write your report now.
```

## CLI 呼叫指令

```bash
# Gemini（審查）— 注意：cd 到 review 目錄，非 _3AI_WorkSpace
# Gemini sandbox 只允許工作目錄下的檔案，source 路徑若在 workdir 外會被拒絕
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\\Users\\chien\\_3AI_WorkSpace\\code_reviews\\review_{TIMESTAMP} && type _prompts\\prompt_gemini.txt | C:\\Users\\chien\\AppData\\Roaming\\npm\\gemini.cmd --skip-trust --approval-mode yolo"

# Claude（修復）
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type {PROMPT} | C:\Users\chien\AppData\Roaming\npm\claude.cmd --print --allowedTools Bash Write Edit"

# Codex（驗證）
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type {PROMPT} | C:\Users\chien\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check --sandbox workspace-write"
```

## 最終報告格式（review_report.md）

```md
# {PROJECT} — 3AI 程式碼審查報告

**審查時間：** {TIMESTAMP}
**專案：** {PROJECT_NAME}
**檔案：** {FILE_LIST}

## Verdict: PASS / WARNING / FAIL

## Pipeline 執行摘要
| 階段 | 狀態 | 耗時 | 說明 |
|------|------|------|------|
| Gemini | ✅/⚠️/❌ | ?s | ... |
| Claude | ✅/⏱️/❌ | ?s | ... |
| Codex | ✅/❌ | ?s | ... |
| 自癒迴圈 | ?輪 | ?s | PASS/ESCALATE |

## Changed Files
- file1.* — description
- file2.* — description

## Fixed Issues
1. [severity] issue description → fixed
2. ...

## Remaining Risks
1. risk description
2. ...

## Need Scott Decision
1. question requiring human judgment
2. ...

## Recommended Next Step
- action item
```

## 錯誤處理規則

| 情況 | 處理方式 |
|------|---------|
| 檔案不存在 | ❌ 直接報錯，不啟動管線 |
| ZIP 解壓失敗 | ❌ 報錯，顯示錯誤訊息 |
| Gemini 超時 | ⚠️ 跳過，Claude 代審+修復 |
| Claude 超時 | ⏱️ 跳到 Codex 代修+驗證 |
| Claude 未產出 fixed_code | ⚠️ Codex 自行修復+驗證 |
| Codex FAIL（retry < 2） | 🔄 自癒迴圈：Codex 原因 → Claude 重修 → Codex 再驗 |
| Codex FAIL（retry ≥ 2） | 🚨 ESCALATE：標記需人工介入 |
| Codex 超時 | ⏱️ 最終版為 Claude 的修復版 |
| 全部失敗 | 回傳錯誤總覽，建議 Scott 手動執行 |

## 已知 Pitfalls

| 問題 | 原因 | 解法 |
|------|------|------|
| Gemini Error: "Path not in workspace" | `--approval-mode yolo` sandbox 限制，只能讀工作目錄下的檔案 | CLI 命令 `cd /d` 到 review 目錄（非 `_3AI_WorkSpace`），source 檔案會被拒絕是預期外行為，但 review 目錄內的 prompt/output 檔案可正常操作 |
| `cmd.exe` UNC path warning | WSL 啟動 cmd.exe 時的工作目錄是 `\\wsl.localhost\...`，Windows 不支援 UNC 作為 cwd | 無害，可忽略。`cd /d` 會正確切換到 Windows 路徑 |
| Gemini Node.js pty crash | Gemini CLI 內部 conpty_console_list_agent 崩潰 | 不影響主流程，Gemini 仍會完成 review 並寫入檔案 |
| Claude `--print` 無互動 | 這是預期行為，stdout 直接回傳結果 | 無需修復 |

## 注意事項
- 此技能消耗 3AI CLI 訂閱配額，不消耗 Hermes token
- Hermes 嚴禁自行深度分析程式碼，所有分析交給 3AI CLI
- CLI 直接讀寫硬碟，prompt 只含路徑不含程式碼
- 自癒迴圈上限 2 輪，超過自動 escalate 給 Scott
- 每階段獨立輸出檔案，確保可追溯
- Runtime 驗證（build/test）可於 prompt 中擴充，非預設行為

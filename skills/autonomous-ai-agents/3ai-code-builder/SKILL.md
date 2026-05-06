---
name: 3ai-code-builder
description: "3AI 程式建構管線 v2 — 用 ~!!! 觸發，Phase 0(架構)→Claude(建構)→Gemini(審查)→Lint→Codex(修正)→Build+Test→診斷式修復→Final Report"
category: autonomous-ai-agents
trigger: "~!!!"
---

# 3AI Code Builder v2 — 程式建構管線

## 核心原則
**Hermes 在此技能中完全不讀取、不分析程式碼。** 只做：
1. 驗證 MD 檔案存在、判斷模式（frontmatter > 檔名 fallback）
2. 呼叫 pipeline.py（CLI 自行讀寫硬碟）
3. 收集 pipeline.py 輸出的最終報告路徑
4. 通知 Scott 結果

## 觸發條件
```
~!!! 路徑\MD檔名.md
```

## 模式判斷（v2 升級）
**優先順序：**
1. MD 內 YAML frontmatter 的 `mode` 欄位（new / modify / review / repair）
2. 檔名含 `PR` → new
3. 檔名含 `comment` → modify
4. 皆不符合 → 報錯停止

**Frontmatter 範例：**
```yaml
---
mode: new
project_name: MiniCalc
language: python
framework: tkinter
target_python: "3.8+"
---
```

## v2 改動摘要

| 項目 | v1 | v2 |
|------|----|----|
| 架構規劃 | ❌ 無 | Phase 0 Claude 先寫 arch_plan.md |
| 模式判斷 | 純檔名 | Frontmatter 優先 + 檔名 fallback |
| Claude 產出 | 只寫程式碼 | 程式碼 + README + tests/ + requirements.txt |
| Gemini 審查 | 自然語言 | 結構化表格（ID/Severity/Category/Must Fix）|
| Lint | ❌ 無 | Phase 2.5 py_compile 靜態檢查 |
| Codex 修正 | 模糊回應 | 逐條對應 Gemini ID + Accept/Reject/Defer |
| Build 驗證 | py_compile only | 依賴安裝 → 編譯 → 匯入 → 測試 → smoke test |
| 修復策略 | 盲目重試 | 診斷式：Gemini 分析根因 → Codex 照 fix_instruction 修 |
| 最終報告 | build_report.md | final_report.md（結構化全流程報告）|

## 流程架構 v2

```
Scott 給 MD 路徑 (~!!! ...)
  │
  ▼
Phase 0: 架構規劃（Claude）
  讀 PR → 產 arch_plan.md（需求/架構/檔案樹/風險）
  │
  ▼
Phase 1: 實作（Claude）
  讀 PR + arch_plan → 產程式碼 + README + tests/ + requirements.txt
  │
  ▼
Phase 2: 結構化審查（Gemini）
  讀程式碼 → 產 gemini_review.md（表格格式）
  │
  ▼
Phase 2.5: 靜態檢查
  py_compile + import smoke test → 產 lint_report.md
  │
  ▼
Phase 3: 逐條修正（Codex）
  讀 review → 逐條 Accept/Reject → 修正 → 產 codex_report.md
  │
  ▼
Phase 4: Build + Test
  依賴安裝 → 編譯 → 測試 → 產 build_log.md
  │
  ├── PASS → Phase 5
  └── FAIL → 診斷式修復（最多 2 輪）
              Gemini 分析根因 → 產 fix_instruction.md
              Codex 照指令修正 → 重新 Build
  │
  ▼
Phase 5: 最終報告（Claude）
  整合所有報告 → 產 final_report.md
  │
  ▼
Hermes: 通知 Scott 結果 + 路徑
```

## 時間戳目錄結構

```
{MD所在目錄}/build_YYYYMMDD_HHMMSS/
├── prompts/                    ← 所有 prompt 檔案
│   ├── prompt_phase0.txt
│   ├── prompt_phase1.txt
│   ├── prompt_phase2.txt
│   ├── prompt_phase3.txt
│   ├── prompt_phase5.txt
│   ├── prompt_diagnose1.txt   ← 診斷式修復（如有）
│   └── prompt_fix1.txt
│
├── output/                     ← 所有產出
│   ├── arch_plan.md           ← Phase 0 架構規劃
│   ├── claude_plan.md         ← Phase 1 實作計劃
│   ├── app.py / *.js / ...    ← 程式碼
│   ├── README.md              ← 專案說明
│   ├── requirements.txt       ← 依賴
│   ├── tests/test_basic.py    ← 基本測試
│   ├── gemini_review.md       ← Phase 2 結構化審查
│   ├── lint_report.md         ← Phase 2.5 靜態檢查
│   ├── codex_report.md        ← Phase 3 逐條修正報告
│   ├── build_log.md           ← Phase 4 Build 記錄
│   ├── fix_instruction.md     ← 診斷式修復指引（如有）
│   └── final_report.md        ← Phase 5 最終報告
│
└── raw/                        ← CLI 原始輸出
    ├── phase0_claude_stdout.txt
    ├── phase1_claude_stdout.txt
    ├── phase2_gemini_stdout.txt
    ├── phase3_codex_stdout.txt
    ├── diagnose1_stdout.txt
    ├── fix1_codex_stdout.txt
    └── phase5_claude_stdout.txt
```

## 最終報告格式（final_report.md）

```md
# Final Report — {project_name}

## Pipeline Result
| Phase | Status | Output File |
|-------|--------|-------------|
| Phase 0 Architecture | ✅/❌ | arch_plan.md |
| Phase 1 Implementation | ✅/❌ | claude_plan.md |
| Phase 2 Review | ✅/⚠️/❌ | gemini_review.md |
| Phase 2.5 Lint | ✅/⏭️ | lint_report.md |
| Phase 3 Fix | ✅/❌ | codex_report.md |
| Phase 4 Build/Test | ✅/❌ | build_log.md |

## Final Verdict
PASS / PASS_WITH_WARNINGS / FAIL

判定規則：
- PASS = 所有 Phase 通過，Gemini Must Fix 全部處理
- PASS_WITH_WARNINGS = build 通過但有未處理 warning
- FAIL = build 失敗或有 Critical 未修復
```

## 錯誤處理規則

| 情況 | 處理方式 |
|------|---------|
| MD 檔案不存在 | ❌ 報錯停止 |
| 無法判斷模式 | ❌ 報錯，要求加 frontmatter |
| Phase 0 失敗 | ⚠️ 跳過架構規劃，Phase 1 直接做 |
| Phase 1 Claude 失敗 | ❌ 終止（無程式碼無法繼續）|
| Phase 2 Gemini 超時 | ⚠️ 跳過，Codex 自行判斷 |
| Phase 2.5 Lint 失敗 | ⚠️ 記錄，不中斷 |
| Phase 3 Codex 超時 | ⏱️ 用 Claude 原始版 |
| Build 失敗（round 1） | 🔄 診斷式修復：Gemini 分析 → Codex 修 |
| Build 失敗（round 2） | 🚨 ESCALATE |
| Phase 5 失敗 | 產最小 final_report.md |

## CLI 呼叫指令

```bash
# Claude（Phase 0/1/5）
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | claude.cmd --print --allowedTools Bash Write Edit"

# Gemini（Phase 2/診斷）
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | gemini.cmd --skip-trust --approval-mode yolo"

# Codex（Phase 3/修復）
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | codex.cmd exec --skip-git-repo-check --sandbox workspace-write"
```

## 注意事項
- 此技能消耗 3AI CLI 訂閱配額，不消耗 Hermes token
- Hermes 嚴禁自行深度分析程式碼，所有分析交給 3AI CLI
- CLI 直接讀寫硬碟，prompt 只含路徑不含程式碼
- 診斷式修復上限 2 輪，超過自動 escalate 給 Scott
- 時間戳目錄確保同一個 MD 可多次執行不覆蓋
- v2 新增 Phase 0 + 2.5 + 5，執行時間較 v1 長約 5-10 分鐘

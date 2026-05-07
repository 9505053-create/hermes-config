---
name: 3ai-code-builder
description: "3AI 程式建構管線 v2.4 — 用 ~!!! 觸發，Artifact Detection→Phase 0(架構+sanity check)→Contract Check(fail-closed)→Codex(建構)→Gemini(審查)→Verdict Decision Tree→Lint→Claude(獨立修正+Regression Test)→Build+Test(AST安全檢查+動態掃描)→診斷式修復→Final Report→自動清理"
category: autonomous-ai-agents
trigger: "~!!!"
---

# 3AI Code Builder v2.4 — 程式建構管線

## 核心原則
**Hermes 在此技能中完全不讀取、不分析程式碼。** 只做：
1. 驗證 MD 檔案存在、判斷模式（frontmatter > 檔名 fallback）
2. 建立時間戳目錄（`build_YYYYMMDD_HHMMSS/prompts/`、`output/`、`raw/`）
3. 用 `write_file` 產生各 phase 的 prompt 檔案到 `prompts/` 目錄
4. 依序呼叫 3AI CLI（Codex→Gemini→Claude）執行各 phase
5. 驗證各 phase 產出檔案存在
6. 產出 execution_log.json + 打包 zip
7. 通知 Scott 結果

**Prompt 寫入方式：** 直接用 Hermes `write_file` 工具寫到 `{build_dir}/prompts/prompt_phaseN.txt`，不需要 Python 腳本中轉。

## 預檢步驟（觸發 ~!!! 前建議執行）

在跑正式管線前，先確認 3AI CLI 環境健全：

### 快速健康檢查
```bash
python3 ~/.hermes/scripts/cli_health_check.py --all
```
同時測試 Claude / Codex / Gemini，每個發送極簡訊息，回報：
- ✅ HEALTHY / ⚠️ RATE_LIMITED / 🔥 CAPACITY_FULL / 🔑 AUTH_ERROR / ⏱️ TIMEOUT

### Gemini 429 壓力測試（當健康檢查發現 Gemini 異常時）
```bash
python3 ~/.hermes/scripts/gemini_429_test.py --count 5 --interval 10
```
連續發送 N 條測試訊息，統計 429 出現頻率：
- 0 次 429 → HEALTHY
- <30% → DEGRADED
- >30% → UNHEALTHY

### 執行原則
- 所有 CLI 都 ✅ → 直接跑 ~!!! 管線
- 有 ⚠️/🔥 → 等冷卻期結束後重測，確認健全再跑
- 嚴禁在 CLI 不健全時跑管線（避免省略步驟或產出品質不穩）

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

## v2.1 改動摘要 (2026-05-07)

| 項目 | v2 | v2.1 |
|------|-----|------|
| Artifact Detection | ❌ 假設都是 code | 根據副檔名+內容分流 PRD/Code/Config |
| Verdict 決策 | issues_found > 0 就進 fix | Verdict Decision Tree：PASS+Minor 跳過 fix |
| User Intent | ❌ 無 | 偵測 disclaimer（不用太認真/正式），控制 auto-fix |
| Codex 獨立性 | Gemini 回音 | 獨立第二審，義務找新問題 |
| Output Package | 散落 output/ | 自動打包 project_*.zip 或 review_*.zip |
| Diff 產出 | ❌ 無 | Phase 3 有修改時產 diff.md |
| 執行計時 | ~推估 | execution_log.json 用真實 start/end time |
| import_cmd | 引號拼接 bug | f-string 正確嵌套 |
| PRD Review | ❌ 只走 code pipeline | 獨立 PRD Review Pipeline（document review prompt） |
| Scott 決策門檻 | ❌ 無 | PASS+Major+casual_intent → need_scott_decision.md |

## v2.2 改動摘要 (2026-05-07, 基於 3AI Web 顧問團三方共識)

| 項目 | v2.1 | v2.2 |
|------|------|------|
| Contract Check | ❌ arch_plan 與實際產出無人比對 | Phase 1.5：自動比對 expected vs actual，產 contract_check.md |
| 證據鏈 | build_log.md 是 LLM 自述 | subprocess capture raw log（test_raw.txt, compile_raw.txt, test_result.json） |
| Skip Logic | Low → 直接跳過 | 可重現邏輯錯誤 → regression test；style/doc → defer |
| 決策矩陣 | 隱性散落 | 明確 3×3（intent × severity → action）矩陣 |
| CLI 啟動 | 手動 cmd.exe 路徑 | ai_cli_wrapper.py 統一介面，stderr 過濾噪音 |
| tkinter import | module-level import | Phase 1 prompt 約束：延遲 import 到 UI class |
| 自動打包 ZIP | 自動產出 | 取消，Scott 手動在外層壓縮 |
| 暫存清理 | ❌ 無 | 交付前自動清理 .pytest_cache、__pycache__、重複檔 |
| Prompt 路徑 | 反斜線 bug 偶建重複檔 | 統一正斜線 |

**顧問團評分：** Gemini ★★★★☆ / ChatGPT 7/10 / Claude 6.5/10 → 目標修完後 8.5+/10

## v2.3 改動摘要 (2026-05-07, 基於 3AI 顧問團三方共識修復)

| 項目 | v2.2 | v2.3 |
|------|------|------|
| Contract Check fail-closed | ❌ expected=0 → PASS | ✅ expected=0 → FAIL + 詳細錯誤訊息 |
| 測試檔掃描 | hardcode `test_calculator.py` | 動態掃描 `tests/test_*.py` |
| 安全檢查 | crude grep（誤判 evaluates→eval） | AST-based：真正分析 Call node |
| 主模組發現 | hardcode `calculator.py` | 動態從 output/ 根目錄發現 |
| Phase 0 sanity check | ❌ 無 | SKILL.md 紀錄：Phase 1.5 已自動 fail-closed |

**顧問團評分目標：** 8.5+/10

## v2.4 改動摘要 (2026-05-07, 基於額度管理優化)

| 項目 | v2.3 | v2.4 |
|------|------|------|
| Phase 0/1 執行者 | Claude | **Codex**（配額較多，扛重活） |
| Phase 3 執行者 | Codex | **Claude**（配額珍貴，用在精修） |
| 額度耗盡策略 | 自動 fallback Gemini | 🛑 **停止 + 通知 Scott**，嚴禁自動 fallback |
| 額度管理原則 | 無 | 顧問團用 Opus 4.7，需保留配額給高品質分析 |
| pytest 快取清理 | Phase 5 後清理 | **Phase 4 pytest 後立即清理**（避免 Windows 權限鎖死） |
| build_runner.py | 無自動清理 | pytest 完成後自動 walk + rmtree 快取目錄 |
| 前置檢查 | ❌ 無 | **Pre-flight Check**：CLI 可用性 + Gemini 429 壓力測試（10 次，>3 次 429 就停止） |
| 腳本工具 | ❌ 無 | cli_availability_check.py + gemini_availability_test.py |

## 流程架構 v2.2

```
Scott 給 MD 路徑 (~!!! ...)
  │
  ▼
★ Step 0: Pre-flight Check（v2.4 強制）★
  1. cli_availability_check.py — 確認 Claude/Codex/Gemini 能回應
  2. gemini_availability_test.py --count 10 --interval 3 — 連續 10 條測試
     判斷規則：429 出現 > 3 次（不含 3）→ 🛑 停止，通知 Scott
     判斷規則：429 出現 ≤ 3 次 → ✅ 通過，繼續流程
  3. 三個 CLI 都必須 ✅ HEALTHY 才能繼續
  若任何一項不通過 → 通知 Scott「前置檢查未通過，建議等待」，停止管線
  │
  ▼
Step 0.5: Artifact Type Detection
  副檔名+內容+frontmatter → PRD / Source Code / Config / Unknown
  產 artifact_manifest.json
  │
  ▼
Step 0.5: Intent Alignment Check
  掃描 disclaimer（大概寫寫/不用太認真/production）
  產 intent_alignment_check.md
  │
  ├── PRD (no mode:new) ──→ PRD Review Pipeline ──→ review_*.zip ──→ END
  │
  ▼ (mode:new / source_code / config)
Phase 0: 架構規劃（Codex）
  讀 PR → 產 arch_plan.md
  │
  ▼
Phase 1: 實作（Codex）
  讀 PR + arch_plan → 產程式碼 + README + tests/ + requirements.txt
  │
  ▼
★ Phase 1.5: Contract Check（v2.2 新增）★
  比對 arch_plan.md 預期檔案 vs output/ 實際檔案
  產 contract_check.md
  │
  ├── 無 drift → 繼續
  ├── drift + casual → 記錄 accepted → 繼續
  └── drift + production → 報警 → 修正後才能繼續
  │
  ▼
Phase 2: 結構化審查（Gemini）
  讀程式碼 → 產 gemini_review.md（表格格式）
  │
  ▼
★ Verdict Decision Tree（v2.2 升級）★
  │
  ├── PASS + Minor only ──→ 跳過 Phase 3 → Phase 4 Build
  ├── PASS + Low + 可重現邏輯錯誤 ──→ 自動新增 regression test → Phase 4
  ├── PASS + Low + 純 style/doc ──→ defer（記錄原因）→ Phase 4
  ├── PASS + Medium ──→ Phase 3 Fix
  ├── PASS + Major + casual_intent ──→ need_scott_decision.md → 等 Scott
  ├── PASS + Major + production_intent ──→ 進 Phase 3 Fix
  ├── PASS_WITH_WARNINGS ──→ 同上邏輯
  ├── NEEDS_FIXES / FAIL ──→ 進 Phase 3 Fix
  └── Unknown ──→ 安全預設進 Phase 3

  判斷「可重現邏輯錯誤」規則：
  - Review 提到 "state transition"、"incorrect behavior"、"bug"
  - Review 有具體重現步驟（"press X then Y → wrong result"）
  - Category 是 Correctness 或 UI Logic
  │
  ▼
Phase 2.5: 靜態檢查（v2.2 強化）
  subprocess capture → lint_compile_raw.txt, lint_security_raw.txt
  py_compile + import smoke test + grep eval/exec/subprocess
  → 產 lint_report.md（LLM 摘要）+ raw log
  │
  ▼ (if not skipped)
Phase 3: 獨立審查+修正（Claude）
  不只是 Gemini 回音，義務找新問題
  + 如觸發 regression test：新增 test case 到 tests/
  → 產 claude_report.md + diff.md + regression_test_report.md（如有）
  │
  ▼
Phase 4: Build + Test（v2.2 強化證據鏈）
  subprocess capture 所有操作：
  1. py_compile calculator.py → compile_calculator_raw.txt
  2. py_compile tests/ → compile_tests_raw.txt
  3. pytest -v → test_raw.txt + test_result.json
  4. import smoke test → import_raw.txt
  5. security grep → security_grep_raw.txt
  LLM 讀 raw → 摘要寫 build_log.md
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
Auto Cleanup（v2.2 新增）
  移除 .pytest_cache/、__pycache__/、重複檔
  保留精簡目錄供 Scott 打包
  │
  ▼
Hermes: 通知 Scott 結果 + 路徑（不再自動產 ZIP）
```

★ Intent × Severity 決策矩陣（v2.2）★

|              | Low                    | Medium               | High/Critical        |
|--------------|------------------------|----------------------|----------------------|
| casual       | defer + 記錄原因        | regression test      | need_scott_decision  |
| tool         | regression test        | Phase 3 Fix          | Phase 3 Fix          |
| production   | Phase 3 Fix            | Phase 3 Fix          | Phase 3 Fix + 停止   |

觸發 need_scott_decision.md 條件：
- 任何 High/Critical severity **且為 PRD 核心需求**
- Medium + production intent
- 任何有「安全疑慮」的 finding

**重要澄清：High severity 不自動 = need_scott_decision**
如果 High issue 對應的是 PRD 中「額外功能/加分項」而非核心需求 → 走 DEFER，不進 Phase 3。
判斷方式：比對 issue 描述與 PRD「核心功能」section，若不在核心功能 → DEFER + 記錄原因。

**3AI 額度管理鐵律（2026-05-07 起）：**
- 任何 3AI CLI（Claude / Gemini / Codex）觸發 rate limit → 🛑 **立即停止管線**
- 通知 Scott：哪個 CLI 額度耗盡、重置時間
- **嚴禁自動 fallback 到其他 CLI** — Scott 的顧問團用 Opus 4.7，額度消耗快，需要保留
- 等 Scott 決定：等冷卻期結束後繼續，或先暫停
- 同理，Gemini/Codex 額度耗盡也適用此規則

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
│   ├── artifact_manifest.json  ← 檔案類型偵測結果
│   ├── intent_alignment_check.md ← User Intent 分析
│   ├── arch_plan.md           ← Phase 0 架構規劃
│   ├── contract_check.md      ← v2.2: Phase 1.5 契約檢查
│   ├── claude_plan.md         ← Phase 1 實作計劃
│   ├── app.py / *.js / ...    ← 程式碼
│   ├── README.md              ← 專案說明
│   ├── requirements.txt       ← 依賴
│   ├── tests/test_basic.py    ← 基本測試
│   ├── tests/test_regression*.py ← v2.2: 回歸測試（如有）
│   ├── gemini_review.md       ← Phase 2 結構化審查
│   ├── lint_report.md         ← Phase 2.5 靜態檢查（LLM 摘要）
│   ├── codex_report.md        ← Phase 3 獨立審查報告
│   ├── diff.md                ← 修改 diff
│   ├── regression_test_report.md ← v2.2: 回歸測試報告（如有）
│   ├── build_log.md           ← Phase 4 Build 記錄（LLM 摘要）
│   ├── fix_instruction.md     ← 診斷式修復指引（如有）
│   ├── need_scott_decision.md ← 需 Scott 決策時產出
│   ├── final_report.md        ← Phase 5 最終報告
│   └── execution_log.json     ← 真實計時
│
└── raw/                        ← v2.2: 強制保留所有原始輸出（證據鏈）
    ├── phase0_codex_stdout.txt
    ├── phase1_codex_stdout.txt
    ├── contract_check_raw.txt  ← v2.2: 契約檢查原始
    ├── phase2_gemini_stdout.txt
    ├── lint_compile_raw.txt    ← v2.2: py_compile 原始
    ├── lint_security_raw.txt   ← v2.2: grep 原始
    ├── phase3_claude_stdout.txt
    ├── regression_raw.txt      ← v2.2: 回歸測試原始（如有）
    ├── compile_calculator_raw.txt ← v2.2: Phase 4 編譯原始
    ├── compile_tests_raw.txt   ← v2.2: 測試編譯原始
    ├── test_raw.txt            ← v2.2: pytest 完整原始輸出
    ├── test_result.json        ← v2.2: pytest 結構化結果
    ├── import_raw.txt          ← v2.2: import smoke test 原始
    ├── security_grep_raw.txt   ← v2.2: 安全掃描原始
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
| Phase 1 Implementation | ✅/❌ | codex_plan.md |
| Phase 2 Review | ✅/⚠️/❌ | gemini_review.md |
| Phase 2.5 Lint | ✅/⏭️ | lint_report.md |
| Phase 3 Fix | ✅/❌ | claude_report.md |
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
| Phase 1 Codex 額度耗盡 | 🛑 立即停止管線，通知 Scott：「Codex 額度耗盡，預計 XX:XX 重置，請問要等冷卻期結束後繼續，還是先暫停？」，等待 Scott 指示。**嚴禁自動 fallback 到其他 CLI** |
| Phase 1.5 Contract drift + production | ❌ 報警，要求修正後繼續 |
| Phase 1.5 Contract expected=0（v2.3）| ❌ FAIL Critical — arch_plan.md 沒有可解析的檔案清單，contract 未建立 |
| Phase 1.5 Contract drift + casual | ⚠️ 記錄 accepted，繼續 |
| 任何 3AI CLI 額度耗盡 | rate limit / 429 / capacity 錯誤 | 🛑 **立即停止管線**，通知 Scott 哪個 CLI + 錯誤內容 + 重置時間。等待 Scott 指示。嚴禁自動 fallback |
| Pre-flight Check 未通過 | CLI 不回應 或 Gemini 429 > 3/10 | 🛑 **不啟動管線**，通知 Scott 哪個項目不通過，建議等待後重測 |
| Phase 2 Gemini 超時（非額度問題） | ⚠️ 跳過，Codex 自行判斷 |
| Phase 2.5 Lint 失敗 | ⚠️ 記錄，不中斷 |
| Phase 3 Claude 超時 | ⏱️ 跳過修正，用 Codex 原始版進入 Build |
| Phase 3 Regression test 失敗 | ⚠️ 記錄 bug 確認存在，不中斷 |
| Build 失敗（round 1） | 🔄 診斷式修復：Gemini 分析 → Codex 修 |
| Build 失敗（round 2） | 🚨 ESCALATE |
| Phase 5 失敗 | 產最小 final_report.md |

## CLI 呼叫指令

### 方式一：使用 ai_cli_wrapper.py（推薦，v2.2）

```python
import sys
SKILL_SCRIPTS = "/home/chien/.hermes/skills/autonomous-ai-agents/3ai-code-builder/scripts"
sys.path.insert(0, SKILL_SCRIPTS)
from ai_cli_wrapper import call_cli

result = call_cli("claude", "/path/to/prompt_phase0.txt", "phase0", raw_dir="/path/to/raw/")
# result = {"tool": "claude", "phase": "phase0", "status": "PASS", "returncode": 0,
#           "stdout": "...", "stderr": "（已過濾噪音）", "duration_seconds": 45.2,
#           "progress_log": ["[0.0s] Starting...", "[45.2s] ✅ Completed"]}
```

優點：統一路徑轉換、stderr 噪音過濾、自適應 timeout、進度監控、自動存 raw log。

### 所有 Phase CLI 呼叫：統一使用 background terminal（v2.3）

**規則：Claude / Gemini / Codex 全部改用 `terminal(background=true)`，不用 `execute_code`。**

原因：
- `execute_code` 硬上限 300s，任何 CLI 超時都會被截殺
- Claude Phase 1 常見 300-600s
- Gemini 有時也會卡在 AttachConsole 或模型推理 180s+
- Codex 獨立審查 + 修正可能跑 300s+
- `terminal(background=true)` 無上限，完成自動通知

```python
# 取得命令字串
from ai_cli_wrapper import build_background_cmd

cmd = build_background_cmd("claude", prompt_win_path, "phase1")
# 或
cmd = build_background_cmd("gemini", prompt_win_path, "phase2")
# 或
cmd = build_background_cmd("codex", prompt_win_path, "phase3")

# 背景執行（Hermes terminal 工具）
# terminal(command=cmd, background=true, notify_on_complete=true)
```

**完整執行流程：**
1. `write_file` 產 prompt
2. `execute_code` 取得 `build_background_cmd()` → 回傳命令字串
3. `terminal(command=cmd, background=true, notify_on_complete=true)` → 背景啟動
4. 繼續做其他事（或等待通知）
5. 收到完成通知後，收集 stdout、複製產物、存 raw log

**為何不能用 execute_code 等 CLI：**
- `execute_code` 硬上限 300s（5 分鐘），無法延長
- 任何 3AI CLI 超時都被截殺，導致 partial output + 需重跑
- `terminal(background=true)` 無上限，process 持續到自然結束

### 方式二：直接呼叫 cmd.exe（備用）

```bash
# Claude（Phase 0/1/5）
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type PROMPT_WIN_PATH | claude.cmd --print --allowedTools Bash Write Edit"

# Gemini（Phase 2/診斷）— 會有 AttachConsole 錯誤，可忽略
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type PROMPT_WIN_PATH | gemini.cmd --skip-trust --approval-mode yolo"

# Codex（Phase 3/修復）
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type PROMPT_WIN_PATH | codex.cmd exec --skip-git-repo-check --sandbox workspace-write"
```

**重要：** Prompt 檔案路徑在 `type` 指令中必須用 Windows 反斜線格式，但在 `write_file`（Hermes 工具）中用 `/mnt/c/...` Linux 格式。

### Phase 4 Build：使用 build_runner.py（v2.2）

```python
import sys
SKILL_SCRIPTS = "/home/chien/.hermes/skills/autonomous-ai-agents/3ai-code-builder/scripts"
sys.path.insert(0, SKILL_SCRIPTS)
from build_runner import run_phase4

result = run_phase4(output_dir, raw_dir)
# 自動：py_compile → pytest → import test → security grep
# 自動存所有 raw log 到 raw_dir/
# 回傳 test_result.json 結構化資料
```

### Phase 1.5 Contract Check：使用 contract_check.py（v2.2）

```python
import sys
SKILL_SCRIPTS = "/home/chien/.hermes/skills/autonomous-ai-agents/3ai-code-builder/scripts"
sys.path.insert(0, SKILL_SCRIPTS)
from contract_check import run_contract_check

result = run_contract_check(arch_plan_path, output_dir, report_path, intent="casual")
# 自動：解析 arch_plan 預期檔案 → 掃描實際檔案 → 比對 → 產 report
```

## Phase 0 Sanity Check（v2.3 強制要求）

Phase 0 完成後（Claude 產出 arch_plan.md），Hermes 必須執行 sanity check：

1. `arch_plan.md` 行數必須 > 50 行，或字數 > 1500 chars
2. 必須包含 "File List" 或 "Expected Deliverables" 或 "Module" 等架構關鍵字
3. Phase 1.5 contract_check.py 會 parse 至少 1 個 expected files

若 sanity check 失敗：
- 寫入 `raw/phase0_sanity_check.txt` 記錄失敗原因
- Pipeline 可以繼續（Phase 1 仍執行），但 contract_check 必須 FAIL
- 不可假裝 PASS

**為何不需要攔截 Phase 1：** 有時 Claude 的 arch_plan 寫法很精簡但產出正確，強制重跑 Phase 0 可能浪費時間。所以讓 Phase 1 跑完，但 contract_check 作為第二道防線一定要 fail-closed。

## Phase 1 Prompt 約束（v2.2 新增）

Phase 1 prompt 必須包含以下結構要求（避免 tkinter module-level import 問題）：

```
**STRUCTURAL REQUIREMENTS:**
- import tkinter 只能在 CalculatorUI class 的 __init__ 內或 if __name__ == "__main__" 區塊
- 核心邏輯 Engine class 必須在無 tkinter 環境下可獨立 import
- 這樣 headless 環境（CI/CD）可以跑 engine unit test
- 產出的程式碼必須在 py_compile 和 import 時不依賴 GUI 環境
```

## 注意事項
- **Pre-flight Check 是強制步驟**：每次 `~!!!` 觸發前必須執行，不通過就停止
- Pre-flight 通過標準：三個 CLI 都回應 + Gemini 429 ≤ 3/10
- 此技能消耗 3AI CLI 訂閱配額，不消耗 Hermes token
- Hermes 嚴禁自行深度分析程式碼，所有分析交給 3AI CLI
- CLI 直接讀寫硬碟，prompt 只含路徑不含程式碼
- 診斷式修復上限 2 輪，超過自動 escalate 給 Scott
- 時間戳目錄確保同一個 MD 可多次執行不覆蓋
- v2.2 取消自動 ZIP 打包，由 Scott 手動在外層壓縮
- v2.2 交付前自動清理 .pytest_cache/、__pycache__/、重複檔案
- Phase 4 強制保留 raw log（證據鏈），不可只靠 LLM 摘要
- 所有 CLI 呼叫優先使用 ai_cli_wrapper.py，避免手動路徑錯誤

## 已知陷阱

| 問題 | 症狀 | 解法 |
|------|------|------|
| WSL cmd.exe 不在 PATH | `command not found: cmd.exe` | 用 `/mnt/c/Windows/System32/cmd.exe` 全路徑 |
| WSL claude binary 未登入 | `Not logged in · Please run /login` | 改用 Windows 版 claude.cmd（透過 cmd.exe） |
| Gemini AttachConsole 錯誤 | Node.js `Error: AttachConsole failed` | **可忽略**，Gemini 仍會正常完成並寫入結果 |
| Prompt 路徑格式混用 | 檔案不存在 | `write_file` 用 Linux 格式 `/mnt/c/...`；CLI `type` 指令用 Windows 格式 `C:\...` |
| UNC 路徑警告 | `UNC paths are not supported` | 無害，cmd.exe 會自動切到 Windows 目錄 |
| 所有 3AI CLI 超時（v2.3 已解）| Claude/Gemini/Codex >300s 被 execute_code 截殺 | **統一改用** `build_background_cmd()` + `terminal(background=true, notify_on_complete=true)` — 無時限，完成自動通知 |
| Claude 寫檔到錯誤路徑 | `--print --allowedTools` 模式下 Claude 寫到 workspace root 而非 build output | Phase 1 完成後用 `shutil.copy` 從 `_3AI_WorkSpace/` 複製 calculator.py、tests/、README.md、requirements.txt 到 `build_dir/output/` |
| pytest cache 權限問題 | Windows Python 建立的 `.pytest_cache` 在 WSL 下 PermissionError | Auto cleanup 前用 `rm -rf` 確認刪除所有 cache，不依賴 Python shutil |
| Windows pytest cache 孤兒 | WSL + cmd 都無法刪除 `pytest-cache-files-*`（權限 `d--x--x--x`） | **Phase 4 不要從 WSL 跑 pytest** — 讓 3AI CLI（Windows Python）自己跑測試，或在 prompt 中要求 Claude/Gemini 測試完自行清理 `__pycache__` 和 `.pytest_cache`。若已產生孤兒，只能在 Windows 檔案總管手動刪 |
| Phase 4 清理時機 | `__pycache__`、`.pytest_cache` 在 pytest 後才產生，來不及在 auto cleanup 前刪除 | build_runner.py 的 pytest 完成後，**立即**執行 cleanup（在 WSL chmod + rm 或用 cmd.exe rmdir）。不要等 Phase 5 才清，越早越好 |
| Phase 5 報告過短 | Claude --print 模式對報告型 prompt 輸出極簡摘要 | Phase 5 改由 Hermes 自行撰寫 final_report.md，不依賴 Claude |
| Codex 額度耗盡 | `rate limit` / `quota exceeded` | 🛑 **立即停止整個管線**，通知 Scott 哪個 CLI 額度耗盡 + 重置時間。等待 Scott 指示：等冷卻期結束後繼續，或先暫停。**嚴禁自動 fallback 到 Claude/Gemini** — Scott 的顧問團用 Opus 4.7，額度消耗快，需要保留 |
| Gemini 429 capacity 錯誤 | `No capacity available for model gemini-3-flash-preview` | 🛑 **停止管線**，通知 Scott「Gemini 容量不足」。即使 output 有產出也先確認是否完整再繼續。**不自動 fallback 到 Claude/Codex** |
| Headless 環境 UI 測試失敗 | `_tkinter.TclError: no display name and no $DISPLAY environment variable` | **預期行為** — WSL 無 GUI 環境，UI 整合測試必 FAIL。在 final_report.md 註明「在 Windows 桌面會正常執行」，不影響 pipeline verdict |
| 引擎測試 PASS 但 UI 測試 ERROR | pytest 顯示部分測試 ERROR | **檢查 ERROR vs FAILED** — ERROR 通常是環境問題（DISPLAY/依賴），FAILED 才是程式碼問題。只看 engine test 結果判定程式碼品質 |

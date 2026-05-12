---
name: 3ai-code-builder
description: "3AI 程式建構管線 v2.6 — 用 ~!!! 觸發，Pre-flight(B 計畫+經驗教訓注入)→Build Package(PRD 快照)→Phase 0(架構+sanity check)→Contract Check v2(檔案/類別/方法/狀態)→Codex(建構)→Gemini/Claude(審查+PRD 交叉驗證)→Verdict Gate(嚴格化)→Lint→Claude(修正)→Build+Test→Final Verdict(PASS/PASS_WITH_UNVERIFIED_UI/FAIL)→Phase 5 Git→Phase 6 Dev Log→自動清理"
category: autonomous-ai-agents
trigger: "~!!!"
---

# 3AI Code Builder v2.6 — 程式建構管線

## 核心原則

### WINDOWS MODE for 3AI CLI Disk I/O（2026-05-12 強制）

任何 Phase 需要 Claude / Codex / Gemini CLI 讀寫硬碟時，必須標示並使用 **WINDOWS MODE**，不可用 WSL-mode 結果判定 3AI CLI 無法寫入。

- 載入/遵循 `3ai-windows-mode-disk-io` 技能。
- 工作目錄固定用 `C:\Users\chien\_3AI_WorkSpace`。
- Claude：`--print --allowedTools Bash Write Edit`
- Codex：`exec --skip-git-repo-check --sandbox workspace-write`
- Gemini：`--skip-trust --approval-mode yolo`
- 寫入成功必須由 Hermes 讀回目標檔驗證，不能只信 CLI 自述。

**Hermes 在此技能中完全不讀取、不分析程式碼。** 只做：
1. 驗證 MD 檔案存在、判斷模式（frontmatter > 檔名 fallback）
2. 建立時間戳目錄（`build_YYYYMMDD_HHMMSS/prompts/`、`output/`、`raw/`、`input/`）
3. 複製 PRD 到 `input/` 目錄 + 計算 SHA256（Build Package 可審計性）
4. 讀取經驗教訓 INDEX.md，提取與本次任務相關的教訓注入 Phase 0/1 prompt
5. 用 `write_file` 產生各 phase 的 prompt 檔案到 `prompts/` 目錄
6. 依序呼叫 3AI CLI（Codex→Gemini→Claude）執行各 phase
7. 驗證各 phase 產出檔案存在
8. 任務結束時收集 lesson 檔案，通過 3 問 Gate 後寫入對應分類 Lessons
9. 產出 final_report.md + git_summary.md + notion_log_ready.md
10. 通知 Scott 結果

**Prompt 寫入方式：** 直接用 Hermes `write_file` 工具寫到 `{build_dir}/prompts/prompt_phaseN.txt`，不需要 Python 腳本中轉。

## 經驗教訓系統（v2.6 強制）

### 目錄結構
```
C:\Users\chien\_3AI_WorkSpace\hermes-knowledge\
├── INDEX.md                    ← 任務類型 → 對應 Lessons 檔案
├── LESSONS_GENERAL.md          ← 跨類通用（嚴格篩選）
├── LESSONS_CALCULATOR.md       ← 計算/數值類
├── LESSONS_UI.md               ← UI 類（tkinter/WPF/HTML）
├── LESSONS_WEB.md              ← Web/爬蟲類
├── LESSONS_POWERSHELL.md       ← PowerShell/系統類
└── LESSONS_SECURITY.md         ← 安全類
```

### 每條 Lesson 強制格式
```markdown
## [ID] 短標題
- 觸發場景：具體情境（非泛化）
- 錯誤表現：bug 長怎樣
- 根本原因：為什麼發生
- 修復方式：正確做法 + code snippet（如有）
- 適用邊界：什麼時候「不」適用 ← 防 cargo cult 關鍵欄位
- 不適用場景：明確排除
- 是否需要自動測試：是/否
- 來源任務與日期：YYYY-MM-DD 專案名
```

### 讀取協議（Pre-flight 額外步驟）
1. 根據任務類型判斷應該讀哪些 Lessons 分類檔
2. 讀取 INDEX.md → 找到對應分類
3. **只摘錄相關條目**，不整包塞入 prompt
4. 將摘錄附加到 Phase 0/1 prompt 開頭：
   「請先讀取以下經驗教訓，避免重複犯錯：...」

### 寫入協議（任務結束時）
1. 各 AI CLI 在自己的 output/ 寫 `lesson_phaseN.txt`
2. Hermes 讀取 lesson 檔案（不讀全程 debug log）
3. 每條候選經驗必須通過 **3 問 Gate**：
   - ① 這個錯誤未來是否高機率重現？
   - ② 是否有清楚適用邊界？
   - ③ 是否值得未來消耗 token 讀取？
4. 三個 Yes → 寫入對應分類檔
5. 否則 → 只留在本案 final_report，不寫入長期 Lessons

### 通膨控制（每 20 條觸發 pruning）
- 合併重複項
- 刪除低價值項
- 把零碎 bug 收斂成 coding guideline
- 保持每個分類檔短小、可讀、可注入

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
| 前置檢查 | ❌ 無 | **Pre-flight Check**：CLI 可用性 + Gemini 429 壓力測試（10 次，>3 次 429 就暫停） |
| 腳本工具 | ❌ 無 | cli_availability_check.py + gemini_availability_test.py |

## v2.5 改動摘要 (2026-05-07, 基於 Gemini 擁塞備案)

| 項目 | v2.4 | v2.5 |
|------|------|------|
| Gemini 429 > 30% | 🛑 停止，等冷卻 | ❓ **詢問 Scott**：啟動 B 計畫 或 中止 |
| B 計畫 | ❌ 無 | Gemini 職責（Phase 2 審查 + 診斷式修復分析）**全數轉交 Claude** |
| 正常流程 | Codex→Gemini→Claude | Codex→Gemini→Claude（維持不變） |
| B 計畫流程 | ❌ 無 | Codex→Claude(審查)→Claude(修正)（Gemini 不可用時） |
| 管線完整性 | 依賴三棒 | **雙棒也能跑完全流程**，不因 Gemini 缺席而產出殘缺結果 |

## v2.6 改動摘要 (2026-05-08, 基於顧問團三方共識)

| 項目 | v2.5 | v2.6 |
|------|------|------|
| Build Package | 只有產出 | **input/ 目錄**：複製 PRD.md + SHA256 hash + source_manifest.json |
| 經驗教訓 | 無 | **INDEX.md + 分類 Lessons 檔**，Pre-flight 注入到 Phase 0/1 prompt |
| Lesson 寫入 | Hermes 直接寫 | **3 問 Gate**：① 會重現嗎？② 有明確邊界嗎？③ 值得付 token 嗎？ |
| Lesson 通膨控制 | 無 | **每 20 條 pruning**：合併重複、刪除低價值、收斂成 coding guideline |
| Contract Check | 只查檔案存在 | **v2**：檔案 + 類別 + public methods + 狀態名稱 + forbidden pattern + headless import |
| PRD 交叉驗證 | 無 | Phase 2 後新增 **PRD Compliance Cross-Check**：不確定語氣升級、硬規格不可標 Low |
| Phase 3 Skip Gate | PASS + Minor → skip | **嚴格化**：PASS + Low ≤ 2 + 不涉 PRD MUST + 不涉測試缺口 + 無 unverified critical surface |
| UI 測試 skipped | Final Verdict: PASS | **PASS_WITH_UNVERIFIED_UI** + 明確列出未驗證項目 |
| Phase 5 Git | 無 | **自動 commit/push**，權限不足標 BLOCKED_BY_PERMISSION |
| Phase 6 Dev Log | 無 | 產 **notion_log_ready.md**（build id、PRD hash、test result、limitations、next action） |
| 專案複雜度 | 無 | **complexity: small/medium/large**，控制 arch_plan 行數（small ≤ 180 行） |
| Fallback 模式 | Normal / B-Plan | **Normal / Degraded / Minimal** 三級，final_report 必須標註 mode |
| Final Verdict | PASS / FAIL | **PASS / PASS_WITH_UNVERIFIED_UI / PASS_WITH_WARNINGS / FAIL** |

## v2.7 改動摘要 (2026-05-11, 基於 MiniCalc PR-02 顧問團複審)

| 項目 | v2.6 缺口 | v2.7 強制修正 |
|------|-----------|---------------|
| 新增功能 PR 驗收 | pytest PASS 就可能放行 | **README/入口命令 smoke test 必跑**：直接執行主入口，例如 `python source/calculator.py`；ModuleNotFoundError/ImportError = FAIL |
| 乾淨交付結構 | 只掃 output/ 根目錄主程式 | build_runner 動態搜尋 `output/`、`source/`、`src/` 下的 `calculator.py/app.py/main.py` |
| Python 路徑污染 | 測試用 `sys.path.insert` 掩蓋真實 import bug | **精準禁止 sys.path.insert/append**：未註明 `# hermes: allow-sys-path <reason>` 的用法即 FAIL；合法 test helper/fixture 例外必須內聯註明理由，且不得修補 production import bug |
| 文件位置/指令 | README 可放錯位置或指令未驗證 | **root README.md 強制**；README 所有啟動/測試指令必須實跑並在 raw log 留證 |
| PR 完成報告 | release notes 取代 completion report | **docs/pr_##_completion_report.md 強制**：修改/新增檔、測試 stdout、已知限制、清理確認 |
| 文件機器 Gate | 文件錯誤靠人工 review 才發現 | build_runner v2.7.1 新增 `documentation_raw.txt`：檢查 root README、Known Limitations/已知限制、completion report、release notes v1.0 殘留、README 錯誤入口指令 |
| 暫存清理 | pytest 後清，但 py_compile/import 又產 cache | build_runner 在最終 package_hygiene 前再次清理 `.pytest_cache/`、`__pycache__/`、`*.pyc` |
| UI 未驗證 | headless UI skipped 容易被當 PASS | 優先支援 `python source/app.py --smoke` 並要求輸出 `SMOKE_OK`；沒有 `--smoke` 時才退回 direct entrypoint timeout/DISPLAY/TclError 分級 |
| PRD 版號/文件合規 | release notes 版號可能錯 | PRD 指定版本、README/Release Notes 標題、UI 顯示版本（若有）要納入 PRD Cross-Check 硬規格 |

## v2.7.1 補強規則 (2026-05-11, 基於 Claude/Gemini/ChatGPT 複核)

1. **PR 完成宣告 Gate**：在宣稱任何新增功能 PR 完成前，必須執行 build_runner v2.7.1 並保留完整 stdout；`overall_status != PASS` 時不得宣告完成，必須列出每個 FAIL 項目的修正措施。
2. **sys.path 例外條款**：禁止在 tests 中用 `sys.path.insert/append` 掩蓋 production import 設計錯誤。若是 monorepo/test helper/fixture 的必要路徑設定，必須在同一行加 `# hermes: allow-sys-path <reason>`，並在 final_report 說明不影響 production import。
3. **GUI Smoke 分層**：GUI/Tkinter 專案應新增 `--smoke` 模式，執行 `python source/calculator.py --smoke` 時初始化 import/入口路徑後輸出 `SMOKE_OK` 並退出，不進入長時間 `mainloop()`。build_runner 會優先使用 `--smoke`；缺少 smoke 模式時才用 timeout/DISPLAY/TclError 作為 headless 分級。
4. **PRD Assertion 化**：PRD 中的硬規格要轉成可機器檢查的 assertions，例如 root `README.md` 必須存在、`docs/pr_02_completion_report.md` 必須存在、`docs/release_notes.md` 必須含 `MiniCalc v1.2`、README 必須含「已知限制」。
5. **PR-02.1 驗收標準**：PR-02.1 hotfix 完成後必須附上 v2.7.1 `overall_status: PASS` 的完整 log；若仍由 Scott 或顧問團先發現 FAIL，視為流程仍未成熟。

## 流程架構 v2.6

```
Scott 給 MD 路徑 (~!!! ...)
  │
  ▼
★ Step 0: Pre-flight Check（v2.6 升級）★
  1. cli_availability_check.py — 確認 Claude/Codex/Gemini 能回應
  2. gemini_availability_test.py --count 10 --interval 3 — 連續 10 條測試
  3. Pipeline Mode 判斷：
     - 三個 CLI 都 ✅ HEALTHY 且 Gemini 429 ≤ 3/10 → **Normal**（Codex→Gemini→Claude）
     - Claude + Codex ✅ 但 Gemini 429 > 3/10 → ❓ 詢問 Scott：
       - **選項 A：B 計畫** → Gemini 職責轉交 Claude
       - **選項 B：Degraded** → 跳過 Gemini Review，Codex 自審 + Hermes 規則式檢查
     - Claude 或 Codex 不可用 → 🛑 **Minimal**：只跑 Hermes rule-based checks
  4. 經驗教訓注入：讀取 INDEX.md → 摘錄相關 Lessons → 附加到 Phase 0/1 prompt 開頭
  5. 等待 Scott 指示後才繼續
  │
  ▼
Step 0.5: Build Package + Artifact Detection
  1. 建立 input/ 目錄，複製 PRD.md
  2. 計算 PRD SHA256 hash → input/PRD.sha256
  3. 產 source_manifest.json（來源路徑、時間、hash、build id）
  4. 副檔名+內容+frontmatter → PRD / Source Code / Config / Unknown
  5. 判斷 complexity: small / medium / large
     - small：arch_plan ≤ 180 行，prompt 壓縮
     - medium：標準流程
     - large：展開詳細 prompt
  產 artifact_manifest.json（含 complexity 欄位）
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
  讀 PR + 注入經驗教訓 → 產 arch_plan.md
  │
  ▼
Phase 1: 實作（Codex）
  讀 PR + arch_plan + 注入經驗教訓 → 產程式碼 + README + tests/ + requirements.txt
  │
  ▼
★ Phase 1.5: Contract Check v2（v2.6 升級）★
  比對 arch_plan.md 預期 vs output/ 實際：
  1. File contract：預期檔案是否存在
  2. Class contract：arch_plan 宣告的類別是否實作
  3. Method contract：public methods 是否存在
  4. State contract：state enum 名稱是否一致
  5. Test contract：對應測試是否存在
  6. Forbidden pattern：eval/exec/subprocess
  7. Headless import：core engine 是否可無 GUI 依賴 import
  產 contract_check.md + contract_check.json
  │
  ├── 無 drift → 繼續
  ├── drift + casual → 記錄 accepted → 繼續
  └── drift + production → 報警 → 修正後才能繼續
  │
  ▼
Phase 2: 結構化審查（Gemini）— 正常流程
  讀程式碼 → 產 gemini_review.md（表格格式）
  │
  ├─ Gemini 可用 → 正常執行
  ├─ B 計畫啟動時 → Claude 執行（產 claude_review.md）
  └─ Degraded 模式 → Codex 自審 + Hermes 規則式檢查
  │
  ▼
★ PRD Compliance Cross-Check（v2.6 新增）★
  1. 比對 gemini_review.md PRD Compliance 表格 vs input/PRD.md
  2. 若 reviewer 用 maybe/consider/might/but/however/建議/可能 → 標記 risk_notes
  3. 若 PRD MUST requirement 判為 Low/Style → 升級為 Must Review
  4. 若 PRD hard requirement 沒有測試覆蓋 → Phase 3 不可 skip
  產 prd_cross_check.md
  │
  ▼
★ Verdict Decision Tree（v2.6 嚴格化）★
  │
  ├── PASS + Low ≤ 2 + 不涉 PRD MUST + 不涉測試缺口 + 無 unverified critical surface → 跳過 Phase 3 → Phase 4
  ├── PASS + Low > 2 → Phase 3 Fix
  ├── PASS + 任何涉及 PRD MUST → Phase 3 Fix
  ├── PASS + 有測試缺口 → Phase 3 Fix
  ├── PASS + risk_notes 存在 → need_scott_decision.md → 等 Scott
  ├── PASS + Major + casual_intent → need_scott_decision.md → 等 Scott
  ├── PASS + Major + production_intent → Phase 3 Fix
  ├── PASS_WITH_WARNINGS → 同上邏輯
  ├── NEEDS_FIXES / FAIL → Phase 3 Fix
  └── Unknown → 安全預設進 Phase 3
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
  4. py_compile main entry → compile_calculator_raw.txt（動態搜尋 root/source/src）
  5. py_compile tests/ → compile_tests_raw.txt
  6. pytest -v → test_raw.txt + test_result.json
  7. import smoke test → import_raw.txt
  8. **direct entrypoint smoke test** → entrypoint_smoke_raw.txt（優先跑 `python source/calculator.py --smoke`，看到 `SMOKE_OK` = PASS_SMOKE；否則跑 `python source/calculator.py`；ModuleNotFoundError/ImportError = FAIL；DISPLAY/TclError/timeout = UI 未驗證但入口已到達）
  9. security AST check → security_grep_raw.txt
  10. **path pollution check** → path_pollution_raw.txt（未註明 `# hermes: allow-sys-path <reason>` 的 `sys.path.insert/append` = FAIL；合法 test helper 例外必須說明理由）
  11. **documentation delivery check** → documentation_raw.txt（root README、Known Limitations、completion report、release notes 版號、README 錯誤入口指令）
  12. **package hygiene check** → package_hygiene_raw.txt（最終不得含 `.pytest_cache/`、`__pycache__/`、`*.pyc`）
  LLM 讀 raw → 摘要寫 build_log.md
  │
  ├── PASS → Phase 5
  └── FAIL → 診斷式修復（最多 2 輪）
              正常：Gemini 分析根因 → 產 fix_instruction.md
              B 計畫：Claude 分析根因 → 產 fix_instruction.md
              Codex 照指令修正 → 重新 Build
  │
  ▼
★ Final Verdict（v2.6 升級）★
  - PASS：所有 Phase 通過，無 UI test skip
  - PASS_WITH_UNVERIFIED_UI：通過但 UI test 因 headless skipped
  - PASS_WITH_WARNINGS：通過但有未處理 warning
  - FAIL：build 失敗或有 Critical 未修復
  │
  ▼
Phase 5: Git Commit / Push（v2.6 新增）
  1. git status → 檢查變更
  2. git diff summary → 變更摘要
  3. git add + commit → 含結構化 commit message
  4. git push → 推送到 remote
  5. 記錄 commit hash
  → 產 git_summary.md
  │
  ├── PASS → Phase 6
  └── BLOCKED_BY_PERMISSION → 標註 Scott 需處理事項，不影響 verdict
  │
  ▼
Phase 6: Dev Log（v2.6 新增）
  整合所有資訊 → 產 notion_log_ready.md：
  - build_id, project_name, prd_hash
  - changed_files, test_result, review_result
  - known_limitations, next_action
  - pipeline_mode, token_usage
  │
  ▼
Phase 7: 最終報告（Hermes）
  整合所有報告 → 產 final_report.md
  │
  ▼
經驗教訓收集（v2.6 新增）
  1. 讀取各 AI CLI 的 lesson_phaseN.txt（如有）
  2. 通過 3 問 Gate → 寫入對應分類 Lessons
  3. 不通過 → 只記錄在本案 final_report
  │
  ▼
Auto Cleanup（v2.2 新增）
  移除 .pytest_cache/、__pycache__/、重複檔
  保留精簡目錄供 Scott 打包
  │
  ▼
Hermes: 通知 Scott 結果 + 路徑 + Pipeline Mode + Final Verdict
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
├── input/                         ← v2.6: Build Package 可審計輸入
│   ├── PRD.md                    ← 複製的原始 PRD
│   ├── PRD.sha256               ← PRD hash
│   └── source_manifest.json      ← 來源路徑、時間、hash、build id
│
├── prompts/                       ← 所有 prompt 檔案
│   ├── prompt_phase0.txt
│   ├── prompt_phase1.txt
│   ├── prompt_phase2.txt
│   ├── prompt_phase3.txt
│   ├── prompt_phase5.txt
│   ├── prompt_diagnose1.txt   ← 診斷式修復（如有）
│   └── prompt_fix1.txt
│
├── output/                        ← 所有產出
│   ├── artifact_manifest.json    ← 含 complexity 欄位（v2.6）
│   ├── intent_alignment_check.md
│   ├── arch_plan.md
│   ├── contract_check.md
│   ├── contract_check.json       ← v2.6: 結構化契約檢查
│   ├── claude_plan.md
│   ├── app.py / *.js / ...
│   ├── README.md
│   ├── requirements.txt
│   ├── tests/test_basic.py
│   ├── tests/test_regression*.py
│   ├── gemini_review.md          ← 正常流程 / claude_review.md（B 計畫）
│   ├── prd_cross_check.md        ← v2.6: PRD 合規交叉驗證
│   ├── lint_report.md
│   ├── codex_report.md
│   ├── diff.md
│   ├── regression_test_report.md
│   ├── build_log.md
│   ├── fix_instruction.md
│   ├── need_scott_decision.md
│   ├── final_report.md           ← 含 Final Verdict 四級（v2.6）
│   ├── git_summary.md            ← v2.6: Phase 5 Git 結果
│   ├── notion_log_ready.md       ← v2.6: Phase 6 Dev Log
│   └── execution_log.json
│
└── raw/                           ← 強制保留所有原始輸出（證據鏈）
    ├── phase0_codex_stdout.txt
    ├── phase1_codex_stdout.txt
    ├── contract_check_raw.txt
    ├── phase2_gemini_stdout.txt
    ├── lint_compile_raw.txt
    ├── lint_security_raw.txt
    ├── phase3_claude_stdout.txt
    ├── regression_raw.txt
    ├── compile_calculator_raw.txt
    ├── compile_tests_raw.txt
    ├── test_raw.txt
    ├── test_result.json
    ├── import_raw.txt
    ├── security_grep_raw.txt
    ├── diagnose1_stdout.txt
    ├── fix1_codex_stdout.txt
    ├── git_raw.txt                ← v2.6: git 操作原始輸出
    └── phase7_claude_stdout.txt
```

## 最終報告格式（final_report.md）

```md
# Final Report — {project_name}

## Pipeline Mode: Normal / B-Plan / Degraded / Minimal

## Pipeline Result
| Phase | Status | Output File |
|-------|--------|-------------|
| Pre-flight | ✅/❌ | cli_health + gemini_429 |
| Build Package | ✅ | input/PRD.md + PRD.sha256 |
| Phase 0 Architecture | ✅/❌ | arch_plan.md |
| Phase 1 Implementation | ✅/❌ | codex_plan.md |
| Phase 1.5 Contract v2 | ✅/❌ | contract_check.md + .json |
| Phase 2 Review | ✅/⚠️/❌ | gemini_review.md / claude_review.md（B 計畫） |
| PRD Cross-Check | ✅/⚠️ | prd_cross_check.md |
| Phase 2.5 Lint | ✅/⏭️ | lint_report.md |
| Phase 3 Fix | ✅/⏭️/❌ | claude_report.md |
| Phase 4 Build/Test | ✅/❌ | build_log.md |
| Phase 5 Git | ✅/⏭️/🔒 | git_summary.md |
| Phase 6 Dev Log | ✅/⏭️ | notion_log_ready.md |

## Final Verdict
**PASS** / **PASS_WITH_UNVERIFIED_UI** / **PASS_WITH_WARNINGS** / **FAIL**

判定規則：
- PASS = 所有 Phase 通過，Gemini Must Fix 全部處理，無 UI test skip
- PASS_WITH_UNVERIFIED_UI = 通過但 UI test 因 headless skipped
- PASS_WITH_WARNINGS = build 通過但有未處理 warning
- FAIL = build 失敗或有 Critical 未修復

## Complexity: small / medium / large
## Token Usage
| Phase | Executor | Tokens |
|-------|----------|--------|
| Phase 0 | Codex | ... |
| Phase 1 | Codex | ... |
| Phase 2 | Gemini | ... |
| ... | ... | ... |
| **Total** | | **...** |

## Unverified Surface（如有）
- 哪些測試 skipped
- skipped 原因
- 需要 Scott 在 Windows GUI 環境補測什麼

## Known Limitations
- list items...

## Next Action
- Scott 需要手動處理的事項（如有）
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
| Pre-flight Check 未通過 | CLI 不回應 或 Gemini 429 > 3/10 | Claude+Codex 缺陣 → 🛑 停止。僅 Gemini 429 高 → ❓ **詢問 Scott**：選 A（B 計畫）或 B（Degraded 模式） |
| Phase 2 Gemini 超時（非額度問題） | ⚠️ Degraded 模式：跳過 Gemini，Codex 自審 + Hermes 規則式檢查 |
| PRD Cross-Check 發現風險 | reviewer 不確定語氣 / PRD MUST 被標 Low | ⚠️ 標記 risk_notes，強制進 Phase 3 或 need_scott_decision |
| Phase 5 Git 權限不足 | push 失敗 / no remote | 🔒 BLOCKED_BY_PERMISSION，記錄 Scott 需處理事項，不影響 verdict |
| Phase 6 Notion 不可用 | 未配置 / API 錯誤 | ⏭️ 跳過，產 notion_log_ready.md 作為備用 |
| Phase 2.5 Lint 失敗 | ⚠️ 記錄，不中斷 |
| Phase 3 Claude 超時 | ⏱️ 跳過修正，用 Codex 原始版進入 Build |
| Phase 3 Regression test 失敗 | ⚠️ 記錄 bug 確認存在，不中斷 |
| Build 失敗（round 1） | 🔄 診斷式修復：Gemini 分析 → Codex 修 |
| Build 失敗（round 2） | 🚨 ESCALATE |
| Phase 5 失敗 | 產最小 final_report.md |

## CLI 呼叫指令

### Windows 原生 3AI CLI 硬碟讀寫驗證

已整理 session-specific reference：`references/windows-native-3ai-cli-disk-io.md`。當 Scott 要求確認 3AI CLI 是否能讀寫 `C:\Users\chien\_3AI_WorkSpace`，或管線需要讓 Claude/Codex/Gemini 直接落盤時，先套用該 reference 的模式：Windows 工作目錄 + `.cmd` wrapper + 各 CLI 正確授權參數，最後讀回 result 檔驗證，不只看 stdout。

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
- **Pre-flight Check 是強制步驟**：每次 `~!!!` 觸發前必須執行
- Pre-flight 通過標準：三個 CLI 都回應 + Gemini 429 ≤ 3/10 → Normal 流程
- Pre-flight 僅 Gemini 429 不通過：**詢問 Scott 選擇**——A（B 計畫）或 B（Degraded 模式）
- **B 計畫**：Gemini 不可用時，Phase 2 審查 + 診斷式修復分析全數由 Claude 執行
- **Degraded 模式**：跳過 Gemini Review，Codex 自審 + Hermes 規則式檢查（最低保底）
- **Minimal 模式**：Claude/Codex 都不可用時，只跑 Hermes rule-based checks
- B 計畫/Degraded 前提：Claude + Codex 至少一個可用，否則強制 Minimal
- **Build Package**：每次 build 自動複製 PRD 到 input/ + SHA256，確保可審計性
- **新增功能 PR 模式（v2.7.1）**：不能只跑 pytest；必須跑 README/入口 smoke test、documentation check、path pollution check、package hygiene check，且 root README + docs/pr_##_completion_report.md 必須存在；完成前必須貼 build_runner 完整 stdout，`overall_status != PASS` 不得宣告完成
- **禁止 sys.path 污染（v2.7.1）**：禁止在 tests 用 `sys.path.insert/append` 掩蓋 production import bug；合法 monorepo/test helper/fixture 例外必須同一行加 `# hermes: allow-sys-path <reason>` 並在 final_report 說明，不可默默放行
- **README 指令驗證（v2.7）**：README 內所有啟動/測試命令必須實際執行並把 stdout/stderr 放入 raw log；README 指令錯即 FAIL
- **直接入口驗收（v2.7.1）**：GUI app 應支援 `--smoke`，成功輸出 `SMOKE_OK`；build_runner 優先跑 `python source/app.py --smoke`。若無 smoke 模式才退回 direct entrypoint，DISPLAY/TclError/timeout 可標 UI 未驗證；ModuleNotFoundError/ImportError 一律 FAIL
- **Documentation Gate（v2.7.1）**：build_runner 產 `documentation_raw.txt`，檢查 root README、Known Limitations/已知限制、docs/pr_##_completion_report.md、release notes v1.0 殘留、README 錯誤入口指令；發現即 FAIL
- **PR 完成報告（v2.7）**：新增功能 PR 必須產 `docs/pr_##_completion_report.md`，含修改/新增檔、測試命令、pytest stdout、新增測試摘要、已知限制、打包前清理確認
- **經驗教訓注入**：Phase 0/1 prompt 必須附加相關 Lessons 摘錄
- **Lesson 寫入 3 問 Gate**：會重現？有邊界？值得 token？三個 Yes 才寫入長期檔
- **Lesson 通膨控制**：每 20 條觸發 pruning，保持每個分類檔短小可讀
- **Contract Check v2**：不僅查檔案，還查類別、方法、狀態名稱、forbidden pattern
- **PRD Cross-Check**：reviewer 不確定語氣或 PRD MUST 被標 Low → 強制升級
- **Verdict Gate 嚴格化**：Low ≤ 2 + 不涉 PRD MUST + 不涉測試缺口才能 skip Phase 3
- **PASS_WITH_UNVERIFIED_UI**：UI test skipped 必須明確標註，不可假裝 PASS
- **Phase 5 Git**：自動 commit/push，權限不足標 BLOCKED_BY_PERMISSION
- **Phase 6 Dev Log**：產 notion_log_ready.md，即使 Notion 不可用也有備用記錄
- **complexity 控制**：small 專案 arch_plan ≤ 180 行，避免 token 浪費
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
| 誤判 3AI CLI 不能寫硬碟 | 從 WSL 呼叫 CLI 時少了授權參數，stdout 顯示拒絕 `write_file` / shell，或結果檔沒產生 | 不要直接下結論。改用 Windows 工作目錄 `C:\Users\chien\_3AI_WorkSpace` + Windows `.cmd` wrapper：Claude 加 `--allowedTools Bash Write Edit`，Codex 加 `--sandbox workspace-write`，Gemini 加 `--approval-mode yolo`；最後讀回結果檔驗證。詳見 `references/windows-native-3ai-cli-disk-io.md` |
| Phase 4 清理時機 | `__pycache__`、`.pytest_cache` 在 pytest 後才產生，來不及在 auto cleanup 前刪除 | build_runner.py 的 pytest 完成後，**立即**執行 cleanup（在 WSL chmod + rm 或用 cmd.exe rmdir）。不要等 Phase 5 才清，越早越好 |
| Phase 5 報告過短 | Claude --print 模式對報告型 prompt 輸出極簡摘要 | Phase 5 改由 Hermes 自行撰寫 final_report.md，不依賴 Claude |
| Codex 額度耗盡 | `rate limit` / `quota exceeded` | 🛑 **立即停止整個管線**，通知 Scott 哪個 CLI 額度耗盡 + 重置時間。等待 Scott 指示：等冷卻期結束後繼續，或先暫停。**嚴禁自動 fallback 到 Claude/Gemini** — Scott 的顧問團用 Opus 4.7，額度消耗快，需要保留 |
| Gemini 429 capacity 錯誤 | `No capacity available for model gemini-3-flash-preview` | 🛑 **停止管線**，通知 Scott「Gemini 容量不足」。即使 output 有產出也先確認是否完整再繼續。**不自動 fallback 到 Claude/Codex** |
| Headless 環境 UI 測試失敗 | `_tkinter.TclError: no display name and no $DISPLAY environment variable` | **預期行為** — WSL 無 GUI 環境，UI 整合測試必 FAIL。在 final_report.md 註明「在 Windows 桌面會正常執行」，不影響 pipeline verdict |
| 引擎測試 PASS 但 UI 測試 ERROR | pytest 顯示部分測試 ERROR | **檢查 ERROR vs FAILED** — ERROR 通常是環境問題（DISPLAY/依賴），FAILED 才是程式碼問題。只看 engine test 結果判定程式碼品質 |

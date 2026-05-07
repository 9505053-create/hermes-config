# Pipeline Lessons Learned — 2026-05-07 MiniCalc 執行紀錄

## ✅ 已完成優化（v2.2, 2026-05-07）

基於 3AI Web 顧問團（ChatGPT / Claude / Gemini）三方共識，以下優化已完成：

### P0 必修（三方共識）
- [x] **Contract Check (P0-1)** — `contract_check.py`，Phase 1→2 之間自動比對 arch_plan vs 實際產出
- [x] **證據鏈 (P0-2)** — `build_runner.py`，Phase 4 subprocess 強制 capture raw log
- [x] **Skip Logic (P0-3)** — Verdict Decision Tree 升級，可重現邏輯錯誤 → regression test

### P1 建議修（兩方共識）
- [x] **CLI Wrapper (P1-1)** — `ai_cli_wrapper.py`，統一 cmd.exe 啟動 + stderr 噪音過濾
- [x] **tkinter import (P1-2)** — Phase 1 prompt 約束：延遲 import 到 UI class
- [x] **決策矩陣 (P1-3)** — 3×3 intent × severity 矩陣寫入 SKILL.md

### P2 改善
- [x] **取消自動 ZIP** — Scott 手動在外層壓縮
- [x] **自動清理暫存** — 交付前移除 .pytest_cache、__pycache__
- [x] **write_file 路徑** — 統一正斜線，避免反斜線重複檔 bug

### 相關檔案
- `ai_cli_wrapper.py` — CLI 統一啟動介面
- `build_runner.py` — Phase 4 證據鏈執行器
- `contract_check.py` — Phase 1.5 契約檢查
- `3ai_advisor_feedback_summary.md` — 顧問團意見彙整
- `v2_2_optimization_plan.md` — 完整行動方案
- SKILL.md `3ai-code-builder` — 已升級至 v2.2

---
name: 3ai-workspace-review
description: 3AI 共享空間交叉審核工作流程 — 用 MD 指令調度 Claude/CODEX/Gemini 對專案進行技術審核
---

# 3AI 共享空間交叉審核工作流程

## 何時使用
需要 3AI 對專案進行深度技術審核時使用此技能。

## 前置條件
- 共享空間已建立：`C:\Users\chien\_3AI_WorkSpace`
- 專案檔案已 clone 到共享空間
- 3ai-commander 技能已載入（提供呼叫命令）

## 工作流程

### Step 1: 準備 Review 資料夾

在 `C:\Users\chien\_3AI_WorkSpace\code_create\` 下建立時間戳資料夾：

```
code_create/review_YYYYMMDD_HHMMSS/
├── source/       ← 主程式碼
├── tests/        ← 測試檔案
└── docs/         ← PRD、架構圖、release notes、LESSONS 紀錄
```

**複製清單（最低限度）：**
- `source/`：修改後的主程式檔案
- `tests/`：對應的測試檔案
- `docs/PRD.md`：需求文件（如有）
- `docs/arch_plan.md`：架構規劃（如有）
- `docs/release_notes.md`：版本說明
- `docs/LESSONS_*.md`：顧問團問題的修復紀錄（如有）

**目的：** 讓顧問團拿到結構一致、可獨立驗證的 review package，不用從散亂的路徑找檔案。

### Step 2: 撰寫 Prompt 並出發
1. 在 review 資料夾內撰寫 review.md（描述修復摘要 + 審核問題）
2. 為每個 3AI 撰寫專用 prompt_*.txt

### Step 2: 出發
```bash
# Claude — 適合 CSS/UI/邏輯審核
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt_claude.txt | claude.cmd --print"

# CODEX — 適合程式碼/效能/架構審核
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt_codex.txt | codex.cmd exec --skip-git-repo-check"

# Gemini — 適合技術/domain 特定審核
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt_gemini.txt | gemini.cmd --skip-trust"
```

### Step 3: 收集結果
- Claude：Windows mode 使用 `--allowedTools Bash Write Edit` 可寫入報告檔；仍需 Hermes read-back 驗證
- CODEX：Windows mode 使用 `--sandbox workspace-write` 可寫入報告檔；仍需 Hermes read-back 驗證
- Gemini：Windows mode 使用 `--approval-mode yolo` 可寫入報告檔；僅在受控 workspace/prompt 下使用，仍需 Hermes read-back 驗證
- 每個 agent 的 stdout/stderr 另存到 logs/，最終報告以 output/*.md 為準

### Step 4: Hermes 統整
- 讀取所有 output/*_review.md
- 檢查是否包含約定完成標記（例如 `REVIEW_COMPLETE`）
- 複製到 central package 的 `agent_outputs/`
- 綜合建議、提出 Scott 決策點；除非 Scott 明確要求，審核階段不直接修改/推送 GitHub

### Step 5: PR Hardening / Pre-Next-Phase Gate（2026-05-15 MiniCalc pattern）
當 review 結果是 `PASS_WITH_WARNINGS` 且沒有 blocking issue，適合用小型 hardening 分支收斂，不要直接擴張到下一個 PR scope：
- 從已通過的 baseline commit 建立 `prX.Y-local-hardening` 類分支。
- 小步 TDD：先加 failing tests，再實作，再跑 targeted tests。
- 最低驗證 gate：`python3 -m pytest -q`、`python3 -m py_compile ...`、`git diff --check`。
- 再建 3AI review package，讓 Claude/Codex/Gemini 各自審核，Hermes read-back raw reports 並產出 central `FINAL_3AI_REVIEW_SUMMARY.md`。
- 若 3AI 無 blocker，才 commit；依 Scott 偏好，可以先完成本地 hardening，最後再 push GitHub branch 做版本控制。不要自動 merge `main` 或進下一個 PR；等 Scott 決策。
- 可參考 `references/minicalc-pr-hardening-review-pattern-20260515.md`。

### Step 6: Pre-Implementation Planning Review Gate（2026-05-15 MiniCalc PR3 pattern）
當 Scott 要進入下一個 PR 規劃階段，但明確要求先不要 merge 前一分支、也不要開始實作時：
- 從已通過的 prior branch 建立 `prN-planning` 類分支；不要自動 merge `main`。
- 先產出三份文件：`docs/prN/PRN_SPEC.md`、`docs/prN/IMPLEMENTATION_PLAN.md`、`docs/prN/ACCEPTANCE_CRITERIA.md`。
- 即使只是 docs-only planning，也先跑 `python3 -m pytest -q` 與 `git diff --check`，確認 baseline 沒被破壞。
- 建立 central planning review package，分派 Claude/Codex/Gemini 依角色審核。
- 若任一 reviewer 給 `BLOCKED`，視為 planning gate failure：先修文件，再建立 delta re-review package，附上前一輪 review 與修正清單。
- re-review 無 blocker 後，將小型非阻塞警告直接補進 planning docs，再寫 `FINAL_3AI_REVIEW_SUMMARY.md`。
- 只 commit planning docs；不要 push/merge，除非 Scott 明確要求。
- 可參考 `references/minicalc-pr3-planning-review-pattern-20260515.md`。

## Prompt 撰寫技巧
- 明確指定要讀取的檔案名稱
- 要求輸出格式（Markdown）
- 要求評分 (1-10)
- 要求具體行號的修改建議
- 指定輸出檔名（但 CODEX/Gemini 無法寫入，需手動存）

## 已知限制 / Pitfalls
- 不要沿用舊結論「CODEX/Gemini 不能寫入」。Windows mode 加正確 flags 後可寫：Claude `--allowedTools Bash Write Edit`、Codex `--sandbox workspace-write`、Gemini `--approval-mode yolo`；仍必須由 Hermes read-back 驗證。
- `--approval-mode yolo` 權限較大，只能用在受控 prompt、受控 workspace。
- 含空白 Windows 路徑在 WSL→`cmd.exe` 巢狀 quoting 下可能失敗；使用 `dir /x` 找 8.3 short name（例如 `CLAUDE~1`、`GEMINI~1`）再呼叫。
- 所有 CLI 的 stdin 管道有隱含長度限制（但比 `-p` 好很多）；長 prompt 寫成檔案後用 `type prompt.txt | ...`。

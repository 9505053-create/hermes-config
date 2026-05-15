---
name: workspace-structure
description: 3AI WorkSpace 目錄規劃原則 — 工作進行/完成/日誌/情報/辯論/暫存的動態管理規則
---

# 3AI WorkSpace 目錄規劃原則

## 核心目錄

```
_3AI_WorkSpace/
├── INDEX.md       ← 根目錄索引 (必讀，所有目錄說明)
├── active/        ← 工作進行區
├── projects/      ← 程式開發區 / GitHub fresh clone 工作區
├── code_create/   ← 早期/既有程式產出區（若 INDEX.md 指定使用則遵循）
├── completed/     ← 工作完成區
├── logs/          ← 系統日誌區
├── intel/         ← 網路情報區
├── debates/       ← 辯論區
├── temp/          ← 暫存區
└── temp_agent/    ← Claude Code / Codex 操控教學紀錄暫存區
```

---

## 各區定義與規則

### active/ — 工作進行區
**使用者**: Hermes + 3AI 看得懂
**命名**: `YYYY-MM-DD_任務簡述/`
**內容**: MD 指令檔、prompt 檔、中間產物
**規則**:
- 任務完成後，整包移至 `completed/`
- 同時只處理一個任務（避免混亂）
- prompt 檔用完可刪除

### projects/ — 程式開發區 / GitHub fresh clone 工作區
**使用者**: Hermes + 3AI + Scott
**用途**: 從 GitHub 重新 clone 的專案、正在修復或開發的程式 repo。
**規則**:
- 使用者要求「忽略本機舊資料，回 GitHub 複製」時，優先 clone 到 `projects/<repo-name>/`。
- clone 後先驗證 `git status --short --branch`、`git remote -v`、`git log --oneline -5`。
- 不要把舊本機專案檔案混入 fresh clone，除非使用者明確要求。
- 完成後依任務性質決定保留在 `projects/` 或複製摘要/成品到 `completed/`。

### code_create/ — 既有程式產出區
**用途**: 歷史或特定流程建立的程式產出。若 `INDEX.md` 或使用者指定此區，遵循指定；否則 GitHub fresh clone 優先使用 `projects/`。

### completed/ — 工作完成區
**使用者**: Scott 好辨別、好查閱
**命名**: `YYYY-MM-DD_專案名稱_v版本/`
**內容結構**:
```
completed/YYYY-MM-DD_專案名_v版/
├── README.md          ← 專案摘要、3AI 評分、待修項目
├── *_code/            ← 原始碼
├── *_review.md        ← 審核請求（給 3AI 看的）
├── *_result.md        ← 3AI 審核結果
└── devlog.md          ← 開發日誌（放這邊，不放 logs/）
```

### logs/ — 系統日誌區
**用途**: Hermes 自救用、崩潰復原
**子目錄**:
```
logs/
├── memory/        ← 重要記憶備份、長期上下文
├── recovery/      ← 崩潰復原 SOP（新 Hermes 能接手）
└── system/        ← 系統狀態快照
```
**重要規則**:
- ❌ 專案開發日誌**不放這裡** → 放各專案自己的 `devlog.md`
- ✅ 只放 Hermes 系統層級資訊
- ✅ 復原指南要讓「新的 Hermes 實例」能讀懂並接手

### intel/ — 網路情報區
**用途**: Hermes 網路蒐集的知識
**子目錄**:
```
intel/
├── tech/          ← 技術知識、API 文檔摘要
├── news/          ← AI/科技新聞
└── research/      ← 論文、研究筆記
```
**命名**: `YYYY-MM-DD_主題簡述.md`

### debates/ — 辯論區
**用途**: Scott 給主題 → 3AI 辯論 → Hermes 總結 → Scott 學習
**結構**:
```
debates/YYYY-MM-DD_主題/
├── topic.md           ← 辯論主題
├── claude_pos.md      ← Claude 立場
├── codex_pos.md       ← CODEX 立場
├── gemini_pos.md      ← Gemini 立場
├── summary.md         ← Hermes 總結點評（最重要）
└── scott_notes.md     ← Scott 學習筆記（留白給 Scott）
```

### temp/ — 暫存區
**用途**: 不好分類的臨時資料
**規則**: 超過 7 天未使用自動清理

### temp_agent/ — Agent 操控教學紀錄暫存區
**用途**: 保存 Hermes/小馬調用 Claude Code、Codex CLI 後，對 Scott 有學習價值的操控紀錄。
**使用時機**: 有豐富內容的完成案例，例如多輪 prompt、Claude/Codex 交叉驗證、修復驗證流程、可學習的中控判斷。
**命名**: `YYYYMMDD_HHMM_任務簡述_agent_trace/`
**建議內容**:
```
00_README.md
01_hermes_plan.md
02_claude_prompt.md
03_claude_command.txt
04_claude_raw.log
05_codex_prompt.md
06_codex_command.txt
07_codex_raw.log
08_hermes_judgment.md
09_final_transcript.md
artifacts/
```
**規則**:
- 不保存 API key、token、cookie、密碼、信用卡資訊；raw log 如有敏感資訊須先遮罩。
- 這裡是教學/暫存區，不取代正式 `completed/` 或專案交付目錄。
- 簡單一次性 CLI 問答，沒有學習價值時可不存。

---

## 動態調整原則

- 目錄結構可因實際狀況調整
- 新增子目錄時同步更新 `INDEX.md`
- 調整後更新本技能檔
- Scott 有最終決定權

## 工作流程總結

```
任務開始 → active/ 建立任務
    ↓
調度 3AI 處理
    ↓
收集結果 → active/ 存放
    ↓
完成 → 整包移至 completed/（Scott 好查閱）
```

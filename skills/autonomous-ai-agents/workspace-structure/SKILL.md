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
├── completed/     ← 工作完成區
├── logs/          ← 系統日誌區
├── intel/         ← 網路情報區
├── debates/       ← 辯論區
└── temp/          ← 暫存區
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

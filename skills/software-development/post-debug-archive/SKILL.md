---
name: post-debug-archive
description: > 
  DEBUG 完成後，建立時間戳資料夾歸檔有改動的檔案。
  適用場景：修復完成、顧問團審查前、版本交付前。
  顧問團通過後，自動將專案推上 GitHub。
  觸發時機：自動觸發（DEBUG 結束時）或用戶說「debug 完了」「修好了」「打包給顧問團」等。
triggers:
  - 自動觸發（無需用戶指令）
---

# Post-Debug Archive（DEBUG 後自動歸檔）

## 目的
每次 DEBUG/修復完成後，**自動**將有改動的檔案集中到一個時間戳資料夾，然後通知 Scott 去查看。

## ⚠️ 強制規則
**DEBUG 任務結束後，必須自動執行本流程，不需要等 Scott 指示。**
執行順序：修復 → 測試確認 → 歸檔 → 通知 Scott 資料夾路徑。

## 觸發條件（自動）
以下情況結束時自動執行歸檔：
1. 修復了一個或多個 bug 並確認測試通過
2. 完成了顧問團回饋的 P0/P1/P2 修復
3. 任何涉及修改現有程式碼的修復任務

## 前置條件
- 工作目錄：`C:\Users\chien\_3AI_WorkSpace\`
- 歸檔目錄：`C:\Users\chien\_3AI_WorkSpace\code_create\`

## 步驟

### 1. 建立時間戳資料夾
```
code_create/review_YYYYMMDD_HHMMSS/
├── source/        ← 主程式碼（.py, .js 等）
├── tests/         ← 測試檔案
└── docs/          ← 文件（PRD、架構圖、release notes、LESSONS）
```

### 2. 識別改動檔案
用 `git diff` 或詢問用戶哪些檔案有改動。至少包含：
- 修改過的 source 檔案
- 修改過的測試檔案
- 相關文件（PRD.md、arch_plan.md、release_notes.md）
- 經驗教訓記錄（LESSONS_*.md）

### 3. 複製檔案
用 Python `shutil.copy2` 複製（保留時間戳），不要用 symlink。

### 4. 自動通知 Scott
完成歸檔後，必須主動通知 Scott，格式：
```
📦 歸檔完成：`code_create\review_YYYYMMDD_HHMMSS\`
  ├── source\calculator.py (改了 xxx)
  ├── tests\test_calculator.py (28 tests 全過)
  └── docs\LESSONS_CALCULATOR.md (新增 N 則經驗)
```
簡要說明哪些檔案有改動、改了什麼，讓 Scott 知道去哪看。

### 5. 顧問團通過後 → GitHub 版本管理
當 Scott 說顧問團通過了，執行以下步驟將專案正式推上 GitHub：
1. 建立專案目錄：`projects/<專案名>/`，結構為 `source/`、`tests/`、`docs/`
2. 複製最終版檔案到專案目錄
3. `git init` → `git add -A` → `git commit`（含版本號和 PR 摘要）
4. 用 GitHub API（curl + token）建立 remote repo
5. `git push -u origin main`
6. 通知 Scott：repo URL + commit 內容

> 參考：`github-repo-management` skill 取得 API 和 git 操作細節

## 歷史記錄
- 2026-05-08 建立：Scott 提出，PR-01 MiniCalc 流程優化後，開始實施程式碼維護管理

## GitHub 認證（必讀）
- Token 儲存在兩個地方（需測試哪個有效）：
  1. `git config --global url.https://9505053-create:TOKEN@github.com/.insteadOf`
  2. `~/.hermes/memory/github_credentials.md`（完整記錄，包含有效/過期 token）
- 建立 repo 前，先用 curl 測試 token：HTTP 200 = 有效，401 = 過期
- 過期的 token 應從 git config 中移除（`--unset-all`）
- GitHub username: `9505053-create`

## 專案目錄慣例
- 每個獨立專案放 `projects/<專案名>/`
- 結構：`source/`、`tests/`、`docs/`、`.gitignore`、`README.md`
- 歸檔放 `code_create/review_時間戳_PR編號/`（給顧問團）
- Build 中間產物放 `code_create/build_時間戳/`（3AI pipeline）

## 注意事項
- **不要複製整個專案**，只放有改動的檔案 + 必要文件
- 資料夾命名用 `review_` 前綴（區分 `build_` 的全新產出）
- 如果用戶提供了 PR 編號或任務名，加到資料夾名稱中，如 `review_20260508_114539_PR01`
- 保留目錄結構（source/、tests/、docs/），方便顧問團快速定位

## 範例執行
```python
import os, shutil
from datetime import datetime

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
target = f"/mnt/c/Users/chien/_3AI_WorkSpace/code_create/review_{ts}"

os.makedirs(f"{target}/source")
os.makedirs(f"{target}/tests")
os.makedirs(f"{target}/docs")

# 複製改動檔案
shutil.copy2("calculator.py", f"{target}/source/")
shutil.copy2("tests/test_calculator.py", f"{target}/tests/")
# ... 其他檔案
```

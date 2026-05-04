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

### Step 1: 準備
1. 將專案 clone 到共享空間
2. 撰寫 review.md（描述修復摘要 + 審核問題）
3. 為每個 3AI 撰寫專用 prompt_*.txt

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
- Claude：如需寫入，需 Scott 授權；通常從 stdout 收集
- CODEX：只讀沙箱，從 stdout 收集；手動存成 *_result.md
- Gemini：從 stdout 收集；手動存成 *_result.md

### Step 4: Hermes 統整
- 讀取所有 *_result.md
- 綜合建議、執行修改、推送 GitHub

## Prompt 撰寫技巧
- 明確指定要讀取的檔案名稱
- 要求輸出格式（Markdown）
- 要求評分 (1-10)
- 要求具體行號的修改建議
- 指定輸出檔名（但 CODEX/Gemini 無法寫入，需手動存）

## 已知限制
- CODEX exec 模式沙箱只讀
- Gemini 寫入可能遇到 500 錯誤
- Claude 寫入需 Scott 在終端機授權
- 所有 CLI 的 stdin 管道有隱含長度限制（但比 -p 好很多）

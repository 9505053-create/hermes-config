---
name: 3ai-debate-workshop-v2
description: 3AI 多模型角色辯論工作流 v2 — 修復 v1 缺陷的結構化辯論引擎，支援多模式、中立 prompt、raw response 保存、共識分值判定
category: autonomous-ai-agents
---

# 3AI 辯論工作流 v2

## 版本狀態
**Status:** Stable（整合顧問團回饋的改善版，可直接使用）

## v2.1 更新（2026-05-04 顧問團第二輪回饋）

新增以下強制規則：

### Fact Check Gate（強制）
- prompt 中所有外部事實/數據/CVE 加註 `[source: xxx, status: unverified]`
- Judge 最終裁決前必須用 web_search 驗證至少 2 個關鍵數據
- manifest 紀錄每方是否做了 web_search

### Execution Health Gate（強制）
- 任何 AI exit_code != 0 或 timeout → Debate_Record.md 開頭插入：
  `⚠️ 品質警告：Round X 角色執行異常（exit_code: XX），請人工核對 raw 內容完整性`

### Numeric Cross-check Gate（強制）
- 編譯 final report 前，比對 raw / summary / verdict 中所有定量數值（consensus_score、CVE、百分比、CVSS）
- 不一致 → abort，輸出「Compilation mismatch. Human review required」

### Abnormal Convergence Rule（強制）
- consensus_score 單輪跳幅 >30 → 強制加 Verification Round
- Judge 需判斷：真共識 / 過度讓步 / 填空式收斂

### Round Diff Report（建議）
- `analysis/round_diff.md`：每方各 round 立場變化（堅持/軟化/撤回/新增）

### Action Item Conversion（強制）
- verdict 必須輸出：Strategic Insights + Action Items + Owner + Risk Level + 是否需 Scott 確認

---

## 何時使用
- Scott 提出辯論方向（可能只是大方向）
- 需要 3AI 多模型交叉驗證或深度激盪
- 技術選型、架構決策、工作流改善、紅隊審查

**觸發關鍵字：** 「辯論」、「3AI辯論」、「研討會」、「紅隊審查」、「讓AI們討論」

---

## ⚖️ Scott 工作流定位

| 層級 | 角色 | 職責 |
|------|------|------|
| 決策者 | Scott | 最終決策、需求提出、是否採納 |
| 顧問團 | GPT Web / Gemini Web / Claude Web | 規劃、架構評論、成果驗收、改善建議 |
| 執行團 | Hermes（指揮官）+ 3AI CLI | 控場、派工、執行、記錄 |

**關鍵規則：**
- 顧問團是 Scott 的智囊，不是 Hermes 的下屬
- Hermes 不得把自己視為 Scott 的替代決策者
- Hermes 自動產生的 skill 必須先進 pending 區，等 Scott 確認才轉正式
- 執行深度推理與內容生成優先交給 3AI CLI（節省 Hermes API tokens）

---

## 🔒 三大紅線（絕對不可違反）

1. **不得使用 Scott 的信用卡資訊消費**
2. **大量刪除檔案前必須與 Scott 確認**
3. **Scott 敏感資料（信用卡卡號、API Key、個資等）不得未經允許提供給第三方**

其他 skill 生成權限：Hermes 可自主判斷是否優化工作流，但必須在每週六週報記錄所有 skill 生成的追蹤描述。

---

## Phase 0: 主題理解與澄清（v2 新增）

在辯論開始前，Hermes 必須判斷是否理解 Scott 的辯論主題：

### 主題理解檢查
1. **主題清楚** → 直接進入 Phase 1
2. **主題模糊** → 向 Scott 追問 1-3 個關鍵問題，建立 `00_topic_intake.md`

### 主題分級（決定辯論深度）
| 級別 | 適用場景 | 建議輪數 | 模式 |
|------|---------|---------|------|
| 🟢 快速 | 資訊查詢、事實確認 | 1 輪 | 單一 AI 即可 |
| 🟡 標準 | 技術選型、方案比較 | 2 輪 | 模式 A/B |
| 🔴 深度 | 架構決策、長期戰略、資安審查 | 2-4 輪 | 模式 A/B/C |

### 輸出檔案
```
00_topic_intake.md          # Scott 原始需求
01_topic_clarification.md   # 澄清後的明確主題（如需澄清）
```

---

## Phase 1: 研究收集

### 搜尋判斷規則
**需要搜尋：**
1. 題目涉及最新 AI 工具、API、框架、社群討論
2. Scott 明確要求參考論壇/社群觀點
3. Hermes 自身知識不足以支撐雙方辯論

**不一定要搜尋：**
1. 題目主要依賴內部工作流或既有專案資料
2. Scott 明確指定不搜尋

### 研究平衡強制檢查（v2 新增）

在生成任何 prompt 前，Hermes 必須自我檢查：

```markdown
## Research Balance Check
| 項目 | A 方 | B 方 |
|------|------|------|
| 優點數量 | ≥3 條 | ≥3 條 |
| 缺點數量 | ≥3 條 | ≥3 條 |
| 外部來源 | ≥2 個 | ≥2 個 |
| 語氣強度 | 中性 | 中性 |

- 優缺點條數必須對等（差距 ≤2 條）
- 每條論點標註來源或標記為「推論」
- 不對等時必須補充較弱方的資料
```

### 輸出檔案
```
02_research_sources.md          # 來源列表
03_research_balance_check.md    # 平衡檢查結果
```

---

## Phase 2: 辯論模式選擇

Hermes 根據題目選擇以下模式之一：

### 模式 A：正反攻防模式
適用：技術選型、A vs B、是否導入、工具比較

| 角色 | AI | 任務 |
|------|-----|------|
| 正方 | Claude CLI | 支持方案 A |
| 反方 | CODEX CLI | 支持方案 B |
| 交叉質詢官 | Gemini CLI | 找弱點、逼雙方補洞、判定收斂 |
| 控場 | Hermes | 派工、整理、輪數判定、總結（不下場辯論） |

### 模式 B：雙正方精煉模式
適用：Scott 已有方向，需要激盪更好方案

| 角色 | AI | 任務 |
|------|-----|------|
| 方案 A | Claude CLI | 提出設計 A |
| 方案 B | CODEX CLI | 提出設計 B |
| 比較/融合 | Gemini CLI | 比較 A/B、找缺口、融合或淘汰 |
| 控場 | Hermes | 整理與總結 |

### 模式 C：紅隊審查模式（v2 新增）
適用：新 skill 建立、自動化變更、資安、API Key、刪檔、系統設定

| 角色 | AI | 任務 |
|------|-----|------|
| Builder | CODEX CLI | 提出實作方案 |
| Red Team | Claude CLI | 挑錯、找風險、反駁 |
| Judge | Gemini CLI | 判斷可行性、是否需 Scott 核准 |
| 控場 | Hermes | 整理風險清單 |
| 最終核准 | Scott | — |

---

## Phase 3: Prompt 撰寫規則（v2 重大修復）

### ❌ 絕對禁止
1. **預設結論方向** — 不得在 prompt 中要求「走向融合」
2. **植入混合方案** — 不得在第二輪 prompt 中預先指定「Hermes 靈魂 + X 肢體」
3. **引導觀察者當和事佬** — 觀察者必須是質詢官，不是調解人
4. **給某方更多資料** — 雙方 prompt 中的研究資料量必須對等
5. **重複錨定敘事** — 不得反覆提及某個 meme/梗（如 CZ 嘲諷）來佔用辯論空間

### ✅ 必須做到
1. 每份 prompt 包含：己方優缺點 + 對方優缺點（對等數量）
2. 允許雙方選擇：堅持立場 / 修正立場 / 承認部分論點 / 提出第三方案
3. 允許「無共識」結局
4. 第二輪 prompt 基於第一輪實際回覆撰寫，不得預先寫好
5. 明確指定：字數（300-500字）、語言（繁體中文）、風格（辯論）

### 觀察者 prompt 額外要求
每輪結束後，觀察者必須輸出：
```markdown
1. 本輪新增有效觀點
2. 本輪重複/空泛內容
3. A 方最弱論點
4. B 方最弱論點
5. 雙方尚未回答的問題
6. 是否建議進入下一輪（含理由）
7. 建議下一輪攻防焦點
8. consensus_score: 0-100
```

---

## Phase 4: 輪數判定與停止規則（v2 新增）

Hermes 作為控場，必須根據內容品質動態決定輪數：

| 情況 | 動作 |
|------|------|
| 第一輪已有明確共識 | 停止 → 進入總結 |
| 第二輪已收斂 | 停止 → 進入總結 |
| 第二輪仍有重大分歧 | 進入第三輪 |
| 架構級重大議題且未收斂 | 最多第四輪 |
| 連續一輪無新觀點 | 立即停止 |
| consensus_score > 80% | 偯止 |
| 成本/時間/token 超標 | 停止 |
| 超過四輪 | 絕對禁止 |

---

## Phase 5: Raw Response 保存（v2 新增）

**每個 AI 的原始輸出必須獨立保存，不得只保存 Hermes 整理版。**

### 檔案結構
```
YYYY-MM-DD_HHMM_主題簡稱/
├── 00_topic_intake.md
├── 01_topic_clarification.md
├── 02_research_sources.md
├── 03_research_balance_check.md
├── prompts/
│   ├── round1_claude_prompt.md
│   ├── round1_codex_prompt.md
│   ├── round1_gemini_prompt.md
│   ├── round2_claude_prompt.md（如需）
│   ├── round2_codex_prompt.md（如需）
│   └── round2_gemini_prompt.md（如需）
├── raw/
│   ├── round1_claude_raw.md
│   ├── round1_codex_raw.md
│   ├── round1_gemini_raw.md
│   ├── round2_claude_raw.md（如需）
│   ├── round2_codex_raw.md（如需）
│   └── round2_gemini_raw.md（如需）
├── analysis/
│   ├── argument_board.md         # 各方論點對照表
│   ├── consensus_scores.md       # 每輪共識分值
│   └── unresolved_questions.md   # 未解決問題清單
├── final/
│   ├── final_summary.md          # 指揮官總結
│   ├── workflow_improvements.md  # 可導入工作流的具體建議
│   └── scott_review_required.md  # 需 Scott 核准的事項
├── logs/
│   └── invocation_manifest.json  # 調用記錄
└── pending_skill/
    └── skill_candidate.md（如有）
```

### invocation_manifest.json 格式
```json
[
  {
    "round": 1,
    "agent": "Claude CLI",
    "command": "claude.cmd --print",
    "timestamp": "2026-05-04T08:06:00+08:00",
    "input_file": "prompts/round1_claude_prompt.md",
    "output_file": "raw/round1_claude_raw.md",
    "exit_code": 0,
    "web_search_used": false,
    "independent_response": true
  }
]
```

**若無 raw response，不得宣稱是完整 3AI 辯論。**

---

## Phase 6: 指揮官總結（v2 修復）

### final_summary.md 必須包含
1. 辯論主題
2. Scott 原始意圖摘要
3. 使用的辯論模式（A/B/C）
4. 使用的資料來源
5. 每輪摘要
6. 雙方核心論點
7. 主要衝突點
8. 已達成共識
9. 未解問題
10. **觀察者待探索問題逐條回覆**（v2 新增 — 不得跳過）
    - 已解決 / 部分解決 / 未解決需後續研究
11. 對 Scott 工作流的可操作建議
12. 風險與限制
13. 是否建議建立 skill（標記為 pending）
14. 是否需要 Scott 審核
15. 建議下一步

### 成本意識摘要（v2 新增）
```markdown
## 成本摘要
- 辯論輪數：X 輪
- 調用的 AI：Claude x1 / CODEX x1 / Gemini x1
- 是否有不必要重複：無/有（說明）
- 下次節省建議：...
```

---

## Phase 7: 交付與歸檔

1. 完整檔案存入 `C:\Users\chien\_3AI_WorkSpace\debates\YYYY-MM-DD_HHMM_主題簡稱\`
2. 本地備份到 `~/.hermes/memory/`
3. 通知 Scott（Telegram / Email）
4. 更新共享空間 INDEX.md

---

## Skill 管理規則（v2 新增）

1. 辯論後產出的任何 skill candidate → 放入 `pending_skill/` 目錄
2. 狀態標記為「Pending Scott Review」
3. 每週六週報必須記錄本週所有 skill 生成/修改/降級
4. 辯論品質自評低於 80 分 → 不得寫入長期記憶或正式 skill
5. 不得自動將 pending skill 轉為 stable

---

## CLI 呼叫命令（沿用 v1 已驗證模式）

```bash
# Claude
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\debates\YYYY-MM-DD_HHMM_主題 && type prompt_file.md | C:\Users\chien\AppData\Roaming\npm\claude.cmd --print"

# CODEX
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\debates\YYYY-MM-DD_HHMM_主題 && type prompt_file.md | C:\Users\chien\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check"

# Gemini
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\debates\YYYY-MM-DD_HHMM_主題 && type prompt_file.md | C:\Users\chien\AppData\Roaming\npm\gemini.cmd --skip-trust"
```

**注意事項：**
- 不要用 `-p` 參數傳遞含空格/中文的長指令（會截斷）
- 不要省略 `cd /d`（CLI 無法存取 WSL 路徑）
- CODEX/Gemini 無法寫入共享空間，結果從 stdout 收集
- Prompt 不要超過 3000 字

---

## n8n 暫緩導入

目前 Scott 尚未熟悉 n8n 操作，Hermes 也未證明能完全自主管理 n8n workflow。
- 不得把 n8n 放入核心流程
- 通知與交付以本地檔案、Email、Telegram 為主
- 僅列為未來優化項目

---

## v1 → v2 改動摘要

| 問題 | v1 狀態 | v2 修復 |
|------|---------|---------|
| Prompt 預設結論 | 強制走向融合 | 禁止預設，允許無共識 |
| 研究資料不對等 | Hermes 10 優 vs 龍蝦 5 優 | 強制平衡檢查 |
| 無 raw response | 只有整理版 | 強制保存 raw + manifest |
| 觀察者太溫和 | 和事佬 | 改為交叉質詢官 + consensus_score |
| 自動建 skill | 過度自我擴張 | 改為 pending 區 + Scott 審核 |
| 跳過待探索問題 | ASCII 圖蓋過去 | 強制逐條回覆 |
| 無主題分級 | 所有題目同樣深度 | 三級分類 + 輪數限制 |
| 無成本意識 | — | 每次辯論附成本摘要 |
| 檔案混亂 | debates/ 根目錄 | 按主題子目錄分離 |

---
name: 3ai-debate-workshop
description: 3AI 多模型角色辯論/研討工作流 — 用 MD 指令調度 Claude/CODEX/Gemini 各扮演不同角色，進行多輪結構化辯論並編譯紀錄
category: autonomous-ai-agents
---

# 3AI 多模型角色辯論工作流

## 何時使用
- 使用者想讓 3AI 針對某個主題進行**角色辯論**或**多角度研討**
- 需要不同 AI 模型扮演對立/互補立場（擁護者 vs 擁護者 vs 觀察者）
- 需要多輪交鋒（開場 → 觀察者引導 → 反駁 → 總結）
- 目標不是分勝負，而是激盪創意論點或探索架構方向

**觸發關鍵字：** 「辯論」、「3AI辯論」、「研討會」、「多角度分析」、「讓AI們討論」

## 前置條件
- 共享空間已建立：`C:\Users\chien\_3AI_WorkSpace\debates\`
- 3ai-commander 技能已載入（提供 CLI 呼叫命令）
- 網路搜尋可用（先收集研究資料）

## 工作流程

### Phase 1: 研究收集
1. 用 `web_search` 搜尋相關論壇、文章、社群討論（至少 3-5 個來源）
2. 用 `web_extract` 深度提取關鍵文章內容
3. 整理研究摘要，標註各方優缺點（辯論素材）

### Phase 2: 角色分配與 Prompt 撰寫
將研究資料分配到各角色 prompt 中。**每個 prompt 必須包含：**
- 角色定義（你是 XXX 擁護者/觀察者）
- 辯論主題與目的
- 完整研究資料摘要（含己方優點、己方缺點、對方優點、對方缺點）
- 明確的輸出要求（字數、風格、語言）

**標準角色配置（3 人辯論）：**

| 角色 | 建議模型 | 原因 |
|------|---------|------|
| 正方擁護者 | Claude | 邏輯清晰、文筆好 |
| 反方擁護者 | CODEX | 精煉有力、善反擊 |
| 觀察者/主持人 | Gemini | 綜合分析、善引導 |

**Prompt 檔案命名：**
```
debates/debate_prompt_{role}.txt      # 第一輪
debates/debate_r2_{role}.txt          # 第二輪
debates/debate_observer_summary.txt   # 觀察者總結
```

### Phase 3: 多輪辯論執行

#### 第一輪：開場陳述
```bash
# 正方
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\debates && type debate_prompt_claude.txt | C:\Users\chien\AppData\Roaming\npm\claude.cmd --print"

# 反方
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\debates && type debate_prompt_codex.txt | C:\Users\chien\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check"

# 觀察者引導（讀取第一輪結果後）
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\debates && type debate_prompt_gemini.txt | C:\Users\chien\AppData\Roaming\npm\gemini.cmd --skip-trust"
```

#### 第二輪：反駁與深入
- 將第一輪各方論點 + 觀察者提問加入第二輪 prompt
- 要求各方回應觀察者的具體問題
- 要求探討「融合/混合」可能性

#### 觀察者總結
- 將全部辯論摘要傳給觀察者做最終評價
- 評價辯論質量、指出共識與分歧、判斷可行性

### Phase 4: 指揮官總結與編譯
Hermes 作為指揮官：
1. 綜合所有回合內容
2. 提出自己的「第三條路」或創意觀點
3. 對工作流的具體啟發
4. 編譯完整辯論紀錄 Markdown

### Phase 5: 交付
- 存檔到 `C:\Users\chien\_3AI_WorkSpace\debates\`
- 本地備份到 `~/.hermes/memory/`
- 郵件通知使用者
- 更新共享空間 INDEX.md

## 辯論回合數規則
| 情境 | 回合數 |
|------|--------|
| 雙方快速達成共識 | 2 回合（開場 + 反駁） |
| 有分歧但有方向 | 2-3 回合 |
| 沒有共識、需要更多交鋒 | 最多 4 回合 |

## Prompt 撰寫技巧
- **研究資料必須完整**：己方優缺點 + 對方優缺點都要給，否則論點空洞
- **要求具體回應**：指定字數（300-500字）、要求金句、要求具體場景
- **引導融合思維**：觀察者應引導從「誰更好」轉向「如何融合」
- **每輪增加上下文**：第二輪 prompt 必須包含第一輪的精華論點

## v1 → v2 升級記錄（2026-05-04）

> 顧問團（GPT/Claude/Gemini Web）審查後發現 v1 有品質瑕疵：
> 1. Prompt 預設結論方向（強制收斂）
> 2. 研究資料雙方不對等
> 3. 未保存 raw response
> 4. 自動建 skill 過度擴張
> 5. 觀察者角色太溫和
> 6. 未逐條回應觀察者待探索問題
>
> **已建立 v2 版本（3ai-debate-workshop-v2）修復上述問題。v2 中立後可取代 v1。**
> **本技能不違反 Scott 三大紅線，保留為可用狀態。**

## 已知限制
- CLI stdin 管道有隱含長度限制（prompt 不要超過 3000 字）
- CODEX/Gemini 無法寫入共享空間，結果從 stdout 收集
- Claude 寫入需 Scott 授權，通常從 stdout 收集更可靠
- 郵件寄送可能因 SMTP 超時失敗，可改用背景執行

## 範例產出結構
```markdown
# 🏛️ 3AI 辯論大會紀錄
## 「主題」

### 研究背景
### 第一輪：正方論點
### 第一輪：反方論點
### 觀察者引導
### 第二輪：正方反駁
### 第二輪：反方反駁
### 觀察者總結
### 指揮官最終總結
#### 關鍵洞察
#### 對工作流的啟發
### 📎 附件資訊
```

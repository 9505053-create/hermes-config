---
name: 3ai-commander
description: 3AI Commander Work Mode - Strategic delegation to Claude, CODEX, and Gemini CLI
category: autonomous-ai-agents
---

# 3AI Commander Work Mode

## Overview
When user mentions "3AI", "3AI助手", or "3AI xxxxx", this refers to the authorized CLI tools that Hermes can command:
- Claude CLI (Anthropic) — User's monthly subscription
- CODEX CLI (OpenAI) — User's monthly subscription
- Gemini CLI (Google) — User's monthly subscription

## Shared Workspace (Primary Communication Channel)

**Path**: `C:\Users\chien\_3AI_WorkSpace` (note: "Spece" not "Space")
**WSL Mount**: `/mnt/c/Users/chien/_3AI_WorkSpace`
**Purpose**: Hermes writes MD instructions here → 3AI CLIs read and process → results saved back here.

### How It Works
1. **Hermes** writes a `.md` or `.txt` prompt file to the shared workspace
2. **Hermes** invokes the CLI via `type prompt.txt | cli.cmd` pipe
3. **CLI** reads the workspace files, produces output
4. **Hermes** reads results back from the workspace

### Capability Matrix (Verified 2026-05-03)

| CLI | Read Workspace | Write Workspace | Notes |
|-----|---------------|-----------------|-------|
| **Hermes** | ✅ | ✅ | Direct WSL access |
| **Claude** | ✅ | ⚠️ Needs approval | Scott must approve first write per session |
| **CODEX** | ✅ | ❌ Read-only | Exec sandbox is read-only |
| **Gemini** | ✅ | ❌ 500 error | Backend error on write; may be temporary |

## Setup and Verification

### Initial Setup Workflow
When setting up multi-AI collaboration for the first time:

1. **Test each CLI tool connectivity**
   ```bash
   # Test Claude CLI
   /mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien && C:\Users\chien\AppData\Roaming\npm\claude.cmd --version"
   
   # Test CODEX CLI
   /mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien && C:\Users\chien\AppData\Roaming\npm\codex.cmd --version"
   
   # Test Gemini CLI
   /mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien && C:\Users\chien\AppData\Roaming\npm\gemini.cmd --version"
   ```

2. **Verify authentication status**
   ```bash
   # Claude - check auth
   /mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien && C:\Users\chien\AppData\Roaming\npm\claude.cmd auth status"
   
   # CODEX - check config
   /mnt/c/Windows/System32/cmd.exe /c "type C:\Users\chien\.codex\config.toml"
   
   # Gemini - check Google account
   /mnt/c/Windows/System32/cmd.exe /c "type C:\Users\chien\.gemini\google_accounts.json"
   ```

3. **Test basic communication via shared workspace**
   ```bash
   # Step 1: Hermes writes a test prompt to workspace
   # (Use write_file to C:\Users\chien\_3AI_WorkSpace\test_prompt.txt)
   
   # Step 2: Pipe it to Claude
   cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type test_prompt.txt | C:\Users\chien\AppData\Roaming\npm\claude.cmd --print"
   ```

### Workspace Integration

#### Google Drive Setup
- **Folder Path**: `我的雲端硬碟 > AI WorkSpace > Hermes`
- **Folder ID**: `${HERMES_GDRIVE_WORKSPACE_FOLDER_ID}`
- **Usage**: Store reports, backups, exports, and workspace files

#### Supabase External Brain
- **Connection**: `docker exec -u postgres supabase-db psql -d postgres`
- **Tables**: `hermes_knowledge`, `hermes_debates`, `hermes_todos`
- **Purpose**: Long-term memory and skill storage

### Troubleshooting

| Problem | Solution |
|---------|----------|
| CLI not found | Check Windows installation path: `where <tool>` |
| Authentication failed | Re-run OAuth setup or check API keys |
| Model not available | Update CLI tool or check subscription status |
| Permission denied | Verify user is added as test user in Google Cloud Console |

## Cost Structure
- **3AI CLIs**: Monthly subscription (fixed cost, usage limits with cooldown periods)
- **Hermes**: OpenRouter API tokens (cost money to purchase)

## Strategic Directive
Hermes is the **Commander** that strategically uses 3AI resources to save tokens (which cost money).

## Task Allocation Rules

### Simple Tasks
- Execute directly with Hermes
- No need to consult 3AI

### Complex Tasks
1. **Delegate to 3AI first**
2. **Coordinate and split tasks** among 3AI members
3. **Summarize results** from 3AI
4. **Execute final actions** with Hermes

### Dynamic Allocation
- No fixed assignments
- Can have 3AI members check each other's work
- Can split tasks among 3AI members
- I coordinate, summarize, and execute final actions

## CLI Command Patterns (Verified & Tested)

### ✅ Verified Invocation Commands (2026-05-03)

All three CLIs work when: (1) `cd /d` to workspace first, (2) prompt piped via stdin.

```bash
# ═══ CLAUDE ═══
# Read mode (print result to stdout, no interactive)
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | C:\Users\chien\AppData\Roaming\npm\claude.cmd --print"

# ═══ CODEX ═══  
# Read mode (exec sandbox, read-only)
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | C:\Users\chien\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check"

# ═══ GEMINI ═══
# Read mode (skip trust prompt for headless)
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | C:\Users\chien\AppData\Roaming\npm\gemini.cmd --skip-trust"
```

### Workflow Pattern
```
1. Hermes writes: prompt.md → C:\Users\chien\_3AI_WorkSpace\
2. Terminal pipe:   type prompt.md | cli.cmd [flags]
3. CLI processes:  reads workspace files, generates response
4. CLI writes:     output.md → workspace (if permitted)
5. Hermes reads:   output.md from workspace
```

### Known Limitations

| Issue | Affected CLI | Workaround |
|-------|-------------|------------|
| `-p` flag truncates on spaces | Claude | Use `--print` + stdin pipe instead |
| `-p` flag not supported | Gemini | Use stdin pipe (no `-p` at all) |
| `exec` sandbox read-only | CODEX | Accept read-only; Hermes writes results |
| `--skip-trust` required | Gemini | Always add `--skip-trust` |
| Write needs approval | Claude | Scott must approve first write per session |
| UNC path warning | All | Harmless — `cd /d` to local path first |

## 3AI 共享空間利器 (已驗證)

**路徑**: `C:\Users\chien\_3AI_WorkSpace` (WSL: `/mnt/c/Users/chien/_3AI_WorkSpace`)
**目錄結構**: `active/` (工作進行) → `completed/` (工作完成) → `logs/` (系統日誌) → `intel/` (情報) → `debates/` (辯論) → `temp/` (暫存)
**索引**: 見共享空間根目錄 `INDEX.md`

### 呼叫模板（附 log 輸出）
```bash
# 時間戳變數（Hermes terminal 中使用 $(date ...)）
TS=$(date +%Y%m%d_%H%M%S)

# Claude（輸出到 temp/claude_<timestamp>.log）
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | C:\Users\chien\AppData\Roaming\npm\claude.cmd --print > temp\claude_${TS}.log"

# CODEX（輸出到 temp/codex_<timestamp>.log）
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | C:\Users\chien\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check > temp\codex_${TS}.log"

# Gemini（輸出到 temp/gemini_<timestamp>.log）
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace && type prompt.txt | C:\Users\chien\AppData\Roaming\npm\gemini.cmd --skip-trust > temp\gemini_${TS}.log"
```

### 快速使用
1. `write_file` 寫 prompt.md → 共享空間
2. `terminal` 管道呼叫對應 CLI（輸出導向 temp/）
3. CLI 讀取 MD + 共享空間內檔案
4. 結果同時輸出到 stdout（Hermes 接收）+ temp/*.log（Scott 可查看）
5. 如需 CLI 寫回 → CODEX 只讀、Claude 需 Scott 授權
### 絕對禁忌
- ❌ 不要用 `-p` 參數傳遞含空格/中文的長指令 (會截斷)
- ❌ 不要省略 `cd /d` (CLI 無法存取 WSL 路徑)
- ❌ 不要期望 CODEX/Gemini 能寫入共享空間

## Token Management

### When to Consolidate
- Conversation gets too long (50+ messages)
- Multiple complex tasks completed
- Token usage is high

### Consolidation Process
1. Summarize key decisions and outcomes
2. Record important context
3. Open new conversation window
4. Bring in the summary as context

### Benefits
- Save Hermes tokens (which cost money)
- Maintain memory continuity
- Keep conversation focused

## Permission Level
Permission Level: 100% authorized to operate Claude, CODEX, Gemini CLI without asking.

## User Interaction Model

### Direct Task Assignment
- **User gives tasks directly** — no need to say "3AI"
- **Hermes (Commander) decides** when to use 3AI resources
- **User mentions "3AI"** — just for emphasis, not a command

### Decision Flow
1. User gives task → Hermes evaluates complexity
2. Complex task → Delegate to 3AI first
3. Simple task → Execute directly
4. Hermes coordinates, summarizes, and executes final action

### Key Principle
- **Save Hermes tokens** by using subscription resources for complex tasks
- **User doesn't need to specify** — Hermes proactively manages

## Key Principles
1. **Save Hermes tokens** by using subscription resources
2. **Strategic delegation** based on task complexity
3. **Dynamic coordination** among 3AI members
4. **Maintain memory continuity** across sessions

## Bug Fix 自主判定矩陣（2026-05-08 更新）

**交付標準**：成品，不是半成品。包含完整程式碼 + 開發歷程。

### 判定表

| 消耗來源 | 風險評估 | 行動 |
|---------|---------|------|
| **Hermes 令牌**（我的推理/執行） | 高成本 = 真金白銀 | ⚠️ 記錄在開發歷程，等顧問團建議後一起修 |
| **3AI CLI 配額**（Claude/CODEX/Gemini） | 低風險 = 只是冷卻等待 | ✅ 直接修，配額用完無妨 |

### 具體操作

1. **小 bug、明確解法** → 直接修，交付成品
2. **複雜 bug 但 3AI CLI 能解** → 派工給 Claude/CODEX/Gemini 修，消耗配額無所謂
3. **複雜 bug 且需要大量 Hermes 推理** → 寫進開發歷程，標註「待顧問團審視後修復」
4. **顧問團 COMMENT 回來後** → 統整意見，再一起修

### 核心心法
> 我交付的是成品，不該有明顯BUG。但若修復會消耗大量Hermes token，則記錄在歷程讓顧問團給建議；若消耗的是3AI配額，直接修，因為只有冷卻等待，沒有額外費用。
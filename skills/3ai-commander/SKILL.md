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
1. **Hermes** writes a `.md` or `.txt` prompt file to the shared workspace or the agent-specific subworkspace
2. **Hermes** invokes the CLI via `type prompt.txt | cli.cmd` pipe
3. **CLI** reads the workspace files, produces output
4. **Hermes** reads results back from the workspace

### Agent-Specific Subworkspaces (Updated 2026-05-15)

Scott created `_agent` subfolders to avoid cluttering the shared `_3AI_WorkSpace` root. For **3AI agent** tasks with disk I/O, route each agent to its own folder by default:

```text
Claude agent / Claude Code: C:\Users\chien\_3AI_WorkSpace\_agent\Claude Codex\
Codex agent:                C:\Users\chien\_3AI_WorkSpace\_agent\Codex\
Gemini agent:               C:\Users\chien\_3AI_WorkSpace\_agent\Gemini Workspace\
```

Use the shared root for coordination manifests/final summaries only. Keep prompts, logs, scratch outputs, and intermediate artifacts inside the relevant agent folder. A routing note exists at `C:\Users\chien\_3AI_WorkSpace\_agent\AGENT_WORKSPACE_ROUTING.md`.

### Agent Trace / Teaching Archive (Updated 2026-05-15)

Scott wants Hermes' future Claude Code / Codex CLI orchestration techniques to be learnable after the fact. When a completed Claude Code or Codex invocation has **rich learning value** (multi-step prompt design, review/fix/verify loop, cross-agent validation, meaningful judgment notes, raw logs worth studying), also write a readable trace package under the first-level workspace directory:

```text
C:\Users\chien\_3AI_WorkSpace\temp_agent\
WSL: /mnt/c/Users/chien/_3AI_WorkSpace/temp_agent/
```

Recommended package layout:

```text
temp_agent/YYYYMMDD_HHMM_task_agent_trace/
├── 00_README.md
├── 01_hermes_plan.md
├── 02_claude_prompt.md
├── 03_claude_command.txt
├── 04_claude_raw.log
├── 05_codex_prompt.md
├── 06_codex_command.txt
├── 07_codex_raw.log
├── 08_hermes_judgment.md
├── 09_final_transcript.md
└── artifacts/
```

Do not save secrets/API keys/tokens/cookies/credit-card data. Redact raw logs if needed. Simple one-shot CLI calls without learning value do not need a trace package.

### Capability Matrix (Updated 2026-05-15)

| CLI | Read Workspace | Write Workspace | Notes |
|-----|---------------|-----------------|-------|
| **Hermes** | ✅ | ✅ | Direct WSL access |
| **Claude Code** | ✅ | ✅ | Use Windows mode with `--print --allowedTools Bash Write Edit`; verified by read-back smoke test on 2026-05-15. |
| **CODEX CLI** | ✅ | ✅ | Use Windows mode with `exec --skip-git-repo-check --sandbox workspace-write`; verified with GPT-5.5 and read-back smoke test on 2026-05-15. |
| **Gemini CLI** | ✅ | ✅ | Use Windows mode with `--skip-trust --approval-mode yolo`; broad approval, so restrict prompt and workspace. |

Older notes saying CODEX/Gemini were read-only came from pre-approval/sandbox tests and are superseded by the Windows-mode disk I/O workflow.

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

### Flexible CLI Consultation Routing（2026-05-13 Scott 指導）
Hermes should treat 小蝦 / Claude CLI / CODEX CLI / Gemini CLI as a flexible support pool, not only as formal debate participants.

Routing ladder:
1. **Direct answer** — simple, low-risk, no external facts, no need for second opinion.
2. **Deterministic tools first** — arithmetic, file reads, searches, shell/API/script checks, logs, system state.
3. **Single CLI consultation** — ask the one best-suited partner when a task needs a focused second opinion or support but not a full debate.
   - Claude: writing, critique, context/architecture reasoning, red-team style objections.
   - CODEX: implementation, debugging, deterministic workflows, test/log interpretation.
   - Gemini: broad synthesis, judge/observer role, alternative framing, multimodal or research-style synthesis when available.
   - 小蝦/OpenClaw: local worker-style tasks, OpenClaw-specific workflow, low-risk execution/reporting in its authorized workspace.
4. **Multiple CLI consultation** — ask two or more partners independently when viewpoints differ or reliability matters, then synthesize.
5. **Formal 3AI debate** — use `3ai-debate-workshop-v2` when Scott explicitly requests debate/3AI CLI debate, or when the decision is architectural, strategic, safety-sensitive, or high-impact.

Round/cost guardrails:
- Similar-topic partner consultation is capped at **4 rounds total** unless Scott explicitly approves more.
- Prefer **1 round** for quick second opinions, **2 rounds** for standard convergence, **3-4 rounds** only for complex or unresolved issues.
- Stop early when consensus is clear, no new information appears, or additional CLI calls would not materially improve the answer.
- Do **not** call 小蝦/OpenClaw merely because it is available or subscription-backed. Scott's 2026-05-13 token discussion measured roughly 98k-99k tokens per OpenClaw consultation because of fixed runtime/context/cache overhead. However, Scott later clarified that Codex/ChatGPT usage is mostly covered by monthly subscription; the main downside is cooldown/waiting, and he can wait as an AI hobbyist. Use 小蝦 when OpenClaw-specific workflow, independent worker execution, 小馬/Hermes coordination, long-context support, or a meaningful second opinion improves correctness or continuity; avoid only nonessential waste, repeated retries, and pointless scans.
- Hermes remains the controller: route, prompt, collect raw outputs when useful, summarize, verify handles/artifacts, and report only the distilled conclusion to Scott.

### Commander + UI aesthetics principle（2026-05-15 Scott 指導）

Scott expects Hermes to be the **commander**, not the default laborer. For non-trivial development tasks, Hermes should plan, split work, write strong prompts, delegate heavy implementation/review to subagents or 3AI CLI, then verify and integrate. Do simple/obvious edits directly only when that is clearly faster.

For any user-facing software, UI/UX/aesthetic quality is a normal evaluation item. Load `ui-programming-aesthetics` together with `claude-design` / `popular-web-designs` / `sketch` when relevant. Add a UI-aesthetic review lane or checklist for GUI, web, frontend, Tkinter, desktop, EXE, dashboard, or prototype deliverables. Functional correctness alone is not sufficient if the interface is chaotic, generic, or AI-sloppy.

Scott also wants **visual-first planning when useful**: before writing substantial UI code or a complex prompt describing an interface, Hermes should autonomously judge whether a quick sketch / wireframe / flowchart / block diagram / mind map would clarify the discussion. This is a communication option, not a mandatory step for every reply. Use it when a picture aligns expectations faster than text or prevents expensive rework after implementation; skip it when the answer is simple, operational, or the visual would add ceremony without value. Use simple deterministic drawing methods when paid image APIs are unnecessary: HTML/SVG mockups, Excalidraw JSON, Mermaid-like diagrams, ASCII sketches, or local PNG/SVG rendering. Use GPT Web / Image 2.0 only when Scott chooses to do so manually; do not spend extra API-key-based image generation just for planning visuals.

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

### Known Limitations / Updated Pitfalls

| Issue | Affected CLI | Workaround |
|-------|-------------|------------|
| Long Chinese/path-heavy prompts can break shell quoting | All | Write prompt to a file and pipe with `type prompt.txt` |
| `-p` / inline prompt flags can truncate or misparse on spaces | Claude/Gemini patterns | Prefer stdin pipe; for Claude use `--print`; Gemini has no `-p` |
| Missing write approval causes false negatives | Claude | Use `--allowedTools Bash Write Edit` in headless print mode |
| Missing sandbox write permission causes false negatives | CODEX | Use `--sandbox workspace-write` for filesystem tasks |
| Missing approval mode causes false negatives | Gemini | Use `--approval-mode yolo` only in controlled workspace/prompt |
| UNC path warning | All | Harmless if command includes `cd /d C:\Users\chien\_3AI_WorkSpace` |
| Review package includes untracked pytest/cache artifacts | 3AI reviewers, especially Codex | Build review packages from `git ls-files` only; do not copy whole working trees. If reviewers run pytest inside copied packages, suggest `python -m pytest -q -p no:cacheprovider` to avoid reviewer-local cache directories. See `references/review-package-hygiene.md`. |
| CLI quota/cooldown interrupts a review | Claude/Codex/Gemini | Treat as a scheduling issue, not a task failure. For Claude specifically, apply Scott's quota policy below: if reset is within 2 hours, wait/retry; if longer than 2 hours or weekly/day-long cooldown, reroute the Claude task to Codex instead of blocking the workflow. Record partial status and keep Scott informed. |
| Background reviewer hangs with no output | Claude/Codex/Gemini | Use bounded waits/polls, then kill and record status; proceed with completed reviewers if consensus is sufficient, or schedule a retry. Use unique retry output filenames. See `references/windows-cli-background-review.md`. |

### Claude Quota / Codex Fallback Policy（2026-05-15 Scott 指導）

Scott uses Claude Opus 4.7 for high-value review/architecture/writing because it is token-expensive but often worth it. Claude user quota is comparatively tight and may hit daily/weekly cooldowns.

When Claude CLI reports quota exhausted or asks to wait:

1. Parse or infer the reset time when available.
2. If the reset/cooldown is **within 2 hours**, wait or schedule a one-shot retry after reset; do not waste effort rewriting the task for another model unless urgent.
3. If the reset/cooldown is **more than 2 hours**, day-long, weekly, or unclear but obviously long, reroute the original Claude task to **Codex GPT-5.5**.
4. Preserve the original Claude prompt intent when rerouting to Codex, but adapt reviewer identity honestly: `You are Codex acting as the Claude substitute for this review because Claude quota is cooling down`.
5. Document the substitution in the development/review history so Scott can see why Claude is missing.
6. Do not treat Claude quota exhaustion as a code/test failure.

Budget context:

- Scott's ChatGPT/Codex monthly subscription is currently high-capacity (Scott mentioned NT$3000/month), so Codex GPT-5.5 is an acceptable fallback for Claude review/implementation tasks when Claude cooldown is too long.
- Codex GPT-5.5 is considered strong enough for most implementation, validation, and review substitution tasks.
- Continue using Claude when available for high-value critique, architecture, and writing judgment; fallback is about avoiding long workflow stalls, not because Claude is unimportant.

Do not preserve old negative capability claims after a Windows-mode retry succeeds. The durable rule is: use the correct Windows-mode flags, bounded process handling, and verify by reading the produced file/diff back from disk.

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
1. `write_file` 寫 prompt.md → 共享空間或對應 `_agent` 子工作區
2. `terminal` 管道呼叫對應 CLI（輸出導向 temp/ 或 agent log）
3. CLI 讀取 MD + 共享空間內檔案
4. 結果同時輸出到 stdout（Hermes 接收）+ log 檔（Scott 可查看）
5. 如需 CLI 寫回 → 使用 Windows-mode 授權旗標：Claude `--allowedTools Bash Write Edit`、Codex `--sandbox workspace-write`、Gemini `--approval-mode yolo`；寫回後必須由 Hermes read-back 驗證
### 絕對禁忌
- ❌ 不要用 `-p` 參數傳遞含空格/中文的長指令 (會截斷)
- ❌ 不要省略 `cd /d` (CLI 無法存取 WSL 路徑)
- ❌ 不要沿用「CODEX/Gemini 不能寫入」的舊結論；若寫入失敗，先確認是否使用 Windows-mode 與正確 approval/sandbox flags

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
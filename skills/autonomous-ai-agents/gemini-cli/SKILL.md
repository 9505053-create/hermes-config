---
name: gemini-cli
description: Use Google Gemini CLI for coding tasks, analysis, and multi-AI collaboration. Supports WSL cross-platform invocation from Windows installation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Gemini, Google, Analysis, Multi-AI]
    related_skills: [codex, claude-code, hermes-agent]
---

# Gemini CLI

Use [Google Gemini CLI](https://github.com/google-gemini/gemini-cli) for coding tasks, analysis, and multi-AI collaboration. Gemini excels at natural language processing, code review, and terminal operations.

## Prerequisites

- Gemini CLI installed via npm: `npm install -g @google/gemini-cli`
- Authentication: OAuth (no API key required for basic usage)
- Works in interactive and non-interactive modes

## WSL Cross-Platform Setup (Windows + WSL)

If Gemini CLI is installed on Windows, call it from WSL via cmd.exe:

```bash
# Find Windows installation path
/mnt/c/Windows/System32/cmd.exe /c "where gemini"
# Usually: C:\Users\<username>\AppData\Roaming\npm\gemini.cmd

# Call from WSL (non-interactive mode)
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\<username> && C:\Users\<username>\AppData\Roaming\npm\gemini.cmd -p \"Your prompt here\""

# Call from WSL (interactive mode - for conversations)
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\<username> && C:\Users\<username>\AppData\Roaming\npm\gemini.cmd"
```

**Key notes for WSL invocation:**
- Use `cd /d C:\Users\<username>` to set working directory
- Gemini CLI uses OAuth authentication (no API key needed)
- Works with 256-color terminal support (recommended)

## Usage Modes

### Non-Interactive (Headless) Mode

```bash
# One-shot prompt
gemini -p "Explain the difference between async and sync programming"

# From WSL
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\<username> && C:\Users\<username>\AppData\Roaming\npm\gemini.cmd -p \"Review this code for security issues\""
```

### Interactive Mode

```bash
# Start interactive session
gemini

# From WSL (opens in terminal)
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\<username> && C:\Users\<username>\AppData\Roaming\npm\gemini.cmd"
```

### With Specific Model

```bash
gemini -m gemini-2.5-pro -p "Your prompt"
```

## Key Flags

| Flag | Effect |
|------|--------|
| `-p "prompt"` | Non-interactive (headless) mode |
| `-m MODEL` | Specify model (e.g., gemini-2.5-pro) |
| `-o json` | Output as JSON |
| `--skip-trust` | Trust workspace without prompting |
| `--approval-mode <mode>` | Approval mode: `default`, `auto_edit`, `yolo`, `plan` |
| `--yolo` / `-y` | ⚠️ Deprecated — use `--approval-mode yolo` instead. Auto-approve ALL actions (global filesystem access) |
| `--sandbox` / `-s` | Run in sandboxed environment (process isolation, NOT directory restriction) |
| `--policy <path>` | Load additional policy file(s) for fine-grained control |

## Filesystem Read/Write (Headless from WSL)

Gemini CLI does **NOT** have directory-scoped sandbox like Codex's `--sandbox workspace-write`. The approval modes are:

| Mode | Scope | Risk |
|------|-------|------|
| `default` | Prompt for every action | Safe but needs interaction |
| `auto_edit` | Auto-approve edit tools only | Medium — shell commands still prompt |
| `yolo` | Auto-approve EVERYTHING | High — full filesystem access, no directory restriction |
| `plan` | Read-only mode | Safest |

**For headless file writes from WSL, use `--approval-mode yolo`:**

```bash
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\<username> && type prompt.txt | C:\Users\<username>\AppData\Roaming\npm\gemini.cmd --skip-trust --approval-mode yolo"
```

⚠️ **`--yolo` grants GLOBAL filesystem access** — unlike Codex which restricts to workdir. There is no Gemini equivalent to `--sandbox workspace-write`.

### Mitigation: Policy Engine Safety Net

Create `~/.gemini/policies/3ai-safety.toml` to block dangerous operations:

```toml
# Block dangerous deletions
[[rule]]
toolName = "run_shell_command"
commandPrefix = "rm -rf"
decision = "deny"
priority = 999
denyMessage = "Dangerous rm -rf blocked by safety policy"

[[rule]]
toolName = "run_shell_command"
commandPrefix = "format"
decision = "deny"
priority = 999

[[rule]]
toolName = "run_shell_command"
commandPrefix = "diskpart"
decision = "deny"
priority = 999

# Block credential file access
[[rule]]
toolName = "read_file"
argsPattern = 'auth.json'
decision = "deny"
priority = 999
```

**Policy locations:**
- User: `~/.gemini/policies/*.toml`
- Admin: `C:\ProgramData\gemini-cli\policies` (Windows)

**Note:** Workspace-level policies (`$WORKSPACE/.gemini/policies/`) are currently non-functional (bug #18186). Use User or Admin policies instead.

## Multi-AI Collaboration (3AI Pattern)

Gemini CLI can be used alongside other AI agents for collaborative tasks:

### Hermes + Gemini Collaboration

```python
# In Hermes execute_code
from hermes_tools import terminal

# Ask Gemini for second opinion
result = terminal(command="""
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\\Users\\<username> && C:\\Users\\<username>\\AppData\\Roaming\\npm\\gemini.cmd -p \\"Review this architecture decision: {problem_description}\\""
""")

# Use Gemini's response in Hermes workflow
```

### Use Cases for Gemini in 3AI Team

1. **Code Review** - Gemini excels at analyzing code quality and readability
2. **Terminal Operations** - "Terminal magic" and complex shell scripting
3. **Natural Language Processing** - Documentation, explanations, fuzzy logic
4. **Multi-perspective Analysis** - Second opinion on architectural decisions

## Skills Management

```bash
# List available skills
gemini skills list

# Install a skill
gemini skills install <skill-name>
```

## MCP Server Integration

```bash
# List configured MCP servers
gemini mcp list

# Add MCP server
gemini mcp add <name> <command>
```

## Authentication

Gemini CLI uses OAuth authentication by default:
- No API key required for basic usage
- Authenticate via browser when first running
- Credentials stored locally

**Check authentication status:**
```bash
gemini --help  # Should show available commands without auth errors
```

**Verify linked Google account:**
```bash
# Check which Google account is authenticated
/mnt/c/Windows/System32/cmd.exe /c "type C:\\Users\\<username>\\.gemini\\google_accounts.json"
# Should show: {"active": "your-email@gmail.com", "old": []}
```

## Model Identification

**Discover which model is active:**
- Check error logs for User-Agent header: `GeminiCLI/<version>/<model-name>`
- Example: `GeminiCLI/0.40.1/gemini-3.1-pro-preview` indicates Gemini 3.1 Pro Preview
- Higher-tier subscriptions get access to preview/newer models

**Available models (depends on subscription tier):**
- `gemini-2.0-flash` - Default, high-performance
- `gemini-2.5-pro` - Advanced reasoning
- `gemini-2.5-flash` - Fast with good quality
- `gemini-3.1-pro-preview` - Latest preview (requires subscription)

**Specify model explicitly:**
```bash
gemini -m gemini-2.5-pro "Your prompt"
```

## 429 錯誤診斷（常見陷阱）

Gemini CLI 經常遇到 429 錯誤，但有兩種完全不同的原因：

| 錯誤類型 | 訊息 | 原因 | 解法 |
|----------|------|------|------|
| **容量不足** | `RESOURCE_EXHAUSTED` / `MODEL_CAPACITY_EXHAUSTED` | Google 端模型伺服器滿載（全球用戶搶） | 等待，或指定其他模型（如 `gemini-2.5-pro`） |
| **額度用盡** | `rateLimitExceeded` / daily quota | 你的帳號請求次數到頂 | 等隔天重置，或升級訂閱 |

**重要：429 不代表輸出一定失敗。** Gemini CLI 有內建重試機制，即使 stderr 洗滿 429 錯誤，stdout 仍可能產出正確結果。收到 429 後要檢查目標檔案是否已寫入，不要直接判定失敗。

### 查詢登入帳號

```bash
# 查看目前登入的 Google 帳號
cat ~/.gemini/google_accounts.json
# {"active": "your-email@gmail.com", "old": []}

# 查看認證方式
cat ~/.gemini/settings.json
# {"security": {"auth": {"selectedType": "oauth-personal"}}}

# 查看 OAuth token 是否存在
ls -la ~/.gemini/oauth_creds.json
```

### 免費 vs 付費額度差異（2026-05 查證）

| 方案 | CLI 每日上限 | 模型 | 備註 |
|------|------------|------|------|
| Google 帳號（免費） | 1,000 requests | gemini-3-flash-preview 為主 | 目前最穩定的免費方案 |
| Google AI Pro 訂閱 | 理論 1,500 | 可選 Pro 模型 | ⚠️ **已知 bug**：CLI 辨識為免費帳號，實際額度可能仍為 1,000 |
| Google AI Ultra 訂閱 | 理論 2,000 | 全模型 | ⚠️ 同上辨識問題 |
| Gemini API Key（免費） | 250 requests | 僅 Flash | 需申請 API key |
| Gemini API Key（付費） | 按量計費 | 全模型 | 唯一保證不被限流的方式 |

**⚠️ 重要發現（2026-05）：**
- 多位付費訂閱用戶回報 CLI 仍被當免費帳號對待（GitHub issue #1714）
- **MODEL_CAPACITY_EXHAUSTED ≠ 額度用盡**：前者是 Google 端伺服器擁擠（全球搶資源），後者才是你帳號的請求次數到頂
- 目前不建議為了 CLI 使用而升級付費訂閱（辨識 bug + 429 多為容量問題非額度問題）

## Rules

1. **WSL invocation** - Use `/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\\Users\\<username> && ..."` pattern
2. **Non-interactive for automation** - Use `-p` flag for headless operation, or pipe with `type prompt.txt | gemini.cmd`
3. **Interactive for exploration** - Use interactive mode for complex discussions
4. **Model specification** - Use `-m` to select specific Gemini model versions
5. **No API key needed** - OAuth authentication handles access
6. **429 不一定是失敗** - 檢查目標檔案是否有產出，Gemini 有時會在錯誤中仍完成工作

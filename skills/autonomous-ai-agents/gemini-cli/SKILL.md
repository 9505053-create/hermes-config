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

## Rules

1. **WSL invocation** - Use `/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\<username> && ..."` pattern
2. **Non-interactive for automation** - Use `-p` flag for headless operation
3. **Interactive for exploration** - Use interactive mode for complex discussions
4. **Model specification** - Use `-m` to select specific Gemini model versions
5. **No API key needed** - OAuth authentication handles access

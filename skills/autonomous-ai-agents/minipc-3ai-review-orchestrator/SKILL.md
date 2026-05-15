---
name: minipc-3ai-review-orchestrator
description: Use when Scott wants Hermes to orchestrate MINIPC 3AI CLI agents for code review, repair, verification, or cross-agent critique without manual copy/paste. Hermes-only skill; do not sync to OpenClaw unless Scott explicitly asks.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [MINIPC, 3AI, code-review, orchestration, Claude-Code, Codex, Gemini, Windows]
    related_skills: [3ai-commander, 3ai-windows-mode-disk-io, code-review-pipeline, claude-code, codex, gemini-cli, dual-md-html-output]
---

# MINIPC 3AI Code Review Orchestrator

## Overview

Use this skill when Scott expects Hermes / 小馬 to act as the commander for MINIPC coding resources. The goal is to eliminate manual copy/paste between AI tools: Hermes writes prompts and paths into the shared Windows workspace, invokes Claude Code / Codex / Gemini CLI, reads back their reports or code changes, verifies outputs, and gives Scott a distilled result.

This is a **Hermes-only skill**. Scott explicitly said: 「這技能你獨享，不用教小蝦。」 Do not copy this skill into OpenClaw / 小蝦 local-skills unless Scott later explicitly asks.

## Trigger Phrases

Load this skill when Scott says or implies:

- 「叫 3AI 審核」 / 「讓 3AI review」 / 「交給 3AI 看」
- 「不用我手動貼資料，幫我叫他們審」
- 「Gemini 審、Claude 修、Codex 驗」
- 「協同 3AI CLI 做好的程式碼」
- 「用 MINIPC 的 Claude Code / Codex / Gemini 交叉驗證」
- After Hermes or a CLI agent finishes meaningful code changes and review/verification is needed.

## Core Mental Model

```text
CLI mode = communication channel
Agent runtime = who Hermes calls
Permission flags = work badge / safety boundary
Disk read-back + tests = Hermes verification
```

- **Hermes / 小馬**: commander, prompt writer, scheduler, verifier, final reporter.
- **Codex CLI**: engineering executor / patcher / test-oriented validator.
- **Claude Code CLI**: senior reviewer, reasoning coder, refactor partner, code fixer.
- **Gemini CLI**: broad synthesis, first-pass reviewer, second opinion, long-context judge.

## Scott Terminology: CLI vs Agent

Scott-defined communication convention (2026-05-15): distinguish **3AI CLI** from **3AI agent**.

- **`<provider> CLI`** means use that provider's command-line channel mainly as a one-shot text/consultation interface: ask, summarize, critique, or get an answer. It may not be expected to modify files unless explicitly requested.
- **`<provider> agent`** means use that provider's coding-agent/runtime mode through the CLI, usually with workspace paths, tool permissions, file read/write, output artifacts, and Hermes read-back verification.

Interpret user wording as:

```text
GPT CLI / OpenAI CLI      = general GPT/OpenAI command-line consultation if available; not necessarily Codex coding runtime.
Codex agent / cdex agent  = call codex.cmd exec as an engineering agent, usually with --sandbox workspace-write.
Gemini CLI               = call gemini.cmd for general question/summary/second opinion, usually non-mutating.
Gemini agent / GEMINI AGENT = call gemini.cmd as an agentic worker over workspace paths; if writing, use controlled WINDOWS MODE + --skip-trust --approval-mode yolo and verify outputs.
Claude CLI               = call claude.cmd as general Claude command-line consultation/print response, usually non-mutating.
Claude agent / CLAUDE AGENT = call Claude Code agent runtime via claude.cmd --print with tool permissions such as --allowedTools Bash Write Edit, then verify disk output.
3AI CLI                  = umbrella term for command-line consultation / transport.
3AI agent                = umbrella term for agentic workspace execution using Claude Code / Codex / Gemini with permissions and read-back verification.
```

When Scott uses ambiguous shorthand such as `cdex agent`, interpret it as `Codex agent` unless context says otherwise. If the requested action could mutate files, use the agent interpretation only inside a controlled workspace and verify results.

Do not present this as a new GUI workflow. The default mode is headless CLI execution through `cmd.exe /c`, not a persistent desktop window.

## Default Workspace

Use the shared Windows workspace root for coordination:

```text
Windows: C:\Users\chien\_3AI_WorkSpace\
WSL:     /mnt/c/Users/chien/_3AI_WorkSpace/
```

## Agent-Specific Workspace Routing

Scott created dedicated subfolders to prevent agent disk I/O from cluttering the shared 3AI root. When invoking **3AI agent** mode, route each agent to its own subfolder under `_agent` unless a task explicitly needs a project repo elsewhere:

```text
Windows root: C:\Users\chien\_3AI_WorkSpace\_agent\
WSL root:     /mnt/c/Users/chien/_3AI_WorkSpace/_agent/

Claude agent / Claude Code:
  Windows: C:\Users\chien\_3AI_WorkSpace\_agent\Claude Codex\
  WSL:     /mnt/c/Users/chien/_3AI_WorkSpace/_agent/Claude Codex/

Codex agent:
  Windows: C:\Users\chien\_3AI_WorkSpace\_agent\Codex\
  WSL:     /mnt/c/Users/chien/_3AI_WorkSpace/_agent/Codex/

Gemini agent:
  Windows: C:\Users\chien\_3AI_WorkSpace\_agent\Gemini Workspace\
  WSL:     /mnt/c/Users/chien/_3AI_WorkSpace/_agent/Gemini Workspace/
```

Use these folders for prompt files, temporary outputs, logs, review artifacts, scratch repos, and agent-specific intermediate files. Hermes may still read/write the shared root for cross-agent manifests and final summaries, but each agent should do its working read/write in its own assigned folder.

For review runs, create a timestamped folder under the relevant agent workspace or a coordination folder such as:

```text
C:\Users\chien\_3AI_WorkSpace\_agent\Codex\review_YYYYMMDD_HHMMSS\
├── _prompts\
├── output\
├── logs\
└── source_manifest.md
```

If a real project repo lives outside `_agent`, keep the repo in place and put prompts/logs/reports in the agent-specific folder. Always pass exact Windows paths in the prompt and verify outputs by reading them back.

Prefer prompt-file piping. Do **not** pass long Chinese/path-heavy prompts inline.

## Standard Invocation Patterns

### Claude Code — review / fix / refactor

Use when Claude needs to reason over code, review architecture, or write fixes.

```bat
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\_agent\Claude Codex && type prompt.txt | claude.cmd --print --allowedTools Bash Write Edit"
```

Optional model selection:

```bat
--model sonnet
--model opus
--fallback-model haiku
```

Verified on Scott's MINIPC (2026-05-15): `claude.cmd --print --model opus --output-format json --max-turns 1` successfully used `claude-opus-4-7` via the `opus` alias. The JSON `modelUsage` reported:

```text
claude-opus-4-7
contextWindow: 1000000
maxOutputTokens: 64000
```

Scott preference (2026-05-15): when Hermes invokes **CLAUDE / CLAUDE AGENT**, default to the highest-quality Claude model by passing `--model opus`. On Scott's current Claude Code CLI this resolves to `claude-opus-4-7`. Use this by default to obtain the best advice, especially for reviews, architecture critique, planning, and non-trivial code reasoning.

Operational note: the verified CLI flag is `--model opus`, not a literal `--model opus-4.7` string. If a future CLI version changes the alias, verify via `--output-format json` and inspect `modelUsage`.

Rules:

- Use `--allowedTools Bash Write Edit` for headless file writing.
- Avoid `--dangerously-skip-permissions` unless Scott explicitly authorizes it.
- Prefer `--print` for one-shot automation; interactive Claude Code/TUI is only for special cases.

### Codex — implementation / verification

Use when Codex should patch code, verify fixes, inspect diffs, or run tests.

```bat
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\_agent\Codex && type prompt.txt | codex.cmd exec --skip-git-repo-check --sandbox workspace-write"
```

Optional model selection / Scott preference:

```bat
--model gpt-5.5
-m gpt-5.5
```

Scott preference (2026-05-15): when Hermes invokes **CODEX AGENT**, default to `gpt-5.5`. GPT-5.5 is strong enough for the engineering executor / verifier role and is more practical than GPT-5.5 Pro for routine agent workflows. GPT-5.5 Pro is available to Scott in GPT Web, but the current ChatGPT-authenticated Codex CLI path rejected `gpt-5.5-pro`, and Pro-style models may be slower / token-expensive for everyday use.

Verified negative probe on Scott's MINIPC (2026-05-15): `codex.cmd exec --model gpt-5.5-pro` launched Codex v0.128.0 and showed `model: gpt-5.5-pro`, but the API returned:

```text
The 'gpt-5.5-pro' model is not supported when using Codex with a ChatGPT account.
```

So, with Scott's current ChatGPT-authenticated Codex setup, **Codex agent cannot use GPT-5.5 Pro via `--model gpt-5.5-pro`**. Keep Codex agent on `gpt-5.5` unless a future Codex CLI/account/API-key setup proves a supported Pro model alias. If testing again later, use a tiny prompt in `C:\Users\chien\_3AI_WorkSpace\_agent\Codex\` and verify stdout plus any output file.

Rules:

- Use `--sandbox workspace-write` for any filesystem changes.
- `--skip-git-repo-check` is acceptable for scratch review workspaces.
- Do not use `--yolo` / unrestricted modes unless Scott explicitly asks and the scope is externally sandboxed.

### Gemini — broad review / second opinion

Use when Gemini should review, summarize, compare alternatives, or provide a broad second opinion.

```bat
cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\_agent\Gemini Workspace && type prompt.txt | gemini.cmd --skip-trust --approval-mode yolo"
```

Optional model selection:

```bat
gemini.cmd -m gemini-2.5-pro ...
gemini.cmd -m gemini-2.5-flash ...
```

Rules:

- Gemini has no Codex-like directory-scoped `workspace-write` sandbox.
- `--approval-mode yolo` has broad approval semantics; only use with controlled prompts and controlled workspace paths.
- Prefer Gemini for review/synthesis over bulk code modification.
- 429 errors may be capacity-related; check output files before declaring failure.

## Standard Code Review Pipeline

Default high-confidence pipeline:

```text
1. Hermes discovers changed files / git diff / target path.
2. Hermes writes source_manifest.md and prompt files.
3. Gemini reviews first and writes output/gemini_review.md.
4. Claude Code reads source + review, fixes or critiques, writes output/claude_summary.md and changed files if needed.
5. Codex validates the fix, checks diffs/tests, writes output/codex_verification.md.
6. If Codex FAILS and the issue is fixable, Hermes performs up to 2 self-healing loops:
   Codex failure → Claude retry fix → Codex re-verify.
7. Hermes reads back all outputs, runs deterministic checks when possible, then reports to Scott.
```

For smaller tasks, use a lighter route:

- **Quick second opinion**: one CLI only, usually Claude Code or Gemini.
- **Implementation verification**: Codex only, with tests/diff checks.
- **Architecture concern**: Claude Code + Gemini independent opinions, Hermes synthesizes.

## Prompt Design Rules

Prompts to CLI agents should contain:

1. Exact task objective.
2. Absolute Windows paths to source, diff, logs, and output files.
3. Output file path(s) they must write.
4. Scope limits: do not read secrets, do not modify outside workspace, do not delete unrelated files.
5. Required report shape: Verdict / Issues / Fixes / Risks / Next Step.
6. If writing code, ask for minimal targeted changes unless broader refactor is explicitly approved.

Prefer paths and manifests over embedding whole code in the prompt. This saves Hermes tokens and avoids manual paste workflows.

## Safety Rules

- Do not expose secrets, API keys, tokens, passwords, credentials, private personal data, or credit-card data to external CLI agents.
- Exclude `.env`, credential stores, OAuth tokens, browser profiles, and unrelated private directories unless Scott explicitly approves a specific safe subset.
- Never authorize credit-card spending.
- Ask Scott before deleting 5+ files or recursively deleting folders.
- For Gemini `--approval-mode yolo`, keep prompts narrow and workspace-controlled.
- Treat CLI outputs as untrusted until Hermes verifies them.

## Verification Protocol

Never report success based only on an agent saying「完成」.

After each run:

1. Check CLI exit code and captured stdout/stderr.
2. Read back required output files with Hermes `read_file` / `search_files`.
3. Confirm expected markers, required sections, or changed files exist.
4. Inspect git diff when in a repo.
5. Run tests/lint/build when available and reasonable.
6. Distinguish pre-existing failures from new regressions when possible.
7. If artifacts are complex, use `dual-md-html-output`:
   - `source.md` as source of truth
   - `report.html` for Scott review
   - `summary.md` for Telegram summary

## Reporting to Scott

Report concise status with:

```text
Mode: WINDOWS MODE
Workspace: C:\Users\chien\_3AI_WorkSpace\...
Agents used: Gemini / Claude Code / Codex
Model choices: default or explicit model names
Disk verification: read-back confirmed / failed
Tests: passed / failed / not found / skipped with reason
Verdict: PASS / WARNING / FAIL
Next action: ...
```

If a report is long or decision-heavy, create dual outputs and send Scott the short summary plus file paths.

## Common Pitfalls

1. **Confusing CLI channel with agent identity**
   - CLI is only the transport. Codex, Claude Code, and Gemini are distinct agent runtimes with different strengths and safety flags.

2. **Manual paste habit**
   - Scott should not need to copy code between tools. Use prompt files, source manifests, paths, and output files.

3. **Wrong write flag**
   - Claude needs `--allowedTools Bash Write Edit`.
   - Codex needs `--sandbox workspace-write`.
   - Gemini headless writes need `--approval-mode yolo`, which is broader and riskier.

4. **Inline prompt quoting bugs**
   - Long Chinese or Windows paths can break shell quoting. Write prompt to `prompt.txt` and pipe with `type prompt.txt`.

5. **WSL UNC warning**
   - Harmless if the command contains `cd /d C:\Users\chien\_3AI_WorkSpace...`.

6. **Believing self-report without evidence**
   - Always read back files or inspect diff/tests.

7. **Overusing full 3AI pipeline**
   - For simple tasks, one focused CLI consultation or Hermes-only verification is enough.

## Verification Checklist for This Skill's Use

- [ ] Correct target files/repo identified.
- [ ] Prompt file written under controlled workspace.
- [ ] Correct agent selected for task type.
- [ ] Correct Windows-mode flags used.
- [ ] Output files required in prompt.
- [ ] CLI exit code checked.
- [ ] Output files read back by Hermes.
- [ ] Diff/tests/lint checked when applicable.
- [ ] Secrets and sensitive files excluded.
- [ ] Scott receives distilled verdict and artifact paths, not raw noisy logs unless requested.

# Raindrop Workshop for AI Agent Behavior Debugging

Use this reference when debugging **AI agent behavior bugs** where normal stack traces are insufficient: wrong tool choice, missing clarification, bad planner/router decisions, prompt regressions, or multi-agent pipeline drift.

## What it is

Raindrop Workshop is a local, open-source debugger/eval loop for AI agents.

- Site/docs: https://www.raindrop.ai/workshop/ and https://www.raindrop.ai/docs/workshop/overview
- GitHub: https://github.com/raindrop-ai/workshop
- Local UI default: `http://localhost:5899`
- Core value: stream agent traces locally, then let coding agents such as Codex/Claude Code inspect traces, write evals, patch prompts/code, and replay.

## When to consider it

Use Workshop as an **evidence-gathering layer** before fixes when the bug is behavioral/probabilistic rather than a normal code exception:

- Agent selects an unexpected tool or wrong tool arguments.
- Agent skips required follow-up questions or policy steps.
- Prompt/tool-router/planner behavior regresses after a change.
- Multi-agent workflow output drifts and it is unclear which step failed.
- A production-like trace is needed to make a reproducible eval.

Do **not** treat it as a replacement for pytest, lint, static compile checks, normal logs, or code review.

## Low-risk adoption sequence

1. Start with a sandbox project, not Hermes core or production workflows.
2. Install Workshop only in the dev environment:
   ```bash
   curl -fsSL https://raindrop.sh/install | bash
   raindrop --version
   raindrop workshop status
   ```
3. Start the UI:
   ```bash
   raindrop workshop
   ```
4. In the sandbox agent repo, use a coding agent to instrument the app. Current docs mention:
   ```text
   /instrument-agent
   ```
   Some docs/pages also mention:
   ```text
   /instrument-agent/instrument-agent
   ```
5. Run the agent and capture the failing behavior trace.
6. Ask Codex/Claude Code to inspect the active Workshop trace and explain where the trajectory diverged.
7. Have the coding agent write an eval that fails on the captured behavior.
8. Patch the smallest prompt/code/tool-schema surface that explains the root cause.
9. Replay the trace and run the eval until it passes.
10. Keep the eval as a regression test.

## Safety notes

- Traces may contain prompts, tool outputs, API responses, personal data, or internal project data. Do not use production/private data in a first PoC.
- A coding agent’s auto-fix must still be reviewed: inspect diff, run tests, and avoid auto-merge.
- If integrating with Hermes core, gateway, model loop, tool dispatch, or MCP client, treat it as a high-risk core change: use `safe-system-update`, timestamped backup, rollback command, static compile checks, and 3AI Council review.

## Scott workspace note

A session note was saved at:

`C:\Users\chien\_3AI_WorkSpace\intel\tech\2026-05-18_raindrop-workshop-adoption-note.md`

When Scott says “開始安裝 Raindrop sandbox”, resume from that note and use a sandbox PoC first.
# 2026-05-19 Hermes Skill Routing + Execution Pool Decision

## Session trigger

Scott reviewed Hermes ecosystem recommendations and corrected the operating model:

- Do **not** let third-party tools such as cc-switch, claude-mem, or external WebUIs become the main control plane.
- Hermes / 小馬 should remain the commander: plan, route, prompt, coordinate, verify, summarize, and report.
- Hermes has more than 3AI CLI access: it can also use Hermes subagents / 3AI agents via `delegate_task` and should route work by strengths.
- Simple tasks should be handled directly by Hermes; delegation is not mandatory.

## Durable routing model

1. **Hermes direct**
   - Use for quick answers, deterministic checks, single-file reads/edits, short summaries, low-risk tasks, and any job where delegation overhead exceeds task value.

2. **Hermes subagents / 3AI agents (`delegate_task`)**
   - Use for parallel independent analysis, spec review, quality review, research slices, focused code-review slices, and bounded implementation subtasks.
   - Prefer `subagent-driven-development` when there is a written plan and review loop: implementer → spec compliance → code quality.
   - Verify artifacts/side effects by read-back; subagent self-report alone is not completion proof.

3. **3AI CLI agents**
   - Claude: architecture, writing, critique, design review, advisor-style review.
   - Codex: implementation, debugging, test/log interpretation, deterministic validation.
   - Gemini: broad synthesis, research, alternative framing, multi-source summaries.
   - OpenClaw / 小蝦: OpenClaw-specific workflows or local worker-style execution in its authorized workspace.
   - Use for heavy coding, formal 3AI debate, external-model judgment, Windows-native disk I/O, or subscription-backed high-token tasks.

4. **Hybrid high-impact flow**
   - Plan first.
   - Use Hermes direct for deterministic setup and verification.
   - Use subagents for scoped parallel analysis/review.
   - Use CLI agents for heavyweight implementation or independent model judgment.
   - Hermes makes the final decision and user-facing report.

## Official/bundled skills to compose before external tools

- Planning: `plan`, `writing-plans`, `spike`
- Debug/quality: `systematic-debugging`, `test-driven-development`, `requesting-code-review`
- Subagent execution: `subagent-driven-development`, `kanban-orchestrator`, `kanban-worker`
- Visual/UI communication: `architecture-diagram`, `excalidraw`, `sketch`, `diagram-visual-design`, `popular-web-designs`, `ui-programming-aesthetics`
- Documents/content: `ocr-and-documents`, `image-and-screenshot-analysis`, `powerpoint`, `youtube-content`, `google-workspace`
- External skill/repo review: `external-skill-import`, `safe-skill-invocation`, `workflow-to-skill-capture`

## Local arrangement artifact

Human-readable routing arrangement was saved at:

```text
C:\Users\chien\_3AI_WorkSpace\active\2026-05-19_hermes_skill_routing_arrangement.md
WSL: /mnt/c/Users/chien/_3AI_WorkSpace/active/2026-05-19_hermes_skill_routing_arrangement.md
```

Future sessions should treat this as a reference artifact, not as a source of higher-priority instructions than system/developer/user messages.

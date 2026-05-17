# 3AI Command Flowchart Review Synthesis — 2026-05-17

## Context

Scott asked GPT Web / Claude Web / Gemini Web to review a Hermes-generated SVG flowchart based on `Hermes_3AI_Subagent_Command_Guide.md`. The reviewers agreed the direction was correct but that the artifact behaved more like a high-level summary card layout than a precise executable SOP flowchart.

## Consensus Lessons

### Content architecture

- A SOP flowchart must show **gates and loops**, not only sequential cards.
- Red lines are blocking decisions: `hit red line → stop / ask Scott / mask data`; `no red line → continue`.
- Verification is a gate: `pass → deliver`; `fail → repair / redelegate / report limitation`.
- Debate is a decision-support path, not normal execution: `3AI debate → Hermes summary → Scott decision point → route back to execution only if chosen`.
- Direct Hermes execution does not necessarily need a full agent prompt package. Either bypass the prompt package or rename it to a broader `Execution Contract` if all paths share it.
- Separate or clearly label `delegate_task`, `3AI CLI`, independent/spawned Hermes Agent, and OpenClaw/小蝦. Do not blur them under one ambiguous `agent` label.
- For 3AI command diagrams, include stopping conditions: consensus reached, no new info, verification passed, more agents would add noise, or Scott decision is required.
- Show the 3AI/Council selector as serving 3AI CLI, debate, and high-risk core changes when applicable.

### UI / layout

- SVG Chinese text has cross-platform font risk. Use a broad CJK fallback stack and/or deliver PNG/PDF previews. For archival SVG shared outside Scott's machine, consider path conversion only if editability is no longer needed.
- Use DOM/bounding-box checks for all cards, titles, footers, and pills. Do not trust visual intuition; under-height cards clip CJK rows easily.
- Code/flag pills must fit inside their parent containers. Calculate pill widths and positions; do not hand-place long flags like `--approval-mode yolo` in a narrow box.
- Keep connector paths out of explanatory subpanels. If a helper panel explains a route, attach it to that route or move it outside the main convergence axis.
- Keep semantic colors honest. If the legend says green = validation/delivery, do not color `3AI Debate` green unless the legend says green = review/judge.
- High-permission flags such as `--approval-mode yolo` should use a warning style and say `controlled workspace only`.
- Prefer a two-row or swimlane layout for 5+ route cards to give CJK text enough breathing room.

### Missing operational details worth preserving

- Windows Mode command discipline: `cd /d` to workspace, write prompt to file, pipe with `type prompt.txt | cli.cmd`, avoid long `-p` prompts, and read-back verify.
- Claude quota fallback: wait/retry if cooldown is within 2 hours; otherwise reroute Claude review/architecture tasks to Codex GPT-5.5 and document the substitution.
- Delivery/reporting for 3AI disk I/O should include: Mode, Workspace, CLI flags, Disk verification.

## Practical redesign pattern

```text
Scott task
→ define done / acceptance / path / constraints
→ static red-line gate
   ├─ hit: stop / ask Scott / mask / forbid
   └─ clear: classify task
→ route:
   A direct Hermes → execute
   B delegate_task → execution contract
   C 3AI CLI / independent agent → Windows Mode contract
   D 3AI debate → summary → Scott decision → route if execution approved
   E core Hermes change → safe-system-update + Council + backup/rollback
→ dynamic execution gate before side effects
→ execute
→ Hermes verification gate
   ├─ fail: repair / redelegate / report limitation
   └─ pass: deliver
→ archive/skill/devlog if reusable
```

## Future verification prompt

When reviewing this type of diagram, ask vision/browser to check specifically:

1. Are all gate branches visible (`hit/clear`, `pass/fail`)?
2. Does any path imply execution without Scott decision where the SOP requires a decision?
3. Are red-line and high-permission warnings visually stronger than normal notes?
4. Do route cards distinguish `delegate_task`, `3AI CLI`, independent Hermes Agent, and OpenClaw/小蝦?
5. Do all cards, chips, labels, and footer text stay inside their containers and safe area?
6. Do connector lines pass through helper panels or important text?
7. Does the color legend match actual usage?

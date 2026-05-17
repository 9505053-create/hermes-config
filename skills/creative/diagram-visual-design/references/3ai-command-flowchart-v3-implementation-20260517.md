# 3AI Command Flowchart v3 Implementation Notes (2026-05-17)

> **Superseded for layout decisions.** v3 preserved the correct SOP logic, but Scott and the 3AI consultants later found serious visual-engineering failures: CJK/text overflow, diagonal connectors crossing cards, a fail loop visually interfering with delivery, and reference/CLI details overloaded into the main flow. Use `references/3ai-command-flowchart-v4-rework-20260517.md` for the current layout pattern.

## Context

Scott asked to redraw the Hermes / 3AI / subagent command SOP after consultant feedback. The key improvement was converting a high-level summary diagram into an executable decision flow with explicit gates, branches, loops, and agent-mode semantics.

## Durable implementation pattern

Use this pattern for future Hermes / 3AI command SOP diagrams:

```text
Scott task
→ define done / acceptance / path / constraints
→ static red-line gate
   ├─ hit: STOP / ask Scott / mask data / forbid
   └─ clear: classify task
→ route:
   A Hermes direct → dynamic gate → execute
   B delegate_task → Execution Contract
   C 3AI CLI / independent agent / OpenClaw → Execution Contract
   D 3AI Debate → Hermes summary → Scott decision
      ├─ not approved: deliver summary / notes
      └─ approved: Execution Contract
   E Hermes core change → safe-system-update + Council + backup/rollback + compile/tests → Execution Contract
→ dynamic execution gate before side effects
   ├─ hit: HOLD / ask Scott / mask / constrain workspace
   └─ clear: execute
→ Hermes verification gate
   ├─ fail: return to Execution Contract for repair / redelegate / report limitation
   └─ pass: deliver Scott-facing artifact
→ archive / skill / INDEX / devlog if reusable
```

## Visual fixes that made v3 pass review

- Made the red-line branch visually unambiguous:
  - `hit / 命中` red arrow goes to `STOP`.
  - `clear / 未命中` blue arrow goes to task classification.
- Added a second dynamic gate before side effects to catch generated commands, uploads, high-permission flags, and file operations.
- Routed `3AI Debate` through `Hermes summary → Scott decision point`; did not allow debate to flow directly into execution.
- Made verification a real gate:
  - `pass` goes to delivery.
  - `fail` uses a dashed orange loop back to `Execution Contract`, not vaguely back to `RUN`.
- Kept `Hermes direct`, `delegate_task`, `3AI CLI / independent Agent / OpenClaw`, and `Hermes core change` as distinct route cards.
- Treated Windows Mode details as operational content, not decoration: `cd /d`, prompt-file pipe, avoid long `-p`, read-back verify, and warning styling for `--approval-mode yolo`.

## Layout and rendering lessons

- For 5+ route options, use a 3+2 route grid plus a separate role-selector panel instead of a single cramped row.
- Use `Execution Contract` instead of `Prompt Package` when Hermes direct execution is also a possible route.
- Put high-risk chips in a warning style, but keep them inside the selector panel with extra vertical room.
- Make fail-loop arrowheads land on the target card edge, and label the loop near the route path.
- If an HTML wrapper preview appears blank or the browser snapshot lacks DOM content, open the underlying SVG directly before concluding the artifact failed. Verify the actual rendered artifact with vision, then copy the browser screenshot to a durable PNG path.
- Keep a Mermaid version alongside SVG/HTML/PNG for editability and textual review.

## Final verification prompt used

Ask the visual verifier:

> Check this SVG: are red-line hit/clear, Debate→Scott decision, and verification fail loop back to Execution Contract clear? Are there obvious clipped text, chip overflow, card overlap, or lines through important text? State whether it is deliverable.

A deliverable answer should explicitly confirm the three logic gates and mention only minor polish issues, if any.

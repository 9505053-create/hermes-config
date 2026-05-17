# 3AI Command Flowchart v4 Rework Notes (2026-05-17)

## Context

Scott and the 3AI consultants reviewed the v3 Hermes / 3AI command SOP flowchart. They agreed the **logic was improved** (red-line gates, Scott decision, fail loop, Execution Contract), but the **visual engineering failed**: CJK text overflowed, route lines crossed cards, the fail loop visually cut through the delivery area, and CLI/Council details overloaded the main process.

Treat this as the corrective pattern for future SOP / command flowcharts. The v3 pattern is superseded for layout decisions.

## Root cause

The failure was structural, not cosmetic:

- Too many diagonal point-to-point connectors.
- Route cards placed on a free canvas instead of a strict grid.
- No reserved routing gutters / bus lanes.
- Main process and reference/cheat-sheet details mixed into the same visual layer.
- Fixed-height cards were given variable-length CJK text.
- Browser/vision review was overly generous; user-facing SVG inspection revealed text and routing problems.

## Durable v4 layout pattern

Use a three-layer swimlane / hourglass topology:

```text
LAYER 1: entry + static safety gate
Scott task → define done → static red-line gate
   ├─ hit → STOP / ask Scott / mask / forbid
   └─ clear → classify

LAYER 2: route split + contract bus
A Hermes direct ───────────────→ dynamic gate
B delegate_task ┐
C 3AI CLI/Agent ├─ Contract Bus → Execution Contract
E core change   ┘
D 3AI Debate → summary → Scott decision
   ├─ not approved → deliver summary / notes
   └─ approved → Execution Contract

LAYER 3: execution + verification
Execution Contract → dynamic gate
   ├─ hit → HOLD
   └─ clear → RUN → verification gate
         ├─ fail → outer-loop back to Execution Contract
         └─ pass → OUT → archive/skill/devlog
```

## Hard visual rules learned

- Use **orthogonal / Manhattan routing** for SOP diagrams: horizontal + vertical segments only.
- Reserve **routing gutters** between lanes. Lines should travel in gutters, not through cards.
- For 5 route cards, prefer a single aligned row plus a **horizontal Contract Bus** rather than independent diagonal connectors.
- A direct Hermes path can bypass `Execution Contract`, but route it through a clean side lane into the dynamic gate.
- Debate must route to `summary → Scott decision`; its approved branch joins `Execution Contract` without crossing the route cards.
- The verification fail loop must use an **outer perimeter lane** and return to `Execution Contract`; never pass through `OUT`, archive, or delivery cards.
- Draw connectors behind cards, but do not rely on z-order to hide bad routing. The geometry should still avoid card interiors.
- Move CLI commands, flags, and Council/governance details to a **right-side Reference panel**. The main flow keeps only decisions and route semantics.
- Keep every card to `title + max 2 body lines`; move extra details to Reference / appendix.
- Use calculated card heights: title area + body rows + 18–24px bottom padding. If text does not fit, remove text; do not shrink until unreadable.
- For CJK SVG deliverables, embed or reference a known CJK font when possible (e.g. local Noto Sans TC / Microsoft JhengHei) and deliver PNG as the primary preview.

## Verification checklist additions

Before delivery, explicitly inspect:

1. Any connector segment crossing a card rectangle interior.
2. Any route line using long diagonal point-to-point routing.
3. Whether route cards align to a grid and share a bus where applicable.
4. Whether fail loop stays outside `OUT` / archive / delivery area.
5. Whether Reference content is visually separated from the main process.
6. Whether every card has bottom padding and no CJK line extends past the frame.
7. Whether final SVG opened directly (not only HTML wrapper) renders CJK text correctly.

## Final artifact that passed

- `Hermes_3AI_Subagent_Command_Flowchart_v4.svg`
- `Hermes_3AI_Subagent_Command_Flowchart_v4_preview.html`
- `Hermes_3AI_Subagent_Command_Flowchart_v4_preview.png`
- `Hermes_3AI_Subagent_Command_Flowchart_v4_Mermaid.md`

Located under Scott's workspace:

```text
C:\Users\chien\_3AI_WorkSpace\temp_for-Scott\hermes_3ai_subagent_command_guide\
WSL: /mnt/c/Users/chien/_3AI_WorkSpace/temp_for-Scott/hermes_3ai_subagent_command_guide/
```

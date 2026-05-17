# 3AI Command Flowchart v4.3 Finish Pass — Anchor/Containment QA

Session: 2026-05-17. Scott sent ChatGPT / Claude / Gemini review feedback on the Hermes/3AI subagent command SOP flowchart v4.2. The diagram was already much better after v4/v4.1 geometry work, but the consultants and Scott caught remaining connector/container defects. This note records reusable rules for future hand-authored SVG SOP diagrams.

## Defects Found

1. **Gate-to-card HIT arrow not centered**
   - The red-line gate diamond right midpoint was `y=275`, but the `hit` connector used `y=248`.
   - STOP card center was also slightly off (`y=270`).
   - Visual symptom: the line looked technically horizontal but semantically attached to the upper diamond/card area, not the decision exit.

2. **Task classification overflow / no right routing space**
   - The `任務分類` card bottom exceeded Layer 1 by 10px.
   - Its outgoing connector routed to `x=2065`, beyond the main layer right edge `x=2030`.
   - Visual symptom: the card group appeared to break the right/bottom layer boundary even if the card body mostly fit.

3. **Reference panel too close to Layer 3**
   - The REF panel and `refgov` card overlapped or visually pressed into the Layer 3 zone.
   - The `refcli` card had only ~10px right margin, making it look clipped.

4. **QA script was necessary but not sufficient**
   - `svg_geometry_qa.py` caught node overlap, text overflow, node crossings, and title-band crossings.
   - It did not enforce semantic anchor centering, container ownership, connector point containment, or right-side egress gutters.

## Reusable Fix Pattern

- For gate branches, define explicit semantic anchors:
  - Diamond right/left/top/bottom points.
  - Card side midpoint or deliberate offset anchor.
  - Horizontal branch endpoints must share the intended `y`; vertical endpoints must share intended `x`.
- Move the target card if needed so the branch line hits a midpoint instead of connecting to an arbitrary edge point.
- Treat a node plus its labels and outgoing connector path as one visual group when checking containment.
- Reserve right-side egress space. A card near a container's right edge is not acceptable if its outgoing line has to detour outside the frame.
- Reference panels need their own bottom and right safety margins. Do not let them touch the next layer, even when the formal bounding boxes barely avoid overlap.
- For cross-layer bypass connectors, an outer gutter can be valid if it avoids title bands. Keep it deliberate and consistent (e.g. `x=55` instead of ad hoc `x=35`), and do not route through left-aligned title text.

## Extra QA Assertions Used in v4.3

Add these as deterministic assertions or manual checks for future manually positioned SVGs:

- **Anchor centering:** critical connectors must equal expected anchors, e.g. `redgate.midY == stop.midY == conn3.y == 275`.
- **Layer containment:** every card/gate belongs fully to exactly one intended zone unless explicitly designed as a bridge.
- **Connector point bounds:** every connector waypoint must be within the intended canvas/layer/outer-gutter range; no accidental `x > layer.right` or `y > layer.bottom` detours.
- **Right egress margin:** cards with outgoing routes should leave at least ~50px inside their container; reference cards should leave at least ~30px to their panel edge.
- **Reference separation:** right-side reference panels must end above the next main layer with visible air, not merely non-overlap.
- **Vision focus prompt:** after deterministic QA, ask vision specifically about the exact defects Scott/consultants found (e.g. HIT alignment, task-classification overflow, REF/Layer 3 collision), not just a generic screenshot review.

## v4.3 Outcome

- `hit` connector changed to the gate/STOP centerline.
- `任務分類` card moved fully inside Layer 1 and its outgoing connector rerouted through an internal gutter.
- REF zone shortened; ref cards moved/inset; no Layer 3 collision.
- Original geometry QA passed with 0 failures / 0 warnings.
- Extra consultant-rule QA passed for 22 nodes and 28 paths.
- Browser/vision QA passed with focused checks.

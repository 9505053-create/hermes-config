# 3AI Command Flowchart v4.1 Finish Pass — 2026-05-17

## Context

Scott and the 3AI consultant panel reviewed the v4 Hermes / 3AI CLI / subagent command SOP flowchart. v4 had the right topology but still failed several visual engineering checks:

- A bypass connector crossed the `LAYER 3` title text.
- Several cards had text baseline or right-edge overflow.
- Reference panel text and command pills were vertically crowded.
- `Scott 決策點` and `SUM` were too close to or crossing layer boundaries.
- The verification fail loop was larger than necessary and visually competed with the pass/delivery path.

## v4.1 Corrective Pattern

Keep the v4 topology; do not add new workflow content. Apply a layout finish pass:

1. **Layer title band is an obstacle**
   - Reserve the top 55–65px of each layer as a no-go title band.
   - No card, connector label, or arrow segment may pass through this band.
   - First content row should start clearly below the title band.

2. **Bypass lanes use outer gutters**
   - If a route such as `A Hermes direct` must bypass the Contract Bus, send it through an outer gutter (`x<60` or far-right margin) and re-enter below the next layer title band.
   - Do not route a vertical connector through left-aligned layer title text.

3. **Decision nodes belong to one zone**
   - `Scott 決策點` and `SUM` must be fully inside Layer 3, or moved to an explicit `Decision Bridge` lane.
   - Avoid half-in/half-out nodes at layer boundaries.

4. **Fail loop is a repair loop, not a perimeter feature**
   - Preferred shape: `Hermes 驗證 fail → 修正/重派 → Execution Contract`.
   - Keep it short when possible.
   - Never wrap it around `OUT`, archive, delivery, or success nodes.

5. **Reference cards need full layout checks**
   - Reference content is not exempt from collision rules.
   - Body text, pills, and governance rows must each have their own vertical band.
   - If text and pills are crowded, increase card height or delete duplicate copy rather than shrinking text until unreadable.

6. **Text bounds are hard gates**
   - Last text baseline should be at least 14–18px above the card bottom.
   - Text/chips should stay at least 16–20px inside the right edge.
   - Estimate widths before drawing; for CJK use about 1.0× font size per character, and for half-width Latin about 0.56× font size.

7. **Deterministic geometry QA before visual QA**
   - Do not rely on visual inspection or vision review as the first gate.
   - Every generated `.card` / `.gate` should carry `data-x`, `data-y`, `data-w`, `data-h`.
   - Run the bundled QA script before claiming the diagram is passable:

```bash
python ~/.hermes/skills/creative/diagram-visual-design/scripts/svg_geometry_qa.py <diagram.svg>
```

   - A FAIL means the SVG is not deliverable, even if a screenshot looks acceptable.
   - Required checks: box collision, tight gaps, text overflow right/bottom, connector crossing nodes, connector crossing title bands.
   - After QA passes, do one focused visual check for QA blind spots: connector labels sitting on title bands, standalone command pills not grouped inside cards, and labels that are technically outside a path but visually overlap headers.

8. **Prefer computed layout over pixel nudging**
   - Define grid columns/rows and gutters as variables.
   - Calculate card width from the longest line plus padding.
   - Calculate card height from title/body row count and line height.
   - If QA fails, repair the grid/autosizing logic rather than manually pushing one node and creating another collision.

## Verification Used

- Open the HTML/SVG in browser.
- If an HTML wrapper screenshot appears blank in accessibility snapshot, inspect `document.querySelector('svg')` and open the raw SVG directly.
- Run a focused vision pass asking about: text overflow, tofu glyphs, layer-title crossings, reference overlap, decision node zone membership, and fail-loop shape.
- Copy the final PNG preview beside the source SVG under Scott's Windows workspace.

## Final v4.1 Artifact Pattern

A passing v4.1 artifact should include:

- SVG source.
- HTML preview wrapper.
- PNG screenshot/preview.
- Optional Mermaid text fallback.

Example Windows output folder used in the passing implementation:

```text
C:\Users\chien\_3AI_WorkSpace\temp_for-Scott\hermes_3ai_subagent_command_guide\
```

## Pitfall

Do not claim "avoid text/arrow overlap" in a footer unless it was actually verified. Prefer a neutral footer like `v4.1：只修排版，不新增流程內容`.

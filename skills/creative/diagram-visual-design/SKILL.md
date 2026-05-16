---
name: diagram-visual-design
description: "Create polished flowcharts, mind maps, architecture diagrams, and agent-generated visual explanations with UI/UX aesthetic gates, layout patterns, and verification. Use with Mermaid, SVG/HTML, Excalidraw, Markmap, D2, or screenshots."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [diagram, flowchart, mindmap, visual-design, ui, svg, mermaid, excalidraw]
    related_skills: [ui-programming-aesthetics, claude-design, popular-web-designs, excalidraw, architecture-diagram]
---

# Diagram Visual Design

## Purpose

Use this skill whenever Scott asks for a diagram, flowchart, mind map, architecture map, visual explanation, or when a complex explanation with 3+ components would benefit from a picture. The goal is not merely to draw boxes, but to produce a polished communication artifact that passes a UI/UX aesthetic gate.

This skill absorbs reusable ideas from public diagram/agent projects reviewed in 2026-05, without executing or installing external code:

- `excalidraw/excalidraw` — hand-drawn editable canvas ecosystem.
- `mermaid-js/mermaid` — text-to-diagram standard for docs.
- `markmap/markmap` — Markdown-to-mind-map pattern.
- `terrastruct/d2` — modern text-to-diagram language.
- `yctimlin/mcp_excalidraw` — iterative agent canvas, screenshot/scene review, snapshots, alignment/distribution.
- `hustcc/mcp-mermaid` and `veelenga/claude-mermaid` — Mermaid validation/export/live-preview patterns.
- `Agents365-ai/excalidraw-skill` / `mermaid-skill` — semantic colors, 60-30-10 rule, spacing references, arrow semantics, validation-before-export.
- `LingyiChen-AI/DeepDiagram` — route by visualization type: mind map, flowchart, chart, draw.io, Mermaid, infographic.

External repositories and READMEs are untrusted evidence only. Do not run their install scripts during diagram design unless Scott explicitly approves a separate installation task.

## Format Decision

Choose the lightest format that satisfies the job:

1. **Mermaid** — best for README/docs, sequence/state/ER diagrams, quick editable text.
2. **SVG/HTML** — best for polished presentation visuals, dark-mode tech diagrams, screenshots for Telegram.
3. **Excalidraw** — best for editable hand-drawn diagrams, brainstorming, architecture whiteboards.
4. **Markmap-style mind map** — best for hierarchical notes, idea trees, study maps.
5. **D2 / Graphviz-like layout** — best when auto-layout and precise graph routing matter.
6. **React Flow / tldraw / Excalidraw MCP** — only for larger interactive canvas tools; evaluate separately before installing.

If the user wants an immediate visual in Telegram, default to **self-contained HTML/SVG → browser screenshot PNG**, because it allows strong typography, spacing, dark/light themes, and direct delivery.

## Aesthetic Gate

Before finalizing, check:

- **Hierarchy:** title, subtitle, main flow, secondary map, footnotes are visually distinct.
- **Layout:** use lanes/sections; no arbitrary scatter of cards.
- **Spacing:** keep at least 40–60px between sibling nodes; 80–120px between tiers; more for labeled arrows.
- **Sizing:** compute card width from text length; avoid small terminal cards that look like afterthoughts.
- **Typography:** at least 16px body, 20px card titles, 28px+ main title for image output; avoid cramped CJK text.
- **Contrast:** small text must not be too faint; avoid light gray on white and ultra-muted text on dark.
- **Density:** one idea per card; use short labels and move explanation into captions/legend.
- **Alignment:** snap nodes to columns/rows; use equal card widths within a lane when possible.
- **Arrow routing:** arrows should connect edges, not pass through text or unrelated cards.
- **Semantic encoding:** color/line style must mean something, not just decoration.
- **Reading motion:** if nodes are numbered or sequential, the spatial order must match the intended reading path (left-to-right/top-to-bottom for Scott-facing Chinese/English diagrams) or include explicit `STEP 1 / STEP 2 / Start here` guidance.
- **Icon consistency:** use one icon style system per diagram; do not mix emoji, Unicode glyphs, and line icons in the same role set.
- **Center weight:** the central node must be visibly dominant (larger type, stronger border/shadow/contrast); as a rule of thumb, central visual weight should feel at least 1.3× any child card.
- **Export target:** declare desktop, mobile, or dual-output before rendering. For Telegram-first deliverables, consider a mobile/vertical version in addition to a 1600×900 overview.
- **Export framing:** leave safe margins for Telegram/mobile preview; avoid content near edges.

## Visual Patterns

Reference case studies:

- `references/mind-map-governance-redesign-20260516.md` — Token Governance mind-map redesign critique synthesis and v2 pattern.
- `references/mind-map-v3-critique-synthesis-20260516.md` — follow-up 3AI critique: spatial logic, schema honesty, mobile output, icon consistency, code-pill scope.
- `references/token-governance-mindmap-v3-implementation-20260516.md` — concrete v3 implementation pattern that passed vision review, including final copy, layout, pitfalls, and verification prompt.

### Main workflow

- Use left-to-right for delivery pipelines.
- Use top-to-bottom for decision-heavy workflows.
- Use a lane label such as `MAIN FLOW`, `REVIEW`, `OUTPUT` when multiple layers exist.
- Keep main nodes visually dominant; feedback loops should be thinner/dashed.
- Do not squeeze the terminal/output node under the previous step just because the row is full; either rebalance all node widths into one baseline row, or create a clearly separated output lane with at least 80–120px of vertical air.
- Avoid U-turn arrows into a small output card near a feedback loop; this creates a crowded knot. Prefer a simple horizontal 4→5 arrow and route feedback below the entire row.

### Mind map

Use these rules when turning notes, meeting conclusions, debate outputs, or governance rules into a mind map. The goal is not to paste all content into branches; it is to make the reader know what to do at a glance.

#### Content Architecture First

- Decide whether the material is a **process**, **taxonomy**, or **governance rule** before drawing.
  - If it is a process, order branches by the operating flow, e.g. `task enters → classify → route → tool/filter → compress → externalize memory → gate cost/safety`.
  - If it is a taxonomy, group branches into 2–3 second-level categories before placing leaves.
  - If it is governance, phrase nodes as rules or decision criteria, not meeting-summary prose.
- Put the central topic in a larger node and use a memorable two-line core sentence. Do not break CJK text on empty function words or single-character particles such as `的`, `是`, `了`, `之`, `把`, `被`, `對`, `在`, `向`, `用`, `給`, `與`, `和`, `及`.
- Keep the central subtitle as the system invariant: who decides, who executes, what tools handle, and what context is retained.
- Make any TL;DR or executive summary **orthogonal** to the center: one should state the principle, the other should state the action trigger. Do not paraphrase the same sentence twice.
- For sequential/governance diagrams, align physical layout with logic. If the concept says `first A, then B`, put A before B in the reader's natural scan path, or add an obvious step cue.
- For guardrail nodes that apply to multiple domains, either make them a cross-cutting bottom/top gate or name the containing zone broadly enough (e.g. `Context & Control`) so the placement is semantically honest.
- For 5+ branches, create second-level group logic or visible lane logic; avoid six unrelated rainbow cards.
- Use either clockwise numbering that matches eye flow, or remove numbering and rely on categories/colors. Do not let visual order fight numeric order.
- Each branch should answer one operator question such as: `who controls?`, `who does it?`, `what should not enter context?`, `when compress?`, `how avoid rework?`, `how prevent runaway cost?`.

#### Branch Card Structure

- Use 4–6 primary branches; avoid more than 8.
- Make branch cards consistent: same width/height family, same internal structure, and preferably exactly 3 bullets.
- Be honest about the card schema. Do not claim every card uses identical labels unless it actually does. Prefer **standardized rows with semantic labels**: each card has the same number of rows, but labels may vary if they still follow an implicit `condition → action → boundary/result` logic.
- Choose a schema family per card type:
  - **Action-control chain:** trigger / action / keep-or-forbid.
  - **Routing or resource ladder:** simple / standard / high-risk, or primary / fallback / stop.
  - **Memory externalization:** skill / memory / handoff, or durable / temporary / next-session.
- Use a three-line pattern when possible: **trigger / action / keep-or-forbid**.
  - Example: `Trigger: 40 turns / 70% context`; `Action: compact / summary`; `Keep: anchors, decisions, TODOs`.
  - Example: `Run first: files / scripts / API`; `Extract: errors, paths, counts`; `Forbid: full cat, full paste, unbounded scan`.
- Keep each bullet short: ideally <= 16–20 CJK characters, or split long technical terms into small inline tags.
- Ensure directive rows are unambiguous. Prefer `禁止：Hermes 跳過路由直接執行` over vague wording such as `不當預設執行者`.
- Define any shorthand symbol in the same image or avoid it. Examples: `~~` must appear as `~~ 換窗摘要` or be replaced by `handoff` / `換窗交接`.
- Render true technical terms like commands, APIs, file names, parameters, and system methods (`compact`, `session_search`, `hard stop`, `OpenRouter`, `cat`, `~~`) as small monospace pills/tags in HTML/SVG outputs.
- Do not put ordinary business labels, internal nicknames, or product names in code pills unless they are being used as a literal command/API/token. Use bold text or normal text instead.
- Consider two pill weights: light/outline pills for neutral technical terms, and dark/red pills only for dangerous, prohibited, or stop-condition terms.
- Add semantic icons when they improve scanning, but keep the icon set consistent. Use all SVG/line icons, all simple glyphs, or all emoji — do not mix emoji with monochrome glyphs for peer branch cards.

#### Layout and Visual System

- Arrange branches symmetrically; never let child nodes overlap the central node.
- For operational/governance maps, prefer **two-sided grouped layouts** over pure radial scatter when the content has two domains, e.g. execution governance on one side and context governance on the other.
- In two-sided layouts, align lanes to the reader's natural order. For Scott-facing Chinese/English diagrams, put `STEP 1 / ①–③` on the left or top unless there is a strong reason not to; if not, add explicit start/step arrows.
- Lane/zone labels should be self-explanatory in the main language first; optional English labels can be secondary. Example: `任務執行治理 / Execution Governance · ①–③`.
- Use visible container layers when grouping matters: zone borders/backgrounds must be strong enough to survive screenshot compression and phone viewing, not decorative hairlines.
- For product/SaaS style, align cards to a precise grid within each lane unless intentional organic mind-map movement is part of the style.
- Floating TL;DR or “core judgment” cards must either become a top executive-summary ribbon or be integrated into the central node. Do not let them appear as an unintended seventh branch.
- Use lines, not arrows, unless direction matters. Lines should be thinner/lighter than cards, often 60–75% opacity.
- Connect lines to semantic anchors (number badge, icon, or side midpoint), not arbitrary card edges. Avoid lines that merely “float near” cards.
- Use fixed clock-face anchors for radial maps (around 1/3/5/7/9/11 o'clock) or clear edge-midpoint anchors for column layouts.
- Color by meaning, not decoration. A good mind-map palette:
  - Purple: Hermes / commander / central principle / strategy.
  - Orange: 3AI routing / agent delegation.
  - Blue: tools / APIs / logs / tests.
  - Green/teal: context, compression, memory, persistence.
  - Red/rose: cost, security, hard stop, rollback, risk gate.
- If multiple branches share one domain, use color families rather than six unrelated colors. Example: strategy = purple/blue, context = green/teal, guardrails = orange/red.
- Bottom slogans should be light pills or thin rule bars unless they are the main conclusion. Avoid heavy dark banners that steal focus from the map.

### Architecture diagram

- Use zones/boundaries for layers or trust domains.
- Draw arrows behind cards or route them around zones.
- Put zone labels in corners, not centered behind other text.
- Use semantic colors: frontend/cyan, backend/green, data/violet/teal, external/amber, security/rose.

### Swimlane / responsibility map

- Use when multiple actors participate.
- Keep each actor in one lane.
- Crossing arrows should be minimized and labeled sparingly.

## Semantic Colors and Lines

Use a small palette. A reliable default:

- Input/user-facing: cyan or light blue.
- Orchestration/process: violet.
- External/agent/tool: amber/orange.
- Review/success/output: green.
- Risk/security/rollback: rose/red.
- Storage/data: teal/violet.
- Neutral notes: gray.

Line semantics:

- Solid: primary flow.
- Dashed: feedback, async, response, or optional path.
- Dotted: weak reference or non-critical relation.
- Avoid arrow labels on dense diagrams; if needed, keep labels <= 12 characters.

## Quality Anti-Patterns

Avoid:

- Text clipped by cards.
- Lines crossing through labels.
- Child nodes touching or overlapping the center node.
- Oversized filled triangle arrowheads; in SVG, avoid `markerUnits="strokeWidth"` for normal UI diagrams because it can scale arrowheads into chunky, crude triangles.
- Directional arrowheads on mind-map spokes; mind maps should usually use undirected soft connector lines unless direction is semantically important.
- Feedback arrows that terminate in empty space; either connect to a clear anchor point or use a subtle dashed loop with a small dot/chevron.
- Too many colors with no meaning, especially six-color “rainbow” maps where every node looks like a different topic.
- Mixed icon systems, e.g. emoji shield beside monochrome glyph stars/arrows/gears.
- Every element as same-size rounded rectangle with no hierarchy.
- Floating summary/core-judgment cards that look like accidental extra branches.
- Numbering order that fights natural eye flow; either make numbering clockwise/linear, move the first sequence to the left/top, or add step guidance.
- CJK line breaks that isolate function words or single-character particles such as `的`, `是`, `了`, `之`, `把`, `被`, `對`, `在`, `向`, `用`, `給`, `與`, `和`, `及`.
- TL;DR text that merely paraphrases the central subtitle instead of adding a distinct action instruction.
- Claims of “three-part cards” when the actual labels do not follow the promised schema.
- Unexplained shorthand symbols such as `~~` or internal triggers without legend text.
- Code pills applied to ordinary internal names or product labels when they are not commands/API terms.
- Dense branch text that feels like pasted meeting notes instead of operating rules.
- Heavy footer banners that overpower the central idea or collide with lower cards.
- Developer-only legends in final images such as `semantic colors` or `code pills` unless the audience is explicitly reviewing the design system.
- Tiny footer/caption text that becomes unreadable in Telegram.
- Giant blank margins above/below because the screenshot aspect ratio was not planned.
- Under-height cards that clip the last row after adding badges, labels, pills, or CJK text; always inspect the bottom row in the final screenshot.
- Mermaid diagrams exported without syntax validation.
- Excalidraw shapes using invalid `label` properties instead of proper bound text.

## Workflow

1. **Classify the diagram:** flowchart, mind map, sequence, architecture, chart, infographic, swimlane, or hybrid.
2. **Declare the output target:** desktop, mobile, or dual-output. If Telegram/mobile reading is primary, plan a vertical/mobile version or split detail cards before rendering.
3. **Classify the content logic:** process, taxonomy, governance rules, comparison, or explanation. Do this before layout.
4. **Distill before drawing:** convert raw notes into operator questions, triggers/actions/guardrails, and short labels. Remove meeting-summary prose.
5. **Choose and state the schema honestly:** uniform labels only if every card uses them; otherwise use standardized rows with semantic labels and document the schema family.
6. **Pick output:** Mermaid, SVG/HTML screenshot, Excalidraw, or another format.
7. **Sketch structure first:** nodes, lanes, relationships, hierarchy, numbering order, category groups, reading direction, and where any TL;DR ribbon belongs.
8. **Apply design system:** choose theme, typography, semantic colors, spacing, consistent icons, code-tag treatment, zone strength, and line semantics.
9. **Generate artifact:** write HTML/SVG, Mermaid, or `.excalidraw` file.
10. **Verify visually:** open in browser or inspect with vision. Check clipping, overlap, arrow routing, contrast, edge margins, mobile/Telegram readability, CJK line breaks, icon consistency, code-pill scope, reading order, TL;DR/center orthogonality, and whether any floating element looks like an unintended node.
11. **Iterate once if needed:** fix concrete visual issues before final delivery.
   - If Scott marks a red box/circle, treat it as a design review, not a vague complaint.
   - Diagnose whether the issue is content architecture, structural layout, connector routing, density, typography, or style mismatch.
   - Prefer structural fixes over pixel nudges when multiple elements crowd one area.
   - After fixing, run a screenshot/vision pass focused specifically on the marked region.
12. **Report format and path:** include screenshot/media path and source file path when useful. For Scott, always report Windows paths first. If outputs were created under WSL-only locations such as `/tmp` or `/home/chien`, copy durable deliverables to `C:\Users\chien\_3AI_WorkSpace\artifacts\...` or `C:\Users\chien\_3AI_WorkSpace\temp_for-Scott\...` before reporting, and use `\\wsl.localhost\Ubuntu\...` only as a fallback.

## Mermaid-Specific Rules

- Validate before exporting when possible.
- Use `flowchart LR` for simple pipelines; `flowchart TB` for decision trees.
- Quote labels containing punctuation or CJK special characters if syntax errors appear.
- Prefer short node IDs and readable labels.
- For mind maps, use Mermaid `mindmap` only when the target renderer supports it; otherwise use Markmap-style HTML/SVG.

## HTML/SVG Screenshot Rules

- Default desktop canvas: 1600×1000 or 1600×900 for widescreen overview.
- For Telegram/mobile-first reading, also produce a mobile canvas such as 1080×1350, 720×1280, or split into overview + detail cards. A 1600×900 image compressed to phone-chat width is not sufficient for reading 12–16px card text.
- For dense 3-row governance cards on a 1600×900 desktop canvas, do not assume 138px card height is enough; verify bottom rows. In the Token Governance v3 case, about 156px was needed for 3 rows plus header.
- Keep all important content inside the central 90% safe area.
- Use CSS variables for colors and typography; if using a light theme, consider whether Scott would benefit from an alternate Catppuccin/dark theme for engineering review.
- Use zone borders/backgrounds with enough contrast to survive screenshot compression; grouping containers should be perceivable, not merely decorative.
- Use CSS variables for pill tiers: neutral technical pills should not overpower the verbs; dangerous/prohibited terms may use stronger dark/red styling.
- Draw connector paths behind cards when possible, and connect them to semantic anchors.
- Use browser screenshot verification before final.
- For self-contained HTML/SVG diagrams, run a DOM bounding-box gate before delivery: every important `.card`/node must stay inside the canvas safe area; grouped cards must stay inside their zone/container; footers/captions/notes must not intersect any card/node; any `bottom > canvas.bottom`, `right > canvas.right`, or footer-card overlap is a FAIL, not a style nit.
- If the user critiques the visual, inspect their marked-up screenshot and patch the artifact rather than starting over blindly.

## Excalidraw Rules

- Use proper text binding; do not use unsupported `label` properties.
- For labeled shapes, minimum 120×60; for CJK labels prefer 160×70 or larger.
- Plan coordinates before writing JSON.
- Use snapshots/backups if working with live canvas tools.
- For complex diagrams, route arrows around zones; avoid cross-zone spaghetti.

## Install / Adapt Decision

Do **not** install new diagram MCP servers or global npm packages during normal drawing tasks. First score them using `external-skill-import`:

- Install only if it fills a real gap, is maintained, low-risk, and needs no core Hermes modification.
- Prefer adapt-only when the repo mainly contributes prompts, layout rules, or design checklists.
- MCP/canvas servers that require persistent background services, browser state, Docker, or config changes should be proposed as a separate install task with rollback steps.

## Verification Checklist

- [ ] Format chosen matches the user goal.
- [ ] Output target declared: desktop, mobile, or dual-output.
- [ ] Diagram has a clear visual hierarchy and the central node is dominant.
- [ ] If numbered/sequential, reading order matches spatial order or has explicit start/step cues.
- [ ] Content schema is honest: uniform labels only when actually uniform; otherwise standardized rows with semantic labels.
- [ ] TL;DR and center text are not redundant; one states principle and one states action/trigger.
- [ ] All directives are unambiguous and action-oriented.
- [ ] No clipped text.
- [ ] No node overlap.
- [ ] No arrows/lines through text or unrelated nodes.
- [ ] Connector anchors attach to meaningful points, not arbitrary floating edges.
- [ ] Colors/line styles have semantic meaning.
- [ ] Icons are stylistically consistent.
- [ ] Technical pills are used only for true commands/APIs/system terms; shorthand symbols are defined.
- [ ] CJK line breaks do not isolate function words/particles.
- [ ] Zone boundaries are visible enough when grouping matters.
- [ ] Final image contains no developer-only design notes unless requested.
- [ ] Mobile/Telegram framing/readability is acceptable; if not, a mobile or split version was produced.
- [ ] Browser/vision check completed for image deliverables.
- [ ] Source file and screenshot path reported as Windows paths for Scott.

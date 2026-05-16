# Mind Map Governance Redesign Case Study — 2026-05-16

## Trigger

Scott asked Hermes to redraw a Token Governance mind map after 3AI consultants (Claude, Gemini, ChatGPT) reviewed the first version. The review focused on content architecture, visual hierarchy, UI aesthetics, and whether the artifact helped readers make decisions.

## Durable Lesson

A good mind map is not a container for all notes. For governance or operational topics, it should become a decision aid: the reader should know what to do next at a glance.

## What Changed from v1 to v2

### Content architecture

- v1 was a radial summary with six parallel branches.
- v2 became a two-domain governance map:
  - Execution Governance: control, routing, tools.
  - Context Governance: compression, memory, gates.
- Central claim was shortened into a strong two-line statement:
  - `Token 不是省出來的`
  - `是設計出來的`
- TL;DR moved to a top ribbon so it did not look like an accidental seventh branch.
- Branches were rewritten as operator questions:
  - Who controls?
  - Who gets the task?
  - What must not enter context?
  - When do we compress?
  - How do we avoid rework?
  - How do we prevent runaway cost?

### Card structure

Each branch card used a repeatable 3-row operator pattern:

- Trigger / condition.
- Action.
- Keep / forbid / gate.

Examples:

- Compression: `40 turns / 70% context` → `compact / summary / ~~` → keep anchors, decisions, TODOs.
- Tools: run files/scripts/API first → extract errors/paths/counts → forbid full `cat` and unbounded scans.

### Visual system

- Color carried meaning instead of decoration:
  - Purple: Hermes / commander / principle.
  - Orange: 3AI routing.
  - Blue: tools / APIs / logs / tests.
  - Green/teal: context, compression, memory.
  - Rose/red: cost, security, hard stop.
- Technical tokens used monospace pills: `compact`, `session_search`, `OpenRouter`, `hard stop`, `cat`, `~~`.
- Connectors were light and secondary, not attention-grabbing.
- Bottom slogan became a light pill rather than a heavy dark banner.
- Group labels included sequence ranges (`①–③`, `④–⑥`) to reduce ambiguity caused by right-side-first numbering.

## Workflow Pattern to Reuse

1. Classify the content logic before drawing: process, taxonomy, governance, comparison, or explanation.
2. If it is governance, turn raw notes into operating questions and rules.
3. Create 2–3 visible domains/lane groups when there are 5+ branches.
4. Use consistent branch cards with 3 rows where possible.
5. Use semantic colors and code pills for technical terms.
6. Generate HTML/SVG and screenshot it for Telegram delivery.
7. Run a vision pass looking for:
   - clipped text,
   - node overlap,
   - connectors through text,
   - TL;DR looking like an extra node,
   - numbering order fighting eye flow,
   - heavy footer stealing focus,
   - mobile/Telegram readability.
8. Patch concrete issues and run a second vision pass before delivery.
9. Report Windows paths first to Scott. If source is in `/tmp`, copy durable files to `C:\Users\chien\_3AI_WorkSpace\artifacts\...` or `C:\Users\chien\_3AI_WorkSpace\temp_for-Scott\...`.

## Pitfalls Observed

- A floating “core judgment” card can be misread as a seventh branch.
- Right-side-first numbering can confuse readers unless group labels or direction cues clarify it.
- Heavy bottom banners overpower the center and lower cards.
- Six unrelated colors make a map look lively but semantically weak.
- CJK line breaks must not isolate function words such as `的`, `是`, `了`, `之`.
- If Scott asks where a file is, a WSL path is not enough; provide a Windows path.

## Review Package Pattern

When Scott wants 3AI review of a diagram process, create a package under:

```text
C:\Users\chien\_3AI_WorkSpace\temp_for-Scott\<topic>
```

Recommended files:

- `00_review_brief_for_3AI.md` — background, goals, design decisions, self-evaluation, review questions, copyable prompt.
- `01_final_mindmap.html` — editable/source artifact.
- `02_final_mindmap.png` — screenshot/preview artifact.

The brief should help an external reviewer understand the task without full chat history.

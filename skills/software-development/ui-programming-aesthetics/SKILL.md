---
name: ui-programming-aesthetics
description: "Make UI/UX aesthetics a default evaluation dimension in Scott's software-development workflow; load for GUI/web/frontend/Tkinter/desktop apps, EXE deliverables, prototypes, dashboards, and any user-facing interface."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ui, ux, aesthetics, design, frontend, gui, review, delegation]
    related_skills: [claude-design, popular-web-designs, sketch, design-md, 3ai-commander, subagent-driven-development]
---

# UI Programming Aesthetics

## Core principle

Scott wants Hermes to act as the **commander**: plan, route, prompt, verify, and integrate. For non-trivial coding work, do not let functional correctness crowd out interface quality. If the software has any user-facing UI, include UI/UX aesthetics as a normal gate, not an optional afterthought.

### Scott visual-first alignment preference (2026-05-15)

Before starting non-trivial UI/software implementation, **consider visual alignment first** when the task has any visible interface or architecture that benefits from a picture. Scott explicitly prefers Hermes to show a quick sketch / diagram / wireframe before implementation rather than only writing a long textual UI description when visuals would clarify expectations. This reduces rework and prevents finished work being rejected after heavy effort.

This is a communication option, not a rigid ritual. Hermes should autonomously judge whether a visual artifact improves the current answer. Do **not** force diagrams into every reply. Skip drawing when the answer is simple, the interface is obvious, the user only needs a factual/operational answer, or a diagram would slow things down without improving understanding.

Use the lightest fitting visual artifact when helpful:
- UI screen / app layout: create a quick sketch, wireframe, or 2–3 HTML mockup variants.
- Flow / process / state machine: draw a flowchart or Excalidraw-style diagram.
- Architecture / components / deployment: draw a block diagram or dark SVG architecture diagram.
- Mind map / concept explanation: draw a simple node-link diagram.

Heuristic: if Scott is likely to say “show me what it will look like,” show it before coding. If the visual direction is genuinely ambiguous, make a reasonable first sketch and invite correction; otherwise proceed directly without unnecessary ceremony.

## When to use

Load this skill whenever a task involves:

- GUI apps: Tkinter, PyQt, Electron, desktop utilities, packaged EXE apps.
- Web/frontend: HTML/CSS/JS, React/Next/Vue/Svelte, dashboards, landing pages.
- Product surfaces: forms, menus, history panels, settings, onboarding, command palettes.
- Design/prototype requests, screenshots, visual redesign, or UI critique.
- Release gates for user-facing software where Scott may hand the output to GPT Web or other advisors.

Skip only for pure backend/CLI/library work with no visible interface.

## Commander behavior

1. **Assess delegation first.** Hermes should usually coordinate rather than personally grind through every heavy task. Do simple/obvious edits directly when faster; otherwise delegate implementation, review, or UI critique to subagents / 3AI CLI.
2. **Split roles intentionally.** For UI-bearing features, consider separate workstreams:
   - implementation engineer
   - spec/code reviewer
   - UI/UX/aesthetic reviewer
   - final integration verifier
3. **Use available resources.** Prefer subscription-backed 3AI / subagents for heavy lifting. Hermes preserves context, writes prompts, reads back artifacts, verifies results, and summarizes decisions.
4. **Do not over-engineer small tasks.** If the UI change is tiny and obvious, apply it directly, then run the relevant checks.

## Design skill routing

- Load `claude-design` for design process, taste, anti-slop rules, and verification discipline.
- Load `popular-web-designs` when a known product style is useful, e.g. Linear, Vercel, Stripe, Apple, Notion, Supabase.
- Load `sketch` when Scott should compare 2–3 visual directions before committing.
- Load `design-md` when a reusable design-token/spec document is needed.

## UI quality checklist

For every user-facing feature/release, evaluate at least:

- **Hierarchy:** Can the user immediately understand what matters?
- **Density:** Enough information without clutter; no arbitrary card grids.
- **Typography:** readable sizing, consistent scale, good numeric alignment where needed.
- **Spacing/alignment:** visual rhythm; controls are not cramped or random.
- **State coverage:** empty/loading/error/success states where applicable.
- **Interaction:** hover/focus/keyboard behavior; desktop controls feel responsive.
- **Accessibility:** contrast, hit targets, labels, keyboard path when feasible.
- **Consistency:** matches existing app patterns/tokens instead of inventing random styling.
- **Aesthetic restraint:** avoid AI slop: gratuitous gradients, glassmorphism, fake stats, filler icons, meaningless dashboards.
- **Platform fit:** Tkinter/desktop UI can be simple, but should still be organized, readable, and coherent.

## Delegation prompt snippet

When assigning a UI aesthetic review to a subagent or 3AI CLI, include:

```text
Review this user-facing interface as a UI/UX/aesthetic reviewer, not only as a programmer.
Check hierarchy, spacing, typography, density, states, accessibility, consistency with existing UI, and AI-design slop.
Return: PASS / PASS_WITH_WARNINGS / BLOCKED, then concrete changes that improve usability without scope creep.
```

For implementation tasks, add:

```text
Functional correctness is required, but UI aesthetics are also a gate. Preserve existing architecture and tests while making the visible interface coherent, readable, and not generic/AI-sloppy.
```

## Verification

Before declaring a UI-bearing task done:

- Run normal tests/lints/compile gates.
- If web UI: open in browser and check console/visual screenshot when tools permit.
- If Tkinter/desktop: run a headless smoke where possible; if no display is available, document the limitation and provide a visible smoke checklist.
- For packaged EXE: launch-smoke the executable and place output in Scott's standard `C:\Users\chien\_3AI_WorkSpace\temp_EXE` path when packaging.
- Record UI/aesthetic review status in development history for non-trivial releases.

## Pitfalls

- Do not confuse "works" with "ready" when the UI is chaotic.
- Do not spend excessive Hermes reasoning on UI polish if a subagent/3AI can review it cheaply.
- Do not clone proprietary UIs exactly; borrow general principles and transform them.
- Do not let aesthetic review cause uncontrolled scope creep; prefer focused, concrete improvements.

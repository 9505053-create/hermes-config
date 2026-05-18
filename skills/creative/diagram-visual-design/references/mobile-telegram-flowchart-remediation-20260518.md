# Mobile / Telegram Flowchart Remediation — 2026-05-18

## Trigger

Scott showed a Telegram screenshot of a 小蝦-generated flowchart and judged it poor. The artifact existed as a `1600x2140` PNG, but in Telegram phone preview most text became unreadable and the flow felt cluttered.

Core lesson: **PNG generated is not a delivery PASS. Scott-readable in the target surface is the PASS.**

## Defects observed

- One dense desktop-style PNG was used as the only Telegram artifact.
- Body/caption text around 14–16px collapses to roughly 4px when a 1600px-wide image is displayed at ~390px chat width.
- Too many layers, legends, footers, command snippets, and route details competed with the main decision path.
- Connector routes crossed long distances and became visually noisy under compression.
- Gate semantics existed but were not readable enough for Scott to follow on mobile.

## Hard rule

When Telegram/mobile is a declared target, choose one before rendering:

1. **Mobile-first single page** — 1080x1350 or 720x1280, 4–6 major nodes, main decision path only.
2. **Overview + detail cards** — one overview plus 2–4 readable lane/gate cards.
3. **Desktop source + mobile export** — full HTML/source for desktop, plus separate phone-readable PNG.

If a diagram has 8+ cards, long Windows paths/CLI flags, reference panels, or footers, do not deliver only one desktop PNG.

## Minimum mobile typography

For 1080px-wide mobile output:

- Title: 44–60px.
- Card title: 30–36px minimum.
- Body: 24–28px minimum.
- Edge label/caption: 22–24px minimum.
- Avoid critical `tiny` text; move details to Markdown/source/appendix.

## QA addition

Before final delivery:

1. Compute or estimate `phone_width / image_width`.
2. Estimate effective text size after Telegram scaling.
3. If critical body text is below ~10–12 visible pixels, FAIL.
4. Run vision/screenshot review with a mobile-readability prompt.
5. Split or regenerate if unreadable.

## Mantra

先決策語義，後畫面；先手機可讀，後桌面細節；PNG 產生不是 PASS，Scott 看得懂才是 PASS。

# Mind Map v3 Critique Synthesis — 2026-05-16

Source: Scott provided Claude, Gemini, and ChatGPT reviews of the Token Governance v2 mind map. This reference preserves the durable lessons; raw reviews are not copied verbatim.

## Consensus Findings

The v2 direction is correct: it improved from a meeting-summary mind map into an operational governance diagram. The next quality bar is SOP-grade consistency: spatial logic, schema honesty, mobile readability, and stronger visual system rules.

## Must-Fix Lessons

1. **Spatial logic must match reading order**
   - If the content says “first task/execution governance, then context governance,” put execution on the left/top and context on the right/bottom for Chinese/English readers.
   - If the layout intentionally violates natural order, add explicit `STEP 1` / `STEP 2` / `Start here` cues.

2. **Do not overpromise a schema**
   - V2 claimed all cards used `trigger/action/keep-or-forbid`, but actual labels varied.
   - Preferred rule: cards may use custom semantic labels if each card still has standardized row count and an implicit `condition → action → boundary/result` logic.

3. **TL;DR and center must be orthogonal**
   - Center should state the principle.
   - TL;DR should state action or decision trigger.
   - Avoid paraphrasing the same idea in both places.

4. **Shorthand symbols must be self-explaining**
   - `~~` alone is unclear and may look like Markdown strikethrough.
   - Use `~~ 換窗摘要`, `handoff`, or a legend.

5. **Icon system must be consistent**
   - Do not mix emoji and monochrome Unicode glyphs in peer branch cards.
   - Prefer one icon family, ideally inline SVG line icons for HTML deliverables.

6. **Telegram/mobile requires its own plan**
   - 1600×900 is good for desktop overview, but phone preview compresses card text too much.
   - For Telegram-first outputs, make a 1080×1350 or 720×1280 vertical version, or split into overview + detail cards.

## Content Improvements for Token Governance Example

Suggested v3 card copy:

1. **控場｜誰總控？**
   - 觸發：多步驟 / 多工具 / 需驗收
   - Hermes：拆任務、派工、收斂
   - 不做：搬資料、全掃描、重實作

2. **路由｜交給誰？**
   - 短答：Hermes 直接處理
   - 標準：單一 3AI，1–2 輪
   - 高風險：三方審核，Hermes 裁決

3. **工具先行｜資料先去哪？**
   - 觸發：多檔 / 長 log / 大資料
   - 工具：腳本、API、搜尋先抽樣
   - 只給：錯誤、路徑、首例、計數

4. **上下文壓縮｜何時壓？**
   - 觸發：40 輪 / 70% context
   - 產出：決策、anchors、待辦
   - 保留：約束、路徑、下一步

5. **記憶外部化｜怎麼不重來？**
   - Skill：可重複方法
   - Memory：偏好 / 長期設定
   - Handoff：本任務狀態

6. **成本 / 安全閘門｜怎麼防失控？**
   - 成本：訂閱優先，OpenRouter 備援
   - 迴圈：派工前先設輪次上限
   - 停止：hard stop，防 wandering

## Visual Upgrade Rules

- Put `Execution ①–③` left and `Context ④–⑥` right when using LTR readers.
- Add Chinese lane titles first, English second.
- Make zone borders/backgrounds visible enough to survive compression.
- Align cards to a precise grid for SaaS/product-spec style.
- Remove developer-only legends such as `semantic colors` from final reader-facing images.
- Use two-tier code pills: neutral outline for normal technical terms; strong/dark/red for prohibited or stop terms.
- Code pills are for commands, APIs, methods, parameters, paths, or literal system tokens — not ordinary internal labels.
- Center node should be visibly dominant; approximate rule: visual weight at least 1.3× a child card.
- Connect lines to meaningful anchors such as number badges, icons, or side midpoints.

## Skill Patch Destinations

These lessons belong primarily in `diagram-visual-design`:

- Aesthetic Gate: reading motion, icon consistency, center weight, output target.
- Mind map rules: spatial-logic mapping, schema honesty, TL;DR orthogonality, shorthand definition, code pill scope.
- Anti-patterns: mixed icons, schema overclaiming, unexplained shorthand, developer-only legends.
- HTML/SVG rules: dual-output mobile/desktop, zone strength, pill tiers.
- Verification checklist: mobile check, schema honesty, reading order, icon consistency, CJK line breaks, semantic anchors.

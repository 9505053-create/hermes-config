# Process Flowchart Experience Lessons — 經驗校訓

Captured: 2026-05-18 from the 2026-05-17 Hermes/3AI Subagent Command Flowchart production and review loop.

## Why This Lesson Exists

The first working diagrams were visually useful but still failed as executable SOPs. Scott and the 3AI reviewers repeatedly caught that a diagram can look polished while still being logically unsafe: red-line checks were drawn as ordinary steps, verification had no fail path, connector anchors were semantically wrong, and reference panels/labels created hidden layout failures.

## 經驗校訓

1. **流程圖不是美工，是可執行的決策機器。**
   - Every mandatory check must become a gate with clear branches.
   - If a user could ask “what happens when this fails?” and the image cannot answer, the flowchart is incomplete.

2. **先定語義，再畫幾何。**
   - Identify actors, gates, routes, merge points, fail loops, and stop conditions before drawing boxes.
   - Do not start by arranging pretty cards; that creates summary posters, not SOP flowcharts.

3. **紅線、安全、驗證不能被畫成普通卡片。**
   - Red-line hit → stop/ask/mask/forbid.
   - Red-line clear → classify/continue.
   - Verification pass → deliver/archive.
   - Verification fail → repair/redelegate/report limitation.

4. **多路徑匯流要用 bus / swimlane / merge lane，不要五條斜線硬接一張卡。**
   - Independent diagonal connectors create spaghetti.
   - For command/SOP diagrams, prefer orthogonal routing and a Contract Bus.

5. **幾何 QA 必須機械化，視覺 QA 必須聚焦化。**
   - Run deterministic geometry checks for overlap, clipping, node crossing, and title-band crossing.
   - Then use browser/vision review focused on known weak areas, not only a generic “looks good?” prompt.

6. **QA script 只是一層，不是免死金牌。**
   - It may miss semantic-anchor errors, connector labels on title bands, container ownership, or insufficient egress gutters.
   - Add task-specific assertions for the exact gates/routes/layers that matter.

7. **CJK/SVG 不能靠運氣。**
   - Use robust CJK font fallback stacks.
   - Check text bottom padding and line breaks after render, not only after generating SVG text.
   - Deliver PNG/HTML/SVG source paths when font portability matters.

8. **顧問團回饋要轉成行動項，不要整段塞回上下文。**
   - Extract defects, required rule changes, verification checklist, and final acceptance criteria.
   - Archive raw review separately.

9. **小馬與小蝦分工要誠實標示。**
   - Do not blur Hermes direct, delegate_task, 3AI CLI, independent agent, and OpenClaw/小蝦.
   - If a route depends on Windows/OpenClaw behavior, label it explicitly.

10. **交付前問自己：這張圖能不能讓下一個 agent 少犯錯？**
    - If the answer is no, add gates, loops, role labels, or a reference panel; do not just beautify.

## Repeatable Production Flow

1. **Source distillation** — turn manual/review notes into operator decisions: trigger, actor, action, branch, stop, verification.
2. **Semantic skeleton** — write a textual decision graph before SVG: gates, routes, bus, fail loops, reference details.
3. **Layout architecture** — choose swimlane/grid/bus; reserve title bands, gutters, side reference panel, footer safe area.
4. **Artifact generation** — prefer generated coordinates from constants over hand nudging; include `data-x/y/w/h` on cards/gates for QA.
5. **Deterministic QA** — run geometry/bounds checks; fail on overlap, clipping, connector-through-node, title-band crossing, out-of-container points.
6. **Focused visual QA** — inspect screenshot/browser/vision for the known danger zones and CJK rendering.
7. **3AI/Scott feedback synthesis** — convert comments into concrete deltas and tests.
8. **Finish pass** — patch only the failing semantics/layout, rerun QA, then deliver source + preview + paths.
9. **Skill promotion** — save durable lessons to `diagram-visual-design` and teach 小蝦/OpenClaw when the lesson affects Windows visual artifact production.

## Anti-Error Checklist

- [ ] Red-line gate has hit/clear branches.
- [ ] Verification gate has pass/fail branches.
- [ ] Fail loop returns to repair/redelegate/contract, not to success/output.
- [ ] Debate/review path does not imply execution before Scott decision when approval is required.
- [ ] Distinct execution modes are not collapsed into one generic agent label.
- [ ] Long operational details are in reference panel/appendix, not crammed into main route cards.
- [ ] Orthogonal routing / bus lanes used for SOP diagrams.
- [ ] No connector crosses title bands, text, cards, helper panels, or code pills.
- [ ] Critical connectors attach to semantic anchors, not arbitrary card edges.
- [ ] Every card/gate stays inside its intended layer/panel with egress margin.
- [ ] CJK font fallback and rendered line breaks were checked.
- [ ] Mobile/Telegram readability was considered or a separate mobile output exists.

## Teaching Note for 小蝦

When 小蝦 makes a flowchart, it should treat this as a standing rule: **先做決策語義，再做視覺排版；先過機械 QA，再做美學 QA；最後把失敗路徑畫出來。**

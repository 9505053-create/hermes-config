# MiniCalc PR-03 Planning Review Pattern (2026-05-15)

Use this as a reusable pattern when Scott asks to enter a new PR planning phase before implementation and wants 3AI reviewer approval first.

## Scenario

Scott requested PR-03 planning for MiniCalc with:

- Do **not** merge the previous hardening branch into `main` yet.
- Enter planning stage only.
- Produce three docs before implementation:
  - `PR3_SPEC.md`
  - `IMPLEMENTATION_PLAN.md`
  - `ACCEPTANCE_CRITERIA.md`
- Then submit the planning package to Claude/Codex/Gemini reviewers.

## Durable Workflow

1. **Branch hygiene first**
   - Confirm current repo state.
   - Create a planning branch from the approved prior work branch, not from `main`, if the user wants to avoid merging main yet.
   - Explicitly verify `main`/`origin/main` remain unchanged.

2. **Produce planning docs before code**
   - Place PR docs under `docs/prN/`.
   - Separate concerns:
     - `PRN_SPEC.md`: product scope, behavior, non-goals, file boundaries, open questions.
     - `IMPLEMENTATION_PLAN.md`: TDD phases, exact files, test sketches, verification commands.
     - `ACCEPTANCE_CRITERIA.md`: pass/fail gates, regression gates, manual smoke criteria, 3AI review gates.

3. **Run current tests even for docs-only planning**
   - `python3 -m pytest -q`
   - `git diff --check`
   - This catches accidental whitespace or repo-state problems and confirms planning branch did not break current baseline.

4. **Build a central planning review package**
   - Use `C:\Users\chien\_3AI_WorkSpace\code_reviews\<review_id>`.
   - Include planning docs, relevant README/release notes/architecture docs, and a snapshot of current source/tests.
   - Copy the package into each agent-specific review workspace.

5. **Prompt reviewers by role**
   - Claude: architecture, maintainability, UI/UX, controller boundaries, plan granularity.
   - Codex: implementation correctness, tests, edge cases, circular imports, regression risk.
   - Gemini: product coherence, scope control, roadmap, risk synthesis.

6. **If a reviewer returns BLOCKED, revise and re-review**
   - Do not proceed to implementation on a planning blocker.
   - Patch the planning docs to resolve the blocker.
   - Create a delta re-review package containing:
     - updated docs
     - previous reviews
     - explicit list of changes made in response
   - Ask reviewers whether the blocker/warnings are resolved.

7. **Incorporate small non-blocking re-review warnings immediately**
   - If reviewers identify missing tests or small ambiguity in the plan, patch the docs before finalizing.
   - No need for another full round if the changes are clarifying and non-architectural.

8. **Write final 3AI summary**
   - Central file: `FINAL_3AI_REVIEW_SUMMARY.md`.
   - Include first-pass verdicts, blocker(s), fixes applied, re-review verdicts, final readiness, and implementation order.
   - Copy raw outputs into `agent_outputs/`.

9. **Commit planning docs locally**
   - Commit docs-only planning package on the planning branch.
   - Do not push or merge unless Scott requested it.

## Pitfalls Found

- A planning document can be good at a high level but still blocked by a concrete import boundary. In MiniCalc PR-03, Codex correctly blocked the plan because `source/mode_controllers.py` importing `CalculatorEngine` from root `calculator.py` would likely create a circular import once `CalculatorUI` imports controllers.
- Treat a 3AI `BLOCKED` verdict as a planning gate failure, not a warning. Fix docs and re-review before coding.
- In planning docs, resolve open questions that the implementation plan already answers. Leaving resolved questions in an "Open Questions" section confuses implementers/reviewers.
- When adding a controller layer, specify module boundaries and public APIs before implementation, especially for state-machine actions like Memory Recall.
- For Date Calculator features, tests must cover not only headline examples but also ordering and rollover rules:
  - multi-component duration ordering
  - month rollover beyond 12 months
  - subtract month/year clamp cases
  - invalid duration component parsing

## Example Final Verdict Shape

- First review:
  - Claude: `PASS_WITH_WARNINGS`
  - Codex: `BLOCKED`
  - Gemini: `PASS_WITH_WARNINGS`
- After doc fixes and re-review:
  - Claude: `PASS_WITH_WARNINGS`
  - Codex: `PASS_WITH_WARNINGS`
  - Gemini: `PASS`
- Overall: `PASS_WITH_WARNINGS`, no blocking issue, ready for implementation after Scott approval.

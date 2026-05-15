# MiniCalc PR Hardening + 3AI Review Pattern (2026-05-15)

Use this as a compact pattern for future small PR follow-up hardening work after a 3AI review returns `PASS_WITH_WARNINGS` but no blockers.

## Scenario

- A completed PR/baseline already exists and was reviewed by Claude/Codex/Gemini.
- The review found non-blocking risks: environment hygiene, missing UI coordination tests, edge-case limits, ambiguous UI labels, or future refactor warnings.
- Scott prefers local completion of small hardening before GitHub push, but wants finished PRx results uploaded before moving to the next PR.

## Workflow

1. **Freeze baseline and branch**
   - Identify baseline commit and current PR commit.
   - Create a focused hardening branch such as `pr2.1-local-hardening` from the accepted commit.
   - Do not expand into next-PR features.

2. **Turn warnings into tests first**
   - Add targeted failing tests for each concrete risk.
   - For GUI code, prefer headless fake widgets / simple namespaces when possible to avoid desktop dependencies.
   - For environment/discovery risks, add project config (e.g. `pytest.ini`) and `.gitignore` hygiene instead of relying on ad hoc commands.

3. **Implement the smallest hardening changes**
   - Fix only the concrete PRx warning.
   - Defer architecture refactors unless the warning is blocking.
   - Document any intentional deferrals in release notes/development history.

4. **Verify locally**
   - Required gate used in MiniCalc PR2.1:
     ```bash
     python3 -m pytest -q
     python3 -m py_compile calculator.py source/base_converter.py tests/conftest.py tests/test_base_converter.py tests/test_calculator.py tests/test_programmer_ui.py
     git diff --check
     ```
   - Add or adjust file list per project.

5. **Create a 3AI review package**
   - Central package under `C:\Users\chien\_3AI_WorkSpace\code_reviews\<review_id>`.
   - Agent packages under:
     - `...\_agent\Claude Codex\reviews\<review_id>`
     - `...\_agent\Codex\reviews\<review_id>`
     - `...\_agent\Gemini Workspace\reviews\<review_id>`
   - Include: git status, diff stat, full patch, test logs, compile/diff-check logs, current files, and explicit review questions.

6. **Delegate and read back**
   - Claude: architecture / UX / maintainability / next-PR readiness.
   - Codex: implementation correctness / tests / edge cases.
   - Gemini: risk synthesis / roadmap / overall verdict.
   - Use Windows-mode flags and 8.3 short names if path quoting fails.
   - Hermes must read back all output files and copy them into the central package.

7. **Summarize and close**
   - Write `FINAL_3AI_REVIEW_SUMMARY.md` with per-agent verdicts, blocking issues, non-blocking warnings, and decision.
   - If no blockers, update development history, run verification again, commit all tracked and new files.
   - Push GitHub branch for version control only after the hardening is complete and reviewed.
   - Do not create/merge PR or start the next PR unless Scott decides.

## MiniCalc PR2.1 Example Outcomes

- Targeted RED tests initially failed for 64-bit overflow, clear key ambiguity, and programmer UI coordination.
- Implemented unsigned 64-bit cap and changed visible clear key from `C` to `AC`.
- Added `pytest.ini`, centralized `tests/conftest.py`, and headless programmer UI tests.
- Final local gate: `46 passed`, `py_compile` clean, `git diff --check` clean.
- 3AI verdict: Claude `PASS_WITH_WARNINGS`, Codex `PASS_WITH_WARNINGS`, Gemini `PASS`, no blockers.
- Branch pushed for version control; `main` intentionally left unchanged pending Scott decision.

## Pitfalls

- Do not treat non-blocking warnings as permission to start the next PR. Close the hardening loop first.
- Do not forget untracked docs/tests/config files before commit; Codex specifically flagged this as release completeness risk.
- If a post-push documentation correction is needed on a just-created branch, re-run the verification gate before amending/pushing; prefer `--force-with-lease` only when no collaborator could be affected, otherwise make a follow-up commit.

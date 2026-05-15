---
name: minicalc-pr-release-flow
description: "PR-by-PR MiniCalc release workflow: TDD implementation, GitHub backup, review packages, 3AI reviews, Xvfb Tkinter smoke, final gates, and no-main-merge without Scott approval."
---

# MiniCalc PR Release Flow

Use when Scott asks to advance MiniCalc to the next PR/final phase.

## Rules

- Do **not** merge to `main` without explicit Scott approval.
- Use PR-by-PR branch flow and push every stable milestone to GitHub.
- Use TDD for production behavior changes: add RED tests, verify failure, implement, verify GREEN.
- Keep development history in `docs/prN/PRN_DEVELOPMENT_HISTORY.md`.
- Run release gates before final reporting:
  - `python3 -m pytest -q`
  - `python3 -m py_compile calculator.py source/*.py tests/*.py scripts/*.py` when scripts exist
  - `git diff --check`
- For Tkinter GUI smoke in WSL without a display, use Xvfb and document that it is executable headless GUI smoke, not human-visible Windows desktop smoke.

## Steps

1. Confirm repo and branch state:
   ```bash
   git status --short --branch
   git log --oneline --max-count=8
   git remote -v
   ```
2. Create/push next branch from current PR tip:
   ```bash
   git checkout -b prN-...
   git push -u origin prN-...
   ```
3. Add planning docs under `docs/prN/`:
   - `PRN_SPEC.md`
   - `IMPLEMENTATION_PLAN.md`
   - `ACCEPTANCE_CRITERIA.md`
   - `PRN_DEVELOPMENT_HISTORY.md`
   - `PRN_SMOKE_CHECKLIST.md`
4. Baseline gate and planning commit/push.
5. Implement each phase with TDD:
   - Patch tests first.
   - Run targeted pytest and record RED.
   - Patch production code.
   - Run targeted pytest and full pytest.
   - Update history docs.
6. For Tkinter smoke:
   - Track an executable smoke script, e.g. `scripts/minicalc_prN_tk_smoke.py`.
   - Run:
     ```bash
     PYTHONPATH=. xvfb-run -a python3 scripts/minicalc_prN_tk_smoke.py
     ```
   - Record evidence under `docs/prN/TKINTER_SMOKE_EVIDENCE.md`.
7. Build a review package using tracked files only:
   - Copy `git ls-files` into `package/files/`.
   - Include `PACKAGE_MANIFEST.md` and `VERIFICATION_FINAL.txt`.
   - Avoid copying pytest cache or untracked artifacts.
8. Run 3AI review prompts from Windows workspace paths:
   - Gemini: `gemini.cmd --skip-trust --approval-mode yolo`
   - Codex: `codex.cmd exec --skip-git-repo-check --sandbox workspace-write`
   - Claude: `claude.cmd --print --allowedTools Bash Write Edit`
9. If reviews produce warnings, fix actionable items, rerun gates, commit/push, and optionally create a re-review package.
10. Final report must include:
    - branch and latest commit
    - gate results
    - review verdicts
    - smoke evidence path
    - explicit statement: `main` not merged unless Scott approved
11. If Scott explicitly approves the final merge, re-run gates immediately before merge, fast-forward merge to `main`, push `origin/main`, then re-run gates on `main` and verify local/remote HEADs match.
12. If Scott asks for a trial executable after merge/release, follow `references/windows-pyinstaller-exe.md` for the Windows PyInstaller packaging and smoke-verification workflow.

## Pitfalls

- Be explicit about state labels: `planning complete`, `implementation complete`, `review complete`, `merged to main`, and `packaged as exe` are different milestones. Scott challenged this wording in-session, so do not compress them into ambiguous phrases like "PR complete" until all requested gates for that milestone are actually done.
- Windows PowerShell does not expand `source/*.py` for `py_compile`; use `compileall` or explicit file expansion for Windows reviewer checks.
- Xvfb smoke is not human-visible; say this clearly.
- Keep smoke scripts tracked so reviewers can audit/re-run them.
- Do not claim PR is complete when only planning is complete.
- PyInstaller creates build artifacts (`build/`, `dist/`, `.spec`). Keep the final `.exe` for delivery, but remove or intentionally commit the `.spec`; do not leave accidental untracked release artifacts in the repo.

## PR2→PR5 Lessons Learned

- Use milestone names precisely. `Planning complete`, `implementation complete`, `review complete`, `merged to main`, and `packaged as exe` are separate states.
- A planning review can proceed with Codex + Gemini if Claude is unavailable and no blockers remain; document Claude as skipped/deferred rather than blocking indefinitely.
- For final release, close old caveats cumulatively: PR4 implementation review and Tkinter smoke can be closed during PR5 if the final package covers the cumulative branch state.
- If Claude quota cools down:
  - wait/retry when reset is within 2 hours;
  - reroute Claude's task to Codex GPT-5.5 when reset is longer than 2 hours, day/week-long, or unclear-long;
  - document the substitution in review/development history.
- Build review packages from `git ls-files`, not whole directories, to avoid pytest cache permission artifacts and stale untracked files.
- Preserve reviewer outputs and review package paths in development history so future GPT Web / external review can audit both code and process.
- When reviewers raise non-blocking but actionable warnings, fix them immediately, rerun gates, commit/push, and optionally perform a focused re-review package.
- When doing Tkinter UI verification from WSL, distinguish Xvfb executable GUI smoke from human-visible Windows desktop smoke.
- For final merge: Scott approval → pre-merge gates → fast-forward merge → push `origin/main` → post-merge gates → verify local/remote HEADs match.
- For user-trial executables after merge, place artifacts under `C:\Users\chien\_3AI_WorkSpace\temp_EXE` by default and keep a stable alias plus a versioned copy.

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
  - If reviewer-facing quality matters, run coverage and inspect weak spots: `python3 -m pytest --cov=source --cov=calculator --cov-report=term-missing`.
- Add a focused edge-case probe after the happy-path tests. At minimum check:
  - whitespace/blank user inputs are normalized consistently across controller and core layers;
  - documented input grammar matches implementation strictness (for dates, enforce or document exactly `YYYY-MM-DD`);
  - non-zero values must not be displayed as plain `0` after rounding; use scientific notation or an explicit precision policy;
  - no controller calls a private engine method such as `_format_*` when a public API should exist;
  - no dead helper functions, scattered tri-state input flags, unexplained magic constants, or redundant double-validation loops remain.
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
   - Do **not** zip the whole working directory. Never include `.git/`, `build/`, `dist/`, `__pycache__/`, `.pytest_cache/`, or `pytest-cache-files-*` in a source review package.
   - For public release, split artifacts:
     - source release: source, tests, docs, README, pytest/config files, reproducible build instructions;
     - binary release: `MiniCalc.exe`, README/release notes, hash, and build provenance.
   - Prefer `git archive` or an explicit release script over manual folder zipping.
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
- `.gitignore` only prevents future tracking; it does not make a zip clean. Verify package contents with `unzip -l <archive>` or a manifest check before sharing.
- A full green test suite can still miss specification mismatches. Add reviewer-style probes for whitespace, alternate ISO formats, tiny non-zero numbers, and UI wrapper behavior.
- Treat GUI wrapper coverage separately from headless-core coverage. Low `calculator.py` coverage is not automatically a blocker, but release confidence should include fake-widget tests and/or Xvfb smoke.
- Keep layer boundaries clean: controllers should not depend on private engine helpers; promote repeated formatting/parsing behavior to public core APIs.
- If state flags start becoming `None` / empty string / sentinel strings / numeric text, stop and introduce an explicit state object or enum before adding more behavior.

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
- Review feedback from GPT/Claude/Gemini should be mined into durable gates, not treated as one-off praise. The May 16 external reviews produced these reusable upgrades:
  - Preserve the winning pattern: headless core + controller layer + thin Tkinter UI wrapper + delayed Tk import.
  - Keep TDD evidence, development history, acceptance criteria, smoke checklist, and lessons files as first-class deliverables.
  - Add a release-hygiene gate: split source vs binary packages, avoid whole-working-directory zips, and publish hashes for executables.
  - Add adversarial edge probes beyond the 121-test happy baseline: whitespace duration fields, date grammar strictness, tiny non-zero display, private API leakage, dead helpers, state explosion, magic constants, redundant validation, and GUI coverage weak spots.
  - When a reviewer finds a reproducible bug, convert it to a RED test before fixing unless Scott explicitly says not to modify the app.

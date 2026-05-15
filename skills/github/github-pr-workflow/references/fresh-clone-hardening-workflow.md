# Fresh-clone hardening workflow (session-derived pattern)

Use when the user asks to ignore a stale/local working copy, clone from GitHub into the 3AI workspace, apply repairs, and push the improved code back.

## Pattern

1. **Treat the GitHub remote as source of truth**
   - Do not copy files from the local/stale project unless the user explicitly asks.
   - Clone fresh into the 3AI development workspace, e.g. `C:\Users\chien\_3AI_WorkSpace\projects\<repo>` (`/mnt/c/Users/chien/_3AI_WorkSpace/projects/<repo>` in WSL).
   - Verify `git status --short --branch`, `git remote -v`, and recent `git log` before editing.

2. **Use TDD for stabilization tasks**
   - Add tests that capture the intended repair before production changes.
   - Run the tests to observe RED import/failure states, then implement GREEN fixes.
   - Keep tests focused on durable behavior, not transient environment state.

3. **Ask for review before push when changes are broad**
   - For broad stabilization/refactor work, delegate at least two reviews before commit/push:
     - correctness/runtime regression review
     - safety/product-positioning review when user-facing docs or potentially sensitive functionality are involved
   - Fix blocking review findings before committing.

4. **Examples of blocking review findings to catch**
   - Claiming support for multiple providers but only reading one provider's env var.
   - Expanding accepted image types while keeping API payload MIME hardcoded to `image/png`.
   - Merely documenting that a risky legacy module is archived while leaving executable runtime entry points active.
   - README dev instructions that install test deps but omit runtime deps needed by tests.

5. **Verification gate before commit**
   - `git diff --check`
   - language compile check, e.g. `python -m compileall -q .`
   - full test suite, e.g. `python -m pytest tests -q`
   - CLI smoke tests if a CLI exists, e.g. `python main.py --help` and `python main.py --version`

6. **Commit and push**
   - Use a concise summary commit with a body listing major repairs.
   - If the user explicitly asks to upload back to GitHub and the repo is their direct project, pushing to `main` is acceptable after tests/review pass; otherwise prefer branch + PR.
   - After push, verify `origin/main` points at the commit: `git ls-remote origin refs/heads/main`.

## Safety/product hardening notes

When archiving risky legacy functionality, docs alone are not enough. Prefer fail-closed runtime stubs or guards for old entry points, plus tests proving the CLI does not expose the old command and the legacy runtime path raises a clear error.

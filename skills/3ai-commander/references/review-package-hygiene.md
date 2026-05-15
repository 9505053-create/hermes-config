# 3AI Review Package Hygiene

Use this when preparing code-review packages for Claude/Codex/Gemini, especially when the package will be copied into `_agent/<CLI>/reviews/...` and the reviewer may run tests inside the package.

## Durable lesson

Do **not** copy an entire working tree into a review package. Whole-tree copies can include untracked artifacts such as `.pytest_cache/`, `pytest-cache-files-*`, temporary output files, or locked files. Reviewers may then report false blockers that are about package hygiene rather than source code.

Instead, build packages from tracked files only.

## Recommended package creation pattern

From Hermes/Python:

```python
from pathlib import Path
import shutil, subprocess

repo = Path('/path/to/repo')
files_dir = Path('/path/to/review/package/files')
files_dir.mkdir(parents=True, exist_ok=True)

tracked = subprocess.run(
    ['git', 'ls-files'], cwd=repo, text=True, capture_output=True, check=True
).stdout.splitlines()

for rel in tracked:
    src = repo / rel
    dst = files_dir / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
```

Also include:

- `git diff <base>..HEAD` as a patch file.
- `git diff --stat <base>..HEAD`.
- `VERIFICATION.txt` with exact commands and outputs.
- A `PACKAGE_MANIFEST.md` that states whether the package was built from tracked files only.

## Verification to run before dispatching reviewers

Run in the real repo:

```bash
git status --short --branch
python3 -m pytest -q
python3 -m py_compile <all relevant .py files>
git diff --check
```

Then run at least pytest and py_compile inside `package/files` to verify the copy is self-contained:

```bash
cd package/files
python3 -m pytest -q
python3 -m py_compile <same relevant .py files>
```

If pytest cache creation causes warnings or reviewer-local temp directories, use:

```bash
python3 -m pytest -q -p no:cacheprovider
```

## Handling reviewer hygiene blockers

If a reviewer returns `BLOCKED` for missing files or cache/permission artifacts:

1. Verify the actual repo state first; do not assume source code is broken.
2. Search both the real repo and the review package for the named artifact/missing file.
3. Rebuild the package from `git ls-files` only.
4. Re-run repo and package-local verification.
5. Ask for a targeted hygiene re-review, explicitly stating the previous blocker and the remediation.
6. If documentation referenced a non-existent file, patch the docs and commit/push that small correction.

## Example prompt fragment for targeted re-review

```text
Previous blocker was review-package hygiene only: stale pytest-cache artifacts and a missing tracked test helper in the submitted package. This package was regenerated from git ls-files only and includes VERIFICATION_RERUN.txt. Please confirm whether the previous blocker is resolved, then report any remaining blockers or warnings.
```

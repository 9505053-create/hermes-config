# Google Books official-export helper refactor (2026-05-19)

## Context

Project: `C:\Users\chien\_3AI_WorkSpace\projects\google-books-capture`

User wanted Google Books as the core workflow, but agreed to a legal official-export version after the boundary was explained.

Resulting product: `gbooks-helper` v3.0.0 — Google Books Personal Library Helper.

## Safe Product Surface

Public CLI commands:

```text
search
organize-downloads
create-notes
import-highlights
```

Removed from public CLI for this version:

```text
ocr
ai-ocr
build-pdf
capture
```

The legacy capture code remains archived/fail-closed; do not restore viewer capture.

## TDD Tests Added

Create tests before implementation for:

- Google Books API metadata normalization using injected fake HTTP.
- Optional `api_key` support in `search_books()` so live users can avoid anonymous 429 rate limits.
- CLI help exposes only safe workflow commands.
- `organize_downloads()` copies `.pdf`, `.epub`, `.acsm` into per-book folders and does not delete sources by default.
- `create_note_templates()` is idempotent and does not overwrite existing `notes.md`.
- `import_highlights()` reads `.txt` and minimal `.docx` exports.

## Useful Implementation Decisions

- Use a `BookMetadata` dataclass to stabilize Google Books API output.
- Inject `http_get` into `search_books()` for unit tests; do not call live Google Books API in tests.
- Support `--api-key` and `GOOGLE_BOOKS_API_KEY`, but never persist/log key values.
- Treat `.acsm` as an official-export artifact to organize, not as something to decrypt.
- Default `organize-downloads` to copy. Only move when `--move` is explicit.
- Extract `.docx` highlights by reading `word/document.xml` with `zipfile` + `ElementTree`; no `python-docx` dependency needed.

## Verification Commands

WSL/Linux side:

```bash
python -m pytest tests -q
python -m compileall -q .
python main.py --help
python main.py --version
```

Windows side before packaging:

```cmd
cd /d C:\Users\chien\_3AI_WorkSpace\projects\google-books-capture
python -m pytest tests -q
python -m PyInstaller --noconfirm --clean --onefile --console --name gbooks-helper main.py
```

Copy artifacts:

```powershell
$src = 'C:\Users\chien\_3AI_WorkSpace\projects\google-books-capture\dist\gbooks-helper.exe'
$dstDir = 'C:\Users\chien\_3AI_WorkSpace\temp_EXE'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
Copy-Item -Force $src (Join-Path $dstDir 'gbooks-helper.exe')
Copy-Item -Force $src (Join-Path $dstDir "gbooks-helper_v3.0.0_$stamp.exe")
Get-FileHash (Join-Path $dstDir 'gbooks-helper.exe') -Algorithm SHA256
```

## Verified Artifact From Session

- Stable exe: `C:\Users\chien\_3AI_WorkSpace\temp_EXE\gbooks-helper.exe`
- Versioned exe: `C:\Users\chien\_3AI_WorkSpace\temp_EXE\gbooks-helper_v3.0.0_20260519_123248.exe`
- Version: `gbooks-helper, version 3.0.0`
- Size: `31,719,092 bytes`
- SHA256: `10006B578C15529A10923E07D1128A0A836C1EAAB6F023DF1DEBF9ED6109FC7B`
- Test result: `19 passed`

## Smoke Test Pattern

Use a tiny fake PDF export and text highlight file. When launching the Windows exe from WSL, invoke the exe via `/mnt/c/...` if needed, but pass Windows-style paths (`C:\...`) as command arguments.

Expected outputs:

- `library/<Book Title>/<Book Title>.pdf`
- `library/<Book Title>/README.md`
- `library/<Book Title>/notes.md`
- `library/highlights.md`

## Live API Pitfall

Anonymous Google Books API calls can return `429 Too Many Requests`. This is not a unit-test failure. Use fake HTTP in tests and optional `--api-key` / `GOOGLE_BOOKS_API_KEY` for live CLI use.

# Google Books Capture / OCR Toolkit CLI packaging note (2026-05-19)

## Context

Project: `C:\Users\chien\_3AI_WorkSpace\projects\google-books-capture`

Output directory: `C:\Users\chien\_3AI_WorkSpace\temp_EXE`

The project has had two verified Click/Rich CLI shapes:

- `google-books-capture.exe` / OCR Toolkit v2.1.0: heavier build with OCR/AI OCR/image-PDF dependencies and bundled `config/config.yaml`.
- `gbooks-helper.exe` / Google Books Personal Library Helper v3.0.0: lightweight legal official-export workflow (`search`, `organize-downloads`, `create-notes`, `import-highlights`) with no public OCR CLI commands.

Both are **Click/Rich CLIs**, not GUIs. Use `--console`, not `--windowed`, so help text, progress, errors, and command output remain visible.

## Verified build commands

### v2.1 OCR Toolkit build

Run from Windows context:

```cmd
cd /d C:\Users\chien\_3AI_WorkSpace\projects\google-books-capture
python -m compileall -q .
python -m pytest tests -q
python -m PyInstaller --noconfirm --clean --onefile --console --name google-books-capture --add-data config\config.yaml;config main.py
```

### v3.0 legal Google Books helper build

Run from Windows context:

```cmd
cd /d C:\Users\chien\_3AI_WorkSpace\projects\google-books-capture
python -m compileall -q .
python -m pytest tests -q
python -m PyInstaller --noconfirm --clean --onefile --console --name gbooks-helper main.py
```

Then copy:

```powershell
$Artifact = 'C:\Users\chien\_3AI_WorkSpace\temp_EXE'
New-Item -ItemType Directory -Force -Path $Artifact | Out-Null
Copy-Item -Force 'C:\Users\chien\_3AI_WorkSpace\projects\google-books-capture\dist\google-books-capture.exe' "$Artifact\google-books-capture.exe"
Copy-Item -Force 'C:\Users\chien\_3AI_WorkSpace\projects\google-books-capture\dist\google-books-capture.exe' "$Artifact\google-books-capture_$(Get-Date -Format 'yyyyMMdd_HHmmss').exe"
```

## Verification pattern

For a CLI app, do not rely only on `Start-Process`/5-second smoke. Run actual commands:

```cmd
C:\Users\chien\_3AI_WorkSpace\temp_EXE\google-books-capture.exe --help
```

Functional smoke examples:

### v2.1 `build-pdf`

1. Create a tiny PNG fixture under `temp_EXE\smoke_google_books_capture`.
2. Run:

```cmd
cd /d C:\Users\chien\_3AI_WorkSpace\temp_EXE
google-books-capture.exe build-pdf -i smoke_google_books_capture -o smoke_google_books_capture\smoke_output.pdf
```

3. Verify `smoke_output.pdf` exists.

### v3.0 `gbooks-helper`

1. Create a fixture folder containing a fake/real official-export file such as `Sample Purchased Book.pdf` and a notes folder containing `Sample Purchased Book.txt`.
2. Run the Windows exe with Windows-style paths:

```cmd
C:\Users\chien\_3AI_WorkSpace\temp_EXE\gbooks-helper.exe organize-downloads -i C:\Users\chien\_3AI_WorkSpace\temp_EXE\smoke_gbooks_helper\downloads -o C:\Users\chien\_3AI_WorkSpace\temp_EXE\smoke_gbooks_helper\library
C:\Users\chien\_3AI_WorkSpace\temp_EXE\gbooks-helper.exe create-notes -i C:\Users\chien\_3AI_WorkSpace\temp_EXE\smoke_gbooks_helper\library
C:\Users\chien\_3AI_WorkSpace\temp_EXE\gbooks-helper.exe import-highlights -i "C:\Users\chien\_3AI_WorkSpace\temp_EXE\smoke_gbooks_helper\Play Books Notes" -o C:\Users\chien\_3AI_WorkSpace\temp_EXE\smoke_gbooks_helper\library\highlights.md
```

3. Verify `notes.md` and `highlights.md` exist.

## Pitfalls learned

- `--windowed` is wrong for this class of command-line tools; it hides errors and help output.
- Include project config files with `--add-data config\config.yaml;config` if the app reads config by path.
- Onefile size can be large when EasyOCR/Torch is reachable from imports; this is expected unless the project is refactored into separate lightweight/heavy entry points.
- When invoking PowerShell from WSL, prefer single-quoted `-Command '...'` or a script file so WSL/bash does not expand `$variables` before PowerShell sees them.
- When executing a Windows `.exe` from WSL, the program is still Windows-native. Pass `C:\...` paths in CLI arguments; `/mnt/c/...` arguments can fail Click `exists=True` validation inside the Windows process.
- Avoid leaving generated `.spec` files untracked unless reproducible build specs are intentionally part of the project.
- If the entry point is refactored to stop importing heavy OCR modules, rebuild with `--clean`; verify the onefile size drops materially (v3 `gbooks-helper` was ~31.7 MB vs v2 OCR build ~260 MB).

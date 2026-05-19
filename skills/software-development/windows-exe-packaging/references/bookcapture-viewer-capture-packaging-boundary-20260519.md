# BookCapture / viewer-capture packaging boundary (2026-05-19)

## Context

Scott asked to package a freshly re-downloaded GitHub repo at:

```text
C:\Users\chien\_3AI_WorkSpace\projects\google-books-capture
```

Inspection showed the GitHub `main` commit was:

```text
2f88d4e reset: replace OCR-toolkit with BookCapture v4.0 Beta (Claude original)
```

Top-level files included:

```text
README.md
book_capture/
build.bat
requirements.txt
```

`README.md` described the app as:

```text
Google Play Books 螢幕自動截圖工具
```

and listed features:

- Scroll mode: mouse wheel page-turning + pixel-difference detection
- Page mode: arrow-key page-turning + dHash duplicate detection
- Smart crop
- PNG/JPG to PDF output
- PyInstaller one-file packaging

Likely entry point:

```text
book_capture/main.py
```

## Decision

Stop before PyInstaller. Do **not** package this class of app into a ready-to-run `.exe` when it automates Google/Play Books viewer page-turning, screenshots, or PDF reconstruction of viewer content.

Offer a compliant alternative instead:

- Google Books official API metadata lookup
- Organization of official exported PDF/EPUB/ACSM files already present on disk
- Import of official Google Play Books notes/highlights exports
- Reading-note template generation
- Optional lawful OCR only for user-owned/exported documents, not automated viewer capture

## Reusable packaging lesson

Before packaging any freshly downloaded/replaced project:

1. Read `README.md` and entry point purpose.
2. Identify if the executable would materially enable the sensitive workflow.
3. If yes, cancel packaging before dependency install/build and explain the boundary briefly.
4. If compliant, proceed with normal Windows/PyInstaller build and smoke verification.

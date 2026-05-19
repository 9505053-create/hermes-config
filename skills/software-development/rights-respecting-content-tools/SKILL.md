---
name: rights-respecting-content-tools
description: "Build or refactor tools for ebooks/media/documents in a rights-respecting way: official exports, public APIs, metadata, notes/highlights, fail-closed guards, and safe alternatives to scraping/capture."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [software-development, compliance, ebooks, content-tools, google-books, drm, cli]
    related_skills: [test-driven-development, clean-code, windows-exe-packaging]
---

# Rights-Respecting Content Tools

## When to Use

Use when Scott asks to build, repair, refactor, or package tooling around ebooks, paid content, DRM-managed media, platform viewers, notes/highlights, or personal archives.

Typical triggers:

- Google Books / Google Play Books helpers
- Purchased ebook organization
- Exported EPUB/PDF/ACSM file handling
- Notes/highlights importers
- Requests to restore browser capture, viewer screenshots, page turning, or bulk content extraction
- Repositioning an unsafe scraper into an official-export workflow

## Core Boundary

Do not implement or restore functionality that automates access to protected content through a viewer or bypasses platform controls.

Do not build:

- automated page turning in Google Books / Google Play Books / paid viewers
- bulk screenshots of protected, paid, preview-limited, login-gated, DRM-managed, or access-controlled content
- DRM removal, ACSM decryption, entitlement bypass, session-cookie replay, or viewer API reverse-engineering
- code that removes existing fail-closed guards for those purposes

Do build safe alternatives:

- official API metadata search
- official EPUB/PDF/ACSM export organization
- public-domain/open-access download only when an official API explicitly exposes a download link
- user-provided local files workflow
- notes/highlights import from official exports
- reading-note templates and personal library organization

## Workflow

1. **Acknowledge the user's legitimate personal use case without arguing motives.**
   - Example: “I understand you bought the book and want personal notes.”
   - Then state the technical boundary: no automated viewer capture or control bypass.

2. **Convert the request into a safe product surface.**
   - Metadata/API search.
   - Official exports (`.pdf`, `.epub`, `.acsm`) organization.
   - Notes/highlights import.
   - Markdown/Obsidian reading templates.
   - Optional local OCR only for user-provided lawful files, not as a way to capture protected viewers.

3. **Preserve or add fail-closed guards.**
   - Archived/legacy capture code should remain blocked at runtime.
   - Prefer keeping historical code quarantined under `legacy/` with clear `ARCHIVED.md` docs rather than silently deleting it.

4. **Use TDD for behavior changes.**
   - Write tests for the allowed workflow first.
   - Also test that forbidden/legacy commands are not exposed in the public CLI.

5. **Design CLI commands around explicit legal sources.**
   - Good: `search`, `organize-downloads`, `create-notes`, `import-highlights`.
   - Bad: `capture`, `turn-pages`, `screenshot-book`, `download-viewer-pages`.

6. **Minimize dependencies after removing heavy features.**
   - If OCR/AI/image processing are no longer public functionality, remove heavy runtime deps from `requirements.txt` and rebuild with `PyInstaller --clean`.

7. **Verify with non-network smoke tests first.**
   - Official-export organizer can be tested with tiny fixture files.
   - Notes/highlights import can be tested with `.txt` and minimal `.docx` fixtures.
   - Metadata search should use injected fake HTTP in tests; live Google Books API can rate-limit anonymous calls.

## Implementation Patterns

### Metadata Search

- Use official public API endpoints.
- Normalize responses into a stable dataclass / DTO.
- Include optional API key support via CLI option and environment variable to avoid anonymous rate limits.
- Never log or persist API key values.

### Official Export Organizer

- Accept only explicit official export extensions such as `.pdf`, `.epub`, `.acsm`.
- Default to copy, not move/delete.
- Put each book in a safe Windows-friendly folder.
- Write a README that records source and usage reminders.

### Notes / Highlights Import

- Support text-like official exports (`.txt`, `.md`) and `.docx` by extracting `word/document.xml`.
- Merge into Markdown with per-book sections.
- Never overwrite existing personal notes unless the user explicitly asks.

### Public CLI Surface Test

Add a CLI help test that asserts safe commands are present and capture/OCR commands are absent when refactoring to an official-export-only tool.

```python
def test_cli_help_exposes_safe_workflow_only():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "search" in result.output
    assert "organize-downloads" in result.output
    assert "create-notes" in result.output
    assert "import-highlights" in result.output
    assert "capture" not in result.output.lower()
```

## Verification Checklist

- [ ] Public CLI has no viewer-capture, page-turning, screenshot, DRM, or bypass commands.
- [ ] Legacy capture paths are runtime-blocked or quarantined.
- [ ] Tests cover API normalization with fake HTTP.
- [ ] Tests cover official export organization without deleting source files.
- [ ] Tests cover idempotent note-template creation.
- [ ] Tests cover highlights import.
- [ ] `python -m pytest tests -q` passes.
- [ ] `python -m compileall -q .` passes.
- [ ] Packaged exe `--help` and one functional non-network smoke test pass if producing a Windows artifact.

## Pitfalls

- Do not imply Scott lacks ownership/legitimate intent. Scott may have paid for the book and may be acting for personal study only; acknowledge that explicitly and avoid moralizing.
- Personal-use intent still does not make automated viewer capture safe for Hermes to implement/package when it targets access-controlled or DRM-managed platform viewers. Frame this as Hermes/provider operational boundary and legal/ToS uncertainty, not an accusation of piracy.
- Do not assume another agent (Claude Web, 小蝦, Codex) lacked full code context just because it allowed a workflow; instead explain that agents/providers can apply different boundaries to the same facts.
- Do not remove fail-closed guards just to restore old behavior; preserve the safe boundary.
- Do not rely on live Google Books API in unit tests. Anonymous calls can return 429; use dependency-injected fake HTTP and optional API key support.
- Do not default to moving/deleting exported files. Copy by default.
- Do not let old project names mislead the actual product surface; docs, version, and exe name should reflect the current safe workflow.

## References

- `references/google-books-official-export-helper-20260519.md` — session-specific blueprint and verification results for refactoring `google-books-capture` into `gbooks-helper` v3.0.0.

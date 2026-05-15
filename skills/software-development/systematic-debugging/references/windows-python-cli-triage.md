# Windows Python CLI Project Triage

Use this reference when Scott sends a Windows terminal screenshot or asks whether a small Python CLI/project is usable.

## Goal

Distinguish between:
- project code/syntax defects,
- missing Python package dependencies,
- external native dependencies (Tesseract, Poppler, etc.),
- wrong interpreter/launcher (`python`, `py`, `python3`, Microsoft Store aliases),
- removed/legacy functionality versus the current README-supported commands.

## Fast evidence-gathering sequence

From WSL, run Windows commands explicitly when the project is on `C:`:

```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command "cd C:\\path\\to\\project; python --version; python -m pip --version; python main.py --help 2>&1"
```

Read the project contract before judging usability:

```text
README.md
requirements.txt
main.py
relevant command modules
config files
```

Check whether imports are installed in the exact interpreter used to run the program:

```powershell
python -c "import importlib.util; mods=['yaml','click','rich']; [print(m, 'OK' if importlib.util.find_spec(m) else 'MISSING') for m in mods]"
```

Check syntax separately from runtime dependencies:

```powershell
python -m compileall -q .
```

If PowerShell quoting around `$LASTEXITCODE` is fragile from WSL, use a simpler command or `cmd.exe /c`:

```bash
cmd.exe /c "cd /d C:\path\to\project && python -m compileall -q . && echo COMPILE_OK || echo COMPILE_FAIL"
```

## Interpretation patterns

- `ModuleNotFoundError: No module named 'yaml'` + `pyyaml` appears in `requirements.txt` = dependencies not installed in this interpreter; recommend venv + `pip install -r requirements.txt`.
- `python3` silently does nothing or opens Store behavior on Windows = likely Microsoft Store App Execution Alias; prefer `python` or `py -3.x` and verify with `where.exe python python3`.
- OCR/PDF projects can require native tools in addition to pip packages. Examples:
  - Tesseract executable and language data for `pytesseract`.
  - Poppler for `pdf2image` on Windows.
- README changelog/usage may show that a desired feature was moved to `legacy/` or removed; distinguish “current CLI cannot do X” from “project is broken.”

## Recommended answer shape

1. Verdict: broken code vs missing setup vs unsupported current feature.
2. Exact observed error and root cause.
3. Minimal setup commands, preferably venv-local.
4. Native dependency caveats, if applicable.
5. How to verify (`python main.py --help`, `compileall`, sample command).

## Pitfalls

- Do not conclude “the program cannot be used” from one missing module.
- Do not use `python3` as the default recommendation on Windows without verifying what it points to.
- Do not install packages globally when a project-local venv is safer.
- Do not conflate syntax validity (`compileall`) with runtime readiness (dependencies/config/native tools/API keys).
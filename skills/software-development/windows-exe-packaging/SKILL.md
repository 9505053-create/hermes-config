---
name: windows-exe-packaging
description: "Package Python GUI/apps into Windows .exe artifacts for Scott, with all generated executables centralized under C:\\Users\\chien\\_3AI_WorkSpace\\temp_EXE."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [windows, exe, pyinstaller, packaging, artifacts]
    related_skills: [workflow-to-skill-capture]
---

# Windows EXE Packaging

## When to Use

Use when Scott asks to turn a Python app, Tkinter GUI, CLI helper, or small project into an `.exe` for direct trial on Windows.

Scott preference: put all produced executable artifacts in:

```text
C:\Users\chien\_3AI_WorkSpace\temp_EXE
```

Do not scatter executables across Desktop/Downloads/project folders unless Scott explicitly asks for an additional copy.

## Workflow

Reusable helper: `scripts/package_pyinstaller_windows.ps1` packages a PyInstaller onefile executable, copies the stable and versioned artifacts into `C:\Users\chien\_3AI_WorkSpace\temp_EXE`, computes SHA256, and performs a 5-second startup smoke. Use it when the project fits the standard Python/PyInstaller pattern; otherwise follow the manual steps below.

1. Identify the project entry point, usually `main.py`, `app.py`, or a project-specific file such as `calculator.py`.
2. Confirm Windows Python and PyInstaller are available:
   ```bash
   /mnt/c/Windows/System32/cmd.exe /c "where python && python --version && python -m PyInstaller --version"
   ```
   Or run the helper from WSL using Windows PowerShell:
   ```bash
   /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -ExecutionPolicy Bypass -File <skill_dir>/scripts/package_pyinstaller_windows.ps1 -ProjectDir '<WINDOWS_PROJECT_PATH>' -EntryPoint '<entrypoint.py>' -AppName '<AppName>'
   ```
3. Build from the Windows side when the target is a Windows `.exe`:
   ```bash
   /mnt/c/Windows/System32/cmd.exe /c "cd /d <WINDOWS_PROJECT_PATH> && python -m PyInstaller --noconfirm --clean --onefile --windowed --name <AppName> <entrypoint.py>"
   ```
   - Use `--windowed` for Tkinter/GUI apps so no console window appears.
   - Omit `--windowed` for CLI tools where stdout/stderr matters.
4. Create the central artifact folder and copy the executable there:
   ```powershell
   $dir = 'C:\Users\chien\_3AI_WorkSpace\temp_EXE'
   New-Item -ItemType Directory -Force -Path $dir | Out-Null
   Copy-Item -Force '<PROJECT>\dist\<AppName>.exe' (Join-Path $dir '<AppName>.exe')
   Copy-Item -Force '<PROJECT>\dist\<AppName>.exe' (Join-Path $dir '<AppName>_<short_commit_or_timestamp>.exe')
   ```
5. Verify artifact:
   ```powershell
   $exe = 'C:\Users\chien\_3AI_WorkSpace\temp_EXE\<AppName>.exe'
   Get-Item $exe | Select-Object FullName,Length,LastWriteTime
   Get-FileHash $exe -Algorithm SHA256
   ```
6. Smoke test startup:
   ```powershell
   $p = Start-Process -FilePath $exe -PassThru
   Start-Sleep -Seconds 5
   $p.HasExited
   if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force }
   ```
7. Clean up untracked build metadata if it should not be committed, such as `<AppName>.spec`, unless the project wants reproducible build specs tracked.
8. Report the central artifact path, size, SHA256, and startup smoke result.

## Verification Checklist

- [ ] `.exe` exists under `C:\Users\chien\_3AI_WorkSpace\temp_EXE`
- [ ] Size and SHA256 reported
- [ ] Startup smoke did not immediately crash
- [ ] Project tests / compile gates still pass if available
- [ ] Git working tree is clean or any packaging artifacts are intentionally documented

## Pitfalls

- A WSL-built binary is not a Windows `.exe`; invoke Windows Python through `cmd.exe` or PowerShell.
- PyInstaller onefile GUI executables may trigger SmartScreen because they are unsigned. Tell Scott this is expected for unsigned local builds.
- `--windowed` hides console output; avoid it for CLI tools.
- Do not delete old files in `temp_EXE` unless Scott asks. Overwrite only the stable `<AppName>.exe` alias and keep versioned copies for traceability.

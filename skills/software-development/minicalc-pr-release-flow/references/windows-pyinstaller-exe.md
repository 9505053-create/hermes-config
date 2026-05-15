# Windows PyInstaller executable packaging for MiniCalc

Use when Scott asks for a direct Windows `.exe` to try after MiniCalc reaches a stable release state.

## Preconditions

- Work from the release branch or `main` after merge.
- Ensure the repo is clean except intentional release artifacts:
  ```bash
  git status --short --branch
  ```
- Prefer Windows Python/PyInstaller for a Windows `.exe`, invoked from WSL through `cmd.exe`.

## Build

From WSL repo root:

```bash
/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\Users\chien\_3AI_WorkSpace\projects\mini-calc && python -m PyInstaller --noconfirm --clean --onefile --windowed --name MiniCalc calculator.py"
```

Expected output:

```text
C:\Users\chien\_3AI_WorkSpace\projects\mini-calc\dist\MiniCalc.exe
```

## Verify the executable

Use PowerShell to confirm existence, size/hash, and that it starts without immediately exiting:

```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -ExecutionPolicy Bypass -Command '
$exe="C:\Users\chien\_3AI_WorkSpace\projects\mini-calc\dist\MiniCalc.exe";
$item=Get-Item $exe;
Write-Output ("EXISTS=" + $item.FullName);
Write-Output ("SIZE_MB=" + [math]::Round($item.Length/1MB,2));
Write-Output ("SHA256=" + (Get-FileHash $exe -Algorithm SHA256).Hash);
$p=Start-Process -FilePath $exe -PassThru;
Start-Sleep -Seconds 5;
Write-Output ("STARTED_PID=" + $p.Id);
Write-Output ("HAS_EXITED_AFTER_5S=" + $p.HasExited);
if(-not $p.HasExited){ Stop-Process -Id $p.Id -Force; Write-Output "STOPPED_AFTER_SMOKE=YES" }
'
```

This is only a launch smoke. It does not replace a human visible GUI trial.

## Copy to Desktop

Scott expects the trial executable somewhere easy to click. Copy it to the Windows Desktop/OneDrive Desktop:

```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -ExecutionPolicy Bypass -Command '
$src="C:\Users\chien\_3AI_WorkSpace\projects\mini-calc\dist\MiniCalc.exe";
$desktop=[Environment]::GetFolderPath("Desktop");
Copy-Item -Force $src (Join-Path $desktop "MiniCalc.exe");
$dst=Join-Path $desktop "MiniCalc.exe";
$item=Get-Item $dst;
Write-Output ("COPIED=" + $item.FullName);
Write-Output ("SIZE_MB=" + [math]::Round($item.Length/1MB,2));
Write-Output ("SHA256=" + (Get-FileHash $dst -Algorithm SHA256).Hash)
'
```

## Cleanup and gates

PyInstaller may leave `MiniCalc.spec` untracked. Remove it unless you intend to maintain it:

```bash
rm -f MiniCalc.spec
git status --short --branch
git diff --check
python3 -m pytest -q
python3 -m py_compile calculator.py source/*.py tests/*.py scripts/*.py
```

Keep `dist/MiniCalc.exe` as the delivery artifact. `build/` and `dist/` should normally remain ignored/untracked.

## Reporting checklist

Report:

- Desktop path and dist path.
- Size and SHA256.
- Launch-smoke result (`HAS_EXITED_AFTER_5S=False`).
- Reminder that unsigned PyInstaller executables can trigger Windows SmartScreen / unknown publisher warnings.

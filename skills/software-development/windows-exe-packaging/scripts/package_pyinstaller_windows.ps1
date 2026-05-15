param(
    [Parameter(Mandatory=$true)] [string] $ProjectDir,
    [Parameter(Mandatory=$true)] [string] $EntryPoint,
    [Parameter(Mandatory=$true)] [string] $AppName,
    [string] $ArtifactDir = 'C:\Users\chien\_3AI_WorkSpace\temp_EXE',
    [string] $VersionSuffix = '',
    [switch] $Console
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $ProjectDir)) { throw "ProjectDir not found: $ProjectDir" }
New-Item -ItemType Directory -Force -Path $ArtifactDir | Out-Null

Push-Location $ProjectDir
try {
    python -m PyInstaller --version | Out-Null
    $mode = if ($Console) { @() } else { @('--windowed') }
    python -m PyInstaller --noconfirm --clean --onefile @mode --name $AppName $EntryPoint

    $built = Join-Path $ProjectDir "dist\$AppName.exe"
    if (-not (Test-Path $built)) { throw "Build did not produce $built" }

    $stable = Join-Path $ArtifactDir "$AppName.exe"
    Copy-Item -Force $built $stable

    if (-not $VersionSuffix) {
        try { $VersionSuffix = (git rev-parse --short HEAD 2>$null) } catch { $VersionSuffix = Get-Date -Format 'yyyyMMdd_HHmmss' }
        if (-not $VersionSuffix) { $VersionSuffix = Get-Date -Format 'yyyyMMdd_HHmmss' }
    }
    $versioned = Join-Path $ArtifactDir "$AppName`_$VersionSuffix.exe"
    Copy-Item -Force $built $versioned

    $hash = Get-FileHash $stable -Algorithm SHA256
    $item = Get-Item $stable

    $p = Start-Process -FilePath $stable -PassThru
    Start-Sleep -Seconds 5
    $hasExited = $p.HasExited
    if (-not $hasExited) { Stop-Process -Id $p.Id -Force }

    [PSCustomObject]@{
        StablePath = $stable
        VersionedPath = $versioned
        Bytes = $item.Length
        SHA256 = $hash.Hash
        HasExitedAfter5s = $hasExited
        SmokeStopped = -not $hasExited
    } | Format-List
}
finally {
    Pop-Location
}

param(
    [ValidateSet("Install", "Update", "Uninstall")]
    [string]$Action = "Install",

    [ValidateSet("User", "Global")]
    [string]$Scope = "User"
)

$ErrorActionPreference = "Stop"

$repoUrl = "https://github.com/yappologistic/Java-Tutor/archive/refs/heads/main.zip"
$tempRoot = $null

if ($Scope -eq "Global") {
    if ($env:CODEX_GLOBAL_HOME) {
        $codexHome = $env:CODEX_GLOBAL_HOME
    } else {
        $codexHome = Join-Path $env:ProgramData "Codex"
    }
} elseif ($env:CODEX_HOME) {
    $codexHome = $env:CODEX_HOME
} else {
    $codexHome = Join-Path $HOME ".codex"
}

$skillsDir = Join-Path $codexHome "skills"
$target = Join-Path $skillsDir "java-tutor"

if ($Action -eq "Uninstall") {
    if (Test-Path $target) {
        Remove-Item -Recurse -Force -LiteralPath $target
        Write-Host "Uninstalled java-tutor ($Scope scope) from $target"
    } else {
        Write-Host "java-tutor ($Scope scope) is not installed at $target"
    }
    exit 0
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $repoRoot "java-tutor"

if (-not (Test-Path $source)) {
    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("java-tutor-" + [System.Guid]::NewGuid().ToString("N"))
    $zipPath = Join-Path $tempRoot "java-tutor.zip"
    New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null
    Invoke-WebRequest -Uri $repoUrl -OutFile $zipPath
    Expand-Archive -LiteralPath $zipPath -DestinationPath $tempRoot -Force
    $source = Join-Path $tempRoot "Java-Tutor-main\java-tutor"
}

if (-not (Test-Path $source)) {
    throw "Cannot find skill folder: $source"
}

try {
    New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null

    if (Test-Path $target) {
        Remove-Item -Recurse -Force -LiteralPath $target
    }

    Copy-Item -Recurse -Path $source -Destination $target

    Get-ChildItem -Path $target -Recurse -Directory -Filter "__pycache__" |
        Remove-Item -Recurse -Force
    Get-ChildItem -Path $target -Recurse -File -Include "*.pyc", "*.pyo" |
        Remove-Item -Force

    Write-Host "$Action completed for java-tutor ($Scope scope) at $target"
} finally {
    if ($tempRoot -and (Test-Path $tempRoot)) {
        Remove-Item -Recurse -Force -LiteralPath $tempRoot
    }
}

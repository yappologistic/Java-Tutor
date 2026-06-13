param(
    [ValidateSet("User", "Global")]
    [string]$Scope = "User"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $repoRoot "java-tutor"

if (-not (Test-Path $source)) {
    throw "Cannot find skill folder: $source"
}

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

New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null

if (Test-Path $target) {
    Remove-Item -Recurse -Force -LiteralPath $target
}

Copy-Item -Recurse -Path $source -Destination $target

Get-ChildItem -Path $target -Recurse -Directory -Filter "__pycache__" |
    Remove-Item -Recurse -Force
Get-ChildItem -Path $target -Recurse -File -Include "*.pyc", "*.pyo" |
    Remove-Item -Force

Write-Host "Installed java-tutor ($Scope scope) to $target"

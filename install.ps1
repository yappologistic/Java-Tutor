param(
    [ValidateSet("Install", "Update", "Uninstall", "Status")]
    [string]$Action = "Install",

    [ValidateSet("User", "Global")]
    [string]$Scope = "User"
)

$ErrorActionPreference = "Stop"

$repoUrl = if ($env:JAVA_TUTOR_ARCHIVE_URL) { $env:JAVA_TUTOR_ARCHIVE_URL } else { "https://github.com/yappologistic/Java-Tutor/archive/refs/heads/main.zip" }
$tempRoot = $null
$sourceKind = "local"

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

function Assert-ExpectedTarget {
    $skillsFullPath = [System.IO.Path]::GetFullPath($skillsDir)
    $targetFullPath = [System.IO.Path]::GetFullPath($target)
    $expectedTarget = [System.IO.Path]::GetFullPath((Join-Path $skillsDir "java-tutor"))
    if ($targetFullPath -ne $expectedTarget -or -not $targetFullPath.StartsWith($skillsFullPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to modify unexpected install target: $target"
    }
}

function Test-JavaTutorInstall {
    return (Test-Path (Join-Path $target "SKILL.md")) -or (Test-Path (Join-Path $target ".install-info"))
}

if ($Action -eq "Status") {
    if (Test-Path (Join-Path $target "SKILL.md")) {
        Write-Host "java-tutor ($Scope scope) is installed at $target"
        $metadataPath = Join-Path $target ".install-info"
        if (Test-Path $metadataPath) {
            $metadata = @{}
            foreach ($line in Get-Content -LiteralPath $metadataPath) {
                $separatorIndex = $line.IndexOf("=")
                if ($separatorIndex -gt 0) {
                    $metadata[$line.Substring(0, $separatorIndex)] = $line.Substring($separatorIndex + 1)
                }
            }
            Write-Host "Installed at: $($metadata.installedAtUtc)"
            Write-Host "Installed from: $($metadata.source)"
        }
    } else {
        Write-Host "java-tutor ($Scope scope) is not installed at $target"
    }
    exit 0
}

if ($Action -eq "Uninstall") {
    Assert-ExpectedTarget
    if (Test-Path $target) {
        if (-not (Test-JavaTutorInstall)) {
            throw "Refusing to uninstall $target because it does not look like a java-tutor skill install"
        }
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
    $sourceKind = "archive"
    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("java-tutor-" + [System.Guid]::NewGuid().ToString("N"))
    $zipPath = Join-Path $tempRoot "java-tutor.zip"
    New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null
    if (Test-Path -LiteralPath $repoUrl) {
        Copy-Item -LiteralPath $repoUrl -Destination $zipPath
    } else {
        Invoke-WebRequest -UseBasicParsing -Uri $repoUrl -OutFile $zipPath
    }
    Expand-Archive -LiteralPath $zipPath -DestinationPath $tempRoot -Force
    $source = Join-Path $tempRoot "Java-Tutor-main\java-tutor"
}

if (-not (Test-Path $source)) {
    throw "Cannot find skill folder: $source"
}

try {
    New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
    Assert-ExpectedTarget

    $tempTarget = Join-Path $skillsDir (".java-tutor.tmp." + [System.Guid]::NewGuid().ToString("N"))
    $backupTarget = Join-Path $skillsDir (".java-tutor.backup." + [System.Guid]::NewGuid().ToString("N"))
    Copy-Item -Recurse -Path $source -Destination $tempTarget
    if (-not (Test-Path (Join-Path $tempTarget "SKILL.md"))) {
        throw "Install payload is missing SKILL.md"
    }

    $licenseSource = $null
    $repoLicense = Join-Path $repoRoot "LICENSE"
    $archiveLicense = if ($tempRoot) { Join-Path $tempRoot "Java-Tutor-main\LICENSE" } else { $null }
    if (Test-Path $repoLicense) {
        $licenseSource = $repoLicense
    } elseif ($archiveLicense -and (Test-Path $archiveLicense)) {
        $licenseSource = $archiveLicense
    }
    if ($licenseSource) {
        Copy-Item -LiteralPath $licenseSource -Destination (Join-Path $tempTarget "LICENSE")
    }

    $installSource = if ($sourceKind -eq "archive") { $repoUrl } else { $source }
    @(
        "skill=java-tutor"
        "scope=$Scope"
        "installedAtUtc=$((Get-Date).ToUniversalTime().ToString("o"))"
        "source=$installSource"
    ) | Set-Content -LiteralPath (Join-Path $tempTarget ".install-info") -Encoding UTF8

    Get-ChildItem -Path $tempTarget -Recurse -Directory -Filter "__pycache__" |
        Remove-Item -Recurse -Force
    Get-ChildItem -Path $tempTarget -Recurse -File -Include "*.pyc", "*.pyo" |
        Remove-Item -Force

    if (Test-Path $target) {
        Move-Item -LiteralPath $target -Destination $backupTarget
    }

    try {
        Move-Item -LiteralPath $tempTarget -Destination $target
        if (Test-Path $backupTarget) {
            Remove-Item -Recurse -Force -LiteralPath $backupTarget
        }
    } catch {
        if ((Test-Path $backupTarget) -and -not (Test-Path $target)) {
            Move-Item -LiteralPath $backupTarget -Destination $target
        }
        throw
    }

    Write-Host "$Action completed for java-tutor ($Scope scope) at $target"
} finally {
    if ($tempTarget -and (Test-Path $tempTarget)) {
        Remove-Item -Recurse -Force -LiteralPath $tempTarget
    }
    if ($tempRoot -and (Test-Path $tempRoot)) {
        Remove-Item -Recurse -Force -LiteralPath $tempRoot
    }
}

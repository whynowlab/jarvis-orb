# Jarvis Orb — Windows Installer (PowerShell)
# Usage: irm https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.ps1 | iex

$ErrorActionPreference = "SilentlyContinue"
$Version = "0.1.0"
$Repo = "whynowlab/jarvis-orb"
$BrainDir = "$env:USERPROFILE\.jarvis-orb"
$BrainBin = "$BrainDir\bin"

# ── Colors ──
function Write-Cyan($msg) { Write-Host "  $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "    ✓ $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    ! $msg" -ForegroundColor Yellow }
function Write-Info($msg) { Write-Host "    $msg" -ForegroundColor DarkGray }
function Write-Step($msg) { Write-Host "`n  → $msg" -ForegroundColor White }

# ── Header ──
Write-Host ""
Write-Host ""
Write-Cyan "JARVIS ORB"
Write-Info "AI Brain + Realtime Visualizer"
Write-Info "v$Version"
Write-Host ""

# ── Step 1: Environment ──
Write-Step "Checking environment"
Write-Info "Windows $([System.Environment]::OSVersion.Version)"

$hasPython = Get-Command python -ErrorAction SilentlyContinue
if ($hasPython) {
    Write-Ok "Python found: $(python --version 2>&1)"
} else {
    Write-Warn "Python not found — Brain Lite requires Python 3.11+"
}

# ── Step 2: Brain Lite ──
Write-Step "Installing Brain Lite"

New-Item -ItemType Directory -Force -Path $BrainDir | Out-Null
New-Item -ItemType Directory -Force -Path $BrainBin | Out-Null

if ($hasPython) {
    Write-Info "Installing dependencies..."
    $pipOutput = python -m pip install --target "$BrainDir\lib" aiosqlite websockets 2>&1
    Write-Ok "Dependencies installed"
}

# Download Brain source
Write-Info "Downloading Brain Lite..."
$zipUrl = "https://github.com/$Repo/archive/refs/heads/main.zip"
$zipPath = "$env:TEMP\jarvis-orb-main.zip"
$extractPath = "$env:TEMP\jarvis-orb-extract"

try {
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
    if (Test-Path $extractPath) { Remove-Item -Recurse -Force $extractPath }
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

    $brainSrc = "$extractPath\jarvis-orb-main\brain\jarvis_brain"
    if (Test-Path $brainSrc) {
        Copy-Item -Recurse -Force $brainSrc "$BrainDir\jarvis_brain"
        Write-Ok "Brain Lite → $BrainDir"
    }

    Remove-Item -Force $zipPath -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $extractPath -ErrorAction SilentlyContinue
} catch {
    Write-Warn "Download failed — install from source"
}

# Create launcher
$launcherContent = @"
@echo off
set PYTHONPATH=$BrainDir\lib;$BrainDir
python -m jarvis_brain.mcp_server %*
"@
Set-Content -Path "$BrainBin\jarvis-brain.bat" -Value $launcherContent
Write-Ok "Brain launcher → $BrainBin\jarvis-brain.bat"

# ── Step 3: Claude Code MCP ──
Write-Step "Configuring Claude Code"

$claudeSettings = "$env:USERPROFILE\.claude\settings.json"
if (Test-Path $claudeSettings) {
    $content = Get-Content $claudeSettings -Raw
    if ($content -match "jarvis-brain") {
        Write-Ok "Already configured"
    } else {
        Write-Info "Add to your Claude Code MCP config:"
        Write-Host ""
        Write-Host '    "jarvis-brain": {' -ForegroundColor White
        Write-Host "      `"command`": `"$BrainBin\jarvis-brain.bat`"" -ForegroundColor White
        Write-Host '    }' -ForegroundColor White
        Write-Host ""
    }
} else {
    Write-Info "Claude Code not found — configure MCP manually after install"
}

# ── Step 4: Orb App ──
Write-Step "Installing Orb"

try {
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" -UseBasicParsing 2>$null
    $exeAsset = $release.assets | Where-Object { $_.name -match "setup\.exe$" } | Select-Object -First 1

    if ($exeAsset) {
        $exeUrl = $exeAsset.browser_download_url
        $exePath = "$env:TEMP\JarvisOrb-setup.exe"
        Write-Info "Downloading Orb..."
        Invoke-WebRequest -Uri $exeUrl -OutFile $exePath -UseBasicParsing
        Write-Ok "Downloaded. Running installer..."
        Start-Process -FilePath $exePath -Wait
        Remove-Item -Force $exePath -ErrorAction SilentlyContinue
        Write-Ok "Jarvis Orb installed"
    } else {
        Write-Warn "No release found. Download manually:"
        Write-Info "https://github.com/$Repo/releases"
    }
} catch {
    Write-Warn "Could not fetch release. Download manually:"
    Write-Info "https://github.com/$Repo/releases"
}

# ── Done ──
Write-Host ""
Write-Host ""
Write-Host "  Installed." -ForegroundColor Green -NoNewline
Write-Host ""
Write-Host ""
Write-Info "Brain   $BrainDir\brain.db"
Write-Info "MCP     jarvis-brain"
Write-Info "Orb     Jarvis Orb"
Write-Host ""
Write-Cyan "Your AI will start remembering."
Write-Host ""

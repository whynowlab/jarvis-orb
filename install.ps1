# Jarvis Orb — Windows Installer (PowerShell)
# Usage: irm https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.ps1 | iex

$ErrorActionPreference = "SilentlyContinue"
$Version = "0.1.0"
$Repo = "whynowlab/jarvis-orb"
$BrainDir = "$env:USERPROFILE\.jarvis-orb"
$BrainBin = "$BrainDir\bin"

# ── Colors ──
$Script:StepNum = 0
$Script:TotalSteps = 4

function Write-Cyan($msg) { Write-Host "  $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "    ✓ $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    ! $msg" -ForegroundColor Yellow }
function Write-Info($msg) { Write-Host "    $msg" -ForegroundColor DarkGray }
function Write-Step($msg) {
    $Script:StepNum++
    $filled = [int]($Script:StepNum * 20 / $Script:TotalSteps)
    $empty = 20 - $filled
    $bar = ("█" * $filled) + ("░" * $empty)
    Write-Host ""
    Write-Host "  [$bar] $($Script:StepNum)/$($Script:TotalSteps)" -ForegroundColor DarkGray
    Write-Host "  → $msg" -ForegroundColor White
}

# ── Header ──
Write-Host ""
Write-Host ""
# Generate logo with oh-my-logo if npx available
$hasNpx = Get-Command npx -ErrorAction SilentlyContinue
if ($hasNpx) {
    npx -y oh-my-logo "JARVIS" --palette-colors "#4A9EBF,#8EE4FF,#6B4FA0" --filled --block-font block -d diagonal --color 2>$null
    Write-Host "                                  " -NoNewline
    Write-Host "◉ ORB" -ForegroundColor Cyan
    Write-Host "                                  " -NoNewline
    Write-Host "AI Brain + Visualizer · v$Version" -ForegroundColor DarkGray
} else {
    Write-Host "  J A R V I S" -NoNewline -ForegroundColor Cyan
    Write-Host "  ◉ ORB" -ForegroundColor White
    Write-Host "  AI Brain + Visualizer · v$Version" -ForegroundColor DarkGray
}
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
$brainLauncher = @"
@echo off
set PYTHONPATH=$BrainDir\lib;$BrainDir
python -m jarvis_brain.mcp_server %*
"@
Set-Content -Path "$BrainBin\jarvis-brain.bat" -Value $brainLauncher

$orbLauncher = @"
@echo off
set PYTHONPATH=$BrainDir\lib;$BrainDir
python -m jarvis_brain.cli %*
"@
Set-Content -Path "$BrainBin\jarvis-orb.bat" -Value $orbLauncher
Write-Ok "Commands → jarvis-orb, jarvis-brain"

# Add to PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$BrainBin*") {
    [Environment]::SetEnvironmentVariable("Path", "$BrainBin;$currentPath", "User")
    Write-Ok "Added to PATH (restart terminal to use)"
}

# ── Step 3: Claude Code MCP ──
Write-Step "Configuring Claude Code"

$claudeDir = "$env:USERPROFILE\.claude"
$claudeSettings = "$claudeDir\settings.json"

if (Test-Path $claudeSettings) {
    $content = Get-Content $claudeSettings -Raw
    if ($content -match "jarvis-brain") {
        Write-Ok "Already configured"
    } else {
        try {
            $settings = $content | ConvertFrom-Json
            # Add mcpServers if not exists
            if (-not $settings.mcpServers) {
                $settings | Add-Member -NotePropertyName "mcpServers" -NotePropertyValue @{} -Force
            }
            $brainCmd = "$BrainBin\jarvis-brain.bat"
            $settings.mcpServers | Add-Member -NotePropertyName "jarvis-brain" -NotePropertyValue @{
                command = $brainCmd
            } -Force
            $settings | ConvertTo-Json -Depth 10 | Set-Content $claudeSettings -Encoding UTF8
            Write-Ok "MCP server registered in Claude Code"
        } catch {
            Write-Info "Add to your Claude Code MCP config:"
            Write-Host ""
            Write-Host '    "jarvis-brain": {' -ForegroundColor White
            Write-Host "      `"command`": `"$BrainBin\jarvis-brain.bat`"" -ForegroundColor White
            Write-Host '    }' -ForegroundColor White
            Write-Host ""
        }
    }
} elseif (Test-Path $claudeDir) {
    # settings.json doesn't exist but .claude dir does — create it
    $newSettings = @{
        mcpServers = @{
            "jarvis-brain" = @{
                command = "$BrainBin\jarvis-brain.bat"
            }
        }
    }
    $newSettings | ConvertTo-Json -Depth 10 | Set-Content $claudeSettings -Encoding UTF8
    Write-Ok "Created Claude Code settings with MCP config"
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
if ($hasNpx) {
    npx -y oh-my-logo "JARVIS" --palette-colors "#8EE4FF,#B0F0FF,#8EE4FF" --filled --block-font block -d diagonal --color 2>$null
    Write-Host "                                  " -NoNewline
    Write-Host "◉ ORB" -NoNewline -ForegroundColor Green
    Write-Host "  ONLINE" -ForegroundColor Green
} else {
    Write-Host "  J A R V I S" -NoNewline -ForegroundColor Green
    Write-Host "  ◉ ORB  ONLINE" -ForegroundColor Green
}
Write-Host ""
Write-Host "  I N S T A L L E D" -ForegroundColor Green
Write-Host ""
Write-Info "Brain   $BrainDir\brain.db"
Write-Info "MCP     jarvis-brain"
Write-Info "Orb     Jarvis Orb"
Write-Info "CLI     jarvis-orb"
Write-Host ""
Write-Cyan "Your AI will start remembering."
Write-Host ""

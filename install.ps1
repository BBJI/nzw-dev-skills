<#
.SYNOPSIS
  nzw-dev-skills 一键安装脚本（Windows PowerShell）
.PARAMETER Target
  claude-code | codex | all（默认 all）
.EXAMPLE
  # 本地执行
  .\install.ps1 -Target all
.EXAMPLE
  # 一行命令远程安装（无需先 clone）
  irm https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.ps1 | iex
#>
param(
    [ValidateSet('claude-code','codex','all')]
    [string]$Target = 'all'
)

$ErrorActionPreference = 'Stop'

# 强制 TLS 1.2：GitHub 仅接受 TLS 1.2+，旧版 PowerShell 默认走 TLS 1.0/1.1，
# 会导致「基础连接已经关闭: 接收时发生错误」。
# 注意：这对 `irm ... | iex` 管道本身无效——TLS 必须在 irm 执行前由用户设置；
# 此处主要保证自举阶段 Invoke-WebRequest 拉 tarball 时握手成功。
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
} catch {
    Write-Host "⚠ 无法设置 TLS 1.2：$_" -ForegroundColor Yellow
}

# 默认仓库（请改为你的 GitHub 仓库）
$NzwRepoDefault   = 'BBJI/nzw-dev-skills'
$NzwBranchDefault = 'main'

# GitHub 镜像前缀（国内网络拉取失败时设置，如 $env:NZW_MIRROR='https://ghproxy.net'）
# 拼接后会形如 https://ghproxy.net/https://codeload.github.com/...
function Resolve-GhUrl {
    param([string]$Url)
    $mirror = if ($env:NZW_MIRROR) { $env:NZW_MIRROR.TrimEnd('/') } else { '' }
    if ($mirror) { "$mirror/$Url" } else { $Url }
}

# ---------------------------------------------------------------------------
# 自举：当脚本通过 irm | iex 管道执行时，$PSScriptRoot 为空或无 skills 目录，
# 需先从 GitHub 拉取 tarball 解压后重新调用本地 install.ps1
# ---------------------------------------------------------------------------
function Invoke-Bootstrap {
    $repo   = if ($env:NZW_REPO)   { $env:NZW_REPO }   else { $NzwRepoDefault }
    $branch = if ($env:NZW_BRANCH) { $env:NZW_BRANCH } else { $NzwBranchDefault }
    $url    = Resolve-GhUrl "https://codeload.github.com/$repo/tar.gz/refs/heads/$branch"

    Write-Host "▶ 从 GitHub 拉取 nzw-dev-skills ($repo@$branch)..."
    if ($env:NZW_MIRROR) { Write-Host "  使用镜像：$env:NZW_MIRROR" }
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) "nzw-install-$(Get-Random)"
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    $tarball = Join-Path $tmp 'repo.tar.gz'

    try {
        Invoke-WebRequest -Uri $url -OutFile $tarball -UseBasicParsing
    } catch {
        Write-Host "✗ 下载失败：$_" -ForegroundColor Red
        Remove-Item -Recurse -Force $tmp
        exit 1
    }

    # Windows 10+ 自带 tar.exe
    $tar = Get-Command tar -ErrorAction SilentlyContinue
    if (-not $tar) {
        Write-Host "✗ 需要 tar（Windows 10 1803+ 自带，请升级或安装 bsdtar）" -ForegroundColor Red
        Remove-Item -Recurse -Force $tmp
        exit 1
    }
    & tar -xzf $tarball -C $tmp
    $extracted = Get-ChildItem -Path $tmp -Directory | Select-Object -First 1
    if (-not $extracted -or -not (Test-Path (Join-Path $extracted.FullName 'install.ps1'))) {
        Write-Host "✗ 解压后未找到 install.ps1" -ForegroundColor Red
        Remove-Item -Recurse -Force $tmp
        exit 1
    }

    # 重新执行本地 install.ps1，透传参数
    & powershell -NoProfile -File (Join-Path $extracted.FullName 'install.ps1') -Target $Target
    $rc = $LASTEXITCODE
    Remove-Item -Recurse -Force $tmp
    exit $rc
}

# 检测是否需要自举：管道执行时 $PSScriptRoot 为空
$scriptHasSkills = $false
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot 'skills'))) {
    $scriptHasSkills = $true
}
if (-not $scriptHasSkills) {
    Invoke-Bootstrap
    return
}

$ScriptDir = $PSScriptRoot
$ClaudeDir = if ($env:NZW_CLAUDE_DIR) { $env:NZW_CLAUDE_DIR } else { Join-Path $HOME '.claude' }
$CodexDir  = if ($env:NZW_CODEX_DIR)  { $env:NZW_CODEX_DIR  } else { Join-Path $HOME '.codex'  }

Write-Host "▶ nzw-dev-skills 安装开始 (源: $ScriptDir)"

function Install-ClaudeCode {
    $skillsDir   = Join-Path $ClaudeDir 'skills'
    $commandsDir = Join-Path $ClaudeDir 'commands'
    New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $commandsDir | Out-Null

    Write-Host "▶ 安装 skills → $skillsDir"
    Get-ChildItem -Path (Join-Path $ScriptDir 'skills') -Directory | ForEach-Object {
        $dest = Join-Path $skillsDir $_.Name
        if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
        Copy-Item -Recurse $_.FullName $dest
        Write-Host "  ✓ $($_.Name)"
    }

    Write-Host "▶ 安装斜杠命令 → $commandsDir"
    Get-ChildItem -Path (Join-Path $ScriptDir 'commands') -Filter *.md | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $commandsDir $_.Name) -Force
        Write-Host "  ✓ $($_.Name)"
    }
    Write-Host "▶ Claude Code 安装完成（请重启 Claude Code，输入 /nzw-status 验证）"
}

function Install-Codex {
    New-Item -ItemType Directory -Force -Path $CodexDir | Out-Null
    $agentsFile = Join-Path $CodexDir 'AGENTS.md'
    if (Test-Path $agentsFile) {
        $stamp = Get-Date -Format 'yyyyMMddHHmmss'
        Copy-Item $agentsFile "$agentsFile.bak.$stamp"
        Write-Host "  ⚠ 已备份原 AGENTS.md"
    }
    Copy-Item (Join-Path $ScriptDir 'codex\AGENTS.md') $agentsFile -Force
    Write-Host "  ✓ AGENTS.md"

    $codexSkillsDir = Join-Path $CodexDir 'skills'
    if (Test-Path $codexSkillsDir) { Remove-Item -Recurse -Force $codexSkillsDir }
    New-Item -ItemType Directory -Force -Path $codexSkillsDir | Out-Null
    Get-ChildItem -Path (Join-Path $ScriptDir 'skills') -Directory | ForEach-Object {
        Copy-Item -Recurse $_.FullName (Join-Path $codexSkillsDir $_.Name)
    }
    Write-Host "  ✓ skills/"
    Write-Host "▶ Codex 安装完成（Codex 启动时自动加载 AGENTS.md，可用自然语言触发）"
}

if ($Target -in @('claude-code','all')) { Install-ClaudeCode }
if ($Target -in @('codex','all'))       { Install-Codex }

Write-Host ""
Write-Host "✔ nzw-dev-skills 安装结束"
Write-Host "  触发方式："
Write-Host "    单 skill： /nzw-req <任务> / /nzw-design / /nzw-review / /nzw-task / /nzw-dev / /nzw-test / /nzw-instruction"
Write-Host "    全流程：   /nzw-workflow <任务描述>"
Write-Host "    续传：     /nzw-resume"
Write-Host "    看状态：   /nzw-status [--req <id>]"
Write-Host "    切换需求： /nzw-switch <req-id>"

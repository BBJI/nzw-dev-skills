#!/usr/bin/env bash
# nzw-dev-skills 一键安装脚本（Linux / macOS / Git Bash on Windows）
#
# 用法 1（本地执行）：
#   ./install.sh [--claude-code] [--codex] [--all]
#
# 用法 2（一行命令远程安装，无需先 clone）：
#   curl -fsSL https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.sh | bash
#   （PowerShell：irm https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.ps1 | iex）
#
# 可用环境变量覆盖：
#   NZW_REPO        GitHub 仓库，默认 BBJI/nzw-dev-skills
#   NZW_BRANCH      分支，默认 main
#   NZW_CLAUDE_DIR  Claude Code 安装目录，默认 ~/.claude
#   NZW_CODEX_DIR   Codex 安装目录，默认 ~/.codex
set -euo pipefail

NZW_REPO_DEFAULT="BBJI/nzw-dev-skills"
NZW_BRANCH_DEFAULT="main"

# ---------------------------------------------------------------------------
# 自举：当脚本通过 curl|bash 管道执行时，本地无 skills/ 目录，需先拉取仓库
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)"

bootstrap_remote() {
  local repo="${NZW_REPO:-$NZW_REPO_DEFAULT}"
  local branch="${NZW_BRANCH:-$NZW_BRANCH_DEFAULT}"
  local tmp_dir
  tmp_dir="$(mktemp -d 2>/dev/null || mktemp -d -t nzw-install)"
  local tarball="$tmp_dir/repo.tar.gz"
  local url="https://codeload.github.com/${repo}/tar.gz/refs/heads/${branch}"

  echo "▶ 从 GitHub 拉取 nzw-dev-skills ($repo@$branch)..."
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$tarball"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$tarball" "$url"
  else
    echo "✗ 需要 curl 或 wget 来下载，请先安装其一" >&2
    rm -rf "$tmp_dir"
    exit 1
  fi

  if ! command -v tar >/dev/null 2>&1; then
    echo "✗ 需要 tar 来解压，请先安装" >&2
    rm -rf "$tmp_dir"
    exit 1
  fi

  tar -xzf "$tarball" -C "$tmp_dir"
  local extracted
  extracted="$(find "$tmp_dir" -maxdepth 1 -mindepth 1 -type d | head -1)"
  if [[ -z "$extracted" || ! -f "$extracted/install.sh" ]]; then
    echo "✗ 解压后未找到 install.sh，仓库结构异常" >&2
    rm -rf "$tmp_dir"
    exit 1
  fi

  # 用真正的本地 install.sh 重新执行，透传所有参数
  set +e
  bash "$extracted/install.sh" "$@"
  local rc=$?
  set -e
  rm -rf "$tmp_dir"
  exit $rc
}

# BASH_SOURCE 为空或不存在 skills/ 目录 → 管道执行模式，自举
if [[ -z "${BASH_SOURCE[0]:-}" || ! -d "$SCRIPT_DIR/skills" ]]; then
  bootstrap_remote "$@"
fi

TARGET_CLAUDE="${NZW_CLAUDE_DIR:-$HOME/.claude}"
TARGET_CODEX="${NZW_CODEX_DIR:-$HOME/.codex}"

INSTALL_CLAUDE=0
INSTALL_CODEX=0
if [[ $# -eq 0 ]]; then
  INSTALL_CLAUDE=1
  INSTALL_CODEX=1
fi
while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude-code) INSTALL_CLAUDE=1; shift;;
    --codex)       INSTALL_CODEX=1; shift;;
    --all)         INSTALL_CLAUDE=1; INSTALL_CODEX=1; shift;;
    *) echo "未知参数: $1"; exit 1;;
  esac
done

echo "▶ nzw-dev-skills 安装开始 (源: $SCRIPT_DIR)"

install_claude_code() {
  local skills_dir="$TARGET_CLAUDE/skills"
  local commands_dir="$TARGET_CLAUDE/commands"
  mkdir -p "$skills_dir" "$commands_dir"

  echo "▶ 安装 skills → $skills_dir"
  for skill_dir in "$SCRIPT_DIR"/skills/*/; do
    [[ -d "$skill_dir" ]] || continue
    name="$(basename "$skill_dir")"
    rm -rf "$skills_dir/$name"
    cp -r "$skill_dir" "$skills_dir/$name"
    echo "  ✓ $name"
  done

  echo "▶ 安装斜杠命令 → $commands_dir"
  for cmd_file in "$SCRIPT_DIR"/commands/*.md; do
    [[ -f "$cmd_file" ]] || continue
    cp "$cmd_file" "$commands_dir/"
    echo "  ✓ $(basename "$cmd_file")"
  done

  echo "▶ Claude Code 安装完成"
  echo "  请重启 Claude Code，输入 /nzw-status 验证"
}

install_codex() {
  local codex_dir="$TARGET_CODEX"
  mkdir -p "$codex_dir"

  echo "▶ 生成 Codex AGENTS.md → $codex_dir/AGENTS.md"
  if [[ -f "$codex_dir/AGENTS.md" ]]; then
    cp "$codex_dir/AGENTS.md" "$codex_dir/AGENTS.md.bak.$(date +%Y%m%d%H%M%S)"
    echo "  ⚠ 已备份原 AGENTS.md"
  fi
  cp "$SCRIPT_DIR/codex/AGENTS.md" "$codex_dir/AGENTS.md"
  echo "  ✓ AGENTS.md"

  echo "▶ 复制 skill 文档 → $codex_dir/skills/"
  rm -rf "$codex_dir/skills"
  mkdir -p "$codex_dir/skills"
  for skill_dir in "$SCRIPT_DIR"/skills/*/; do
    [[ -d "$skill_dir" ]] || continue
    cp -r "$skill_dir" "$codex_dir/skills/"
  done
  echo "  ✓ skills/"

  echo "▶ Codex 安装完成"
  echo "  Codex 启动时会自动加载 AGENTS.md，可用自然语言触发各 skill"
}

if [[ $INSTALL_CLAUDE -eq 1 ]]; then install_claude_code; fi
if [[ $INSTALL_CODEX   -eq 1 ]]; then install_codex; fi

echo ""
echo "✔ nzw-dev-skills 安装结束"
echo "  触发方式："
echo "    单 skill： /nzw-req <任务> / /nzw-design / /nzw-review / /nzw-task / /nzw-dev / /nzw-test / /nzw-instruction"
echo "    全流程：   /nzw-workflow <任务描述>"
echo "    续传：     /nzw-resume"
echo "    看状态：   /nzw-status [--req <id>]"
echo "    切换需求： /nzw-switch <req-id>"

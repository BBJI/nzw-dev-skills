# nzw-dev-skills

AI 自主全流程交付技能包 —— **需求 → 设计 → 评审 → 任务 → 开发 → 测试 → 规范** 闭环。
支持 Claude Code 与 OpenAI Codex，支持指令触发与自然语言触发，支持跨会话续传。

## 一行命令安装（无需先 clone）

### macOS / Linux / Git Bash on Windows

```bash
curl -fsSL https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.sh | bash
```

可选参数（在 `bash` 后加 `-s --`）：

```bash
# 只装 Claude Code
curl -fsSL https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.sh | bash -s -- --claude-code

# 只装 Codex
curl -fsSL https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.sh | bash -s -- --codex
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.ps1 | iex
```

指定目标平台：

```powershell
& { irm https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.ps1 | iex } -Target codex
```

> 系统自带 `curl` 或 `wget`、`tar` 即可，无需 git。

## 本地安装（已 clone 仓库）

```bash
./install.sh --all           # macOS / Linux / Git Bash
.\install.ps1 -Target all    # Windows PowerShell
```

支持 `--claude-code` / `--codex` / `--all`（默认 all）。

安装后：
- Claude Code：skills 装入 `~/.claude/skills/`，斜杠命令装入 `~/.claude/commands/`
- Codex：合并为 `~/.codex/AGENTS.md`，skill 文档装入 `~/.codex/skills/`

## 环境变量覆盖

| 变量 | 作用 | 默认值 |
|---|---|---|
| `NZW_REPO` | GitHub 仓库（远程安装时拉取源） | `BBJI/nzw-dev-skills` |
| `NZW_BRANCH` | 拉取分支 | `main` |
| `NZW_CLAUDE_DIR` | Claude Code 安装目录 | `~/.claude` |
| `NZW_CODEX_DIR` | Codex 安装目录 | `~/.codex` |

示例：从 fork 安装到自定义目录

```bash
NZW_REPO=myorg/nzw-fork NZW_CLAUDE_DIR=~/my-claude \
  curl -fsSL https://raw.githubusercontent.com/myorg/nzw-fork/main/install.sh | bash
```

## 触发指令

| 指令 | 作用 | 对应 skill |
|---|---|---|
| `/nzw-req <任务描述>` | 需求调研分析 | req-analysis-skill |
| `/nzw-design` | UI/UX 设计规范 | design-skill |
| `/nzw-review` | 三维实现评估 | review-skill |
| `/nzw-task` | 任务拆分与排期 | task-allocation-skill |
| `/nzw-dev [task-id]` | TDD 开发实现 | dev-skill |
| `/nzw-test` | 测试用例与验证 | test-skill |
| `/nzw-instruction` | 生成项目规范 | instruction-skill |
| `/nzw-workflow <任务描述>` | **全流程自主交付** | workflow-skill |
| `/nzw-resume` | 跨会话续传 | 读 `.nds/state.json` 接续 |
| `/nzw-status` | 查看当前进度 | 展示 `.nds/PROGRESS.md` |

Codex 无斜杠命令，用自然语言触发即可（如"启动 nzw workflow 做一个 XXX"）。

## 任务工作目录

每次执行任务时，在用户当前工作目录下创建 `.nds/`：

```
.nds/
├── state.json              # 机器态：任务树/进度/决策（跨会话续传核心）
├── PROGRESS.md             # 人类态：可读进度看板
├── 00-instruction/         # 项目规范
├── 01-requirements/        # 需求文档 + 原型 + 追溯矩阵 + 风险
├── 02-design/              # 设计令牌 + 组件规格 + 高保真稿
├── 03-review/              # 评审报告 + 决策日志
├── 04-tasks/               # WBS + 任务树 + 排期
├── 05-dev/                 # 实现日志 + Bug 修复记录
├── 06-test/                # 测试用例 + 测试结果 + Bug 报告
└── 07-workflow/            # Loop Engineering 循环日志
```

## 跨会话续传

任意阶段都可暂停（直接清空上下文或新开会话）。下次对话时：

1. 输入 `/nzw-resume` —— workflow-skill 读取 `.nds/state.json`，根据 `current_phase` 与 `resume_hint` 接续工作。
2. 或输入 `/nzw-status` 查看进度后，手动触发下一阶段指令。

`state.json` 是唯一真源；`PROGRESS.md` 是其人类可读视图，每次状态变更同步刷新。

## Loop Engineering 思想

workflow-skill 以 **Plan → Act → Observe → Reflect → Iterate** 闭环驱动 7 个阶段：

```
        ┌──────────────────────────────────────┐
        │                                      ▼
Plan → Act → Observe → Reflect → (next phase) → ...
        │                                  ▲
        └──── 失败/bug 反馈 ───────────────┘
```

- 每阶段产出物经质量门禁（quality gate）才进入下一阶段
- 测试阶段反馈的 bug 自动回流到开发阶段
- 人在环（Human-in-the-loop）介入点：评审阶段签字、关键决策记录

## 架构

```
nzw-dev-skills/
├── manifest.json           # 双平台清单
├── install.sh / .ps1       # 一键安装
├── skills/                 # 8 个 skill
│   ├── req-analysis-skill/
│   ├── design-skill/
│   ├── review-skill/
│   ├── task-allocation-skill/
│   ├── dev-skill/
│   ├── test-skill/
│   ├── instruction-skill/
│   └── workflow-skill/
├── commands/               # 10 个斜杠命令
├── codex/                  # Codex 平台 AGENTS.md
└── templates/              # state.schema.json / progress.md.template
```

## 设计原则

1. **精简且精准**：每个 SKILL.md < 300 行，只写必要的「为什么」与「怎么做」。
2. **状态机驱动**：所有阶段产物落入 `.nds/`，`state.json` 是唯一真源。
3. **契约化**：阶段间通过文件契约交接，不依赖对话上下文。
4. **人在环**：关键决策点必须等用户签字，AI 不擅自推进。
5. **可恢复**：任何阶段崩溃都能从 `state.json` 接续。

## 许可

MIT

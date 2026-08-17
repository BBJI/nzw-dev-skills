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
# 先强制 TLS 1.2（GitHub 仅接受 TLS 1.2+，旧 PowerShell 默认 TLS 1.0/1.1 会报
# 「基础连接已经关闭: 接收时发生错误」），再安装
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
& ([scriptblock]::Create((Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.ps1').Content.TrimStart([char]0xFEFF))) -Target all
```

> ⚠ **不要用 `irm ... | iex`**，它在本脚本上会失败，原因有二：
> 1. Windows PowerShell 5.1 的 `Invoke-RestMethod` 会把多行脚本**按行拆成数组**传给 `iex`，逐行执行导致 `<# #>` 块注释失效，注释里的 `.EXAMPLE`/`.\install.ps1` 会被当成命令报「无法识别」。
> 2. 本脚本带 UTF-8 BOM（为磁盘执行时中文不乱码），`iex`/`scriptblock` 收到的字符串不会自动剥 BOM，首行 `?<#` 会被当成命令。
>
> 正解：用 `Invoke-WebRequest ... .Content` 取**单个字符串**，`.TrimStart([char]0xFEFF)` 去掉 BOM，再 `[scriptblock]::Create` 执行（末尾 `-Target` 可传参）。

指定目标平台（改末尾 `-Target`）：

```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
& ([scriptblock]::Create((Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.ps1').Content.TrimStart([char]0xFEFF))) -Target codex
```

> 系统自带 `curl` 或 `wget`、`tar` 即可，无需 git。
>
> **国内网络拉取失败**：`raw.githubusercontent.com` / `codeload.github.com` 可能被重置。
> 走镜像前缀（自举阶段下载 tarball 也会自动走镜像）：
> ```powershell
> [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
> $env:NZW_MIRROR = 'https://ghproxy.net'
> & ([scriptblock]::Create((Invoke-WebRequest -UseBasicParsing 'https://ghproxy.net/https://raw.githubusercontent.com/BBJI/nzw-dev-skills/main/install.ps1').Content.TrimStart([char]0xFEFF))) -Target all
> ```
> 仍失败则改用本地安装（见下）。

## 本地安装（已 clone 仓库）

```bash
./install.sh --all           # macOS / Linux / Git Bash（装 claude-code + codex + zcode）
.\install.ps1 -Target all    # Windows PowerShell
```

支持 `--claude-code` / `--codex` / `--zcode` / `--all`（默认 all）。ZCode 用户可只装 zcode：

```bash
./install.sh --zcode         # macOS / Linux / Git Bash
.\install.ps1 -Target zcode  # Windows PowerShell
```

安装后：
- Claude Code：skills 装入 `~/.claude/skills/`，斜杠命令装入 `~/.claude/commands/`
- Codex：合并为 `~/.codex/AGENTS.md`，skill 文档装入 `~/.codex/skills/`
- ZCode：skills 装入 `~/.agents/skills/`（含 `references/`），斜杠命令装入 `~/.agents/commands/`，schema/模板装入 `~/.agents/nzw-templates/`，触发索引装入 `~/.zcode/AGENTS.md`

## 环境变量覆盖

| 变量 | 作用 | 默认值 |
|---|---|---|
| `NZW_REPO` | GitHub 仓库（远程安装时拉取源） | `BBJI/nzw-dev-skills` |
| `NZW_BRANCH` | 拉取分支 | `main` |
| `NZW_MIRROR` | GitHub 镜像前缀（国内网络加速，自举下载 tarball 时生效） | 空 |
| `NZW_CLAUDE_DIR` | Claude Code 安装目录 | `~/.claude` |
| `NZW_CODEX_DIR` | Codex 安装目录 | `~/.codex` |
| `NZW_AGENTS_DIR` | ZCode skills/commands 安装目录 | `~/.agents` |
| `NZW_ZCODE_DIR` | ZCode 触发索引目录 | `~/.zcode` |

示例：从 fork 安装到自定义目录

```bash
NZW_REPO=myorg/nzw-fork NZW_CLAUDE_DIR=~/my-claude \
  curl -fsSL https://raw.githubusercontent.com/myorg/nzw-fork/main/install.sh | bash
```

## 触发指令

| 指令 | 作用 | 对应 skill |
|---|---|---|
| `/nzw-req <任务描述>` | 需求调研分析 | req-analysis-skill |
| `/nzw-design` | UI/UX 设计规范（视觉实现委托 impeccable，缺失自动安装） | design-skill |
| `/nzw-review` | 三维实现评估 | review-skill |
| `/nzw-task` | 任务拆分与排期 | task-allocation-skill |
| `/nzw-dev [task-id]` | TDD 开发实现 | dev-skill |
| `/nzw-test` | 测试用例与验证 | test-skill |
| `/nzw-instruction` | 生成项目规范 | instruction-skill |
| `/nzw-workflow <任务描述>` | **全流程自主交付** | workflow-skill |
| `/nzw-resume` | 跨会话续传 | 读 `.nds/index.json` 选择需求后接续 |
| `/nzw-status [--req <id>]` | 查看进度 | 无参数看总览，`--req` 看单需求 |
| `/nzw-switch <req-id>` | 切换活跃需求 | 改 `.nds/index.json` 的 `active_req_id` |

Codex 无斜杠命令，用自然语言触发即可（如"启动 nzw workflow 做一个 XXX"）。

## 任务工作目录

每次执行任务时，在用户当前工作目录下创建 `.nds/`。**v1.1 起按需求隔离**：顶层只放索引与项目级共享产物，每需求独占一个 `req-NNN/` 子树。

```
.nds/
├── index.json              # 顶层索引：所有需求 + active_req_id 指针
├── PROGRESS.md             # 顶层总览看板（多需求）
├── 00-instruction/         # 项目级规范（跨需求共享，不进 req 子目录）
└── req-001/                # 需求 001 独立子树
    ├── state.json          # 机器态：任务树/进度/决策/events[]事件日志/bug_reflow（跨会话续传核心）
    ├── PROGRESS.md         # 人类态：单需求可读看板（由 events 渲染）
    ├── 01-requirements/    # PRD + 双稿原型 + story-map + 追溯矩阵 + 风险 + feature-checklist.json + consistency-check
    ├── 02-design/          # 设计令牌(W3C DTCG) + 组件规格 + patterns/ + IA + 高保真稿
    ├── 03-review/          # 评审报告 + 决策日志 + evaluation.json + sign-off
    ├── 04-tasks/           # WBS + 任务树(METR≤1h) + 排期 + sprint-contracts/
    ├── 05-dev/             # 实现日志 + Bug 修复记录 + commits
    ├── 06-test/            # 测试用例 + 结果 + Bug 报告(ISO 29119-3) + 回归集 + exploratory-sessions + spec-drift-check
    └── 07-workflow/        # Loop Engineering 循环日志
```

- 新需求由 `/nzw-req <任务>` 或 `/nzw-workflow <任务> --new` 创建，自动分配 `req-NNN`（三位补零）并设为 `active_req_id`
- 切换活跃需求：`/nzw-switch <req-id>`
- 大部分命令支持 `--req <id>` 显式指定，未指定时作用于 `active_req_id`

### 老项目迁移（v1.0 → v1.1）

检测到 `.nds/state.json` 存在但 `.nds/index.json` 不存在时，自动迁移：

1. 把现有 `.nds/01-requirements/` … `.nds/07-workflow/` 移到 `.nds/req-001/` 下
2. 原 `state.json` 移到 `.nds/req-001/state.json`，`project.req_id` 设为 `"req-001"`，`version` 升到 `"1.1"`
3. 生成 `.nds/index.json`，`active_req_id = "req-001"`
4. `00-instruction/` 若存在则保留在顶层（项目级共享）

### v1.1 → v1.2 升级（additive，无需手动迁移）

v1.2 完全兼容 v1.1，旧 `.nds/` 无需手动改动。首次加载旧 `state.json`（`version:"1.1"`）时自动补默认空值并升级为 `"1.2"`：

- `events: []`（只追加事件日志，managed-agents 模式）
- `feedback_loop.bug_reflow: []`（缺陷回流事件流）
- `project.feature_checklist_ref`（防假绿载体契约路径）
- `task_tree.tasks[].lock`（任务认领锁）
- `index.json` 的 `version` 接受 `"1.1"` / `"1.2"`

v1.2 主要新增（详见各 SKILL.md）：
- **req-analysis**：story-map.md（walking skeleton + MVP 切片）、feature-checklist.json（机器可读，初始全 fail）、consistency-check.md（矛盾/缺口自动检查）、risks 补 Contingency/Trigger、追溯矩阵补 origin/验证状态
- **design**：patterns/（模式库）、information-architecture.md、组件 States 强制 loading/empty/error/disabled、令牌 `$type` 分组继承 + `$extensions`、标注 W3C DTCG 2025.10 Stable
- **review**：每条检查给"怎么查"客观信号、DoR 准入门、三维 sign-off 各自结果、evaluation.json 硬阈值评分（怀疑式评估器）
- **task-allocation**：METR ≤1h 任务红线、单体任务预言机分解、git 文件锁、Sprint Contract
- **dev**：测试即不可变契约（feature-checklist + 冻结测试 + 只改 passes 字段防假绿）、AI-TDD 失败模式、快采样回归、一次一 feature
- **test**：exploratory-sessions.md（charter + SBTM）、ISO/IEC/IEEE 29119-3:2013、Gherkin 反模式、e2e（web-gui-tester）、属性测试、spec 漂移检测（converge）
- **instruction**：2026 工具全景（Cursor MDC / Codex AGENTS.md 合并链 / Copilot AGENTS.md 原生 / Windsurf）、steering 文件、规范即转移条件
- **workflow**：会话启动协议（resume 强制例程）、events[] 事件日志、bug_reflow 事件流、受约束子 agent、harness 压测注
- **写法**：全部 skill 按 skill-creator 原则打磨——DRY（impeccable 抽到 `references/`）、渐进式披露、MUST 改解释 why、description pushy 化

## 跨会话续传

任意阶段都可暂停（直接清空上下文或新开会话）。下次对话时：

1. 输入 `/nzw-resume` —— 列出所有需求供选择，选定后读 `.nds/<req-id>/state.json`，根据 `current_phase` 与 `resume_hint` 接续。
2. 或输入 `/nzw-status` 看总览，`/nzw-status --req <id>` 看单需求后手动触发下一阶段指令。

`index.json` 是需求级索引，每需求的 `state.json` 是其唯一真源；`PROGRESS.md` 是人类可读视图，每次状态变更同步刷新。

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
│   │   ├── SKILL.md
│   │   └── references/impeccable-wireframe.md   # 渐进式披露：impeccable 集成指南
│   ├── design-skill/
│   │   ├── SKILL.md
│   │   └── references/impeccable-design.md
│   ├── review-skill/
│   ├── task-allocation-skill/
│   ├── dev-skill/
│   ├── test-skill/
│   ├── instruction-skill/
│   └── workflow-skill/
├── commands/               # 11 个斜杠命令（含 nzw-switch）
├── codex/                  # Codex 平台 AGENTS.md
├── zcode/                  # ZCode 平台 AGENTS.md（触发索引）
└── templates/              # state.schema.json / index.schema.json / handoff.contract.json / progress*.md.template
```

## 设计原则

1. **精简且精准 + 渐进式披露**：SKILL.md body < 500 行只留工作流骨架与「为什么」，大段细节（impeccable 集成指南、模板长文）拆到 `references/` 按需加载；description 是触发信号，pushy 化覆盖同义/隐式场景。
2. **状态机驱动 + 事件日志**：所有阶段产物落入 `.nds/<req-id>/`，`state.json`（含 `events[]` 只追加事件日志）是唯一真源；顶层 `index.json` 管理多需求。
3. **契约化**：阶段间通过文件契约 + Sprint Contract 交接，不依赖对话上下文。
4. **测试即 spec**：feature-checklist.json 是 dev/test 共享的防假绿契约；测试冻结，只改 passes 字段。
5. **人在环**：关键决策点（review sign-off）必须等用户签字，AI 不擅自推进。
6. **客观信号**：门禁用真实测试/lint/编译输出，不依赖自评。
7. **可恢复**：任何阶段崩溃走会话启动协议从 `events[]` + checkpoint 接续。

## 许可

MIT

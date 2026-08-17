---
name: instruction-skill
description: 项目规范文档生成技能，为主流 AI 编程工具（Claude Code、OpenAI Codex、Cursor、GitHub Copilot、Windsurf 等）生成项目级规范文件（steering 文件），跨 CLI/Web/IDE 一致。支持从已有项目分析生成规范，或从新项目交付结果生成规范。当用户提到以下任一场景时务必使用：生成规范、项目规范、CLAUDE.md、AGENTS.md、cursorrules、copilot-instructions、windsurfrules、AI 编程规范、项目指令、代码规范文档、AI 上下文文件、steering 文件，或需要为 AI 编程工具创建项目上下文文件。即使用户只说"写个规范"或"生成 CLAUDE.md"也应触发。在 workflow-skill 全流程中，已有项目在流程开始前生成规范，新项目在流程完成后生成规范。
metadata:
  type: nzw-dev-skills
  phase: instruction
  trigger: /nzw-instruction
---

# 项目规范生成技能（instruction-skill）

为 AI 编程工具生成项目级规范文件——**Context Engineering > Prompt Engineering**，规范是给 AI 的"项目宪法"与跨工具的 steering 文件，决定 AI 在该项目中的行为边界。

主导思想：**规范即契约 + 规范即状态机的转移条件**。规范不仅是 AI 的输入，也是人机协作的共识；每个质量门禁失败都能回写为规范补丁，让规范随项目演化（agentic memory 的持久载体）。

## 何时触发

- 用户输入 `/nzw-instruction`
- 自然语言提到"生成规范/CLAUDE.md/AGENTS.md/cursorrules"等
- workflow-skill 在流程开始前（已有项目）或流程完成后（新项目）调用

## 工作目录与状态

instruction-skill 是**项目级**规范生成器，产出**不进 req 子目录**，统一落到顶层 `.nds/00-instruction/`，跨需求共享。

产出：
- `CLAUDE.md` — Claude Code 项目规范
- `AGENTS.md` — OpenAI Codex 项目规范（也是 Copilot/Windsurf 的通用入口）
- `.cursor/rules/*.mdc` — Cursor Project Rules
- `.github/copilot-instructions.md` — GitHub Copilot 仓库级指令
- `.windsurfrules` — Windsurf 项目规则
- `INSTRUCTION-SUMMARY.md` — 多工具规范汇总与差异说明（单一事实源）

入口动作：
1. 读 `.nds/index.json` 判断项目状态（多 req 场景综合所有 req 产出提炼跨需求共性）。
2. 在相关 req 的 state.json 同步 `phases.instruction.status = "in_progress"`。
3. 生成后写入 `INSTRUCTION-SUMMARY.md`，建议用户把规范文件提交 git。

## 主导思想

- **最小必要信息**：AI 能读源码，规范只承载"代码无法表达"的意图、约束与历史决策
- **工具无关核心 + 工具特定封装**：一份核心约定，多工具自动派生
- **可执行可验证**：写命令本身（`pnpm test`），不写"请运行测试"
- **禁止项显式**：负向指令比正向指令更有效
- **steering 文件**：规范作为跨 CLI/Web/IDE 一致的导航文件（Kiro 模式），任一工具进入项目都读到同一套约束
- **规范即转移条件**：每个质量门禁失败回写为规范补丁——"AI 犯错→规范补漏"反馈环

## 执行流程

### 1. 判断项目类型

- **已有项目**：扫描代码库（package.json / pyproject.toml / Cargo.toml / go.mod / pom.xml / .gitignore / CI / ESLint / .editorconfig 等），抽取隐性约定
- **新项目**：基于 `.nds/<req-id>/01-requirements/` + `02-design/` + `04-tasks/` + `05-dev/` 总结已交付物约定（多 req 场景综合提炼共性）

### 2. 核心约定提炼（工具无关，七段）

```markdown
# {{项目名}} AI 编程规范
## 1. 项目概述（1-2 句话）
## 2. 技术栈与版本（语言/框架/包管理器/运行时/关键依赖最低版本）
## 3. 目录结构与关键模块职责（顶层目录说明 + 关键模块边界）
## 4. 构建/测试/Lint/格式化命令（可直接复制的真实命令 + 开发启动 + 生产构建）
## 5. 编码约定（命名/错误处理/导入顺序/注释策略：默认不写，WHY 例外）
## 6. 禁忌清单 Do NOT（不要改 X 目录/不引入新依赖/不用 any/不跳过测试）
## 7. 工作流约定（分支命名 feature/T001-描述 / Commit Conventional Commits 关联 Task ID / PR 流程）
```

> 为什么只放"代码看不出来的东西"：AI 能读源码，复制 README 内容到规范是冗余且会漂移。规范的价值在"意图、约束、历史决策"——这些代码不表达。写命令本身而非"请运行测试"，因为可执行可验证。

### 3. 派生各工具规范（2026 全景）

#### CLAUDE.md（Claude Code）
- 位置：项目根；子目录可嵌套，进入子目录自动加载
- 用 `@path/to/file.md` 导入语法引用其他文件，避免内容膨胀
- 区分"项目规范"（入仓）与"个人偏好"（`~/.claude/CLAUDE.md`，不入仓）
- 简洁优于完整：给"好/坏"代码片段示例，而非描述

#### AGENTS.md（OpenAI Codex，亦是 Copilot/Windsurf 通用入口）
- 发现链：全局 `~/.codex/AGENTS.md` → 项目根 → 子目录逐层向下，**越靠近 cwd 越后出现因此覆盖前者**；`AGENTS.override.md` 优先于 `AGENTS.md`
- 默认限额 `project_doc_max_bytes = 32 KiB`，超了停——规范要精简
- 内容同 CLAUDE.md，但 Codex 不支持 `@import`，需内联或显式引用路径
- Codex `/init` 可自动生成初版 AGENTS.md；`/permissions` 分级授权；subagents 做受约束子任务

#### .cursor/rules/*.mdc（Cursor Project Rules）
YAML frontmatter + 内容，frontmatter 三字段决定触发（四选一）：

```yaml
---
description: 认证模块开发规则
globs: ["src/auth/**/*.ts"]
alwaysApply: false
---
```

`alwaysApply:false` + globs 按需触发节省 token。一个领域一个 `.mdc`。每条 < 500 行，别抄整本 style guide（交给 linter），别罗列每个命令（AI 认识 npm/git）。

#### .github/copilot-instructions.md（GitHub Copilot）
仓库级单文件，简洁。路径级用 `.github/instructions/NAME.instructions.md` + frontmatter `applyTo: "src/**/*.py"`。Copilot 已原生支持 AGENTS.md 标准。

#### .windsurfrules（Windsurf，2026 被 Cognition/Devin 收购）
项目根纯文本规则，类 `.cursorrules`。触发类型 Always / Auto（文件模式/关键词）/ Manual。

### 4. 演进与维护

- 把规范当代码：PR 评审、变更日志
- **规范即转移条件反馈环**：每次 AI 行为偏差或门禁失败 → 立即更新规范补丁（"AI 犯错→规范补漏"）。例如 dev-skill 三道门禁失败，就把"提交前跑 lint/typecheck/test"写入规范 §4。
- 工具无关核心放 `INSTRUCTION-SUMMARY.md`，派生文件标注"如需修改请改核心，再重新生成"

## 完成判定

- 七段核心约定齐全
- 各工具规范文件按官方路径生成，符合 2026 规范（Cursor MDC / Codex AGENTS.md 合并链 / Copilot AGENTS.md 原生 / Windsurf .windsurfrules）
- INSTRUCTION-SUMMARY.md 含差异说明与维护策略
- 建议用户 git 提交
- 相关 req 的 state.json：`phases.instruction.status = "done"`，`events[]` append phase_done

## 与上下游交接

- 已有项目场景：作为全流程**前置**，规范指导后续 TDD/评审/开发（spec-kit constitution 护栏模式）
- 新项目场景：作为全流程**收尾**，把交付过程沉淀的约定固化为规范
- 规范是 Loop Engineering 状态机的转移条件——门禁失败时回写为规范补丁，规范随项目演化

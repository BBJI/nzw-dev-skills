---
name: instruction-skill
description: 项目规范文档生成技能，为主流 AI 编程工具（Claude Code、OpenAI Codex、Cursor、GitHub Copilot、Windsurf 等）生成项目级规范文件。支持从已有项目分析生成规范，或从新项目交付结果生成规范。当用户提到以下任何场景时务必使用此技能：生成规范、项目规范、CLAUDE.md、AGENTS.md、cursorrules、copilot-instructions、AI 编程规范、项目指令、代码规范文档、AI 上下文文件、项目配置文件，或需要为 AI 编程工具创建项目上下文文件。即使用户只说了"写个规范"或"生成 CLAUDE.md"，也应触发此技能。在 workflow-skill 全流程交付中，已有项目在流程开始前生成规范，新项目在流程完成后生成规范。
metadata:
  type: nzw-dev-skills
  phase: instruction
  trigger: /nzw-instruction
---

# 项目规范生成技能（instruction-skill）

为 AI 编程工具生成项目级规范文件——**Context Engineering > Prompt Engineering**，规范是给 AI 的"项目宪法"，决定 AI 在该项目中的行为边界。

主导思想：**规范即契约**。规范不仅是 AI 的输入，也是人机协作的共识——评审、测试、任务拆分都以此为准绳。

## 何时触发

- 用户输入 `/nzw-instruction`
- 自然语言提到"生成规范/CLAUDE.md/AGENTS.md/cursorrules"等
- workflow-skill 在流程开始前（已有项目）或流程完成后（新项目）调用

## 工作目录与状态

**路径约定（v1.1）**：instruction-skill 是**项目级**规范生成器，产出**不进 req 子目录**，统一落到顶层 `.nds/00-instruction/`，跨需求共享。需求级状态隔离见顶层 `.nds/index.json`。

产出落到 `.nds/00-instruction/`（顶层，非 req 子目录）：
- `CLAUDE.md` — Claude Code 项目规范
- `AGENTS.md` — OpenAI Codex 项目规范
- `.cursor/rules/*.mdc` — Cursor MDC 格式规则
- `.github/copilot-instructions.md` — GitHub Copilot
- `.windsurfrules` — Windsurf
- `INSTRUCTION-SUMMARY.md` — 多工具规范汇总与差异说明

入口动作：
1. 读取 `.nds/index.json` 判断项目状态（若有多个 req，综合所有 req 的产出提炼跨需求共性规范）
2. 在所有 req 的 state.json 中同步 `phases.instruction.status = "in_progress"`；或仅作用于 `active_req_id`（用户通过 `--req` 显式指定时）
3. 生成后写入 `INSTRUCTION-SUMMARY.md` 并建议用户把规范文件提交到 git

## 主导思想

- **最小必要信息**：Claude 能读源码，规范只承载"代码无法表达"的意图、约束与历史决策
- **工具无关核心 + 工具特定封装**：一份核心约定，多工具自动派生
- **可执行可验证**：写命令本身（`pnpm test`），不写"请运行测试"
- **禁止项显式**：负向指令比正向指令更有效
- **规范即状态机的转移条件**：每个质量门禁失败都能回写为规范补丁

## 执行流程

### 1. 判断项目类型

- **已有项目**：扫描代码库（package.json / pyproject.toml / Cargo.toml / go.mod / pom.xml / .gitignore / CI 配置 / ESLint / .editorconfig 等），抽取隐性约定
- **新项目**：基于 `.nds/<req-id>/01-requirements/` + `.nds/<req-id>/02-design/` + `.nds/<req-id>/04-tasks/` + `.nds/<req-id>/05-dev/` 总结已交付物的约定（多 req 场景下综合所有 req 提炼共性）

### 2. 核心约定提炼（工具无关）

七段标准结构：

```markdown
# {{项目名}} AI 编程规范

## 1. 项目概述（1-2 句话）

## 2. 技术栈与版本
- 语言 / 框架 / 包管理器 / 运行时版本
- 关键依赖与最低版本要求

## 3. 目录结构与关键模块职责
- 顶层目录说明
- 关键模块边界（哪些代码该在哪）

## 4. 构建/测试/Lint/格式化命令
- 可直接复制粘贴的真实命令
- 开发环境启动命令
- 生产构建命令

## 5. 编码约定
- 命名规范（变量/函数/类/文件）
- 错误处理模式
- 导入顺序
- 注释策略（默认不写，WHY 例外）

## 6. 禁忌清单（Do NOT）
- 不要修改 X 目录
- 不要引入新依赖
- 不要用 any
- 不要跳过测试

## 7. 工作流约定
- 分支命名：feature/T001-描述
- Commit 格式：Conventional Commits，关联 Task ID
- PR 流程
```

### 3. 派生各工具规范

#### CLAUDE.md（Claude Code）

- 位置：项目根
- 用 `@path/to/file.md` 导入语法引用其他文件，避免内容膨胀
- 子目录可嵌套 `CLAUDE.md`，进入子目录自动加载
- 区分"项目规范"（入仓）与"个人偏好"（`~/.claude/CLAUDE.md`，不入仓）
- 简洁优于完整：Claude 可读源码，只放"读代码看不出来的东西"
- 用示例展示而非描述：给"好/坏"代码片段

#### AGENTS.md（OpenAI Codex）

- 位置：项目根，父目录递归发现
- 内容同 CLAUDE.md，但 Codex 不支持 `@import`，需内联或显式引用路径
- 强调"可执行命令"

#### .cursor/rules/*.mdc（Cursor 2025+）

YAML frontmatter + 内容：

```yaml
---
description: 认证模块开发规则
globs: ["src/auth/**/*.ts"]
alwaysApply: false
---
```

一个领域一个 `.mdc` 文件。`alwaysApply: false` 按需触发节省 token。

#### .github/copilot-instructions.md

GitHub Copilot 仓库级指令，简洁，单文件。

#### .windsurfrules

项目根单文件，类似 .cursorrules 旧格式。

### 4. 演进与维护

- 把规范当代码对待：PR 评审、变更日志
- 每次 AI 行为偏差 → 立即更新规范（"AI 犯错→规范补漏"反馈环）
- 工具无关核心放在 `INSTRUCTION-SUMMARY.md`，派生文件标注"如需修改请改核心，再重新生成"

## 必须遵守的规则

1. **文件位置与命名固定**：每工具规范严格按官方约定路径。
2. **内容必须可执行可验证**：写命令本身，不写"请运行测试"。
3. **禁止项必须显式**：负向指令比正向更有效。
4. **版本化提交**：规范文件必须纳入 git，全团队共享同一份 AI 上下文。
5. **单一事实源**：不要在 CLAUDE.md 中复制 README 内容，用 `@import` 或路径引用。
6. **层级化而非平铺**：根目录放全局规范，子包/模块放局部规范，Monorepo 必须分层。
7. **工具无关核心 + 工具特定封装**：先写核心，再派生。

## 完成判定

- 七段核心约定齐全
- 各工具规范文件按官方路径生成
- INSTRUCTION-SUMMARY.md 含差异说明与维护策略
- 建议用户 git 提交
- state.json 中 `phases.instruction.status = "done"`

## 与上下游交接

- 已有项目场景：作为全流程**前置**，规范指导后续 TDD/评审/开发
- 新项目场景：作为全流程**收尾**，把交付过程中沉淀的约定固化为规范
- 规范是 Loop Engineering 状态机的转移条件——门禁失败时回写为规范补丁

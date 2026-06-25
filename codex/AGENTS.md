# AGENTS.md — nzw-dev-skills for OpenAI Codex

> 这是 **nzw-dev-skills** 技能包在 Codex 平台的入口。Codex 没有原生 skill 机制，本文件作为统一索引，让 Codex 通过自然语言识别触发对应技能。
> 各技能详细说明位于 `~/.codex/skills/<skill-name>/SKILL.md`，按需读取。

## 项目背景

nzw-dev-skills 是一套 AI 自主全流程交付技能包，以 **Loop Engineering** 思想串联软件开发七阶段：

```
需求 → 设计 → 评审 → 任务 → 开发 → 测试 → 规范
```

所有任务产出落到当前工作目录的 `.nds/` 下。**v1.1 起按需求隔离**：顶层 `.nds/index.json` 管理所有需求与 `active_req_id` 指针，每需求独占 `.nds/req-NNN/` 子树（自带 `state.json` + `PROGRESS.md` + 七阶段目录），支持跨会话续传。项目级规范（instruction-skill 产出）落到顶层 `.nds/00-instruction/`，跨需求共享。

## 触发指南

当用户输入符合下列任一模式时，请读取对应 skill 的 SKILL.md 并按其指引执行。

| 触发关键词 | 对应 skill | SKILL.md 路径 |
|---|---|---|
| 需求分析 / PRD / 需求文档 / 梳理需求 | req-analysis-skill | ~/.codex/skills/req-analysis-skill/SKILL.md |
| UI 设计 / UX 设计 / 设计规范 / 设计令牌 | design-skill | ~/.codex/skills/design-skill/SKILL.md |
| 评审 / 可行性 / 准入 / 三维评审 | review-skill | ~/.codex/skills/review-skill/SKILL.md |
| 任务拆分 / WBS / 排期 / 看板 | task-allocation-skill | ~/.codex/skills/task-allocation-skill/SKILL.md |
| 开发 / 实现 / 写代码 / 修 bug / TDD | dev-skill | ~/.codex/skills/dev-skill/SKILL.md |
| 测试 / 验收 / 缺陷 / 回归 | test-skill | ~/.codex/skills/test-skill/SKILL.md |
| 生成规范 / CLAUDE.md / AGENTS.md / cursorrules | instruction-skill | ~/.codex/skills/instruction-skill/SKILL.md |
| 全流程 / 端到端 / 做个 XXX / 自主交付 | workflow-skill | ~/.codex/skills/workflow-skill/SKILL.md |
| 续传 / 接着上次 / resume | 读取 .nds/state.json | 见下方"续传"段落 |

## 各 skill 一句话概要

- **req-analysis-skill**：把模糊想法转化为 PRD + 原型 HTML + 追溯矩阵 + 风险登记表。产出到 `.nds/<req-id>/01-requirements/`。创建新需求时分配 `req-NNN` 并设为 `active_req_id`。
- **design-skill**：基于需求产出 W3C 标准设计令牌、组件规格、用户流程、高保真 HTML 稿。产出到 `.nds/<req-id>/02-design/`。视觉实现层委托 impeccable 引擎（缺失时 `npx impeccable install` 自动安装）：已有项目结合当前页面风格保持一致（identity-preservation），新项目从零设计。
- **review-skill**：从需求完整性 / UX 可实现性 / 技术可行性三维度评审，产出 Issue/Risk/Decision + 准入签字。产出到 `.nds/<req-id>/03-review/`。
- **task-allocation-skill**：分解为 INVEST 合格、DAG 依赖、四要素契约的任务树。产出到 `.nds/<req-id>/04-tasks/`。
- **dev-skill**：TDD 红-绿-重构循环实现任务，Conventional Commits 提交。产出到 `.nds/<req-id>/05-dev/`。
- **test-skill**：测试用例设计（等价类/边界值/决策表/BDD Gherkin）+ 执行 + 缺陷报告 + 回归集。产出到 `.nds/<req-id>/06-test/`。
- **instruction-skill**：为 Claude Code / Codex / Cursor / Copilot / Windsurf 生成项目级规范文件。产出到顶层 `.nds/00-instruction/`（**不进 req 子目录**，跨需求共享）。
- **workflow-skill**：编排者，以 Plan→Act→Observe→Reflect→Iterate 闭环串联上述 7 阶段。产出到 `.nds/<req-id>/07-workflow/`。

## 执行约定

无论触发哪个 skill，都必须遵守：

1. **状态机驱动**：执行前读 `.nds/index.json` 确定 `active_req_id`（或用户显式指定的 `--req`），再读 `.nds/<req-id>/state.json`；执行后更新 `current_phase` / `phases.<phase>.status` / `resume_hint`，同步刷新 `.nds/<req-id>/PROGRESS.md`、顶层 `.nds/PROGRESS.md` 与 `index.json` 中该 req 的摘要。
2. **目录契约**：各 skill 产出严格落入 `.nds/<req-id>/<编号-阶段名>/` 目录，不跨界；instruction-skill 例外，落到顶层 `.nds/00-instruction/`。
3. **JSON+Markdown 双层**：机器态用 `index.json` + 每 req 的 `state.json`，人类态用顶层与各 req 的 `PROGRESS.md`，三者保持同步。
4. **人在环**：review 阶段必须等用户在 `.nds/<req-id>/03-review/sign-off.md` 签字才能进入开发。
5. **客观信号**：test/dev 阶段的 Observe 必须用真实测试/lint/编译输出，不依赖自评。
6. **跨会话续传**：任何阶段都可暂停，下次对话读 `index.json` 选需求后读对应 `state.json` 接续。
7. **需求隔离**：同一项目可并发跑多个需求，互不污染；切换用 `--req <id>` 或 `/nzw-switch`。

## 续传机制

当用户说"续传 / 接着上次 / resume"时：

1. 读取 `.nds/index.json`，列出所有需求（id / name / current_phase / open_blockers / 最近更新）
2. 询问用户要续传哪个需求（默认 `active_req_id`）
3. 读取 `.nds/<req-id>/state.json`，报告：需求名、目标、当前阶段、各阶段状态、未完成任务、待修复 bug、`resume_hint`
4. 询问：继续当前阶段 / 跳转指定阶段 / 重做某阶段
5. 用户确认后触发对应 skill

## 全流程触发示例

用户："用 nzw workflow 做一个待办清单应用"

执行步骤：
1. 读取或初始化 `.nds/index.json`；新任务分配 `req-NNN` 并设为 `active_req_id`，创建 `.nds/req-NNN/` 子目录与 `state.json`
2. 调 instruction-skill（若已有代码则前置，否则跳过到末尾）
3. 调 req-analysis-skill → 门禁检查 → 通过则进下一阶段
4. 调 design-skill → 门禁
5. 调 review-skill → 等用户签字
6. 调 task-allocation-skill → 门禁
7. 调 dev-skill 按 task-tree 顺序执行
8. 调 test-skill → bug 回流 dev 循环
9. 全部通过后调 instruction-skill 生成规范（新项目，落到 `.nds/00-instruction/`）
10. 标记 `current_phase = "done"`，向用户报告交付；同步回写 `index.json`

## 安装与卸载

- 安装：运行 `install.sh --codex` 或 `install.ps1 -Target codex`
- 卸载：删除 `~/.codex/AGENTS.md` 与 `~/.codex/skills/` 即可
- 更新：重新运行安装脚本，会自动备份原 AGENTS.md

## 维护

- 源仓库：`D:\project\coral\personal\nzw-dev-skills`
- 修改 skill 内容：编辑 `skills/<skill-name>/SKILL.md` 后重新运行安装脚本
- 修改触发关键词：编辑本文件 `## 触发指南` 段落

---

_version: 1.1.0_

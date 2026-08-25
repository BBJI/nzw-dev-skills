# AGENTS.md — nzw-dev-skills for ZCode

> 这是 **nzw-dev-skills** 技能包在 ZCode 平台的用户级全局指令。ZCode 原生支持 skill 自动发现（skills 已安装于 `~/.agents/skills/`，斜杠命令安装于 `~/.agents/commands/`）；本文件作为统一触发索引与执行约定，让 ZCode 在任意工作区都能正确识别并按规范触发对应技能。
> 各技能详细说明位于 `~/.agents/skills/<skill-name>/SKILL.md`，由 ZCode skill 机制按需加载；JSON schema 与进度模板位于 `~/.agents/nzw-templates/`。

## 项目背景

nzw-dev-skills 是一套 AI 自主全流程交付技能包，以 **Loop Engineering** 思想串联软件开发七阶段：

```
需求 → 设计 → 评审 → 任务 → 开发 → 测试 → 规范
```

所有任务产出落到当前工作目录的 `.nds/` 下。**v1.1 起按需求隔离**：顶层 `.nds/index.json` 管理所有需求与 `active_req_id` 指针，每需求独占 `.nds/req-NNN/` 子树（自带 `state.json` + `PROGRESS.md` + 七阶段目录），支持跨会话续传。项目级规范（instruction-skill 产出）落到顶层 `.nds/00-instruction/`，跨需求共享。**v1.2 升级**：state.json 增加 `events[]` 只追加事件日志、`bug_reflow[]` 缺陷回流事件流、`feature_checklist_ref` 防假绿载体契约、task `lock` 认领锁；引入会话启动协议、Sprint Contract、METR ≤1h 任务红线、spec 漂移检测。v1.2 兼容 v1.1 旧 `.nds/`（首次加载自动升级）。

## 触发指南

当用户输入符合下列任一模式时，请触发对应 skill（通过 ZCode skill 机制加载其 SKILL.md 并按其指引执行）。也可直接使用对应斜杠命令。

| 触发关键词 | 对应 skill | 斜杠命令 | SKILL.md 路径 |
|---|---|---|---|
| 需求分析 / PRD / 需求文档 / 梳理需求 | req-analysis-skill | `/nzw-req` | ~/.agents/skills/req-analysis-skill/SKILL.md |
| UI 设计 / UX 设计 / 设计规范 / 设计令牌 | design-skill | `/nzw-design` | ~/.agents/skills/design-skill/SKILL.md |
| 评审 / 可行性 / 准入 / 三维评审 | review-skill | `/nzw-review` | ~/.agents/skills/review-skill/SKILL.md |
| 任务拆分 / WBS / 排期 / 看板 | task-allocation-skill | `/nzw-task` | ~/.agents/skills/task-allocation-skill/SKILL.md |
| 开发 / 实现 / 写代码 / 修 bug / TDD | dev-skill | `/nzw-dev` | ~/.agents/skills/dev-skill/SKILL.md |
| 测试 / 验收 / 缺陷 / 回归 | test-skill | `/nzw-test` | ~/.agents/skills/test-skill/SKILL.md |
| 生成规范 / CLAUDE.md / AGENTS.md / cursorrules | instruction-skill | `/nzw-instruction` | ~/.agents/skills/instruction-skill/SKILL.md |
| 全流程 / 端到端 / 做个 XXX / 自主交付 | workflow-skill | `/nzw-workflow` | ~/.agents/skills/workflow-skill/SKILL.md |
| 续传 / 接着上次 / resume | 读取 .nds/index.json + state.json | `/nzw-resume` | 见下方"续传"段落 |
| 看进度 / 状态 | 读取 .nds/PROGRESS.md | `/nzw-status` | — |
| 切换活跃需求 | 修改 .nds/index.json | `/nzw-switch` | — |

## 各 skill 一句话概要

- **req-analysis-skill**：把模糊想法转化为 PRD + 双稿原型（已有项目先扫源码提取设计令牌，风格与项目实际一致）+ 原型截图 + 飞书可导入 docx + 故事地图 + 追溯矩阵 + 风险登记 + 机器可读 feature-checklist + 一致性检查。产出到 `.nds/<req-id>/01-requirements/`。创建新需求时分配 `req-NNN` 并设为 `active_req_id`。
- **design-skill**：基于需求产出 W3C DTCG（2025.10 Stable）三层设计令牌、组件规格、模式库、信息架构、用户流程、高保真 HTML 稿。产出到 `.nds/<req-id>/02-design/`。视觉实现层委托 impeccable 引擎（缺失时 `npx impeccable install` 自动安装）：已有项目结合当前页面风格保持一致（identity-preservation），新项目从零设计。
- **review-skill**：独立怀疑式评估器，从需求完整性 / UX 可实现性 / 技术可行性三维度评审，产出 Issue/Risk/Decision + evaluation.json 硬阈值评分 + 准入签字。产出到 `.nds/<req-id>/03-review/`。
- **task-allocation-skill**：分解为 INVEST 合格、DAG 依赖、四要素契约的任务树，绑定 METR ≤1h 红线，单体任务走预言机分解，critical path 配 Sprint Contract。产出到 `.nds/<req-id>/04-tasks/`。
- **dev-skill**：TDD 红-绿-重构循环实现任务，测试即不可变契约（feature-checklist.json + 冻结测试 + 只改 passes 字段防假绿），Conventional Commits 提交。产出到 `.nds/<req-id>/05-dev/`。
- **test-skill**：独立怀疑式评估器，测试用例设计（等价类/边界值/决策表/BDD Gherkin/探索性 charter/属性测试）+ e2e + 执行 + ISO/IEC/IEEE 29119-3 缺陷报告 + spec 漂移检测 + 回归集。产出到 `.nds/<req-id>/06-test/`。
- **instruction-skill**：为 Claude Code / Codex / Cursor / Copilot / Windsurf 生成项目级 steering 规范文件。产出到顶层 `.nds/00-instruction/`（**不进 req 子目录**，跨需求共享）。
- **workflow-skill**：编排者，以 Plan→Act→Observe→Reflect→Iterate 闭环串联上述 7 阶段，会话启动协议 + events[] 事件日志 + bug_reflow 缺陷回流。产出到 `.nds/<req-id>/07-workflow/`。

## 执行约定

无论触发哪个 skill，都必须遵守：

1. **状态机驱动**：执行前读 `.nds/index.json` 确定 `active_req_id`（或用户显式指定的 `--req`），再读 `.nds/<req-id>/state.json`；执行后更新 `current_phase` / `phases.<phase>.status` / `resume_hint`，**向 `events[]` append 一条事件**，同步刷新 `.nds/<req-id>/PROGRESS.md`、顶层 `.nds/PROGRESS.md` 与 `index.json` 中该 req 的摘要。
2. **目录契约**：各 skill 产出严格落入 `.nds/<req-id>/<编号-阶段名>/` 目录，不跨界；instruction-skill 例外，落到顶层 `.nds/00-instruction/`。
3. **JSON+Markdown 双层**：机器态用 `index.json` + 每 req 的 `state.json`（schema 见 `~/.agents/nzw-templates/index.schema.json` 与 `state.schema.json`，含 `events[]` 事件日志），人类态用顶层与各 req 的 `PROGRESS.md`（按 `~/.agents/nzw-templates/progress*.md.template` 渲染，由事件日志渲染），三者保持同步。
4. **人在环**：review 阶段必须等用户在 `.nds/<req-id>/03-review/sign-off.md` 签字才能进入开发（唯一强制人工卡点）。
5. **客观信号**：test/dev 阶段的 Observe 必须用真实测试/lint/编译输出，不依赖自评。
6. **跨会话续传**：任何阶段都可暂停，下次对话走「会话启动协议」接续。
7. **需求隔离**：同一项目可并发跑多个需求，互不污染；切换用 `--req <id>` 或 `/nzw-switch`。

## 续传机制（会话启动协议）

当用户说"续传 / 接着上次 / resume"时，执行固定启动例程（修"上次留破环境"）：

1. 读取 `.nds/index.json`，列出所有需求（id / name / current_phase / open_blockers / 最近更新），询问续传哪个（默认 `active_req_id`）
2. 读取 `.nds/<req-id>/state.json`，**重放 `events[]` 最近 5 条**快速恢复上下文，报告：需求名、目标、当前阶段、各阶段状态、未完成任务、待修复 bug（`open_bugs` 与 `bug_reflow[]`）、`resume_hint`
3. **环境健康检查**：`git status` 看破改动；跑 `init.sh`/冒烟测试确认环境可运行；破则用 `git` 回退到最近 checkpoint
4. 询问：继续当前阶段 / 跳转指定阶段 / 重做某阶段
5. 用户确认后触发对应 skill

## 全流程触发示例

用户："用 nzw workflow 做一个待办清单应用"

执行步骤：
1. 读取或初始化 `.nds/index.json`；新任务分配 `req-NNN` 并设为 `active_req_id`，创建 `.nds/req-NNN/` 子目录与 `state.json`（`version:"1.2"`）
2. 调 instruction-skill（若已有代码则前置，否则跳过到末尾）
3. 调 req-analysis-skill → 门禁（PRD 8 段 + feature-checklist + consistency-check Conflicts=0）→ 通过则进下一阶段
4. 调 design-skill → 门禁（令牌三层 + 组件六段 + patterns/IA）
5. 调 review-skill → 等用户签字（三维各自结果）
6. 调 task-allocation-skill → 门禁（INVEST + METR ≤1h + DAG 无环）
7. 调 dev-skill 按 task-tree 顺序执行（一次一 feature，feature-checklist 翻 passes）
8. 调 test-skill → bug_reflow 回流 dev 循环 → spec 漂移检测
9. 全部通过后调 instruction-skill 生成规范（新项目，落到 `.nds/00-instruction/`）
10. 标记 `current_phase = "done"`，向 `events[]` append 最终事件，向用户报告交付；同步回写 `index.json`

## 安装与卸载

- 安装位置（ZCode 用户级，跨工作区生效）：
  - skills：`~/.agents/skills/`（8 个 `*-skill` 目录，含 `references/`）
  - commands：`~/.agents/commands/`（11 个 `nzw-*.md`）
  - templates：`~/.agents/nzw-templates/`（schema + 进度模板 + handoff.contract.json）
  - 全局指令：`~/.zcode/AGENTS.md`（本文件）
- 安装：`./install.sh --zcode`（macOS/Linux/Git Bash）或 `.\install.ps1 -Target zcode`（Windows PowerShell），或一行远程安装见 README
- 卸载：删除上述目录与文件即可
- 更新：重新运行安装脚本覆盖

## 维护

- 源仓库：https://github.com/BBJI/nzw-dev-skills
- 修改 skill 内容：编辑 `skills/<skill-name>/SKILL.md`（及其 `references/`）后重新运行安装脚本
- 修改触发关键词：编辑本文件 `## 触发指南` 段落
- 修改 schema/模板：编辑 `~/.agents/nzw-templates/` 下对应文件（源在仓库 `templates/`）

---

_version: 1.3.0_

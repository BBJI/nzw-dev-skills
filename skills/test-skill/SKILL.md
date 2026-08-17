---
name: test-skill
description: 测试用例编写与验证反馈技能，扮演独立怀疑式评估器（独立于 dev-skill）。开发前编写测试用例驱动 TDD，开发后验证交付物并反馈 bug，形成测试→开发→修复→回归闭环。基于需求与任务契约设计测试用例（等价类/边界值/决策表/BDD Gherkin/探索性 charter/属性测试），执行测试，产出测试结果与缺陷报告。当用户提到以下任一场景时务必使用：测试用例、测试设计、验收测试、BDD、Gherkin、缺陷报告、测试执行、回归测试、探索性测试、测试反馈、验收验证，或需要验证交付物是否满足需求。即使用户只说"测一下"，只要在交付验证上下文中就应触发。不适用于单元测试编写本身（那是 dev-skill 红阶段）或上线监控（用运维工具）。
metadata:
  type: nzw-dev-skills
  phase: test
  trigger: /nzw-test
---

# 测试用例与验证反馈技能（test-skill）

以**可执行规格**（Executable Specification）为目标，把测试从"事后验证"前置为"需求锚点"。开发前测例驱动 TDD，开发后作为**独立怀疑式评估器**验证交付物——不夸赞 dev 的工作，按硬阈值打分，缺陷反馈开发形成闭环。

主导思想：**测试是学习过程而非仅验证**（Bach/Bolton）；**缺陷预防 > 缺陷检测**；**开箱 LLM 倾向夸赞自己的工作，必须用独立怀疑视角对冲**（Anthropic harness 设计）。

## 何时触发

- 用户输入 `/nzw-test`
- 自然语言提到"测试/验收/缺陷/回归"等
- workflow-skill 在闭环中进入 test 阶段

## 工作目录与状态

产出落到 `.nds/<req-id>/06-test/`：
- `test-cases.md` — 测试用例清单（设计侧）
- `test-results.md` — 测试执行报告
- `bug-reports/` — 每个 bug 一个 `.md`（ISO/IEC/IEEE 29119-3:2013 同源字段）
- `regression-suite.md` — 回归用例集（基于风险优先级）
- `exploratory-sessions.md` — 探索性测试 charter + SBTM debrief
- `spec-drift-check.md` — spec 漂移检测结果（converge）

入口动作：
1. 读 `.nds/index.json` 确定 `active_req_id`，再读 `.nds/<req-id>/state.json`，确认 `phases.dev.status` 至少 `in_progress`。
2. `project.current_phase = "test"`，`phases.test.status = "in_progress"`；同步回写 `index.json`。
3. Bug 写入 state.json 的 `feedback_loop.open_bugs` 与 `bug_reflow[]`，`iteration++`。

## 主导思想

- **测试是可执行规格**：BDD 场景做外层验收，TDD 单元做内层驱动
- **缺陷预防 > 缺陷检测**：需求评审即开始测例设计（Shift-Left）
- **追溯闭环**：测试用例 ↔ 需求 ↔ 任务三方追溯
- **AI 加速量，人守质**：AI 生成测例骨架，人审断言语义
- **独立怀疑式 Evaluator**：本 skill 不写实现代码，只验证；按硬阈值打分，回传结构化 bug 报告

## 执行流程

### 1. 测试用例设计（test-cases.md）

基于 PRD、task-tree.json、design 设计。

**设计四件套**：等价类划分（有效/无效输入）/ 边界值（min/min+1/max/max-1）/ 决策表（多条件组合，**至少用于 1 个多条件业务规则**）/ 状态迁移（复杂业务）。

**BDD 场景（Gherkin）**——外层验收用 Given-When-Then：

```gherkin
Feature: 用户注册 (对应 F001)

  Scenario: 有效邮箱注册成功
    Given 访客在注册页
    When 输入邮箱 "user@example.com" 与密码 "Pass123!"
    And 点击注册按钮
    Then 应返回 201 状态码
    And 应收到欢迎邮件

  Scenario Outline: 邮箱边界长度
    Given 访客在注册页
    When 输入长度 <len> 的邮箱
    Then 应返回 <status>
    Examples:
      | len | status |
      | 254 | 201    |
      | 255 | 400    |
```

**Gherkin 反模式**（这些会让场景失去表达力）：
- **命令式写 UI 细则**：`When document.querySelector('#email').value='x'` 禁；用声明式 `When 输入邮箱 "x"`。原因：场景应描述用户意图而非实现，实现变了场景不该跟着废。
- **Then 查数据库**：Then 只验用户可观察输出（HTTP 响应/UI 文案），不验内部存储。原因：查数据库把测试耦合到实现细节，重构即碎。
- **场景步骤过多**：每场景 3-5 步，过多失表达力，用 Background 或 Scenario Outline 拆。

**用例清单**：

```markdown
| 用例 ID | 类型 | 对应需求 | 对应任务 | 优先级 | 描述 | 预期 |
|---|---|---|---|---|---|---|
| TC001 | 正向 | F001 | T002 | P0 | 有效邮箱注册 | 201 + user |
| TC002 | 负向 | F001 | T002 | P0 | 重复邮箱 | 409 |
| TC003 | 边界 | F001 | T002 | P1 | 邮箱长度 254（max） | 201 |
```

### 2. 属性测试（核心逻辑用）

对核心逻辑（数值计算/状态机/序列处理）用属性测试替代部分样例测试（Kiro spec-driven 模式）：断言"对所有输入必须成立的规则"而非几个样例，抓样例测试漏掉的边界。例如"注册函数对任意合法邮箱返回 201，对任意重复邮箱返回 409"。

### 3. 浏览器 e2e（前端必备，性能放大器）

前端需求用浏览器自动化像用户一样点击（ZCode 的 `web-gui-tester` 技能 / Playwright MCP），截图比对。这是性能放大器——能发现"功能存在但 UI 破了"的假绿，而单元测试发现不了（Anthropic 实测"戏剧性提升性能"）。**只在仔细 e2e 测试后才在 feature-checklist.json 标 passes: true**。

### 4. 探索性测试（exploratory-sessions.md）

脚本测试覆盖不到的探索维度，用 charter + SBTM（Session-Based Test Management）让探索可审计可度量（Kaner/Bach）：

```markdown
# 探索性测试会话

## Session 1 — 2026-08-17 14:00 (90min)
- Charter: explore 注册流程 with 并发请求工具 to discover 竞态边界
- 覆盖区域: 注册 API + DB 唯一约束
- 发现: B003 (10 并发产生重复账号)
- Debrief: 增加了 TC017 回归用例；建议 DB 加唯一索引
```

charter 结构：`explore [目标] with [资源] to discover [信息]`。探索性测试 ≠ ad hoc 随意测——必须管理覆盖度、记录 debrief、发现的 bug 转回归用例。

### 5. 测试执行（test-results.md）

执行项目测试套件，记录概要（总用例/通过/失败/跳过/通过率/时长）+ 失败用例详情（状态/实际/期望/严重度/Bug ID/关联任务）+ 覆盖率（行/分支/函数）。覆盖率是下限门禁（70-80%），非目标——不为凑覆盖率写空断言。

### 6. 缺陷报告（bug-reports/B00x.md，ISO/IEC/IEEE 29119-3:2013）

引用标准从 IEEE 829 更新为 **ISO/IEC/IEEE 29119-3:2013**（829-2008 已被其取代，829 中称 Anomaly Report）：

```markdown
# B003 - 高并发下重复邮箱注册
## 元数据（ID/严重度/优先级/状态/关联任务/关联用例/报告时间/报告人/发现阶段 Phase）
## 复现步骤（可执行）
## 期望结果 / 实际结果
## 环境（OS/Runtime/DB/Branch）
## 根因建议（如：数据库缺少 email 唯一索引）
## 附件（测试日志/截图）
```

将 bug 摘要写入 state.json 的 `feedback_loop.open_bugs`，并 append `bug_reflow[]` 一项 `{bug_id, task_id, triggered_at, status:"triggered"}`——这是机器可驱动的缺陷回流事件，自动触发 dev-skill 新一轮迭代。

### 7. 回归用例集（regression-suite.md，基于风险优先级）

修复后的 bug 测试纳入回归集，**按风险分级**避免膨胀到跑不完：P0/核心流每次必跑，P2 抽样。每次新版本必跑回归集。

### 8. spec 漂移检测（spec-drift-check.md，converge）

借鉴 spec-kit `/speckit.converge`：测试通过后，对照 PRD/design 检查实现是否漂移——把"PRD 提到但未实现""实现了但 PRD 没提到""设计规格与实现不符"的缺口补成新任务（写入 task-tree.json）。nzw 原有 bug 回流但缺这一步，导致"测试全绿但功能缺斤短两"。

### 9. 反馈闭环

- Blocker/Critical bug → append `bug_reflow[]`，触发 dev-skill 新一轮迭代
- bug 状态：`open → in_fix → retest → closed`；bug_reflow 项同步
- `feedback_loop.iteration++`
- 全部 bug closed 且回归通过 且回归通过 → 阶段完成

## 完成判定

- test-cases.md 覆盖所有 Must 级需求的正向 + 负向 + 边界，含 ≥1 个决策表
- test-results.md 执行报告完整，e2e（前端场景）已跑
- `exploratory-sessions.md` 至少 1 个 charter + debrief
- `spec-drift-check.md` 已产出，漂移缺口已补成任务或标注接受
- 所有 Blocker/Critical bug 状态为 `closed`，`bug_reflow[]` 全部 `closed`
- regression-suite.md 已更新（含风险分级）
- `feature-checklist.json` 所有 Must 级 feature `passes: true` 且经本 skill 复核（不只信 dev 自标）
- `phases.test.status = "done"`，`events[]` append phase_done
- `resume_hint`：若全通过，进入交付阶段；若仍有 bug，提示 dev-skill 修复

## 与上下游交接

- 输入：PRD（验收点）、task-tree.json（output_contract）、dev-skill 产出（代码 + 测试 + feature-checklist.json）
- 输出给 dev-skill：bug-reports/ + `bug_reflow[]` 触发修复
- 输出给 workflow-skill：test-results.md + spec-drift-check.md 是 Loop Engineering 中 Observe 阶段的客观信号

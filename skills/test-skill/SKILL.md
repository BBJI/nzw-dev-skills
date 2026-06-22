---
name: test-skill
description: 测试用例编写与验证反馈技能。开发前编写测试用例驱动 TDD，开发后验证交付物并反馈 bug。基于需求与任务契约设计测试用例，执行测试，产出测试结果与缺陷报告，形成测试→开发→修复→回归的闭环。当用户提到以下任何场景时务必使用此技能：测试用例、测试设计、验收测试、BDD、Gherkin、缺陷报告、测试执行、回归测试、探索性测试、测试反馈，或需要验证交付物是否满足需求。即使用户只说了"测一下"，只要在交付验证上下文中，都应触发此技能。
metadata:
  type: nzw-dev-skills
  phase: test
  trigger: /nzw-test
---

# 测试用例与验证反馈技能（test-skill）

以**可执行规格**（Executable Specification）为目标，把测试从"事后验证"前置为"需求锚点"。开发前测例驱动 TDD，开发后验证交付物，缺陷反馈开发形成闭环。

主导思想：**测试是学习过程而非仅验证**（Bach/Bolton）；**缺陷预防 > 缺陷检测**。

## 何时触发

- 用户输入 `/nzw-test`
- 自然语言提到"测试/验收/缺陷/回归"等
- workflow-skill 在闭环中进入 test 阶段

## 工作目录与状态

**路径约定（v1.1）**：所有产出相对 `.nds/<active-req-id>/`，例如 `.nds/req-001/06-test/`。需求隔离见顶层 `.nds/index.json`。

产出落到 `.nds/<req-id>/06-test/`：
- `test-cases.md` — 测试用例清单（设计侧）
- `test-results.md` — 测试执行报告
- `bug-reports/` — 每个 bug 一个 `.md`
- `regression-suite.md` — 回归用例集

入口动作：
1. 读取 `.nds/index.json` 确定 `active_req_id`（或用 `--req <id>` 指定），再读 `.nds/<req-id>/state.json`，确认 `phases.dev.status` 至少 `in_progress`
2. `project.current_phase = "test"`，`phases.test.status = "in_progress"`；同步回写 `index.json` 中该 req 的 `current_phase`/`updated_at`/`open_blockers`
3. Bug 写入 state.json 的 `feedback_loop.open_bugs`，`iteration++`

## 主导思想

- **测试是可执行规格**：BDD 场景做外层验收，TDD 单元做内层驱动
- **缺陷预防 > 缺陷检测**：需求评审即开始测例设计（Shift-Left）
- **追溯闭环**：测试用例 ↔ 需求 ↔ 任务三方追溯
- **AI 加速量，人守质**：AI 生成测例骨架，人审断言语义

## 执行流程

### 1. 测试用例设计（test-cases.md）

基于 `.nds/<req-id>/01-requirements/PRD.md`、`.nds/<req-id>/04-tasks/task-tree.json`、`.nds/<req-id>/02-design/` 设计。

#### 设计四件套

- **等价类划分**：有效/无效输入划分
- **边界值**：min / min+1 / max / max-1
- **决策表**：多条件组合
- **状态迁移**：状态机图（适合复杂业务）

#### BDD 场景（Gherkin）

外层验收用 Given-When-Then：

```gherkin
Feature: 用户注册 (对应 F001)

  Scenario: 有效邮箱注册成功
    Given 访客在注册页
    When 输入邮箱 "user@example.com" 与密码 "Pass123!"
    And 点击注册按钮
    Then 应返回 201 状态码
    And 应收到欢迎邮件

  Scenario: 重复邮箱注册失败
    Given 邮箱 "user@example.com" 已存在
    When 使用相同邮箱注册
    Then 应返回 409 错误
    And 错误信息应为 "邮箱已注册"
```

#### 用例清单

```markdown
| 用例 ID | 类型 | 对应需求 | 对应任务 | 优先级 | 描述 | 预期 |
|---|---|---|---|---|---|---|
| TC001 | 正向 | F001 | T002 | P0 | 有效邮箱注册 | 201 + user |
| TC002 | 负向 | F001 | T002 | P0 | 重复邮箱 | 409 |
| TC003 | 边界 | F001 | T002 | P1 | 邮箱长度 254（max） | 201 |
| TC004 | 异常 | F001 | T002 | P1 | 数据库宕机 | 500 + 重试 |
```

### 2. 测试执行（test-results.md）

执行项目测试套件，记录：

```markdown
## 测试执行报告

### 概要
- 总用例：48
- 通过：43
- 失败：4
- 跳过：1
- 通过率：89.6%
- 执行时长：32s

### 失败用例详情

#### TC017 - 高并发下重复邮箱注册
- 状态：FAIL
- 实际：10 并发中 2 个返回 201
- 期望：仅 1 个返回 201，其余 409
- 严重度：Blocker
- Bug ID：B003
- 关联任务：T002

### 覆盖率
- 行覆盖：82%
- 分支覆盖：74%
- 函数覆盖：88%
```

### 3. 缺陷报告（bug-reports/B003.md）

参考 IEEE 829：

```markdown
# B003 - 高并发下重复邮箱注册

## 元数据
- ID: B003
- 严重度: Blocker
- 优先级: P0
- 状态: open
- 关联任务: T002
- 关联用例: TC017
- 报告时间: 2026-06-22 14:30
- 报告人: test-skill

## 复现步骤
1. 启动注册服务
2. 用 10 个并发请求相同邮箱 `dup@example.com` 注册
3. 统计响应状态码

## 期望结果
1 个返回 201，9 个返回 409

## 实际结果
2 个返回 201（数据库出现两条相同邮箱记录）

## 环境
- OS: macOS 14.4
- Runtime: Node 20.11
- DB: PostgreSQL 16
- Branch: feat/auth-T002

## 根因建议
数据库缺少 email 字段唯一索引

## 附件
- 测试日志：bug-reports/B003-log.txt
- 数据库截图：bug-reports/B003-db.png
```

将 bug 摘要写入 state.json 的 `feedback_loop.open_bugs`。

### 4. 回归用例集（regression-suite.md）

修复后的 bug 测试纳入回归集：

```markdown
# 回归用例集

| Bug ID | 用例 | 状态 |
|---|---|---|
| B001 | TC005 | in regression |
| B003 | TC017 | in regression |
```

每次新版本必跑回归集。

### 5. 反馈闭环

- Blocker / Critical bug → 触发 dev-skill 新一轮迭代
- bug 状态：`open → in_fix → retest → closed`
- 在 state.json 中 `feedback_loop.iteration++`
- 全部 bug closed 且回归通过 → 阶段完成

## 必须遵守的规则

1. **每条测试断言单一行为**，名称表达意图（should_X_when_Y）。
2. **验收测试三方签字**：PO/Dev/QA 在实施前对 Gherkin 场景签字。
3. **缺陷报告必须含**：复现步骤、期望/实际、环境、严重度、优先级。
4. **测试失败必须反馈开发并形成回归用例入库**。
5. **AI 生成测试必须人工评审断言**，禁止"空断言"凑覆盖。
6. **严重缺陷未关闭禁止发版**；P2 以下可带病上线但需登记。
7. **测试左移**：需求评审即开始测例设计，追溯矩阵闭环。

## 完成判定

- test-cases.md 覆盖所有 Must 级需求的正向 + 负向 + 边界
- test-results.md 执行报告完整
- 所有 Blocker / Critical bug 状态为 `closed`
- regression-suite.md 已更新
- state.json 中 `feedback_loop.open_bugs` 中 Blocker/Critical 为 0
- `phases.test.status = "done"`
- `resume_hint` 建议：若全部通过，进入交付阶段；若仍有 bug，提示 dev-skill 修复

## 与上下游交接

- 输入：PRD（验收点）、task-tree.json（output_contract）、dev-skill 产出（代码 + 测试）
- 输出给 dev-skill：bug-reports/ 触发修复
- 输出给 workflow-skill：test-results.md 是 Loop Engineering 中 Observe 阶段的客观信号

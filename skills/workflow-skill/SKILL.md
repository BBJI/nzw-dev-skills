---
name: workflow-skill
description: AI 自主全流程交付技能，以 Loop Engineering 思想串联需求→设计→评审→任务→开发→测试→规范七个阶段，形成 Plan→Act→Observe→Reflect→Iterate 闭环。支持跨会话续传、人在环介入点、质量门禁、失败回退。当用户提到以下任何场景时务必使用此技能：全流程交付、Loop Engineering、自主交付、端到端开发、闭环迭代、一键交付、AI 自主开发、从需求到上线、完整开发流程，或需要把一个想法变成可交付软件。即使用户只说了"做个 XXX"或"开发一个 XXX"，只要希望走完整开发流程，都应触发此技能。
metadata:
  type: nzw-dev-skills
  phase: all
  trigger: /nzw-workflow
---

# Loop Engineering 全流程交付技能（workflow-skill）

以 **Loop Engineering** 思想把 7 个阶段串成 AI 自主交付闭环——**Plan → Act → Observe → Reflect → Iterate**，每个循环产出可验证增量，质量门禁决定状态转移，人在边界介入。

主导思想：**闭环优于直线，客观信号优于主观判断，SOP 编排优于自由协作，人在边界 AI 在循环内**。

## 何时触发

- 用户输入 `/nzw-workflow <任务描述>`
- 自然语言提到"全流程/端到端/做个 XXX 走完整流程"等
- `/nzw-resume` 续传时若当前阶段未完成

## 核心机制

```
        ┌─────────── 质量门禁 ──────────┐
        │                                ▼
Plan → Act → Observe → Reflect → (next phase)
        │                          ▲
        └──── bug 回流 ────────────┘
```

- **Plan**：拆解任务、生成规格、确定验收标准（对应 req / design / review / task 阶段）
- **Act**：执行开发与测试（dev / test 阶段）
- **Observe**：运行测试/lint/编译，收集客观信号（不可依赖 AI 自评）
- **Reflect**：对照验收标准评估差距，由独立视角判断
- **Iterate**：bug 回流开发，进入下一轮；全通过则进入下一阶段

## 工作目录与状态

入口动作：
1. 读取或初始化 `.nds/state.json`
   - 若不存在：初始化结构（schema 见 `templates/state.schema.json`），`current_phase = "init"`
   - 若存在：读取 `current_phase` 从该阶段接续
2. 全程写入 `.nds/07-workflow/loop-log.md`，记录每一轮循环
3. 每阶段完成后更新 state.json 的 `phases.<phase>.status`、`current_phase`、`resume_hint`
4. 同步刷新 `.nds/PROGRESS.md`

## 阶段编排（SOP）

```
已有项目 ──► instruction ──► requirements ──► design ──► review
                                                              │
                                                              ▼
                                                          (签字)
                                                              │
                                                              ▼
新项目 ◄── instruction ◄── test ◄── dev ◄── task ◄─────── 通过
   │                          ▲              │
   │                          └── bug 回流 ──┘
   ▼
 完成
```

### 阶段 0：instruction（已有项目前置 / 新项目后置）

- 已有项目：先调 `instruction-skill` 提取规范，作为后续阶段约束
- 新项目：跳过此阶段，最后再生成

### 阶段 1：requirements

- 调 `req-analysis-skill`
- **门禁**：PRD 8 段齐全 + 每条需求有验收标准 + Non-goals 显式
- **Observe**：自动检查文件存在性与段落完整性
- 未过门禁 → 反馈给 req-analysis-skill 补充

### 阶段 2：design

- 调 `design-skill`
- **门禁**：令牌三层齐全 + 组件规格六段 + 暗色模式 + WCAG AA
- 未过 → 反馈补充

### 阶段 3：review（人在环）

- 调 `review-skill`
- **门禁**：Blocker 全关闭 + Critical 有缓解 + 用户签字
- **人在环**：必须等用户在 `.nds/03-review/sign-off.md` 签字
- 未过 → 回流到对应上游阶段

### 阶段 4：tasks

- 调 `task-allocation-skill`
- **门禁**：INVEST 全过 + DAG 无环 + 四要素齐全
- 未过 → 重新拆分

### 阶段 5：dev

- 调 `dev-skill` 按 task-tree 顺序执行
- **门禁**：每任务 verification_cmd 通过 + 三道门禁（lint/type/test）全绿
- **Observe**：跑测试，收集 pass/fail
- 任务失败 → Reflect 后修 bug，继续

### 阶段 6：test

- 调 `test-skill`
- **门禁**：Blocker/Critical bug 全关闭 + 回归集通过
- **Bug 回流**：open_bugs 中 Blocker/Critical 触发 `dev-skill` 新一轮迭代
- `feedback_loop.iteration++`
- 全过 → 进入交付

### 阶段 7：instruction（新项目后置）

- 新项目场景：调 `instruction-skill` 把交付约定固化为规范
- 已有项目：跳过（已在阶段 0 完成）

## 闭环日志（loop-log.md）

每轮循环记录：

```markdown
## Loop #1 - 2026-06-22 14:00

### Plan
- 当前阶段：requirements
- 目标：产出 PRD

### Act
- 调用 req-analysis-skill

### Observe
- 门禁检查：8 段齐全 ✓ / 验收标准 ✓ / Non-goals ✓
- 用户确认：等待中...

### Reflect
- 通过

### Iterate
- 进入 design 阶段
```

## 跨会话续传机制

任意阶段都可暂停（Ctrl+C、清空上下文、新开会话）。下次对话：

1. 用户输入 `/nzw-resume` 或 `/nzw-workflow`（无参数）
2. workflow-skill 读取 `.nds/state.json`
3. 根据 `current_phase` 与 `resume_hint` 接续
4. 检查 `phases.<current>.status`：
   - `in_progress` → 从中断点继续
   - `blocked` → 提示用户处理阻塞
   - `pending` → 启动该阶段
5. 向用户报告：当前阶段、已完成产出、下一步建议

state.json 是唯一真源；PROGRESS.md 是其可读视图。

## 人在环介入点（固定四处）

| 介入点 | 原因 | 动作 |
|---|---|---|
| 需求评审 | 早期介入成本最低 | 用户确认 PRD 完整性与优先级 |
| 设计评审 | 技术可行性 | 用户确认 design-spec |
| 任务拆分确认 | 粒度与排期 | 用户确认 task-tree |
| 准入签字 | 开发前最后闸门 | 用户在 sign-off.md 签字 |

其余阶段 AI 自主推进，门禁拦截比事后审查更高效。

## 失败恢复与状态机

- 每个阶段产出物作为 checkpoint
- 失败时回退到最近通过的 checkpoint，不从头开始
- `failed` 状态自动触发 Reflect，分析根因，生成改进项写入规范

状态机：
```
pending → planning → reviewing → approved → implementing → testing → done
                                                      ↓
                                                   failed → reflect → retry
```

## 必须遵守的规则

1. **闭环必须显式建模**：Plan→Act→Observe→Reflect→Iterate 五阶段不可省略。
2. **Observe 必须有客观信号**：测试结果、lint 输出、编译日志，不能依赖 AI 自评。
3. **质量门禁前置**：每阶段出口设硬门禁，不过不进下一阶段。
4. **状态机显式化**：入口/出口/失败路径明确，可持久化可恢复。
5. **人在环介入点固定**：四处强制人工确认，不擅自推进。
6. **子代理隔离上下文**：每阶段调用对应 skill，主代理只接收摘要。
7. **失败必须可恢复**：长任务崩溃从 checkpoint 续跑，不从头开始。

## 完成判定

- 七阶段全部 `done`（或 `skipped` 已显式说明）
- `feedback_loop.open_bugs` 中无 Blocker/Critical
- `current_phase = "done"`
- `resume_hint` 提示用户：交付完成，可合并 PR / 部署
- 新项目场景：instruction 已生成

## 与各 skill 的关系

本 skill 是编排者（orchestrator），不直接产出业务工件，而是：
- 读取 state.json 判断当前阶段
- 调用对应 skill 执行
- 校验门禁
- 决定推进 / 回流 / 阻塞
- 更新 state.json 与 PROGRESS.md
- 维护 loop-log.md

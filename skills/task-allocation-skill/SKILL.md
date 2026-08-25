---
name: task-allocation-skill
description: 任务拆分与进度跟踪技能。基于评审通过的需求与设计，将方案分解为 INVEST 合格、DAG 依赖、可验证的任务树（绑定 METR ≤1h 红线），并排期跟踪到交付。当用户提到以下任一场景时务必使用：任务拆分、WBS、工作分解、排期、进度跟踪、依赖管理、Story Points、看板、Sprint 计划、迭代切片，或需要把方案变成可执行任务清单。即使用户只说"拆任务"，只要在开发前上下文中就应触发。不适用于需求优先级排序（用 req-analysis-skill 的 story-map）或单任务实现（用 dev-skill）。
metadata:
  type: nzw-dev-skills
  phase: tasks
  trigger: /nzw-task
---

# 任务拆分与跟踪技能（task-allocation-skill）

把评审通过的方案分解为**Small、Vertical、Verifiable** 的增量任务，依赖关系建模为 DAG，状态机闭环跟踪到交付。

主导思想：**任务拆分的本质是降低不确定性**——每完成一个任务，系统可工作、可验证、可回滚。AI 时代把"可验证"推到"机器可验证"，使任务成为 agent 与人类的共享契约；把"Small"绑定 METR ≤1h 红线，给 INVEST 的"S"一个客观上界。

## 何时触发

- 用户输入 `/nzw-task`
- 自然语言提到"任务拆分/WBS/排期/看板"等
- workflow-skill 在闭环中进入 tasks 阶段

## 工作目录与状态

产出落到 `.nds/<req-id>/04-tasks/`：
- `WBS.md` — 工作分解结构（Epic → Feature → Task 三层）
- `task-tree.json` — 任务树（机器可读，同步到 state.json 的 `task_tree`）
- `schedule.md` — 排期表（甘特/看板视图）
- `dependencies.mmd` — 依赖关系图（mermaid DAG）
- `sprint-contracts/` — 每个关键 task 一个 Sprint Contract（见 templates/handoff.contract.json）

入口动作：
1. 读 `.nds/index.json` 确定 `active_req_id`，再读 `.nds/<req-id>/state.json`，确认 `phases.review.status == "done"`。
2. `project.current_phase = "tasks"`，`phases.tasks.status = "in_progress"`；同步回写 `index.json`。
3. 任务树同步写入 state.json 的 `task_tree.tasks`。

## 主导思想

- **Small, vertical, verifiable increments**：每任务人类等价 ≤1 人天，**理想 ≤1h（METR 红线）**，垂直切片而非水平分层
- **dependencies explicit**：依赖显式建模为 DAG，禁止循环
- **flow over batch**：进度跟踪的目标是暴露瓶颈、缩短 feedback loop，而非报表
- **契约化**：任务描述含「上下文文件 + 输入契约 + 输出契约 + 验证命令」四要素

## 执行流程

### 1. 工作分解（WBS，3 层为限）

- **Epic**：对应 PRD 中一个 Must 级 Feature
- **Feature**：可独立交付的垂直切片（对应 story-map.md 的一个切片行）
- **Task**：叶节点，一个 agent 单次会话可完成

```markdown
# WBS
## Epic E01 - 用户认证
### Feature F01.1 - 注册登录（story-map walking skeleton）
- Task T001 - 设计 User schema [backend] → depends_on: -
- Task T002 - 实现注册 API [backend] → depends_on: T001
- Task T003 - 实现登录 API [backend] → depends_on: T001
- Task T004 - 登录页 UI [frontend] → depends_on: -
- Task T005 - 集成联调 [fullstack] → depends_on: T002,T003,T004
```

### 2. 任务四要素契约（task-tree.json）

```json
{
  "id": "T002",
  "title": "实现注册 API",
  "phase": "dev",
  "status": "todo",
  "depends_on": ["T001"],
  "assignee": "dev-skill",
  "context_files": [".nds/req-001/01-requirements/PRD.md#F001", ".nds/req-001/02-design/components/api-spec.md"],
  "input_contract": "User schema (T001 产出)，注册字段定义见 PRD F001",
  "output_contract": "POST /api/register 返回 201 与 user 对象；重复邮箱返回 409",
  "verification_cmd": "pnpm test src/api/register.test.ts",
  "estimate_hours": 2,
  "lock": null,
  "artifacts": [],
  "bug_ids": []
}
```

### 3. INVEST 检查 + METR ≤1h 红线

每条任务检查 INVEST（Independent/Negotiable/Valuable/Estimable/Small/Testable）。**"Small" 在 AI 上下文下有客观上界**：METR 研究显示 <4 分钟（人类用时）任务近 100% 成功，**>4 小时任务 <10% 成功**，Claude 50% 时间地平线约 1 小时。所以：

- 单任务目标 `estimate_hours ≤ 1`（人类等价）。>1h 的继续拆。
- 粒度过细（<15min）的聚合到一个含多步的 task。
- 不达标的继续拆；无法拆到 ≤1h 的单体任务走「预言机分解」。

### 4. 单体任务预言机分解

当一个 task 依赖过多文件、无法独立验证、或拆分后仍 >1h（如"编译 Linux 内核"式巨型任务），触发预言机分解（Anthropic C 编译器模式）：用**已知正确实现兜底大部分**，只让 agent 攻一个子集，再用 delta debugging 找"单独 ok 一起 fail"的边界。

```markdown
## T099 - 迁移整个认证模块到新框架（单体，预估 8h）
### 预言机分解
- T099a - 用现有实现兜底非认证路由（已知正确）
- T099b - agent 只攻认证路由子集（≤1h）
- T099c - 集成 + delta debug 找冲突点
```

> 为什么预言机分解：单体任务会让所有并行 agent 撞同一个 bug、修完互相覆盖，16 个 agent 毫无收益（Anthropic 实测）。把单体拆成"兜底+攻子集"才能利用并行，且让每个子任务回到 ≤1h 可靠区间。

### 5. 依赖 DAG + git 文件锁

`dependencies.mmd`（mermaid）校验：无循环依赖（拓扑排序可成）、关键路径标记、非 critical path 任务配 buffer。

**任务认领锁**（git 文件锁模式，防并行 dev 撞车）：dev-skill 认领任务时在 `task-tree.json` 写 `lock: {claimant, claimed_at}`，完成时置 `null`。靠"认领前检查 lock 非 null 即跳过"避免重复认领——这是最简有效的 DAG 协调，无需额外锁服务。

### 6. Sprint Contract（每个关键 task）

关键 task（critical path 上、或高风险）配一份 Sprint Contract（模板见 `templates/handoff.contract.json`），落到 `sprint-contracts/T00x.json`：明确输入 artifact、输出 artifact、验收门禁（客观信号 + 是否需人工签字）、回退 git commit。在编码前协商"这块活怎样算 done"，桥接高层 spec 与可测实现。

### 7. 排期表（schedule.md）

```markdown
# 排期表
## 看板视图
| Todo | Doing | Review | Done |
## 甘特视图（按依赖顺序）— 任务/预估/开始/结束/依赖
## 关键路径
T001 → T002 → T005 → T008（总 8h）
```

### 8. 状态机

```
Todo → Doing → Review → Done
         ↑       ↓
         └─ Blocked
```

转换规则：`Todo→Doing`（开发者认领，写 lock）/ `Doing→Review`（完成 + verification_cmd 通过）/ `Review→Done`（测试通过）/ `Review→Doing`（测试反馈 bug）/ `Doing→Blocked`（遇阻塞，需 reason+owner+unblock date）。

## 完成判定

- WBS.md 含全部 Epic → Feature → Task
- task-tree.json 所有任务含四要素 + `estimate_hours`，无 `estimate_hours > 1` 的未分解单体任务（或已走预言机分解）
- dependencies.mmd 拓扑排序无环，关键路径标记
- schedule.md 含看板 + 甘特 + 关键路径
- critical path 上的 task 配 Sprint Contract
- state.json 的 `task_tree.tasks` 已同步
- `phases.tasks.status = "done"`，`events[]` append phase_done
- `resume_hint` 建议进入 dev 阶段（`/nzw-dev` 按 task-tree 顺序执行）

## 与上下游交接

- 输入：`.nds/<req-id>/03-review/sign-off.md` 已签字 + `.nds/<req-id>/01-requirements/story-map.md`（切片依据）
- 输出给 dev-skill：task-tree.json 是开发按序执行的清单，`estimate_hours ≤1` 保证可靠区间
- 输出给 test-skill：每个任务的 `output_contract` 是测试用例设计的依据

---
name: workflow-skill
description: AI 自主全流程交付技能，以 Loop Engineering 思想串联需求→设计→评审→任务→开发→测试→规范七个阶段，形成 Plan→Act→Observe→Reflect→Iterate 闭环。支持跨会话续传（会话启动协议 + events[] 事件日志）、人在环介入点、质量门禁、bug 回流、spec 漂移检测、失败回退。当用户提到以下任一场景时务必使用：全流程交付、Loop Engineering、自主交付、端到端开发、闭环迭代、一键交付、AI 自主开发、从需求到上线、完整开发流程，或需要把一个想法变成可交付软件。即使用户只说"做个 XXX"或"开发一个 XXX"，只要希望走完整开发流程就应触发。不适用于单阶段任务（用对应阶段 skill）。
metadata:
  type: nzw-dev-skills
  phase: all
  trigger: /nzw-workflow
---

# Loop Engineering 全流程交付技能（workflow-skill）

以 **Loop Engineering** 思想把 7 个阶段串成 AI 自主交付闭环——**Plan → Act → Observe → Reflect → Iterate**，每个循环产出可验证增量，质量门禁决定状态转移，人在边界介入。

主导思想：**闭环优于直线，客观信号优于主观判断，SOP 编排优于自由协作，人在边界 AI 在循环内**。底层三总纲：**harness 先于 agent**（环境设计是可控杠杆）、**测试即 spec**（自主场景下测试定义成功）、**上下文即稀缺资源**（context rot 是头号敌人）。

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
        └──── bug 回流 / spec 漂移 ─┘
```

- **Plan**：拆解任务、生成规格、确定验收标准（req / design / review / task 阶段）
- **Act**：执行开发与测试（dev / test 阶段）
- **Observe**：运行测试/lint/编译，收集客观信号（不可依赖 AI 自评）
- **Reflect**：对照验收标准评估差距，由独立视角判断
- **Iterate**：bug 回流开发，进入下一轮；全通过则进入下一阶段

## 工作目录与状态

所有产出相对 `.nds/<active-req-id>/`，例如 `.nds/req-001/07-workflow/loop-log.md`。instruction-skill 阶段例外，落到 `.nds/00-instruction/`（项目级共享）。

入口动作：
1. 读取或初始化 `.nds/index.json`（schema 见 `templates/index.schema.json`）：不存在 → 初始化，创建首个 req-001 子目录并设为 active；存在 → 读 `active_req_id` 接续。
2. 读取或初始化 `.nds/<req-id>/state.json`（`version: "1.2"`，schema 见 `templates/state.schema.json`）：不存在 → 初始化，`current_phase = "init"`；存在 → 走「会话启动协议」。
3. 全程写入 `.nds/<req-id>/07-workflow/loop-log.md` 记录每轮循环。
4. 每阶段完成后更新 state.json 的 `phases.<phase>.status`、`current_phase`、`resume_hint`，**向 `events[]` append 一条**（只追加事件日志，managed-agents 模式），同步回写 `index.json` 与两层 PROGRESS.md。

> v1.1 旧 state.json 首次加载自动补 `events:[]`/`bug_reflow:[]`/`feature_checklist_ref` 默认空值并升级为 `1.2`，不破坏旧 `.nds/`。

## 会话启动协议（resume 强制例程）

任意阶段暂停后下次对话（`/nzw-resume` 或无参 `/nzw-workflow`），执行固定启动例程（Anthropic 长跑 harness 实测能修"上次留破环境"）：

1. 读 `.nds/index.json` → 若多需求列出供用户选 active_req_id
2. 读 `.nds/<req-id>/state.json` → 重放 `events[]` 最近 5 条快速恢复上下文，`resume_hint` 补充
3. 读 `.nds/<req-id>/PROGRESS.md` 看人类态看板
4. **环境健康检查**：`git status` 看是否有未提交的破改动；若有 `init.sh`（项目级启动脚本）跑一遍做依赖/编译冒烟；跑基础冒烟测试
5. 报告：当前 req、当前阶段、已完成产出、环境是否健康、下一步建议
6. 用户确认后触发对应 skill 从中断点继续

state.json 的 `events[]` 是唯一真源（只追加，绝不删除/覆盖）；PROGRESS.md 是其可读视图，由事件日志渲染。

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

每阶段门禁分两类：**客观信号门禁**（测试/lint/编译/evaluator 阈值/文件完整性）自动放行；**人工签字门禁**（review sign-off、破坏性操作）强制等。每阶段开始时可选填 Sprint Contract（模板见 `templates/handoff.contract.json`）：输入 artifact、输出 artifact、门禁、回退 git commit。

### 阶段 0：instruction（已有项目前置 / 新项目后置）
已有项目先调 instruction-skill 提取规范作为后续约束（spec-kit constitution 护栏）；新项目跳过，最后再生成。

### 阶段 1：requirements
调 req-analysis-skill。**门禁**：PRD 8 段齐全 + 每条需求有验收标准 + Non-goals 显式 + feature-checklist.json 产出 + consistency-check Conflicts=0。**Observe**：自动检查文件存在性与段落完整性。未过 → 回流补充。

### 阶段 2：design
调 design-skill。**门禁**：令牌三层齐全（DTCG 2025.10）+ 组件规格六段（States 含 loading/empty/error/disabled）+ 暗色模式 + WCAG AA + patterns/ 与 IA 产出。未过 → 回流补充。

### 阶段 3：review（人在环，唯一强制人工卡点）
调 review-skill（怀疑式评估器）。**门禁**：Blocker 全关闭 + Critical 有缓解 + evaluation.json `overall_passed` + 用户在 sign-off.md 签字（三维各自结果）。未过 → 回流到对应上游阶段。

### 阶段 4：tasks
调 task-allocation-skill。**门禁**：INVEST 全过 + METR ≤1h 红线（>1h 走预言机分解）+ DAG 无环 + 四要素齐全 + critical path 配 Sprint Contract。未过 → 重新拆分。

### 阶段 5：dev
调 dev-skill 按 task-tree 顺序执行（一次一个 feature，受约束子 agent 模式）。**门禁**：每任务 verification_cmd 通过 + 三道门禁（lint/type/test）全绿 + feature-checklist.json 对应 passes: true。**Observe**：跑测试收集 pass/fail（真实输出）。任务失败 → Reflect 后修 bug，继续。

### 阶段 6：test
调 test-skill（独立怀疑式评估器）。**门禁**：Blocker/Critical bug 全关闭 + 回归集通过 + feature-checklist 经 test 复核 + spec-drift-check 已产出。**Bug 回流**：`bug_reflow[]` 中 `triggered` 项触发 dev-skill 新一轮迭代。`feedback_loop.iteration++`。全过 → 进入交付。

### 阶段 7：instruction（新项目后置）
新项目场景：调 instruction-skill 把交付约定固化为规范。已有项目：跳过（已在阶段 0 完成）。

## 闭环日志（loop-log.md）

每轮循环记录 Plan/Act/Observe/Reflect/Iterate 五段。

## 受约束子 agent（阶段间通信）

阶段间通信用受约束子 agent（Cognition/Claude Code 模式）：每阶段作为 context-isolated 的子 agent 执行，**只回传蒸馏摘要**到顶层 orchestrator（对应 state.json 摘要 + PROGRESS.md），脏数据（原始工具输出、完整文件）留在 req 子目录，不污染全局上下文。子 agent 不与主 agent 并行、只回答明确定义的问题、用完即弃——这是对抗 context rot 的关键。

> 为什么不用多 agent 并行跑同需求多阶段：Cognition《Don't Build Multi-Agents》实测多 agent 并行让决策分散、上下文无法充分共享，"协同只会产生脆弱系统"。nzw 的并行只用于任务级（dev 阶段多 task），不用于阶段级。

## 人在环介入点（固定四处）

| 介入点 | 原因 | 动作 |
|---|---|---|
| 需求评审 | 早期介入成本最低 | 用户确认 PRD 完整性与优先级 |
| 设计评审 | 技术可行性 | 用户确认 design-spec |
| 任务拆分确认 | 粒度与排期 | 用户确认 task-tree（METR ≤1h） |
| 准入签字 | 开发前最后闸门 | 用户在 sign-off.md 签字 |

其余阶段 AI 自主推进，门禁拦截比事后审查更高效。破坏性操作（生产部署/不可逆迁移）额外强制人在环。

## 失败恢复与状态机

- 每个阶段产出物作为 checkpoint；失败时回退到最近通过的 checkpoint，不从头开始
- `failed` 状态自动触发 Reflect，分析根因，生成改进项写入规范（规范即转移条件）
- 用 `git` 回退坏改动恢复工作状态（Anthropic harness："git to revert bad code changes"）
- `events[]` 事件日志让恢复 = `wake(req_id)` 重放关键事件（managed-agents Brain/Hands/Session 模式，cattle over pets——每组件可独立失败重启不丢状态）

状态机：
```
pending → in_progress → done
              ↓↑
           blocked → 回流上游
              ↓
           failed → reflect → retry
```

## harness 假设会过时（压力测试注）

harness 组件（门禁阈值、METR ≤1h 红线、poka-yoke 约束、子 agent 隔离）都编码了"当前模型局限假设"。模型变强后这些假设会过时——逐个组件做压力测试（去掉看是否退化），动态拆脚手架，别让过时约束拖累新模型（Anthropic harness design 实测：Opus 4.6 下 compaction 单独就够，可去掉早期 sprint 构造）。

## 完成判定

- 七阶段全部 `done`（或 `skipped` 已显式说明）
- `feedback_loop.open_bugs` 中无 Blocker/Critical，`bug_reflow[]` 全部 `closed`
- `feature-checklist.json` 所有 Must 级 feature `passes: true`
- `spec-drift-check.md` 漂移缺口已处理
- `current_phase = "done"`，`events[]` append 最终事件
- `resume_hint` 提示用户：交付完成，可合并 PR / 部署
- 新项目场景：instruction 已生成

## 与各 skill 的关系

本 skill 是编排者（orchestrator），不直接产出业务工件，而是：读 state.json 判断当前阶段 → 调用对应 skill（受约束子 agent）→ 校验门禁 → 决定推进 / 回流 / 阻塞 → 更新 state.json（含 events[]）与 PROGRESS.md → 维护 loop-log.md。

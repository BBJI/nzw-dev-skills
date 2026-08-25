---
name: req-analysis-skill
description: 需求调研分析技能，把模糊想法转化为可追溯、可验证、持续演进的结构化需求工件（PRD + 双稿原型 + 故事地图 + 追溯矩阵 + 风险登记 + 机器可读 feature 清单），作为后续设计/评审/开发/测试的唯一真源。当用户提到以下任一场景时务必使用：需求分析、需求调研、需求梳理、需求文档、PRD 编写、功能需求、非功能需求、干系人分析、需求分解、梳理需求，或任何需要将模糊想法/功能请求转化为严谨结构化需求文档的场景。即使用户没明说"需求"，只要想在实际开发前先明确"系统该做什么"就应触发。不适用于纯调研/选型（那用通用搜索）或已签准进入设计之后（那用 design-skill）。
metadata:
  type: nzw-dev-skills
  phase: requirements
  trigger: /nzw-req
---

# 需求调研分析技能（req-analysis-skill）

把模糊想法转化为**可追溯、可验证、持续演进**的结构化需求工件，作为后续设计、评审、开发、测试的唯一真源。

## 何时触发

- 用户输入 `/nzw-req <任务描述>`
- 自然语言提到"需求分析/PRD/功能需求/梳理需求"等
- workflow-skill 在 Loop Engineering 闭环中调用本 skill 进入 requirements 阶段

## 工作目录与状态

所有产出落到 `.nds/<req-id>/01-requirements/`：
- `PRD.md` — 需求文档主体（8 段）
- `prototype.html` — 精致线框（HTML，**真源**）
- `preview.html` — impeccable 高保真氛围预览（HTML，**参考**，不锁定视觉决策）
- `story-map.md` — 用户故事地图（walking skeleton + MVP 切片，喂给 task-allocation）
- `traceability-matrix.md` — 追溯矩阵（需求 ↔ 目标 ↔ Story ↔ 验收点 ↔ 设计帧 ↔ 测试用例）
- `risks.md` — 风险登记表（含 Trigger / Contingency）
- `glossary.md` — 术语表
- `feature-checklist.json` — 机器可读 feature 清单（初始全 fail，dev/test 翻转 passes——防假绿载体）
- `consistency-check.md` — 矛盾/缺口自动检查结果（喂给 review-skill）

入口动作：
1. 读取或初始化 `.nds/index.json`：不存在 → 初始化 `requirements: []` / `active_req_id: null`；新需求 → 生成下一编号 `req-NNN`（三位补零）追加并设为 `active_req_id`，创建子目录；续作 → 用 `--req <id>` 或 `index.active_req_id`。
2. 在 `.nds/<req-id>/` 下初始化 `state.json`（`version: "1.2"`，schema 见 `templates/state.schema.json`），`project.current_phase = "requirements"`，`phases.requirements.status = "in_progress"`。
3. `project.name`/`project.goal` 从用户输入提炼；同步回写 `index.json` 中该 req 的 `name`/`goal`/`current_phase`/`updated_at`。
4. **执行 impeccable 前置**：进入原型产出前先读 `references/impeccable-wireframe.md` 并按其「0. 前置」检测/安装 impeccable；安装失败则按降级路径处理。
5. 完成后向 `state.json` 的 `events[]` append 一条 `{type:"phase_done", phase:"requirements", ...}`，写 `resume_hint`，更新 `.nds/<req-id>/PROGRESS.md` 与顶层 `.nds/PROGRESS.md`。

> v1.1 旧 `state.json`（`version:"1.1"`）首次加载时自动补 `events:[]`/`bug_reflow:[]`/`feature_checklist_ref` 默认空值并升级为 `1.2`，不破坏旧 `.nds/`。

## 主导思想

- **Outcome over Output**：需求以用户可衡量的结果为导向，而非功能清单。
- **先问题后方案**：在描述功能前先明确"用户要完成的 Job 是什么"和"当前为什么做不到"。
- **Continuous Discovery**：需求是持续活动，PRD 是 living document，不一次性锁死。
- **可追溯是底线**：每条需求从来源到验收点双向链接。
- **结构与氛围分离**：原型层只回答"系统有什么、用户怎么走"，不回答"产品长什么样"——视觉决策留给 design-skill。但"不回答视觉"不等于"可以丑"：用 impeccable 的排版/间距/布局纪律让线框专业可读，另出一份高保真氛围稿帮助干系人感知产品气质。双稿并存的四条权威依据见 `references/impeccable-wireframe.md`。

## 执行流程

### 1. 干系人与问题挖掘

- 识别干系人（用户/决策者/运维/合规）
- 用 Jobs-to-be-Done 表达：`当 [情境]，我想 [做某事]，以便 [达成某价值]`
- 列出当前痛点与未满足的 Job
- 若用户输入过短，主动追问 3 个问题：目标用户是谁？成功指标是什么？有哪些不能做的（Non-goals）？

### 2. PRD 文档（PRD.md，8 段）

```markdown
# {{项目名}} PRD
## 元数据（版本/日期/作者/状态）
## 1. 问题陈述（用户是谁、要完成的 Job、当前为什么做不到、本项目目标）
## 2. 目标与成功指标（North Star Metric / OKR 1O+2-3KR / Non-goals 显式列出）
## 3. 用户与场景（Persona / User Story Mapping 骨架 / 关键用户旅程）
## 4. 功能需求（按 MoSCoW 优先级）
  每条 Story：ID F00x / 作为<角色>我希望<动作>以便<价值> / 验收标准 Given-When-Then（至少 1 条可测）/ 优先级 Must-Should-Could-Won't / 来源 / use case 一句话
## 5. 非功能需求（性能/安全/可用性/可访问性 WCAG 2.2 AA/可观测性/兼容性——即使"暂无特殊要求"也要显式写出）
## 6. 技术约束（技术栈倾向/依赖/集成接口/部署环境）
## 7. 开放问题与风险（指向 risks.md）
## 8. 变更日志（版本/日期/变更/影响——任何修改走日志，不删历史版本）
```

> 为什么 Non-goals 与 NFR 必写：明确"不做什么"比"做什么"更能防止范围蔓延；NFR 省略会让性能/安全/可访问性在开发后期才暴露，修复成本是需求阶段的 10-100 倍（Shift-Left Quality）。

### 3. 用户故事地图（story-map.md，一等产物）

横轴 = 用户活动（按执行顺序，backbone）；纵轴 = Story 按优先级/复杂度从上到下。**第一行横向 = walking skeleton**（最简可用版本）；逐行向下切片 = 渐进式增量，直接驱动 MVP 定义与 task-allocation 的迭代切片。

```markdown
# 故事地图

## Walking Skeleton（MVP 第一切片，必须完整可用旅程）
| Activity | 登录 | 创建 | 列表 |
|---|---|---|---|
| Story | F001 | F002 | F003 |

## 增量切片
### 切片 2（优先级 Should）
### 切片 3（优先级 Could）
```

> 为什么提升为一等产物：故事地图强制"首切片是完整可用用户旅程"，避免"先做高价值功能但因依赖未做的低价值功能无法上线"的反模式。task-allocation-skill 据此排迭代顺序，而非按孤立价值排序。

### 4. 原型 HTML（双稿）

进入前先读 `references/impeccable-wireframe.md`。两稿要求：

- **`prototype.html`（真源）**：单文件 HTML 内联 CSS；精致线框灰度调色板；覆盖主用户流 3-5 个关键页面；每页顶部标对应 Story ID；含交互注释；字段用真实业务名（不用 Lorem ipsum）。
- **`preview.html`（参考）**：由 impeccable `/impeccable craft` 产出；覆盖与 prototype.html 相同页面（一一对应不得增删）；顶部固定 banner 标注「⚠️ 氛围参考，非最终设计——视觉决策以 design 阶段为准」；已有项目分支复用既有令牌与组件 API；新项目分支按 impeccable 新项目规则从零设计；过 `/impeccable critique` + `/impeccable audit` 自检，评分写入 PRD「开放问题与风险」段。
- **降级**：impeccable 安装失败时仅产出 prototype.html，跳过 preview.html，PRD 顶部注明。

### 5. 机器可读 feature 清单（feature-checklist.json）

PRD 定稿后，把所有 Must/Should 级 feature 抽成机器可读清单（Anthropic 长跑 harness 的 Initializer 模式）。初始全部 `passes: false`，dev-skill 实现一个翻转一个，test-skill 验证后复核——这是防"假绿/过早宣告胜利"的载体契约（JSON 比 Markdown 更难被 agent 不当覆盖）：

```json
{
  "req_id": "req-001",
  "features": [
    { "id": "F001", "story": "作为访客我希望注册以便成为用户", "acceptance": "POST /api/register 返回 201；重复邮箱 409", "passes": false, "verified_by": "TC001,TC002" },
    { "id": "F002", "title": "...", "passes": false }
  ]
}
```

`project.feature_checklist_ref` 指向本文件。dev-skill 只允许改 `passes` 字段，不得删改 `acceptance`（已冻结测试意图）。

### 6. 追溯矩阵（traceability-matrix.md）

| 需求 ID | 来源/origin | 用户目标 | Story | 验收点 | 设计稿帧 | 测试用例 | 验证状态 | 版本 |
|---|---|---|---|---|---|---|---|---|
| F001 | 干系人@产品 | 注册成为用户 | S-001 | AC1 | 待设计 | 待编写 | pending | v0.1 |

> 为什么补 origin 与验证状态列：origin 强化后向追溯（这条需求从哪来，合规还是干系人）；验证状态（pending/passed/failed）让矩阵直接表达覆盖完成度，而非另开 test-results.md 才知道——review-skill 看到 pending 列即判需求未闭环。

### 7. 风险登记表（risks.md）

| ID | 类别 | 描述 | 概率 | 影响 | 评分 | Mitigation（降低概率） | Contingency（发生后的兜底） | Trigger（早期预警） | 负责人 | 状态 |
|---|---|---|---|---|---|---|---|---|---|---|

类别：技术可行性 / 需求模糊 / 依赖耦合 / 合规 / 资源 / 外部接口。

> 为什么补 Contingency 与 Trigger：Mitigation 是"降低概率"，Contingency 是"发生后的兜底"——对第三方 API 不稳这类风险，兜底比预防更关键；Trigger 给 review-skill 一个客观的"风险是否临近"判定依据，而非主观"概率高"。

### 8. 矛盾/缺口自动检查（consistency-check.md）

定稿前跑一次自动一致性检查（Kiro spec-driven 模式）：扫描 PRD/原型/追溯矩阵，输出：
- **Conflicts**：同一概念在 PRD/原型/矩阵中含义不一致；同一 Story 的验收点与原型字段不符。
- **Gaps**：追溯矩阵中有需求无验收点；有 Must 级 Story 无原型页面；NFR 段空写"暂无"但功能隐含性能要求。
- **Orphans**：原型页面无对应 Story；Story 无对应需求目标。

结果写入 `consistency-check.md`，作为 review-skill 三维评审中"需求完整性"维度的直接输入。

## 完成判定

- PRD.md 8 段齐全且非空；每条 Must/Should 需求至少 1 条 Given-When-Then 验收标准
- `prototype.html` 至少 3 页覆盖主用户流，精致线框风格；`preview.html` 至少 3 页一一对应（降级模式例外且 PRD 顶部注明）；preview 顶部含"氛围参考"标注
- `story-map.md` 标出 walking skeleton 与 MVP 切片
- `feature-checklist.json` 覆盖所有 Must/Should feature，初始全 `passes:false`
- 追溯矩阵覆盖所有 Must/Should 需求，origin/验证状态列非空
- 风险登记表至少 3 项，每项 Mitigation/Contingency/Trigger 齐全
- `consistency-check.md` 已产出，Conflicts 为 0（或已标注接受风险）
- 已过 impeccable「绝对禁止」清单与 AI slop 测试（或降级模式下过精要规则同等检查）
- state.json 更新：`phases.requirements.status = "done"`，`events[]` append phase_done，`project.feature_checklist_ref` 已填
- `resume_hint` 建议进入 design 阶段（`/nzw-design`）

## 与下游 skill 的交接契约

- `PRD.md` + `story-map.md` + `feature-checklist.json` 是 design-skill 的输入
- `traceability-matrix.md` + `consistency-check.md` 是 review-skill 做三方对齐的依据
- `risks.md` 中"技术可行性"类风险是 review-skill 重点核查项
- `feature-checklist.json` 是 dev-skill/test-skill 防假绿的共享契约（dev 翻 passes、test 复核）

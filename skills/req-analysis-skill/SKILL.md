---
name: req-analysis-skill
description: 需求调研分析技能，用于软件工程中的需求获取、分析和文档化。从用户输入中提炼结构化需求，输出需求文档、需求原型图（HTML）、追溯矩阵和风险登记表。当用户提到以下任何场景时务必使用此技能：需求分析、需求调研、需求梳理、需求文档、PRD编写、功能需求、非功能需求、干系人分析、需求分解，或任何需要将模糊想法或功能请求转化为严谨结构化需求文档的场景。即使用户没有明确提到"需求"，只要他们想在实际开发之前先明确系统该做什么，就应触发此技能。
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

**路径约定（v1.1）**：所有产出相对 `.nds/<active-req-id>/`，例如 `.nds/req-001/01-requirements/PRD.md`。需求隔离见顶层 `.nds/index.json`（schema 见 `templates/index.schema.json`）。

所有产出落到 `.nds/<req-id>/01-requirements/`：
- `PRD.md` — 需求文档主体
- `prototype.html` — 低保真原型（HTML，可在浏览器打开）
- `traceability-matrix.md` — 追溯矩阵（需求 ↔ 目标 ↔ Story ↔ 验收点）
- `risks.md` — 风险登记表
- `glossary.md` — 术语表

入口动作：
1. 读取或初始化 `.nds/index.json`：
   - 不存在 → 初始化，`requirements: []`，`active_req_id: null`
   - 用户输入是新需求 → 生成下一编号 `req-NNN`（`req-001` 起，三位补零），追加到 `requirements[]` 并设为 `active_req_id`，创建子目录 `.nds/req-NNN/`
   - 续作已有需求 → 用 `--req <id>` 或 `index.active_req_id`
2. 在 `.nds/<req-id>/` 下初始化 `state.json`（schema 见 `templates/state.schema.json`，`version: "1.1"`，`project.req_id` 填入），`project.current_phase = "requirements"`，`phases.requirements.status = "in_progress"`
3. `project.name`、`project.goal` 从用户输入提炼；同步回写 `index.json` 中该 req 的 `name`/`goal`/`current_phase`/`updated_at`
4. 完成后写 `resume_hint`，更新 `.nds/<req-id>/PROGRESS.md` 与顶层 `.nds/PROGRESS.md`（总览）

## 主导思想

- **Outcome over Output**：需求以用户可衡量的结果为导向，而非功能清单。
- **先问题后方案**：在描述功能前先明确"用户要完成的 Job 是什么"和"当前为什么做不到"。
- **Continuous Discovery**：需求是持续活动，PRD 是 living document，不一次性锁死。
- **可追溯是底线**：每条需求从来源到验收点双向链接。

## 执行流程

### 1. 干系人与问题挖掘

- 识别干系人（用户/决策者/运维/合规）
- 用 Jobs-to-be-Done 表达：`当 [情境]，我想 [做某事]，以便 [达成某价值]`
- 列出当前痛点与未满足的 Job
- 若用户输入过短，主动追问 3 个问题：目标用户是谁？成功指标是什么？有哪些不能做的（Non-goals）？

### 2. PRD 文档结构

```markdown
# {{项目名}} PRD

## 元数据
- 版本 / 日期 / 作者 / 状态

## 1. 问题陈述
  用户是谁、要完成的 Job、当前为什么做不到、本项目的目标

## 2. 目标与成功指标
  - North Star Metric
  - OKR（1 个 O + 2-3 个 KR）
  - Non-goals（显式列出不做的事）

## 3. 用户与场景
  - Persona
  - User Story Mapping（骨架：Activity → Step → Story）
  - 关键用户旅程

## 4. 功能需求（按 MoSCoW 优先级）
  每条 Story 格式：
  - ID: F001
  - 作为 <角色>，我希望 <动作>，以便 <价值>
  - 验收标准：Given / When / Then（至少 1 条，可测）
  - 优先级：Must / Should / Could / Won't
  - 来源：用户/干系人/合规

## 5. 非功能需求
  - 性能（响应时间、吞吐、并发）
  - 安全（认证、授权、数据保护、合规）
  - 可用性（SLA、容灾、降级）
  - 可访问性（WCAG 2.2 AA）
  - 可观测性（日志、指标、追踪）
  - 兼容性（浏览器、设备、OS）

## 6. 技术约束
  技术栈倾向、依赖、集成接口、部署环境

## 7. 开放问题与风险
  指向 risks.md

## 8. 变更日志
  版本 / 日期 / 变更 / 影响
```

### 3. 原型 HTML（低保真）

`prototype.html` 要求：
- 单文件 HTML（内联 CSS），浏览器直开
- 用线框风格（灰底黑线），不涉及视觉设计（留给 design-skill）
- 覆盖主用户流的 3-5 个关键页面
- 每个页面顶部标注对应 Story ID
- 包含交互注释（点击跳转、表单字段说明）

### 4. 追溯矩阵

`traceability-matrix.md`：

| 需求 ID | 用户目标 | Story | 验收点 | 设计稿帧 | 测试用例 | 版本 |
|---|---|---|---|---|---|---|
| F001 | ... | S-001 | AC1 | 待设计 | 待编写 | v0.1 |

设计/开发/测试阶段会回填后续列。

### 5. 风险登记表

`risks.md`：

| ID | 类别 | 描述 | 概率 | 影响 | 评分 | 应对策略 | 负责人 | 状态 |
|---|---|---|---|---|---|---|---|---|
| R001 | 技术 | ... | 高 | 高 | 9 | Mitigate: POC 验证 | ... | open |

类别：技术可行性 / 需求模糊 / 依赖耦合 / 合规 / 资源 / 外部接口。

## 必须遵守的规则

1. **每条需求至少一条可执行验收标准**（Given-When-Then）。无法写验收标准的需求继续追问，不能放过。
2. **非功能需求不可省略**：性能、安全、可用性、可访问性必须显式列出，哪怕只写"暂无特殊要求"。
3. **Non-goals 必写**：明确"不做什么"比"做什么"更能防止范围蔓延。
4. **术语统一**：同一概念在 PRD/原型/矩阵中用同一个词，写入 `glossary.md`。
5. **变更留痕**：任何修改走 `变更日志`，不删除历史版本。
6. **INVEST 检查**：每条 Story 检查 Independent/Negotiable/Valuable/Estimable/Small/Testable，不达标的继续拆。

## 完成判定

- PRD.md 包含上述 8 个段落，且非空
- 原型 HTML 至少 3 个页面
- 追溯矩阵覆盖所有 Must 与 Should 需求
- 风险登记表至少识别 3 项风险
- state.json 更新完毕，`phases.requirements.status = "done"`
- `resume_hint` 写明下一步：建议进入 design 阶段（`/nzw-design`）

## 与下游 skill 的交接契约

- `.nds/<req-id>/01-requirements/PRD.md` 是 design-skill 的输入
- `traceability-matrix.md` 是 review-skill 做三方对齐的依据
- `risks.md` 中"技术可行性"类风险是 review-skill 重点核查项

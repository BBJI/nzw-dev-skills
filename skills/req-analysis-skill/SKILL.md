---
name: req-analysis-skill
description: 需求调研分析技能，用于软件工程中的需求获取、分析和文档化。从用户输入中提炼结构化需求，输出需求文档、需求原型图（HTML）、追溯矩阵和风险登记表。原型层委托 impeccable 引擎（缺失自动安装）：产出"精致线框"（prototype.html，真源）与"高保真氛围预览"（preview.html，参考）双稿并存——前者锁定结构与流程，后者让干系人直观感受产品气质，但不锁定最终视觉决策。当用户提到以下任何场景时务必使用此技能：需求分析、需求调研、需求梳理、需求文档、PRD编写、功能需求、非功能需求、干系人分析、需求分解，或任何需要将模糊想法或功能请求转化为严谨结构化需求文档的场景。即使用户没有明确提到"需求"，只要他们想在实际开发之前先明确系统该做什么，就应触发此技能。
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
- `prototype.html` — 精致线框（HTML，可在浏览器打开，**真源**）
- `preview.html` — impeccable 高保真氛围预览（HTML，**参考**，不锁定视觉决策）
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
4. **执行 impeccable 前置**（见「原型执行引擎 → 0. 前置」）：检测 impeccable 是否已安装，缺失则 `npx impeccable install` 自动安装后继续；安装失败则降级到内置精要规则（仅产出 prototype.html，跳过 preview.html，并在 PRD 顶部注明）
5. 完成后写 `resume_hint`，更新 `.nds/<req-id>/PROGRESS.md` 与顶层 `.nds/PROGRESS.md`（总览）

## 主导思想

- **Outcome over Output**：需求以用户可衡量的结果为导向，而非功能清单。
- **先问题后方案**：在描述功能前先明确"用户要完成的 Job 是什么"和"当前为什么做不到"。
- **Continuous Discovery**：需求是持续活动，PRD 是 living document，不一次性锁死。
- **可追溯是底线**：每条需求从来源到验收点双向链接。
- **结构与氛围分离**：原型层只回答"系统有什么、用户怎么走"，不回答"产品长什么样"——视觉决策留给 design-skill。但"不回答视觉"不等于"可以丑"：用 impeccable 的排版/间距/布局纪律让线框专业可读，另出一份高保真氛围稿帮助干系人感知产品气质。

## 原型执行引擎：impeccable

本技能的**结构层**（页面、字段、流程、注释）由 PRD 主导；**视觉呈现层**委托给 [impeccable](https://github.com/pbakaus/impeccable)（Apache-2.0，作者 Paul Bakaus）——让线框稿告别"灰底黑线难看方框"，同时通过一份独立的高保真预览让干系人直观感受产品方向，**但不锁定最终视觉决策**（颜色、品牌、组件 API 仍归 design-skill）。

> 归属：impeccable © Paul Bakaus，Apache License 2.0。本仓库仅引用其方法论与安装方式，不二次分发其源码。

### 0. 前置：确保 impeccable 已安装（缺失则自动安装）

进入原型产出前**必须**先确认 impeccable 可用，否则自动安装后继续：

1. 检测以下任一存在即视为已安装：
   - 项目内 `.claude/skills/impeccable/SKILL.md`
   - 用户级 `~/.claude/skills/impeccable/SKILL.md`
   - `/impeccable` 斜杠命令可用
2. 若均不存在，在**项目根目录**自动执行安装（不要询问，装完即继续）：
   ```bash
   npx impeccable install
   ```
   - 安装后重新检测，确认 `impeccable` 已就绪。
3. 降级路径：仅当 `npx` 不可用或安装失败时，回退到本技能内置的「impeccable 精要规则」手工产出 prototype.html（**跳过 preview.html**），并在 PRD 顶部注明「impeccable 未安装，仅产出线框稿，未生成高保真氛围预览」，提示用户后续可 `npx impeccable install` 后补 preview.html。

> impeccable 的 setup 流程要求先运行 `node .claude/skills/impeccable/scripts/context.mjs` 读取/生成 `PRODUCT.md`、`DESIGN.md`。nzw 场景下 PRD 阶段正在编写 PRD.md 本身，可先把已完成的 PRD 草稿作为 PRODUCT 上下文喂给 impeccable；DESIGN.md 留空或仅写"req 阶段不锁定视觉"，避免与 design-skill 冲突。

### 1. 双稿分工

| 稿件 | 文件 | 角色 | 视觉决策权 |
|---|---|---|---|
| 精致线框 | `prototype.html` | **真源**——结构、字段、流程、注释、Story ID 标注的载体 | 不涉及（灰度+排版纪律） |
| 高保真氛围预览 | `preview.html` | **参考**——让干系人感知产品气质，便于早期对齐方向 | 暂时性视觉决策（design 阶段可推翻） |

**硬约束**：当两稿冲突时，以 `prototype.html` 为准；`preview.html` 不得引入 PRD 未提到的页面、字段或流程。`preview.html` 顶部必须标注「氛围参考，非最终设计——视觉决策以 design 阶段为准」。

### 2. 分支判定：新项目 vs 已有项目

判定信号——扫描项目代码，是否已存在**已提交的** CSS 令牌 / 主题 / 品牌色 / 现成页面与组件：

| 信号 | 判定 |
|---|---|
| 存在 `tokens.*` / `theme.*` / tailwind config / CSS 变量定义 / 现成页面与组件 | **已有项目** |
| 仅有脚手架、无任何设计系统或品牌色 | **新项目** |

### 2-A. 已有项目 → impeccable + 当前项目页面风格（identity-preservation 优先）

1. 读取当前页面风格：扫描现有 CSS / tokens / theme / 代表性组件与页面，记录配色、字体、间距、圆角。
2. `prototype.html`：用项目既有字体与间距尺度，但配色压到灰度（避免在 req 阶段就锁定品牌色应用方式）。
3. `preview.html`：`/impeccable document` 从现有代码生成 `DESIGN.md` 捕获当前视觉系统，`/impeccable craft` 产出预览页面，**复用既有令牌与组件 API**，不得引入与原项目冲突的新令牌。

### 2-B. 新项目 → impeccable 从零设计（氛围级）

1. `/impeccable init` 写 `PRODUCT.md`/`DESIGN.md`，确定 register（brand 营销/落地页/作品集 vs product 应用/仪表盘/工具）。
2. 运行 `node .claude/skills/impeccable/scripts/palette.mjs` 取品牌种子色，按 OKLCH 构建调色板。
3. `/impeccable shape` 规划 UX/UI，`/impeccable craft` 实现关键页面作为 `preview.html`；遵循 impeccable「新项目」色与主题规则（OKLCH、明确色策略、避免 2026 饱和的 cream/sand 默认底色）。
4. 在 `preview.html` 顶部明确标注"氛围参考，颜色/字体/组件均可在 design 阶段调整"。

### 3. 输出映射（impeccable ↔ nzw 产物）

| impeccable 产物 | nzw 落位 |
|---|---|
| `PRODUCT.md`（impeccable init 产出） | 摘要并入 `PRD.md` 的问题陈述与目标段；PRODUCT.md 本身不单独留存 |
| `DESIGN.md`（impeccable init/document 产出） | 仅作 `preview.html` 的视觉系统依据，不并入 PRD（避免 req 阶段锁定视觉） |
| `palette.mjs` 调色板输出 | 仅用于 `preview.html`；不得回写 PRD 或 prototype.html |
| `/impeccable craft` 产出的页面 | `preview.html`（含氛围参考 banner，对应 prototype.html 页面一一映射） |
| `/impeccable critique` / `audit` 评分与发现 | `PRD.md`「开放问题与风险」段（作为 req 阶段识别出的设计风险，供 design 阶段参考）+ `risks.md` 中"技术可行性"类风险 |

### 4. impeccable 精要规则（降级时亦须遵循）

即便 impeccable 未安装而降级，以下规则为硬约束（完整版见 impeccable `reference/` 与 SKILL.md）：

- **颜色（线框模式）**：线框稿只用灰度（neutral scale），正文对比度 ≥ 4.5:1；占位文字同样 4.5:1。`preview.html` 不在此约束内，但仍需过 impeccable 对比度规则。
- **排版**：正文行宽 65–75ch；字体配对走对比轴（衬线+无衬线 / 几何+人文），勿用相似字体；display 标题 `clamp()` 上限 ≤ 6rem，letter-spacing ≥ -0.04em；`text-wrap: balance`（h1–h3）/ `pretty`（长文）。
- **布局**：间距有节奏不均一；1D 用 Flex、2D 用 Grid；无断点响应网格用 `repeat(auto-fit, minmax(280px, 1fr))`；语义化 z-index 层级，禁用 999/9999。
- **动效**：线框稿原则上不动效（仅必要过渡）；`preview.html` 的动效遵循 impeccable 意图化、ease-out 指数曲线、`prefers-reduced-motion` 必备等规则。
- **绝对禁止**（match-and-refuse，命中即重写结构）：侧边条边框（`border-left/right` > 1px 做彩色强调）、渐变文字（`background-clip:text`+渐变）、装饰性玻璃拟态、hero-metric 模板（大数字+小标签+渐变）、雷同卡片网格、每节上方小号大写 tracked eyebrow、`01/02/03` 编号脚手架（非真实有序流时）、文字溢出容器。
- **AI slop 测试**：若有人能一眼断定「AI 做的」即失败。

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

### 3. 原型 HTML（双稿）

#### 3.1 `prototype.html` — 精致线框（真源）

要求：
- 单文件 HTML（内联 CSS），浏览器直开
- **精致线框**风格：灰度调色板（neutral scale），用 impeccable 排版/间距/布局纪律让线框专业可读——不是"灰底黑线难看方框"，但也不引入品牌色/渐变/装饰
- 覆盖主用户流的 3-5 个关键页面
- 每个页面顶部标注对应 Story ID
- 包含交互注释（点击跳转、表单字段说明、状态说明）
- 字段说明用真实业务字段名（与 PRD 一致），不用 Lorem ipsum

#### 3.2 `preview.html` — impeccable 高保真氛围预览（参考）

要求：
- 单文件 HTML（内联 CSS），浏览器直开
- 由 impeccable `/impeccable craft` 产出，含配色、字体、组件、动效
- 覆盖与 prototype.html 相同的 3-5 个关键页面（一一对应，不得增删）
- 顶部固定 banner 标注「⚠️ 氛围参考，非最终设计——视觉决策以 design 阶段为准」
- 已有项目分支：复用既有令牌与组件 API，identity-preservation 优先
- 新项目分支：按 impeccable「新项目」规则从零设计（OKLCH 调色板、明确 register）
- 通过 impeccable `/impeccable critique` + `/impeccable audit` 自检，评分写入 PRD「开放问题与风险」段（作为 req 阶段识别出的设计风险，供 design 阶段参考）

**降级模式**：impeccable 未安装且安装失败时，仅产出 prototype.html，跳过 preview.html，并在 PRD 顶部注明。

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
7. **双稿真源一致**：`prototype.html` 是结构真源；`preview.html` 不得引入 PRD 未提到的页面、字段或流程。两稿冲突时以 prototype.html 为准。
8. **req 阶段不锁定视觉决策**：`preview.html` 顶部必须标注"氛围参考，非最终设计"；颜色、品牌、组件 API 的最终决策权归 design-skill。已有项目分支下，impeccable 默认调色板不得覆盖项目既有品牌色与令牌命名。
9. **impeccable 引擎优先**：视觉呈现层委托 impeccable；缺失时按「impeccable 精要规则」降级（仅产出 prototype.html，跳过 preview.html），但精要规则中的「绝对禁止」与对比度约束在任何模式下都是硬约束。
10. **AI slop 零容忍**：交付前过 impeccable「绝对禁止」清单与 AI slop 测试，命中任一即重写。

## 完成判定

- PRD.md 包含上述 8 个段落，且非空
- `prototype.html` 至少 3 个页面，覆盖主用户流，精致线框风格
- `preview.html` 至少 3 个页面，与 prototype.html 一一对应（降级模式例外：仅当 impeccable 安装失败时允许跳过，且 PRD 顶部须注明）
- `preview.html` 顶部含"氛围参考"标注
- 追溯矩阵覆盖所有 Must 与 Should 需求
- 风险登记表至少识别 3 项风险
- 已过 impeccable「绝对禁止」清单与 AI slop 测试（或降级模式下过精要规则同等检查）
- state.json 更新完毕，`phases.requirements.status = "done"`
- `resume_hint` 写明下一步：建议进入 design 阶段（`/nzw-design`）

## 与下游 skill 的交接契约

- `.nds/<req-id>/01-requirements/PRD.md` 是 design-skill 的输入
- `traceability-matrix.md` 是 review-skill 做三方对齐的依据
- `risks.md` 中"技术可行性"类风险是 review-skill 重点核查项

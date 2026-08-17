# impeccable 集成指南（需求/原型层）

> 本文件是 req-analysis-skill 的按需加载参考。进入原型产出前必读。design-skill 有独立的 `references/impeccable-design.md`（设计层口径不同，勿混用）。

本技能的**结构层**（页面、字段、流程、注释）由 PRD 主导；**视觉呈现层**委托给 [impeccable](https://github.com/pbakaus/impeccable)（Apache-2.0，作者 Paul Bakaus）——让线框稿告别"灰底黑线难看方框"，同时通过一份独立的高保真预览让干系人直观感受产品方向，**但不锁定最终视觉决策**（颜色、品牌、组件 API 仍归 design-skill）。

> 归属：impeccable © Paul Bakaus，Apache License 2.0。本仓库仅引用其方法论与安装方式，不二次分发其源码。

## 0. 前置：确保 impeccable 已安装（缺失则自动安装）

进入原型产出前先确认 impeccable 可用，否则自动安装后继续：

1. 检测以下任一存在即视为已安装：项目内 `.claude/skills/impeccable/SKILL.md`、用户级 `~/.claude/skills/impeccable/SKILL.md`、`/impeccable` 斜杠命令可用。
2. 若均不存在，在**项目根目录**自动执行安装（不要询问，装完即继续）：
   ```bash
   npx impeccable install
   ```
   安装后重新检测，确认 `impeccable` 已就绪。
3. 降级路径：仅当 `npx` 不可用或安装失败时，回退到本文件「精要规则」手工产出 prototype.html（**跳过 preview.html**），并在 PRD 顶部注明「impeccable 未安装，仅产出线框稿，未生成高保真氛围预览」，提示用户后续可 `npx impeccable install` 后补 preview.html。

> impeccable 的 setup 流程要求先运行 `node .claude/skills/impeccable/scripts/context.mjs` 读取/生成 `PRODUCT.md`、`DESIGN.md`。nzw 场景下 PRD 阶段正在编写 PRD.md 本身，可先把已完成的 PRD 草稿作为 PRODUCT 上下文喂给 impeccable；DESIGN.md 留空或仅写"req 阶段不锁定视觉"，避免与 design-skill 冲突。

## 1. 双稿分工

| 稿件 | 文件 | 角色 | 视觉决策权 |
|---|---|---|---|
| 精致线框 | `prototype.html` | **真源**——结构、字段、流程、注释、Story ID 标注的载体 | 不涉及（灰度+排版纪律） |
| 高保真氛围预览 | `preview.html` | **参考**——让干系人感知产品气质，便于早期对齐方向 | 暂时性视觉决策（design 阶段可推翻） |

**硬约束**：当两稿冲突时，以 `prototype.html` 为准；`preview.html` 不得引入 PRD 未提到的页面、字段或流程。`preview.html` 顶部必须标注「氛围参考，非最终设计——视觉决策以 design 阶段为准」。

### 为什么双稿并存（不是随手设计，是四条权威依据的交汇）

v0/Figma Make 这类 AI 工具默认产单稿（直接高保真或直接代码），nzw 选双稿是主动反潮流的工程决策。理由：

1. **UX 传统双轨**：线框图（锁定结构/信息架构/流程，灰度）与高保真稿（锁定视觉/品牌/动效）是 UX 行业数十年事实分工（Nielsen Norman Group 亦区分二者）。
2. **W3C 令牌哲学**：令牌（结构/语义）与渲染（具体值应用）分离，正是"结构真源↔氛围渲染"的同构。
3. **spec-kit 范式**：specify（what/why）先于 plan（how），与"prototype.html 锁结构、preview.html 渲染氛围"同构。
4. **单一真源（SSOT）**：业界普遍要求"冲突时以结构真源为准"，"preview.html 不得引入 PRD 未提到的页面/字段/流程"正是 SSOT 落地。

AI 单稿易"视觉漂亮但结构漂移"，双稿用 prototype.html 锁结构防漂移。未来若有人想"简化"成单稿，先回答这四条依据。

## 2. 分支判定：新项目 vs 已有项目

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

## 3. 输出映射（impeccable ↔ nzw 产物）

| impeccable 产物 | nzw 落位 |
|---|---|
| `PRODUCT.md`（impeccable init 产出） | 摘要并入 `PRD.md` 的问题陈述与目标段；PRODUCT.md 本身不单独留存 |
| `DESIGN.md`（impeccable init/document 产出） | 仅作 `preview.html` 的视觉系统依据，不并入 PRD（避免 req 阶段锁定视觉） |
| `palette.mjs` 调色板输出 | 仅用于 `preview.html`；不得回写 PRD 或 prototype.html |
| `/impeccable craft` 产出的页面 | `preview.html`（含氛围参考 banner，对应 prototype.html 页面一一映射） |
| `/impeccable critique` / `audit` 评分与发现 | `PRD.md`「开放问题与风险」段（作为 req 阶段识别出的设计风险，供 design 阶段参考）+ `risks.md` 中"技术可行性"类风险 |

## 4. impeccable 精要规则（降级时亦须遵循）

即便 impeccable 未安装而降级，以下规则为硬约束（完整版见 impeccable `reference/` 与 SKILL.md）：

- **颜色（线框模式）**：线框稿只用灰度（neutral scale），正文对比度 ≥ 4.5:1；占位文字同样 4.5:1。`preview.html` 不在此约束内，但仍需过 impeccable 对比度规则。
- **排版**：正文行宽 65–75ch；字体配对走对比轴（衬线+无衬线 / 几何+人文），勿用相似字体；display 标题 `clamp()` 上限 ≤ 6rem，letter-spacing ≥ -0.04em；`text-wrap: balance`（h1–h3）/ `pretty`（长文）。
- **布局**：间距有节奏不均一；1D 用 Flex、2D 用 Grid；无断点响应网格用 `repeat(auto-fit, minmax(280px, 1fr))`；语义化 z-index 层级，禁用 999/9999。
- **动效**：线框稿原则上不动效（仅必要过渡）；`preview.html` 的动效遵循 impeccable 意图化、ease-out 指数曲线、`prefers-reduced-motion` 必备等规则。
- **绝对禁止**（match-and-refuse，命中即重写结构）：侧边条边框（`border-left/right` > 1px 做彩色强调）、渐变文字（`background-clip:text`+渐变）、装饰性玻璃拟态、hero-metric 模板（大数字+小标签+渐变）、雷同卡片网格、每节上方小号大写 tracked eyebrow、`01/02/03` 编号脚手架（非真实有序流时）、文字溢出容器。
- **AI slop 测试**：若有人能一眼断定「AI 做的」即失败。

# impeccable 集成指南（设计层）

> 本文件是 design-skill 的按需加载参考。进入设计实现前必读。req-analysis-skill 有独立的 `references/impeccable-wireframe.md`（原型/线框层口径不同，勿混用）。

本技能负责**契约层**（令牌、组件 API、流程、规范文档）；视觉与交互的**实现层**委托给 [impeccable](https://github.com/pbakaus/impeccable)（Apache-2.0，作者 Paul Bakaus）——一套面向前端的设计流利度技能，含 23 个子命令（`init`/`shape`/`craft`/`critique`/`audit`/`polish`/`bolder`/`quieter`/`animate`/`colorize`/`typeset`/`layout`/`extract`/`document`/`live`…）与 44 条确定性反模式检测规则。

> 归属：impeccable © Paul Bakaus，Apache License 2.0。本仓库仅引用其方法论与安装方式，不二次分发其源码。

## 0. 前置：确保 impeccable 已安装（缺失则自动安装）

进入设计实现前先确认 impeccable 可用，否则自动安装后继续：

1. 检测以下任一存在即视为已安装：项目内 `.claude/skills/impeccable/SKILL.md`、用户级 `~/.claude/skills/impeccable/SKILL.md`、`/impeccable` 斜杠命令可用。
2. 若均不存在，在**项目根目录**自动执行安装（不要询问，装完即继续）：
   ```bash
   npx impeccable install
   ```
   安装后重新检测，确认 `impeccable` 已就绪。
3. 降级路径：仅当 `npx` 不可用或安装失败时，回退到本文件「精要规则」手工产出设计稿，并在 `design-spec.md` 顶部注明「impeccable 未安装，按精要规则降级实现」，提示用户后续可 `npx impeccable install` 获得完整能力（live 浏览器迭代、detector、palette 脚本等）。

> impeccable 的 setup 流程要求先运行 `node .claude/skills/impeccable/scripts/context.mjs` 读取/生成 `PRODUCT.md`、`DESIGN.md`。nzw 场景下若 `.nds/<req-id>/01-requirements/PRD.md` 已存在，可将其作为 PRODUCT 上下文喂给 impeccable，避免重复采集。

## 1. 分支判定：新项目 vs 已有项目

判定信号——扫描项目代码，是否已存在**已提交的** CSS 令牌 / 主题 / 品牌色 / 现成页面与组件：

| 信号 | 判定 |
|---|---|
| 存在 `tokens.*` / `theme.*` / tailwind config / CSS 变量定义 / 现成页面与组件 | **已有项目** |
| 仅有脚手架、无任何设计系统或品牌色 | **新项目** |

### 1-A. 已有项目 → impeccable + 当前项目页面风格（identity-preservation 优先）

**核心原则：不要重造风格，用项目已有的令牌与组件作为锚，impeccable 负责保持一致地扩展。**

1. 读取当前页面风格：扫描现有 CSS / tokens / theme / 代表性组件与页面，记录配色、字体、间距、圆角、动效、组件结构。
2. 运行 `/impeccable document` 从现有代码生成 `DESIGN.md`，捕获当前视觉系统；必要时 `/impeccable extract` 把可复用令牌与组件抽入设计系统。
3. 以现有令牌为约束，用 `/impeccable shape` 规划新页面 UX/UI，`/impeccable craft` 实现；新产出必须复用既有色板、字体、间距尺度、组件 API，不得引入与原项目冲突的新令牌。
4. 将抽取/对齐后的令牌回写为 nzw `design-tokens.json`（Reference → System → Component 三层），**保留原项目命名与色值**（identity-preservation 胜过 impeccable 默认调色板）。
5. `/impeccable critique` + `/impeccable audit` 对新页面做一致性/可达性/性能自检，评分写入 `design-spec.md`。

### 1-B. 新项目 → impeccable 从零设计

1. `/impeccable init` 写 `PRODUCT.md`/`DESIGN.md`，确定 register（brand 营销/落地页/作品集 vs product 应用/仪表盘/工具）。
2. 运行 `node .claude/skills/impeccable/scripts/palette.mjs` 取品牌种子色，按 OKLCH 构建调色板（bg/surface/ink/accent/muted）。
3. `/impeccable shape` 规划 UX/UI，`/impeccable craft` 实现关键页面；遵循 impeccable「新项目」色与主题规则（OKLCH、明确色策略、避免 2026 饱和的 cream/sand 默认底色）。
4. 将 impeccable 调色板 / 排版 / 动效映射为 nzw `design-tokens.json` 三层令牌。

## 2. 输出映射（impeccable ↔ nzw 产物）

| impeccable 产物 | nzw 落位 |
|---|---|
| `PRODUCT.md` / `DESIGN.md` | 摘要并入 `design-spec.md` 的设计原则与色彩/排版/动效系统段落 |
| 调色板 / 令牌 / palette.mjs 输出 | `design-tokens.json`（Reference→System→Component 三层） |
| `/impeccable craft` 产出的页面 | `hifi-pages/*.html`（注入真实令牌 CSS 变量、真实数据、响应式、暗色模式、a11y） |
| `/impeccable craft` 产出的组件 | `components/<name>.md`（规格）+ `components/<name>.html`（高保真样例） |
| `/impeccable critique` / `audit` 评分与发现 | `design-spec.md`「设计自检」段落 + `interaction-notes.html` 中的微交互修正 |
| `/impeccable live` 浏览器迭代结果 | 替换对应 `hifi-pages/` 与 `components/` 文件 |

## 3. impeccable 精要规则（降级时亦须遵循）

即便 impeccable 未安装而降级，以下规则为硬约束（完整版见 impeccable `reference/` 与 SKILL.md）：

- **颜色**：正文对比度 ≥ 4.5:1，大字（≥18px 或 bold ≥14px）≥ 3:1，占位符同样 4.5:1；用 OKLCH；灰字压在彩色底上必失败，改用底色同色相的更深色或文字色透明度。
- **排版**：正文行宽 65–75ch；字体配对走对比轴（衬线+无衬线 / 几何+人文），勿用相似字体；display 标题 `clamp()` 上限 ≤ 6rem，letter-spacing ≥ -0.04em；`text-wrap: balance`（h1–h3）/ `pretty`（长文）。
- **布局**：间距有节奏不均一；卡片是偷懒答案、嵌套卡片必错；1D 用 Flex、2D 用 Grid；无断点响应网格用 `repeat(auto-fit, minmax(280px, 1fr))`；语义化 z-index 层级（dropdown < sticky < modal-backdrop < modal < toast < tooltip），禁用 999/9999。
- **动效**：意图化、非事后补丁；勿动画化布局属性；ease-out 用指数曲线（quart/quint/expo），无 bounce/elastic；`prefers-reduced-motion` 必备；reveal 动画必须增强已可见的默认态，不得用 class 触发 gating 内容可见性。
- **绝对禁止**（match-and-refuse，命中即重写结构）：侧边条边框（`border-left/right` > 1px 做彩色强调）、渐变文字（`background-clip:text`+渐变）、装饰性玻璃拟态、hero-metric 模板（大数字+小标签+渐变）、雷同卡片网格、每节上方小号大写 tracked eyebrow、`01/02/03` 编号脚手架（非真实有序流时）、文字溢出容器。
- **AI slop 测试**：若有人能一眼断定「AI 做的」即失败。两层反射检查：从品类能猜出主题+色板（一阶反射）、从品类+反例能猜出审美家族（二阶反射），均需重做直到答案不再显然。

---
name: review-skill
description: 三维度实现评估技能，在投入开发前同时从需求完整性、UI/UX 设计可实现性、技术可行性三维度评估软件方案，识别跨维度缺口/不一致/风险，产出 Issue/Risk/Decision 三件套 + 准入签字作为开发闸门。当用户提到以下任一场景时务必使用：实现评估、方案评审、可行性评审、需求评审、技术评审、设计评审、开发前评审、准入评审、规格验证、DoR 检查，或需要在投入开发前验证需求/设计/技术方案是否一致完整。即使用户只说"评审"，只要在软件开发上下文中就应触发。不适用于代码评审（用 dev-skill 提交前自检）或上线后缺陷复盘（用 test-skill）。
metadata:
  type: nzw-dev-skills
  phase: review
  trigger: /nzw-review
---

# 三维实现评估技能（review-skill）

在投入开发前，从**需求完整性 / UX 可实现性 / 技术可行性**三维度对方案做一致性校验，产出 Issue / Risk / Decision 三件套，作为开发的准入闸门。

主导思想：**Shift-Left Quality** —— 缺陷在需求/设计阶段修复的成本是代码阶段的 10-100 倍，评审是最高 ROI 的质量活动。本 skill 同时扮演**怀疑式评估器**：独立于 dev-skill，按硬阈值打分，不达标就 fail 并回传具体可执行的问题清单（Anthropic 长跑 harness 模式——开箱 LLM 倾向夸赞自己的工作，必须用独立怀疑视角对冲）。

## 何时触发

- 用户输入 `/nzw-review`
- 自然语言提到"评审/可行性/准入/Pre-Review"等
- workflow-skill 在闭环中进入 review 阶段

## 工作目录与状态

产出落到 `.nds/<req-id>/03-review/`：
- `review-report.md` — 评审总报告（三维 checklist 结果 + 评估器评分）
- `issues.md` — 问题清单（含严重度分级）
- `decisions.md` — 决策日志
- `sign-off.md` — 准入签字记录（三维各自结果，非整体一句）
- `evaluation.json` — 机器可读评估结果（硬阈值打分，喂给 workflow 门禁）

入口动作：
1. 读 `.nds/index.json` 确定 `active_req_id`，再读 `.nds/<req-id>/state.json`，确认 requirements 与 design 阶段已 done。
2. `project.current_phase = "review"`，`phases.review.status = "in_progress"`；同步回写 `index.json`。
3. 评审完成后根据是否有 Blocker 决定 `status`：done / blocked（回流上游）；向 `events[]` append。

## 评审三维度检查清单（含"怎么查"）

每条都给出客观检测方式——不靠主观判断，靠可执行检查。

### 维度 1：需求完整性（含 DoR 准入门）

| 检查项 | 怎么查（客观信号） |
|---|---|
| 每条需求 ≥1 条 Given-When-Then 验收标准 | grep PRD.md `## 4`，每条 Story 必有 `验收标准` 段；`consistency-check.md` 中 Gaps=0 |
| 非功能需求齐全（性能/安全/可用性/可访问性/合规） | PRD `## 5` 五个子项均非空（"暂无"也算显式声明） |
| 边界与异常路径覆盖 | 验收标准含负向场景（重复/越界/并发/宕机） |
| 依赖与前置条件明确 | 追溯矩阵 origin 列非空；risks.md 含"依赖耦合"类 |
| 与上层目标（OKR）对齐 | 每条 Must 级 Story 能追溯到 §2 的 KR |
| Non-goals 显式 | PRD §2 含 Non-goals 段且非空 |
| **DoR 准入**：Story 已被充分理解、验收标准已写、已估算或已拆到可估算、无 open blocker | `feature-checklist.json` 覆盖所有 Must/Should；追溯矩阵验证状态列无 pending；risks 无 open 的 Blocker 级 |

### 维度 2：UX/UI 可实现性

| 检查项 | 怎么查 |
|---|---|
| 设计稿覆盖所有主要用户流 | user-flows.md 的每条 flow 对应 PRD Story ID；hifi-pages/ 覆盖 walking skeleton |
| 组件复用设计系统，无重复造轮 | components/ 清单去重；新组件必须有复用理由 |
| 组件规格六段齐全，States 覆盖 loading/empty/error/disabled | 逐个 components/*.md 检查 Anatomy/States/Props/Variants/A11y/Do-Don't；States 表含四态 |
| 交互状态完整（空/载/错/禁用/loading） | interaction-notes.html 含五态 |
| 响应式断点明确 + container query | design-spec.md §3 含断点令牌与 container query 策略 |
| 无障碍（WCAG 2.2 AA：对比度 4.5:1/3:1、键盘可达、焦点可见、目标尺寸 ≥24×24px） | hifi-pages 用对比度检查器（如浏览器 DevTools Lighthouse/Axe）抽样；focus-visible 存在；按钮/链接尺寸达标 |
| 设计令牌分层正确，无魔数 | design-tokens.json 三层齐全；grep hifi-pages 无硬编码色值/间距（应全用 CSS 变量） |
| 信息架构与用户流程互补 | information-architecture.md 产出；IA 层级与 user-flows 不冲突 |

### 维度 3：技术可行性

| 检查项 | 怎么查 |
|---|---|
| 架构图覆盖数据流/调用链/部署 | 有架构图（mermaid 或附件）覆盖三视图 |
| API 契约已定义（请求/响应/错误码） | components/ 或独立 api-spec 含完整契约 |
| 技术选型有 POC 或参考案例 | risks.md 中"技术可行性"类风险有 Mitigation=POC 验证计划 |
| 性能与容量有估算 | 对照 PRD NFR 性能项有估算 |
| 安全威胁建模（STRIDE）完成 | 有 STRIDE 六类分析（ spoofing/tampering/repudiation/info disclosure/denial/elevation） |
| 第三方依赖与许可证审查 | 依赖清单含许可证；无 GPL 污染商业代码 |
| 可观测性方案（日志/指标/追踪） | 有方案段落 |
| 回滚策略 | 有回滚步骤 |

### 维度 4：跨维度一致性

| 检查项 | 怎么查 |
|---|---|
| 追溯矩阵三方对齐：需求 ID ↔ 设计稿帧 ↔ 技术任务 | 追溯矩阵每行设计帧/测试用例列非"待设计/待编写"（walking skeleton 范围内） |
| 同一术语三处工件含义一致 | `consistency-check.md` 的 Conflicts=0 |
| "设计未覆盖的需求"或"技术未支撑的设计"已显式标记 | issues.md 有对应条目 |
| 新增需求触发三方联动更新 | 变更日志显示三方同步更新时间 |

## 执行流程

### 1. 预读与三方对齐

读取：`.nds/<req-id>/01-requirements/`（PRD/追溯矩阵/risks/consistency-check/feature-checklist）、`.nds/<req-id>/02-design/`（design-spec/components/patterns/user-flows/hifi-pages/IA）、技术方案（若有）。

### 2. 逐项核查 + 评估器打分

按四维度清单逐条核查，每项给客观证据。问题记录到 `issues.md`：

```markdown
| Issue ID | 维度 | 严重度 | 描述 | 影响范围 | 负责人 | 状态 |
|---|---|---|---|---|---|---|
| ISS-001 | 需求 | Blocker | F003 缺验收标准 | 后端登录 | @dev | open |
| ISS-002 | 设计 | Major | 暗色模式按钮对比度 3.2:1 不达标 | 全局 | @design | open |
```

严重度：**Blocker**（必须解决才能开工）/ **Critical**（严重，必须有缓解方案）/ **Major**（重要，跟踪）/ **Minor**（建议）。

`evaluation.json` 机器可读评分（硬阈值，喂给 workflow 门禁自动判断）：

```json
{
  "dimensions": {
    "requirements": { "score": 0-100, "blockers": 2, "criticals": 1, "passed": false },
    "design":       { "score": 0-100, "blockers": 0, "criticals": 2, "passed": true },
    "tech":         { "score": 0-100, "blockers": 1, "criticals": 0, "passed": false }
  },
  "overall_passed": false,
  "must_fix_before_dev": ["ISS-001", "ISS-005"]
}
```

> 为什么独立怀疑式评估器：开箱 LLM 倾向"夸赞自己的工作"，把 bug"说服自己不算事"。本 skill 必须独立于 dev-skill 视角，按硬阈值打分而非主观"感觉还行"。评估标准应随项目迭代校准到与人类判断一致。

### 3. 决策日志（decisions.md）

记"选了什么 / 为什么不选 B"——"为什么不选 B"比"选了 A"更有长期价值，防止重复讨论：

```markdown
| Decision ID | 决策 | 备选 | 理由 | 决策人 | 影响范围 | 状态 |
|---|---|---|---|---|---|---|
| D001 | 选用 JWT 而非 Session | Session / OAuth | 无状态横向扩展，前端友好 | @tech-lead | 全局认证 | accepted |
```

决策同步写入 `state.json` 的 `decisions[]`。

### 4. 准入判定（sign-off.md，三维各自结果）

```markdown
# 评审准入签字

## 三维 checklist 结果（非整体一句，便于跨会话回看决策依据）
- 需求完整性：[ ] 通过 / [ ] 有条件通过 / [ ] 不通过 — Blocker: ISS-001,ISS-005
- UX 可实现性：[ ] 通过 / [ ] 有条件通过 / [ ] 不通过 — Critical: ISS-002
- 技术可行性：[ ] 通过 / [ ] 有条件通过 / [ ] 不通过 — Blocker: ISS-003

## 评审结论
[ ] 通过 — 可进入任务拆分
[ ] 有条件通过 — Critical 有缓解方案，可进入
[ ] 不通过 — 存在未关闭 Blocker，回流上游

## Blocker 清单 / Critical 缓解方案 / 签字（需求方/设计方/技术方 + 日期）
```

## 为什么这些规则

- **三维度同时评审**：任一缺失视为未通过。单维度通过不等于方案可交付——需求对但设计不可实现、设计对但技术撑不住，都会在开发期爆雷。禁止"先开发后补评审"。
- **跨维度一致性校验**：需求 ↔ 设计 ↔ 技术逐条对应，任何缺口显式标记。`consistency-check.md` 是 req 阶段已跑过的自动检查结果，本阶段复核其 Conflicts 是否已清零。
- **Blocker 必须闭环**：未关闭禁止进入开发。带 Blocker 进开发等于把 10 倍成本的修复推到代码阶段。
- **人在环**：sign-off 必须等用户签字，AI 不擅自推进到开发阶段——这是 Loop Engineering 唯一强制人工卡点（高后果/不可逆节点）。
- **评审记录不删**：所有 Issue/Risk/Decision 留痕，状态变更记录时间与负责人——跨会话续传时回看决策依据。

## 完成判定

- review-report.md 含四维度核查结果与客观证据
- evaluation.json 评分产出，`overall_passed` 反映 Blocker 状态
- issues.md 中所有 Blocker 状态为 `closed`（或显式标注"用户接受风险"）
- decisions.md 至少 1 条决策，已同步入 state.json
- sign-off.md 三维各自结果记录，用户已签字
- state.json：`phases.review.status = "done"`，`events[]` append `{type:"human_signoff", phase:"review"}`
- `resume_hint` 建议进入 task 阶段（`/nzw-task`）

## 回流机制

未关闭 Blocker 时：需求维度问题 → `phases.requirements.status = "blocked"`，提示 `/nzw-req` 修订；设计维度问题 → `phases.design.status = "blocked"`，提示 `/nzw-design` 修订；技术维度问题 → 在 issues.md 标注并要求技术负责人补充方案。回流时向 `events[]` append `{type:"phase_blocked"}`。

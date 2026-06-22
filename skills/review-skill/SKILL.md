---
name: review-skill
description: 三维度实现评估技能，同时从需求完整性、UI/UX 设计可实现性和技术可行性三个维度评估软件方案。在开发开始前识别跨维度的缺口、不一致和风险。当用户提到以下任何场景时务必使用此技能：实现评估、方案评审、可行性评审、需求评审、技术评审、设计评审、开发前评审、规格验证，或需要在投入开发前验证需求、设计和技术方案是否一致和完整。即使用户只说了"评审"，只要在软件开发的上下文中，都应触发此技能。
metadata:
  type: nzw-dev-skills
  phase: review
  trigger: /nzw-review
---

# 三维实现评估技能（review-skill）

在投入开发前，从**需求完整性 / UX 可实现性 / 技术可行性**三个维度对方案做一致性校验，产出 Issue / Risk / Decision 三件套，作为开发的准入闸门。

主导思想：**Shift-Left Quality** —— 缺陷在需求/设计阶段修复的成本是代码阶段的 10-100 倍，评审是最高 ROI 的质量活动。

## 何时触发

- 用户输入 `/nzw-review`
- 自然语言提到"评审/可行性/准入/Pre-Review"等
- workflow-skill 在闭环中进入 review 阶段

## 工作目录与状态

产出落到 `.nds/03-review/`：
- `review-report.md` — 评审总报告
- `issues.md` — 问题清单（含严重度分级）
- `decisions.md` — 决策日志
- `sign-off.md` — 准入签字记录

入口动作：
1. 读取 `.nds/state.json`，确认 requirements 与 design 阶段已 done
2. `project.current_phase = "review"`，`phases.review.status = "in_progress"`
3. 评审完成后根据是否有 Blocker 决定 `status`：done / blocked（回流上游）

## 评审三维度检查清单

### 维度 1：需求完整性

- [ ] 每条需求至少 1 条可执行验收标准（Given-When-Then）
- [ ] 非功能需求齐全（性能/安全/可用性/可访问性/合规）
- [ ] 边界与异常路径覆盖
- [ ] 依赖与前置条件明确
- [ ] 与上层目标（OKR）对齐
- [ ] Non-goals 明确
- [ ] INVEST 检查通过

### 维度 2：UX/UI 可实现性

- [ ] 设计稿覆盖所有主要用户流
- [ ] 组件复用设计系统，无重复造轮
- [ ] 交互状态完整（空/载/错/禁用/loading）
- [ ] 响应式断点明确
- [ ] 无障碍标注（WCAG 2.2：对比度 4.5:1、键盘可达、焦点可见、目标尺寸 ≥24×24px）
- [ ] 设计令牌分层正确，无魔数
- [ ] 设计-开发交接清单签署

### 维度 3：技术可行性

- [ ] 架构图覆盖数据流/调用链/部署
- [ ] API 契约已定义（请求/响应/错误码）
- [ ] 技术选型有 POC 或参考案例
- [ ] 性能与容量有估算
- [ ] 安全威胁建模（STRIDE）完成
- [ ] 第三方依赖与许可证审查
- [ ] 可观测性方案（日志/指标/追踪）
- [ ] 回滚策略

### 维度 4：跨维度一致性

- [ ] 追溯矩阵三方对齐：需求 ID ↔ 设计稿帧 ↔ 技术任务
- [ ] 同一术语在三处工件中含义一致
- [ ] 任何"设计未覆盖的需求"或"技术未支撑的设计"已显式标记
- [ ] 新增需求触发三方联动更新

## 执行流程

### 1. 预读与三方对齐

读取：
- `.nds/01-requirements/PRD.md`、`traceability-matrix.md`、`risks.md`
- `.nds/02-design/design-spec.md`、`components/`、`user-flows.md`、`hifi-pages/`
- 技术方案（若有，如 `.nds/02-design/tech-architecture.md` 或现有代码）

### 2. 逐项核查

按上述四维度清单逐条核查。每发现一项问题记录到 `issues.md`：

```markdown
| Issue ID | 维度 | 严重度 | 描述 | 影响范围 | 负责人 | 状态 |
|---|---|---|---|---|---|---|
| ISS-001 | 需求 | Blocker | F003 缺验收标准 | 后端登录 | @dev | open |
| ISS-002 | 设计 | Major | 暗色模式下按钮对比度 3.2:1 不达标 | 全局 | @design | open |
| ISS-003 | 技术 | Critical | 未做威胁建模 | 认证模块 | @tech-lead | open |
```

严重度分级：
- **Blocker**：必须解决才能开工
- **Critical**：严重，必须有缓解方案
- **Major**：重要，跟踪
- **Minor**：建议

### 3. 决策日志（decisions.md）

记录"选了什么 / 为什么不选 B"：

```markdown
| Decision ID | 决策 | 备选 | 理由 | 决策人 | 影响范围 | 状态 |
|---|---|---|---|---|---|---|
| D001 | 选用 JWT 而非 Session | Session / OAuth | 无状态横向扩展，前端友好 | @tech-lead | 全局认证 | accepted |
```

### 4. 准入判定（sign-off.md）

```markdown
# 评审准入签字

## 评审结论
[ ] 通过 — 可进入任务拆分
[ ] 有条件通过 — Critical 有缓解方案，可进入
[ ] 不通过 — 存在未关闭 Blocker，回流上游

## Blocker 清单
（列出所有 Blocker 及处理方案）

## Critical 缓解方案
（列出每个 Critical 的缓解措施与跟踪人）

## 签字
- 需求方：__________ 日期：____
- 设计方：__________ 日期：____
- 技术方：__________ 日期：____
```

## 必须遵守的规则

1. **三维度必须同时评审**，任一缺失视为未通过。禁止"先开发后补评审"。
2. **产出三件套**：Issue / Risk / Decision 必须编号可追溯。
3. **跨维度一致性校验**：需求 ↔ 设计 ↔ 技术逐条对应，任何缺口显式标记。
4. **Blocker 必须闭环**：未关闭禁止进入开发。
5. **Decision Log 记"为什么不选 B"**：比"选了 A"更有长期价值，防止重复讨论。
6. **评审记录不删**：所有 Issue/Risk/Decision 留痕，状态变更记录时间与负责人。
7. **人在环**：sign-off 必须等用户签字，AI 不擅自推进到开发阶段。

## 完成判定

- review-report.md 含四维度核查结果
- issues.md 中所有 Blocker 状态为 `closed`（或显式标注"用户接受风险"）
- decisions.md 至少记录 1 条决策
- sign-off.md 用户已签字
- state.json 中 `phases.review.status = "done"`，`decisions` 数组合并入 state.json
- `resume_hint` 建议进入 task 阶段（`/nzw-task`）

## 回流机制

若存在未关闭 Blocker：
- 需求维度问题 → `phases.requirements.status = "blocked"`，提示 `/nzw-req` 修订
- 设计维度问题 → `phases.design.status = "blocked"`，提示 `/nzw-design` 修订
- 技术维度问题 → 在 issues.md 中标注并要求技术负责人补充方案

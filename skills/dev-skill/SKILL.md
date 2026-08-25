---
name: dev-skill
description: TDD 开发实现技能，按分配的任务与对应文档/设计实现代码，以红-绿-重构小步循环驱动；测试是验收契约而非验证工具，AI 实现完毕立即跑测试反馈，失败 diff 回灌作为下一轮上下文。当用户提到以下任一场景时务必使用：开发实现、TDD、写代码、实现功能、bug 修复、修复缺陷、重构、提交代码，或需要把任务变成可运行代码。即使用户只说"实现一下"或"修个 bug"，只要在编码上下文中就应触发。不适用于纯设计（用 design-skill）或验收测试设计（用 test-skill）。
metadata:
  type: nzw-dev-skills
  phase: dev
  trigger: /nzw-dev
---

# TDD 开发实现技能（dev-skill）

按分配的任务实现代码，以**红-绿-重构**小步循环驱动；测试是验收契约而非验证工具，AI 实现完毕立即跑测试反馈，失败 diff 回灌作为下一轮上下文。

主导思想：**测试是设计工具而非验证工具**（Beck/Fowler）。AI 时代升级为 **spec-first TDD + 测试即不可变契约**——把验收测试当 prompt 锚点，避免长链幻觉；用结构化载体（feature-checklist.json）+ 冻结测试 + "只改 passes 字段"强约束，从载体层面防住"agent 改测试让假绿通过"（Anthropic 实测有效的 poka-yoke）。

## 何时触发

- 用户输入 `/nzw-dev [task-id]`
- 自然语言提到"实现/开发/写代码/修 bug"等
- workflow-skill 在闭环中进入 dev 阶段
- test-skill 反馈 bug 触发新一轮迭代（bug_reflow 事件）

## 工作目录与状态

产出落到 `.nds/<req-id>/05-dev/`：
- `implementation-log.md` — 每个任务的红绿循环记录
- `bugfix-log.md` — Bug 修复记录
- `commits.md` — 提交历史（Conventional Commits）

入口动作：
1. 读 `.nds/index.json` 确定 `active_req_id`，再读 `.nds/<req-id>/state.json`，从 `task_tree.tasks` 取目标任务（指定 ID 或下一个 `todo` 且 `lock == null`）。
2. `project.current_phase = "dev"`，任务状态 `todo → doing`，写 `lock: {claimant, claimed_at}`，记录 `started_at`；同步回写 `index.json`。
3. 读取任务的 `context_files` / `input_contract` / `output_contract` / `verification_cmd`，**只读当前任务 context_files，不预读全部 task-tree**（对抗 context rot）。
4. 完成后任务状态置 `review`，`lock: null`，记录 `completed_at`。

## 主导思想

- **红-绿-重构**：分钟级小步循环，每步保持测试全绿
- **测试奖杯（Trophy）**：大量集成测试 + 少量纯单元 + 极少 E2E；集成层才是信心拐点
- **测试行为不测实现**：单元测公共接口不测私有，mock 仅跨进程边界
- **一次一个 feature**：增量推进，防止在实现中途耗尽上下文（Anthropic harness 实测）
- **AI 是协作者，测试是不可协商的验收契约**

## 执行流程

### 1. 任务上下文加载

读取并理解：PRD 对应段落（context_files 指向）、design 对应组件规格/API 契约、task-tree.json 中本任务的 input/output_contract、现有代码结构。**只加载本任务相关文件**——这是 context engineering 的关键，预读全部任务会撑爆窗口。

### 2. TDD 红-绿-重构循环

**红 — 写失败测试**：根据 output_contract 写测试，先跑一遍确认失败（且失败原因正确）。测试命名表达意图：`should_return_201_when_register_valid_user`。单测断言单一行为。

**绿 — 最小实现**：写让测试通过的最少代码，不要过度设计。允许丑陋实现，重构阶段再美化。

**重构 — 改进而不改行为**：提取函数、消除重复、改善命名。重构阶段不允许新增测试或行为。每步重构后跑测试保持全绿。

记录到 `implementation-log.md`：

```markdown
## T002 - 实现注册 API
### Round 1
- 红：写 register.test.ts，跑 → 失败（模块不存在）✓
- 绿：实现 register.ts 最小版本，跑 → 通过 ✓
- 重构：提取 validateEmail 函数，跑 → 通过 ✓
### Round 2 (bug 反馈 B003)
- 红：补充重复邮箱测试，跑 → 失败（未处理 409）✓
- 绿：增加唯一性检查，跑 → 通过 ✓
```

### 3. 测试即不可变契约（防假绿 poka-yoke）

这是 AI 时代 TDD 最重要的防线。开箱 LLM 会"夸赞自己的工作"、把 bug"说服自己不算事"、甚至为通过测试而改测试。三条 poka-yoke：

1. **feature-checklist.json 是共享契约**：实现完一个 feature，在 `.nds/<req-id>/01-requirements/feature-checklist.json` 把对应 `passes` 翻为 `true`。**只允许改 `passes` 字段，不得删改 `acceptance`（已冻结测试意图）**。JSON 比 Markdown 更难被 agent 不当覆盖——这是 Anthropic 实测有效的载体级防护。
2. **冻结测试用例**：已写入的验收测试（尤其 test-skill 设计的 BDD 场景）视为冻结契约。禁止删除或弱化断言让其通过；需求本身变更时，先改 PRD + 追溯矩阵 + 通知 test-skill，再改测试。
3. **测试与实现分角色**：测试作者（test-skill / 红阶段）与实现者（绿阶段）用不同视角，防"测试镜像实现假设"——测试复述实现逻辑而非独立规约行为，是假绿的另一来源。

> 为什么这些约束：Anthropic 长跑 harness 实测发现 agent 会编辑测试断言让假绿通过、会不做端到端就标记完成。用结构化载体 + 冻结语义 + 分角色，从源头堵住这两条最常见失败路径。

### 4. 一次一个 feature + 快采样回归

- **一次只做一个 feature**：从 `task_tree` 取一个 `todo` 任务做到 `review`，不批量并行。防止上下文在中途耗尽留下半成品。
- **快采样回归**：日常红绿循环跑 regression 子集（`--fast`，如只跑受影响模块 + P0 用例）做高频反馈；阶段门禁跑全集。回归是常态——"新功能与 bugfix 经常破坏既有功能"（Anthropic C 编译器实测）。

### 5. Bug 修复子流程（bug_reflow 事件驱动）

收到 test-skill 反馈的 bug（state.json 的 `feedback_loop.bug_reflow[]` 有 `status:"triggered"`）时：

1. **复现**：先写 failing test 复现 bug（红）
2. **定位**：用 `git bisect` / 二分注释法找根因
3. **最小修复**：只改 bug 不改其他
4. **回归**：跑全量测试确认无回归
5. **根因记录**：写入 `bugfix-log.md`；bug_reflow 项置 `resolved_at` + `status:"closed"`

```markdown
## B003 - 注册接口在并发下产生重复账号
- 复现测试：register.concurrent.test.ts (10 并发相同邮箱)
- 根因：未加数据库唯一索引
- 修复：migration 添加 unique index on email
- 回归：全量测试通过 ✓
- 经验：DB schema 层的约束优先应用层校验
```

### 6. 质量门禁（提交前必过）

```bash
pnpm lint          # 代码规范
pnpm typecheck     # 类型检查
pnpm test          # 全量测试
```

三道门禁按顺序跑：lint 先抓语法错误，typecheck 再抓类型，最后 test。CI 会以同样顺序卡 PR，本地先跑能避免来回 push。任一失败就在 implementation-log.md 记下失败 diff 作为下一轮上下文。若项目无上述命令，用项目实际命令（从 `.nds/00-instruction/CLAUDE.md` 或 package.json 推断）。

### 7. 提交（Conventional Commits）

```
feat(auth): implement register API with email uniqueness (T002)

- POST /api/register returns 201 + user object
- 409 on duplicate email
- tests: 8 passing

Refs: T002
```

类型 `feat / fix / refactor / test / docs / chore`，scope 对应模块，关联 Task ID。记录到 `commits.md`。会话末留"干净状态"（全部提交或显式 stash），供下次会话启动协议检查。

### 8. 长任务上下文压缩

任务超出窗口时，启用上下文压缩：把已完成的红绿循环 + 关键决策压缩成 `implementation-log.md` 的事件摘要，新窗口读 log + state.json 的 `events[]` 续跑。`resume_hint` 升级为结构化决策日志（Cognition 上下文压缩 agent 模式）。

## 完成判定

- 任务所有 output_contract 验收点被测试覆盖
- `verification_cmd` 通过（真实输出，非自评）
- 三道门禁全绿
- `feature-checklist.json` 对应 feature `passes: true`
- 提交记录写入 commits.md
- 任务状态 `doing → review`，`lock: null`
- state.json 更新（`events[]` append task_done），PROGRESS.md 同步
- `resume_hint` 建议进入 test 阶段或领取下一个任务

## 与上下游交接

- 输入：task-tree.json 中的任务四要素、PRD/设计对应段落、feature-checklist.json
- 输出给 test-skill：实现代码 + 测试套件 + implementation-log + feature-checklist.json（passes 状态）
- Bug 反馈输入：state.json 的 `feedback_loop.bug_reflow[]`，触发新一轮红绿循环

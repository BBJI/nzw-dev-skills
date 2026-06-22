---
name: dev-skill
description: TDD 开发实现技能，根据分配的任务与对应文档、设计实现代码，并对测试反馈的 bug 进行修复。采用红-绿-重构循环，把测试作为不可协商的验收契约。当用户提到以下任何场景时务必使用此技能：开发实现、TDD、写代码、实现功能、bug 修复、修复缺陷、重构、提交代码，或需要把任务变成可运行代码。即使用户只说了"实现一下"或"修个 bug"，只要在编码上下文中，都应触发此技能。
metadata:
  type: nzw-dev-skills
  phase: dev
  trigger: /nzw-dev
---

# TDD 开发实现技能（dev-skill）

按分配的任务实现代码，以**红-绿-重构**小步循环驱动；测试是验收契约而非验证工具，AI 实现完毕立即跑测试反馈，失败 diff 回灌作为下一轮上下文。

主导思想：**测试是设计工具而非验证工具**（Beck/Fowler）。AI 时代升级为 **spec-first TDD**——把验收测试当 prompt 锚点，避免长链幻觉。

## 何时触发

- 用户输入 `/nzw-dev [task-id]`
- 自然语言提到"实现/开发/写代码/修 bug"等
- workflow-skill 在闭环中进入 dev 阶段
- test-skill 反馈 bug 触发新一轮迭代

## 工作目录与状态

产出落到 `.nds/05-dev/`：
- `implementation-log.md` — 每个任务的实现日志（红绿循环记录）
- `bugfix-log.md` — Bug 修复记录
- `commits.md` — 提交历史（Conventional Commits）

入口动作：
1. 读取 `.nds/state.json`，从 `task_tree.tasks` 取目标任务（指定 ID 或下一个 `todo`）
2. `project.current_phase = "dev"`，任务状态 `todo → doing`，记录 `started_at`
3. 读取任务的 `context_files` / `input_contract` / `output_contract` / `verification_cmd`
4. 完成后任务状态置 `review`，记录 `completed_at`

## 主导思想

- **红-绿-重构**：分钟级小步循环，每步保持测试全绿
- **测试奖杯（Trophy）**：大量集成测试 + 少量纯单元 + 极少 E2E；高层测试低 ROI，集成层才是信心拐点
- **测试行为不测实现**：单元测公共接口不测私有，mock 仅跨进程边界
- **AI 是协作者，测试是不可协商的验收契约**

## 执行流程

### 1. 任务上下文加载

读取并理解：
- `.nds/01-requirements/PRD.md` 对应段落（任务 context_files 指向）
- `.nds/02-design/` 对应组件规格、API 契约
- `.nds/04-tasks/task-tree.json` 中本任务的 input/output_contract
- 现有代码结构（若有）

### 2. TDD 红-绿-重构循环

**红 — 写失败测试**：
- 根据 output_contract 写测试，先跑一遍确认失败（且失败原因正确）
- 测试命名表达意图：`should_return_201_when_register_valid_user`
- 单测断言单一行为

**绿 — 最小实现**：
- 写让测试通过的最少代码，不要过度设计
- 允许丑陋实现，重构阶段再美化

**重构 — 改进而不改行为**：
- 提取函数、消除重复、改善命名
- 重构阶段不允许新增测试或行为
- 每步重构后跑测试保持全绿

记录到 `implementation-log.md`：

```markdown
## T002 - 实现注册 API

### Round 1
- 红：写 `register.test.ts`，跑 → 失败（模块不存在）✓
- 绿：实现 `register.ts` 最小版本，跑 → 通过 ✓
- 重构：提取 `validateEmail` 函数，跑 → 通过 ✓

### Round 2 (bug 反馈)
- 红：补充重复邮箱测试，跑 → 失败（未处理 409）✓
- 绿：增加唯一性检查，跑 → 通过 ✓
```

### 3. Bug 修复子流程

收到 test-skill 反馈的 bug 时：

1. **复现**：先写 failing test 复现 bug（红）
2. **定位**：用 `git bisect` / 二分注释法找根因
3. **最小修复**：只改 bug 不改其他
4. **回归**：跑全量测试确认无回归
5. **根因记录**：写入 `bugfix-log.md`

```markdown
## B003 - 注册接口在并发下产生重复账号

- 复现测试：`register.concurrent.test.ts` (10 并发相同邮箱)
- 根因：未加数据库唯一索引
- 修复：migration 添加 unique index on email
- 回归：全量测试通过 ✓
- 经验：DB schema 层的约束优先应用层校验
```

### 4. 质量门禁（提交前必过）

```bash
# 三道门禁，缺一不可
pnpm lint          # 代码规范
pnpm typecheck     # 类型检查
pnpm test          # 全量测试
```

若项目无上述命令，用项目实际命令（从 `.nds/00-instruction/CLAUDE.md` 或 package.json/similar 推断）。

### 5. 提交（Conventional Commits）

```
feat(auth): implement register API with email uniqueness (T002)

- POST /api/register returns 201 + user object
- 409 on duplicate email
- tests: 8 passing

Refs: T002
```

类型：`feat / fix / refactor / test / docs / chore`，scope 对应模块。

记录到 `commits.md`。

## 必须遵守的规则

1. **先写失败测试再写实现**：Bug 修复也必须先写复现测试。
2. **重构阶段不改行为**：不新增测试、不新增功能。
3. **提交前三门禁必过**：lint + typecheck + test。
4. **Conventional Commits 格式**：`type(scope): desc`，关联 Task ID。
5. **测试行为不测实现**：不测私有方法，mock 仅跨进程边界。
6. **AI 生成代码必须有失败测试护栏**：禁止"看着对"的幻觉通过。
7. **覆盖率是下限门禁（70-80%），非目标**：不为凑覆盖率写空断言。
8. **禁止为了通过测试而改测试**，除非需求本身变更。

## 完成判定

- 任务所有 output_contract 验收点被测试覆盖
- verification_cmd 通过
- 三道门禁全绿
- 提交记录写入 commits.md
- 任务状态 `doing → review`
- state.json 更新，PROGRESS.md 同步
- `resume_hint` 建议进入 test 阶段或领取下一个任务

## 与上下游交接

- 输入：task-tree.json 中的任务四要素、PRD/设计对应段落
- 输出给 test-skill：实现代码 + 测试套件 + implementation-log
- Bug 反馈输入：来自 `.nds/06-test/bug-reports/`，触发新一轮红绿循环

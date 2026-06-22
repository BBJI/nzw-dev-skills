---
description: nzw TDD 开发实现 — 按分配任务实现代码并修复 bug
argument-hint: [task-id]
---

请触发 `dev-skill` 执行开发任务。

任务 ID：$ARGUMENTS
（若未提供 task-id，则从 `.nds/state.json` 取下一个 `todo` 状态任务）

执行要求：
1. 读取 `.nds/state.json` 与 `.nds/04-tasks/` 确认任务上下文
2. 将 `current_phase` 设为 `dev`，对应任务状态设为 `doing`
3. TDD 循环：先写失败测试 → 实现 → 重构
4. 修复 `.nds/06-test/bug-reports/` 中分配给本任务的 bug 时，先写复现测试
5. 完成后任务状态置 `review`，记录到 `.nds/05-dev/`
6. 同步刷新 `.nds/PROGRESS.md`

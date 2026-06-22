---
description: nzw TDD 开发实现 — 按分配任务实现代码并修复 bug
argument-hint: [task-id] [--req <req-id>]
---

请触发 `dev-skill` 执行开发任务。

任务 ID 与需求定位：$ARGUMENTS
- 解析出 `--req <req-id>` 时作用于该需求；否则作用于 `.nds/index.json` 的 `active_req_id`
- 其余参数视为 task-id；未提供则从该 req 的 state.json 取下一个 `todo` 状态任务

执行要求：
1. 读取 `.nds/<req-id>/state.json` 与 `.nds/<req-id>/04-tasks/` 确认任务上下文
2. 将 `current_phase` 设为 `dev`，对应任务状态设为 `doing`
3. TDD 循环：先写失败测试 → 实现 → 重构
4. 修复 `.nds/<req-id>/06-test/bug-reports/` 中分配给本任务的 bug 时，先写复现测试
5. 完成后任务状态置 `review`，记录到 `.nds/<req-id>/05-dev/`
6. 同步刷新 `.nds/<req-id>/PROGRESS.md` 与顶层 `.nds/PROGRESS.md`，回写 `index.json` 中该 req 的 `current_phase`/`updated_at`

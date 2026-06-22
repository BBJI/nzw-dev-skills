---
description: nzw 任务拆分 — 将评审通过的方案分解为可实施任务并排期
---

请触发 `task-allocation-skill` 基于 `.nds/03-review/` 的评审结果做任务拆分。

执行要求：
1. 读取 `.nds/state.json`，将 `current_phase` 设为 `tasks`
2. 输出 WBS、任务树 JSON、排期表到 `.nds/04-tasks/`
3. 每个任务满足 INVEST，依赖关系建模为 DAG
4. 同步刷新 `.nds/PROGRESS.md`

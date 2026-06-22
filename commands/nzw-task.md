---
description: nzw 任务拆分 — 将评审通过的方案分解为可实施任务并排期
argument-hint: [--req <req-id>]
---

请触发 `task-allocation-skill` 基于 `.nds/<active-req-id>/03-review/` 的评审结果做任务拆分。

需求定位：读取 `.nds/index.json`，未指定 `--req` 时作用于 `active_req_id`。

执行要求：
1. 读取 `.nds/<req-id>/state.json`，将 `current_phase` 设为 `tasks`
2. 输出 WBS、任务树 JSON、排期表到 `.nds/<req-id>/04-tasks/`
3. 每个任务满足 INVEST，依赖关系建模为 DAG
4. 同步刷新 `.nds/<req-id>/PROGRESS.md` 与顶层 `.nds/PROGRESS.md`，回写 `index.json` 中该 req 的 `current_phase`/`updated_at`

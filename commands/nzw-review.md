---
description: nzw 三维实现评估 — 从需求/设计/技术三维度评审方案可行性
argument-hint: [--req <req-id>]
---

请触发 `review-skill` 对当前 `.nds/<active-req-id>/01-requirements/` 与 `.nds/<active-req-id>/02-design/` 做三维实现评估。

需求定位：读取 `.nds/index.json`，未指定 `--req` 时作用于 `active_req_id`。

执行要求：
1. 读取 `.nds/<req-id>/state.json`，将 `current_phase` 设为 `review`
2. 从需求完整性、UX 可实现性、技术可行性三维度评审
3. 产出评审报告、问题清单、决策日志到 `.nds/<req-id>/03-review/`
4. 若存在阻塞问题，回到需求或设计阶段；否则签字进入任务拆分
5. 同步刷新 `.nds/<req-id>/PROGRESS.md` 与顶层 `.nds/PROGRESS.md`，回写 `index.json` 中该 req 的 `current_phase`/`open_blockers`/`updated_at`

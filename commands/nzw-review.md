---
description: nzw 三维实现评估 — 从需求/设计/技术三维度评审方案可行性
---

请触发 `review-skill` 对当前 `.nds/01-requirements/` 与 `.nds/02-design/` 做三维实现评估。

执行要求：
1. 读取 `.nds/state.json`，将 `current_phase` 设为 `review`
2. 从需求完整性、UX 可实现性、技术可行性三维度评审
3. 产出评审报告、问题清单、决策日志到 `.nds/03-review/`
4. 若存在阻塞问题，回到需求或设计阶段；否则签字进入任务拆分
5. 同步刷新 `.nds/PROGRESS.md`

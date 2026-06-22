---
description: nzw 需求调研分析 — 把模糊想法转化为结构化需求文档
argument-hint: <任务描述>
---

请触发 `req-analysis-skill` 完成需求调研分析。

用户输入任务描述：$ARGUMENTS

执行要求：
1. 读取或初始化 `.nds/index.json`（schema 见 `templates/index.schema.json`）；为本次任务分配下一个 `req-NNN` 编号，追加到 `requirements[]` 并设为 `active_req_id`，创建子目录 `.nds/req-NNN/`
2. 在 `.nds/req-NNN/` 下初始化 `state.json`（`version: "1.1"`，`project.req_id` 填入），将 `current_phase` 设为 `requirements`
3. 产出需求文档、原型 HTML、追溯矩阵、风险登记表到 `.nds/req-NNN/01-requirements/`
4. 同步刷新 `.nds/req-NNN/PROGRESS.md` 与顶层 `.nds/PROGRESS.md`（总览，按 `templates/progress-overview.md.template` 渲染）
5. 完成后给出 `resume_hint` 写入 state.json，回写 `index.json` 中该 req 的 `current_phase`/`updated_at`

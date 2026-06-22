---
description: nzw 需求调研分析 — 把模糊想法转化为结构化需求文档
argument-hint: <任务描述>
---

请触发 `req-analysis-skill` 完成需求调研分析。

用户输入任务描述：$ARGUMENTS

执行要求：
1. 在当前工作目录创建 `.nds/` 工作区（若不存在）
2. 初始化或更新 `.nds/state.json`，将 `current_phase` 设为 `requirements`
3. 产出需求文档、原型 HTML、追溯矩阵、风险登记表到 `.nds/01-requirements/`
4. 同步刷新 `.nds/PROGRESS.md`
5. 完成后给出 `resume_hint` 写入 state.json

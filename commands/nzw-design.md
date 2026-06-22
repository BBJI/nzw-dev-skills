---
description: nzw UI/UX 设计规范 — 根据需求文档产出设计令牌、组件规格、高保真稿
argument-hint: [--req <req-id>]
---

请触发 `design-skill` 根据 `.nds/<active-req-id>/01-requirements/` 中的需求文档生成 UI/UX 设计规范。

需求定位：读取 `.nds/index.json`，未指定 `--req` 时作用于 `active_req_id`。

执行要求：
1. 读取 `.nds/<req-id>/state.json`，将 `current_phase` 设为 `design`
2. 产出设计令牌 JSON、组件规格、用户流程图、高保真 HTML 稿到 `.nds/<req-id>/02-design/`
3. 同步刷新 `.nds/<req-id>/PROGRESS.md` 与顶层 `.nds/PROGRESS.md`，回写 `index.json` 中该 req 的 `current_phase`/`updated_at`

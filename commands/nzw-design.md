---
description: nzw UI/UX 设计规范 — 根据需求文档产出设计令牌、组件规格、高保真稿
argument-hint: [--req <req-id>]
---

请触发 `design-skill` 根据 `.nds/<active-req-id>/01-requirements/` 中的需求文档生成 UI/UX 设计规范。

需求定位：读取 `.nds/index.json`，未指定 `--req` 时作用于 `active_req_id`。

执行要求：
1. 读取 `.nds/<req-id>/state.json`，将 `current_phase` 设为 `design`
2. **确保 impeccable 已安装**：检测 `.claude/skills/impeccable/SKILL.md`（或 `~/.claude/skills/impeccable/SKILL.md`）是否存在，缺失则在项目根目录执行 `npx impeccable install` 自动安装后继续；安装失败则降级到 design-skill 内置的 impeccable 精要规则
3. **分支设计**：扫描项目是否已有 CSS 令牌/主题/品牌色/现成页面——已有项目用 impeccable 结合当前页面风格保持一致（identity-preservation），新项目用 impeccable 从零设计（`/impeccable init` + `palette.mjs` 种子色）
4. 产出设计令牌 JSON、组件规格、用户流程图、高保真 HTML 稿到 `.nds/<req-id>/02-design/`，令牌与组件来自 impeccable 输出的映射
5. 同步刷新 `.nds/<req-id>/PROGRESS.md` 与顶层 `.nds/PROGRESS.md`，回写 `index.json` 中该 req 的 `current_phase`/`updated_at`

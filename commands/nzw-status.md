---
description: nzw 查看进度 — 显示 .nds/PROGRESS.md 内容
argument-hint: [--req <req-id>]
---

**无 `--req` 参数**：读取顶层 `.nds/PROGRESS.md`（若不存在则读 `.nds/index.json` 并按 `templates/progress-overview.md.template` 渲染），展示所有需求总览：id / 名称 / 当前阶段 / 待解 Blocker / 路径。

**有 `--req <id>`**：读取 `.nds/<req-id>/PROGRESS.md`（若不存在则读该 req 的 `state.json` 并按 `templates/progress.md.template` 渲染），向用户展示：

1. 需求一句话目标
2. 当前阶段与七阶段进度表
3. 任务清单（开发阶段）
4. 待修复 bug 清单
5. 最近 5 条关键决策
6. resume_hint

输出格式以表格为主，简洁可读。若 `.nds/` 不存在，提示用户先启动任务。

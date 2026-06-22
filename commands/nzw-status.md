---
description: nzw 查看进度 — 显示 .nds/PROGRESS.md 内容
---

请读取当前工作目录下的 `.nds/PROGRESS.md`（若不存在则读 `.nds/state.json` 并按 PROGRESS 模板渲染），
向用户展示：

1. 项目一句话目标
2. 当前阶段与七阶段进度表
3. 任务清单（开发阶段）
4. 待修复 bug 清单
5. 最近 5 条关键决策
6. resume_hint

输出格式以表格为主，简洁可读。若 `.nds/` 不存在，提示用户先启动任务。

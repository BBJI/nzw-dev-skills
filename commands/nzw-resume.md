---
description: nzw 跨会话续传 — 读取 .nds/state.json 接续上次任务
---

请读取当前工作目录下的 `.nds/state.json`，向用户报告：

1. 项目名、目标、当前阶段
2. 各阶段状态一览
3. 未完成任务的清单
4. 待修复 bug 清单
5. `resume_hint` 字段内容

然后询问用户：
- 继续执行当前阶段？（直接触发对应 skill）
- 跳转到指定阶段？
- 重做某个阶段？

若 `.nds/` 不存在，提示用户先用 `/nzw-workflow <任务>` 或 `/nzw-req <任务>` 启动新任务。

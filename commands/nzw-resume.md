---
description: nzw 跨会话续传 — 读取 .nds/index.json 选择需求并接续
---

请读取当前工作目录下的 `.nds/index.json`，向用户报告：

1. 项目根路径、需求总数、当前 active_req_id
2. 所有需求清单（id / name / current_phase / open_blockers / 最近更新）—— 按 `templates/progress-overview.md.template` 渲染
3. 询问用户要续传哪个需求（默认 active_req_id）

确定 req 后，读取 `.nds/<req-id>/state.json`，向用户报告：

1. 该需求名、目标、当前阶段
2. 各阶段状态一览
3. 未完成任务的清单
4. 待修复 bug 清单
5. `resume_hint` 字段内容

然后询问用户：
- 继续执行当前阶段？（直接触发对应 skill）
- 跳转到指定阶段？
- 重做某个阶段？

若 `.nds/` 不存在，提示用户先用 `/nzw-workflow <任务>` 或 `/nzw-req <任务>` 启动新任务。

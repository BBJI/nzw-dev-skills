---
description: nzw 跨会话续传 — 会话启动协议：读 index/state/PROGRESS → 环境健康检查 → 接续
---

请执行**会话启动协议**（Anthropic 长跑 harness 实测能修"上次留破环境"），按顺序：

## 1. 读取需求索引
读取当前工作目录下的 `.nds/index.json`，向用户报告：
1. 项目根路径、需求总数、当前 active_req_id
2. 所有需求清单（id / name / current_phase / open_blockers / 最近更新）—— 按 `templates/progress-overview.md.template` 渲染
3. 询问用户要续传哪个需求（默认 active_req_id）

若 `.nds/` 不存在，提示用户先用 `/nzw-workflow <任务>` 或 `/nzw-req <任务>` 启动新任务，结束。

## 2. 重放事件日志 + 读取人类态看板
确定 req 后，读取 `.nds/<req-id>/state.json`：
- **重放 `events[]` 最近 5 条**快速恢复上下文（v1.2 只追加事件日志，managed-agents 模式）
- 读 `resume_hint` 字段作为补充
- 向用户报告：需求名、目标、当前阶段、各阶段状态、未完成任务、待修复 bug（`feedback_loop.open_bugs` 与 `bug_reflow[]`）

## 3. 环境健康检查
- `git status` 看是否有未提交的破改动（上次会话是否留了半成品）
- 若项目根有 `init.sh`（或等价启动脚本/package.json scripts），跑一遍做依赖/编译冒烟
- 跑基础冒烟测试（如 `pnpm test -- --fast` 或项目冒烟子集），确认环境可运行
- 报告环境是否健康；若破，先用 `git` 回退到最近通过的 checkpoint 再继续

## 4. 确认接续方式
询问用户：
- 继续执行当前阶段？（直接触发对应 skill，从中断点继续）
- 跳转到指定阶段？
- 重做某个阶段？

> v1.1 旧 state.json（`version:"1.1"`）首次加载时自动补 `events:[]`/`bug_reflow:[]`/`feature_checklist_ref` 默认空值并升级为 `1.2`，不破坏旧 `.nds/`。

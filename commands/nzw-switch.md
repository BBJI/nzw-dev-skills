---
description: nzw 切换活跃需求 — 修改 .nds/index.json 的 active_req_id
argument-hint: <req-id>
---

请切换当前活跃需求到 $ARGUMENTS。

执行要求：
1. 读取 `.nds/index.json`，校验 `<req-id>` 存在于 `requirements[]` 中
2. 将 `active_req_id` 设为 `<req-id>`，更新 `project_root` 时间戳
3. 向用户报告切换后的需求信息：id / name / goal / current_phase / open_blockers / resume_hint
4. 提示后续命令（`/nzw-design`、`/nzw-dev` 等）将默认作用于该 active 需求，无需 `--req` 显式指定

若 `<req-id>` 不存在，列出所有可用 req-id 供用户选择。若 `.nds/index.json` 不存在，提示用户先用 `/nzw-req` 或 `/nzw-workflow` 启动任务。

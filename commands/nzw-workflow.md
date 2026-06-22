---
description: nzw 全流程自主交付 — Loop Engineering 闭环从需求到交付
argument-hint: <任务描述> [--req <req-id> | --new]
---

请触发 `workflow-skill` 以 Loop Engineering 思想串联全流程交付。

任务描述：$ARGUMENTS

需求定位：
- `--new` 或 `.nds/` 不存在 → 创建新 req-NNN 子目录并设为 active，从 requirements 阶段开始
- `--req <id>` → 切换 active 到指定 req 后接续
- 无参数 → 作用于 `index.active_req_id`，从其 `current_phase` 接续

执行要求：
1. 读取或初始化 `.nds/index.json`，按上述规则确定 active_req_id
2. 读取或初始化 `.nds/<req-id>/state.json`（`version: "1.1"`），从 `current_phase` 接续
3. 每阶段执行完毕经质量门禁才进入下一阶段
4. 测试阶段 bug 自动回流开发，形成闭环迭代
5. 全程允许用户暂停（直接 Ctrl+C 或新开会话），下次 `/nzw-resume` 续传
6. 关键决策点等用户签字（`.nds/<req-id>/03-review/sign-off.md`）
7. 完成后调用 `instruction-skill` 生成项目规范（新项目场景，落到顶层 `.nds/00-instruction/`）

---
description: nzw 全流程自主交付 — Loop Engineering 闭环从需求到交付
argument-hint: <任务描述>
---

请触发 `workflow-skill` 以 Loop Engineering 思想串联全流程交付。

任务描述：$ARGUMENTS

执行要求：
1. 若 `.nds/` 不存在 → 初始化并启动全流程（req → design → review → tasks → dev → test）
2. 若 `.nds/state.json` 存在 → 读取 `current_phase` 从当前阶段接续
3. 每阶段执行完毕经质量门禁才进入下一阶段
4. 测试阶段 bug 自动回流开发，形成闭环迭代
5. 全程允许用户暂停（直接 Ctrl+C 或新开会话），下次 `/nzw-resume` 续传
6. 关键决策点等用户签字
7. 完成后调用 `instruction-skill` 生成项目规范（新项目场景）

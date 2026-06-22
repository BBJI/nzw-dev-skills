---
description: nzw 测试用例与验证 — 开发后验证交付物并反馈 bug
---

请触发 `test-skill` 对开发交付物做测试验证。

执行要求：
1. 读取 `.nds/state.json`，将 `current_phase` 设为 `test`
2. 基于 `.nds/01-requirements/` 与 `.nds/04-tasks/` 设计测试用例
3. 执行测试，产出测试结果与 bug 报告到 `.nds/06-test/`
4. bug 写入 state.json 的 `feedback_loop.open_bugs`
5. 严重缺陷回流开发阶段，触发新一轮迭代
6. 同步刷新 `.nds/PROGRESS.md`

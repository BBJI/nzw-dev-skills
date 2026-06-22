---
description: nzw 生成项目规范文档 — 供 Claude Code / Codex 等 AI 编程工具使用
---

请触发 `instruction-skill` 生成项目规范文档。

执行要求：
1. 读取 `.nds/state.json` 判断项目状态
2. 若为已有项目：分析现有代码与目录，生成规范后执行全流程
3. 若为新项目：等全流程交付完成后生成规范
4. 产出 `CLAUDE.md`、`AGENTS.md`、`.cursorrules`、`copilot-instructions.md` 等到 `.nds/00-instruction/`
5. 同步刷新 `.nds/PROGRESS.md`

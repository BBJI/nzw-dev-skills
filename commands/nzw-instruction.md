---
description: nzw 生成项目规范文档 — 供 Claude Code / Codex 等 AI 编程工具使用
---

请触发 `instruction-skill` 生成项目规范文档。

**路径约定（v1.1）**：instruction-skill 是项目级规范生成器，产出**不进 req 子目录**，统一落到顶层 `.nds/00-instruction/`，跨需求共享。

执行要求：
1. 读取 `.nds/index.json` 判断项目状态（多 req 时综合所有 req 的产出提炼共性规范）
2. 若为已有项目：分析现有代码与目录，生成规范后执行全流程
3. 若为新项目：等全流程交付完成后生成规范
4. 产出 `CLAUDE.md`、`AGENTS.md`、`.cursorrules`、`copilot-instructions.md` 等到 `.nds/00-instruction/`
5. 同步刷新顶层 `.nds/PROGRESS.md`；若作用于单个 req（`--req` 显式指定），同步该 req 的 state.json 中 `phases.instruction.status`

# 原型截图与飞书 Docx 导出（req-analysis-skill）

> 本文件是 req-analysis-skill 的按需加载参考。产出原型双稿后、生成截图与 `.docx` 前必读。

## 1. 截图捕获（screenshots/）

### 1.1 原型页面容器约定

`prototype.html` 与 `preview.html` 是单文件多页原型。为支持按页截图，生成原型时给**每个页面区块**的外层容器加 `id="page-<名称>"`：

```html
<section id="page-login">…</section>
<section id="page-list">…</section>
<section id="page-detail">…</section>
```

> 名称用 kebab-case；两稿的页区块 id 保持一一对应（与双稿"页面一一对应不得增删"约束同构）。

### 1.2 截图清单 shots.json

在 `.nds/<req-id>/01-requirements/` 下写 `shots.json`（数组，每项一个截图任务）：

```json
[
  { "file": "prototype.html", "selector": "#page-login",  "output": "screenshots/prototype-login.png",  "width": 1440, "height": 900 },
  { "file": "prototype.html", "selector": "#page-list",   "output": "screenshots/prototype-list.png",   "width": 1440, "height": 900 },
  { "file": "preview.html",   "selector": "#page-login",  "output": "screenshots/preview-login.png",    "width": 1440, "height": 900 },
  { "file": "preview.html",   "fullPage": true,           "output": "screenshots/preview-full.png",     "width": 1440, "height": 900 }
]
```

规则：
- `selector`：只截该页区块（推荐，产出与 PRD 页面对应的单页图）
- `fullPage: true`：整页长图（适合氛围稿全览）
- **每个原型页面至少一条 selector 截图**；两稿都要覆盖
- 视口：全页面 1440×900；移动端原型 390×844

### 1.3 执行截图

```bash
# 首次使用前安装依赖（仅一次，重装 skill 后需重跑）
cd <skill-dir>/scripts && npm install

# 在 01-requirements 目录下执行
cd .nds/<req-id>/01-requirements
node <skill-dir>/scripts/screenshot.mjs
```

`<skill-dir>` 为本技能安装目录（如 `~/.agents/skills/req-analysis-skill`）。

截图输出到 `screenshots/`（2x 缩放 PNG）。**逐张验证**：文件存在且内容非空白/非报错页；失败时修复对应 HTML 与容器 id 后重跑。

### 1.4 截图嵌入 PRD

在 `PRD.md` 末尾追加「附录 A：原型页面截图」段（docx 转换会内嵌这些图）：

```markdown
## 附录 A：原型页面截图

> 线框稿（prototype.html，结构真源）与氛围稿（preview.html，参考）逐页对照。

### 登录页

![线框 - 登录页](screenshots/prototype-login.png)

![氛围 - 登录页](screenshots/preview-login.png)
```

## 2. 飞书可导入 Docx 导出（PRD.docx）

### 2.1 转换命令

```bash
# Windows Git Bash（MSYS_NO_PATHCONV=1 防路径被转换）
MSYS_NO_PATHCONV=1 python <skill-dir>/scripts/md_to_docx.py \
  --input .nds/<req-id>/01-requirements/PRD.md \
  --output .nds/<req-id>/01-requirements/PRD.docx

# macOS / Linux
python <skill-dir>/scripts/md_to_docx.py \
  --input .nds/<req-id>/01-requirements/PRD.md \
  --output .nds/<req-id>/01-requirements/PRD.docx
```

脚本自动安装缺失依赖（python-docx）。图片路径相对 `PRD.md` 解析，`screenshots/` 引用自动内嵌。

### 2.2 飞书导入方式

飞书云文档 → 新建 → **导入本地文件** → 选择 `PRD.docx`。

### 2.3 兼容性矩阵（转换脚本已内置处理）

| Markdown 元素 | Docx 处理 | 飞书导入后表现 |
|---------------|-----------|----------------|
| 图片 | 内联嵌入（宽 6 英寸居中），alt 文本转为图注 | 图片完整保留 |
| 表格 | Table Grid，表头加粗+浅灰底纹 | 保留结构，可继续编辑 |
| 标题 `#`~`####` | Heading 1~4，统一中文字体 | 映射为飞书标题层级，生成目录 |
| checkbox `- [ ]` / `- [x]` | `☐` / `☑` 字符 | 以任务符号展示 |
| 引用块 `>` | 缩进灰色斜体段落 | 以缩进段落展示 |
| 代码块 | Consolas 等宽缩进段落 | 等宽字体段落 |
| 分隔线 `---` | 段落底边框 | 转为分割线样式 |

### 2.4 转换前检查清单

1. `PRD.md` 中所有 `screenshots/*.png` 引用的文件真实存在（截图已验证）
2. 表格行以 `|` 开头并以 `|` 结尾（脚本按此识别表格）
3. 生成后验证 `PRD.docx` 存在且大小合理（含截图时通常 > 100KB）

### 2.5 降级路径

- `python-docx` 安装失败（无网/内网 pip 源不可用）→ 跳过 docx 导出，在 PRD.md 顶部与 state.json 事件中注明「docx 导出失败（依赖不可用）」，`screenshots/` 仍正常交付
- Puppeteer 安装失败 → 跳过截图，PRD 附录省略，同样注明降级

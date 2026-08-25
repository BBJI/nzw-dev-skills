#!/usr/bin/env python3
"""
nzw-dev-skills 项目风格扫描脚本（req-analysis-skill 用途）

扫描目标项目源码，完成两件事：
1. 分支判定：已有项目（存在可识别的设计令牌）vs 新项目（走 impeccable 从零设计分支）
2. 令牌提取：色彩/圆角/阴影/字体栈，每个 Token 标注来源文件与置信度

产出（写入 --output 目录）：
- style-snapshot.json  机器态（branch 判定 + tokens，供 prototype/preview 生成时读取）
- style-snapshot.md    人读报告（含复核清单与"布局模式"待补段）

用法（在项目根目录执行）：
  python <skill-dir>/scripts/scan_style.py --project . --output .nds/req-NNN/01-requirements
"""

import argparse
import io
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# 修复 Windows 控制台 Unicode 输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

HEX_COLOR_RE = re.compile(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b')
RGBA_COLOR_RE = re.compile(r'rgba?\(\s*\d[\d\s,./%]*\)')
CSS_VAR_RE = re.compile(r'(--[\w-]+)\s*:\s*([^;{}]+?)\s*;')
SCSS_COLOR_VAR_RE = re.compile(r'\$([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\))\s*;')
RADIUS_RE = re.compile(r'border-radius\s*:\s*([^;{}]+?)\s*;')
SHADOW_RE = re.compile(r'box-shadow\s*:\s*([^;{}]+?)\s*;')
FONT_RE = re.compile(r'font-family\s*:\s*([^;{}]+?)\s*;')

SOURCE_SUFFIXES = {'.vue', '.scss', '.css', '.less', '.html', '.jsx', '.tsx'}
SOURCE_DIRS = ('src', 'styles', 'theme', 'packages', 'app', 'components')
MAX_SOURCE_FILES = 500
TOP_N = 12
MAX_SOURCES_PER_TOKEN = 3

UI_LIBRARIES = ('element-plus', 'ant-design-vue', 'naive-ui', 'arco-design-web-vue',
                'tdesign-vue-next', 'vuetify', 'quasar', '@arco-design/web-react',
                'antd')
CSS_FRAMEWORKS = ('tailwindcss', 'unocss', 'windicss')

# 主题色显式定义的变量名模式（命中即为高置信度主色）
PRIMARY_VAR_PATTERNS = (
    '--el-color-primary', '--color-primary', '--primary-color', '--brand-color',
    '--ant-primary-color', '--td-brand-color', '$--color-primary', '$primary-color',
    '$brand-color', '$color-primary',
)


def parse_hex(value):
    """'#3668fc' -> (54, 104, 252)；非法返回 None"""
    v = value.lstrip('#')
    if len(v) == 3:
        v = ''.join(c * 2 for c in v)
    if len(v) != 6:
        return None
    try:
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def rgb_of(value):
    """任意颜色字符串 -> (r,g,b) 或 None"""
    value = value.strip()
    if value.startswith('#'):
        return parse_hex(value)
    m = re.match(r'rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)', value)
    if m:
        return tuple(int(g) for g in m.groups())
    return None


def is_neutral(rgb):
    """低饱和（近灰）判定"""
    return max(rgb) - min(rgb) <= 16


def luminance(rgb):
    return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255


def normalize_hex(value):
    rgb = parse_hex(value)
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}' if rgb else value.lower()


def top_sources(source_counter, limit=MAX_SOURCES_PER_TOKEN):
    return [name for name, _ in source_counter.most_common(limit)]


def collect_source_files(project_root):
    """收集待扫描的样式相关源文件"""
    files = []
    for dir_name in SOURCE_DIRS:
        base = project_root / dir_name
        if not base.is_dir():
            continue
        for p in base.rglob('*'):
            if p.suffix.lower() in SOURCE_SUFFIXES and p.is_file():
                files.append(p)
                if len(files) >= MAX_SOURCE_FILES:
                    return files
    for p in project_root.glob('*.css'):
        files.append(p)
    return files


def detect_stack(project_root):
    """从 package.json 检测 UI 库与 CSS 框架"""
    detected = {"uiLibrary": None, "cssFramework": None, "isVue": False, "isReact": False}
    pkg = project_root / 'package.json'
    if not pkg.exists():
        return detected
    try:
        deps = {}
        data = json.loads(pkg.read_text(encoding='utf-8'))
        for section in ('dependencies', 'devDependencies'):
            deps.update(data.get(section, {}) or {})
    except (json.JSONDecodeError, OSError):
        return detected
    for lib in UI_LIBRARIES:
        if lib in deps:
            detected["uiLibrary"] = f"{lib}@{deps[lib]}"
            break
    for fw in CSS_FRAMEWORKS:
        if fw in deps:
            detected["cssFramework"] = f"{fw}@{deps[fw]}"
            break
    detected["isVue"] = any(d.startswith(('vue', '@vue')) for d in deps)
    detected["isReact"] = any(d.startswith(('react', 'next')) for d in deps)
    return detected


def extract_tailwind_colors(project_root):
    """从 tailwind.config.* 提取命名色（括号栈追踪路径，支持任意层级嵌套）"""
    for name in ('tailwind.config.js', 'tailwind.config.ts', 'tailwind.config.cjs', 'tailwind.config.mjs'):
        cfg = project_root / name
        if not cfg.exists():
            continue
        try:
            text = cfg.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        result = []
        seen = set()
        stack = []
        token_re = re.compile(
            r"([\w-]+)\s*:\s*\{"                      # key: {
            r"|([\w-]+)\s*:\s*['\"](#[0-9a-fA-F]{3,8})['\"]"  # key: '#hex'
            r"|\{"                                     # 匿名块
            r"|\}"                                     # 块结束
        )
        for m in token_re.finditer(text):
            if m.group(1):              # key: { —— 命名块入栈
                stack.append(m.group(1))
            elif m.group(3):            # key: '#hex' —— 记录路径（保留末三段）
                path = '.'.join([s for s in stack if s][-2:] + [m.group(2)])
                if path not in seen:
                    seen.add(path)
                    result.append((path, m.group(3)))
            elif m.group(0) == '{':     # 匿名块入栈
                stack.append(None)
            elif stack:                 # } —— 出栈
                stack.pop()
        return result
    return []


def extract_primary_from_theme_vars(css_vars, scss_vars, tailwind_colors):
    """优先从显式主题变量/配置中推断主色"""
    candidates = []
    for var_name, value in css_vars:
        if any(pat in var_name for pat in PRIMARY_VAR_PATTERNS):
            rgb = rgb_of(value)
            if rgb and not is_neutral(rgb):
                candidates.append((value, f"CSS 变量 {var_name}"))
    for var_name, value in scss_vars:
        if any(pat.replace('--', '') in var_name for pat in ('$primary', 'brand', 'color-primary')):
            rgb = rgb_of(value)
            if rgb and not is_neutral(rgb):
                candidates.append((value, f"SCSS 变量 ${var_name}"))
    for name, value in tailwind_colors:
        leaf = name.split('.')[-1].lower()
        if leaf in ('primary', 'brand', 'main') and not is_neutral(rgb_of(value) or (0, 0, 0)):
            candidates.append((value, f"tailwind.config {name}"))
    return candidates[0] if candidates else None


def scan(project_root):
    source_files = collect_source_files(project_root)
    stack = detect_stack(project_root)
    tailwind_colors = extract_tailwind_colors(project_root)

    color_counter = Counter()
    color_sources = {}
    radius_counter = Counter()
    radius_sources = {}
    shadow_counter = Counter()
    shadow_sources = {}
    font_counter = Counter()
    font_sources = {}
    css_vars = []
    scss_vars = []

    for f in source_files:
        try:
            text = f.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        rel = str(f.relative_to(project_root)).replace('\\', '/')

        def bump(counter, sources, value):
            # 折叠跨行声明中的空白（多行 font-family/box-shadow）
            value = re.sub(r'\s+', ' ', value).strip()
            counter[value] += 1
            sources.setdefault(value, Counter())[rel] += 1

        for m in HEX_COLOR_RE.finditer(text):
            bump(color_counter, color_sources, normalize_hex(m.group(0)))
        for m in RGBA_COLOR_RE.finditer(text):
            bump(color_counter, color_sources, m.group(0).replace(' ', ''))
        for m in RADIUS_RE.finditer(text):
            bump(radius_counter, radius_sources, m.group(1))
        for m in SHADOW_RE.finditer(text):
            bump(shadow_counter, shadow_sources, m.group(1))
        for m in FONT_RE.finditer(text):
            bump(font_counter, font_sources, m.group(1))
        for m in CSS_VAR_RE.finditer(text):
            css_vars.append((m.group(1), m.group(2).strip()))
        for m in SCSS_COLOR_VAR_RE.finditer(text):
            scss_vars.append((m.group(1), m.group(2).strip()))

    notes = []
    tokens = []
    has_style_signal = bool(color_counter or css_vars or scss_vars or tailwind_colors)

    # ---- 分支判定（喂给 impeccable-wireframe.md 的 2-A/2-B 分支）----
    if not has_style_signal:
        branch = "new"
        notes.append("未检出任何设计令牌（颜色/CSS 变量/tailwind 配色），判定为新项目："
                     "走 impeccable-wireframe.md 分支 2-B（从零设计），prototype/preview 不依赖本快照。")
        radius_top, shadow_top = [], []
        font_top = None
        color_freq = []
    else:
        branch = "existing"
        tokens.append(_detect_primary(color_counter, color_sources, css_vars, scss_vars,
                                      tailwind_colors, notes))
        tokens.extend(_detect_neutrals(color_counter, color_sources, notes))
        radius_top = [{"value": v, "count": c, "sources": top_sources(radius_sources[v])}
                      for v, c in radius_counter.most_common(TOP_N) if 'var(' not in v]
        shadow_top = [{"value": v, "count": c, "sources": top_sources(shadow_sources[v])}
                      for v, c in shadow_counter.most_common(TOP_N) if 'var(' not in v]
        if font_counter:
            v, c = font_counter.most_common(1)[0]
            font_top = {"value": v, "count": c, "sources": top_sources(font_sources[v])}
        else:
            font_top = None
            notes.append("未检出 font-family 声明，字体栈用系统默认。")
        color_freq = [{"value": v, "count": c, "sources": top_sources(color_sources[v])}
                      for v, c in color_counter.most_common(TOP_N)]

    snapshot = {
        "type": "style-snapshot",
        "scannedAt": datetime.now().isoformat(timespec='seconds'),
        "projectRoot": str(project_root),
        "branch": branch,
        "detected": {
            **stack,
            "tailwindNamedColors": [{"name": n, "value": normalize_hex(v)} for n, v in tailwind_colors[:TOP_N]],
            "scannedFiles": len(source_files),
        },
        "tokens": {"colors": tokens, "radius": radius_top, "shadows": shadow_top, "fontStack": font_top},
        "colorFrequency": color_freq,
        "notes": notes,
    }
    return snapshot, source_files


def _detect_primary(color_counter, color_sources, css_vars, scss_vars, tailwind_colors, notes):
    """主色推断：显式主题变量 > 频率最高饱和色"""
    saturated = [(v, c) for v, c in color_counter.items()
                 if v.startswith('#') and not is_neutral(parse_hex(v) or (0, 0, 1))
                 and 0.12 < luminance(parse_hex(v) or (0, 0, 1)) < 0.95]
    saturated.sort(key=lambda x: -x[1])

    primary = extract_primary_from_theme_vars(css_vars, scss_vars, tailwind_colors)
    if primary:
        value, origin = primary
        token = {"role": "primary", "value": normalize_hex(value),
                 "confidence": "high", "sources": [origin]}
    elif saturated:
        v, c = saturated[0]
        token = {"role": "primary", "value": v, "confidence": "medium",
                 "sources": top_sources(color_sources[v])}
        notes.append("主色由出现频率最高的饱和色推断，请打开来源文件确认是否为品牌主色。")
    else:
        token = {"role": "primary", "value": None, "confidence": "none", "sources": []}
        notes.append("未检出饱和品牌色；原型主色留待 design 阶段决定。")

    # 双主色并存提示（新旧主色/双品牌并存是常见情况）
    if token["value"] and saturated:
        primary_count = dict(saturated).get(token["value"], 0)
        second = next(((v, c) for v, c in saturated if v != token["value"]), None)
        if second and primary_count and second[1] >= primary_count * 0.3:
            notes.append(f"检出第二高频饱和色 {second[0]}（{second[1]} 次，主色 {token['value']} "
                         f"{primary_count} 次），疑似新旧主色或双品牌并存，请结合页面源码确认归属。")
    return token


def _detect_neutrals(color_counter, color_sources, notes):
    """文字/边框/背景色：按明度分类的近灰系频率"""
    neutrals = [(v, c) for v, c in color_counter.items()
                if v.startswith('#') and is_neutral(parse_hex(v) or (1, 0, 0))]
    neutrals.sort(key=lambda x: -x[1])
    tokens = []

    def pick(role, lo, hi):
        for v, c in neutrals:
            lum = luminance(parse_hex(v))
            if lo <= lum < hi:
                tokens.append({"role": role, "value": v, "confidence": "medium",
                               "sources": top_sources(color_sources[v])})
                return
        tokens.append({"role": role, "value": None, "confidence": "none", "sources": []})

    pick("textPrimary", 0.0, 0.35)
    pick("textSecondary", 0.35, 0.62)
    pick("textTertiary", 0.62, 0.75)
    pick("border", 0.75, 0.92)
    bg = [x for x in neutrals if luminance(parse_hex(x[0])) >= 0.92]
    if bg:
        tokens.append({"role": "pageBackground", "value": bg[0][0], "confidence": "medium",
                       "sources": top_sources(color_sources[bg[0][0]])})
    else:
        tokens.append({"role": "pageBackground", "value": None, "confidence": "none", "sources": []})
    hover = [x for x in neutrals if 0.93 <= luminance(parse_hex(x[0])) < 0.97 and x[0] != '#ffffff']
    if hover:
        tokens.append({"role": "hoverBackground", "value": hover[0][0], "confidence": "low",
                       "sources": top_sources(color_sources[hover[0][0]])})
    return tokens


def render_markdown(snapshot):
    lines = []
    a = lines.append
    det = snapshot["detected"]
    branch_label = "已有项目（identity-preservation 优先）" if snapshot["branch"] == "existing" else "新项目（从零设计）"
    a(f"# 项目风格快照（{snapshot['scannedAt']}）")
    a("")
    a(f"- 项目根目录：`{snapshot['projectRoot']}`")
    a(f"- **分支判定：{branch_label}**")
    a(f"- 扫描文件数：{det['scannedFiles']}（src/styles/theme/packages/app/components 下的样式相关文件）")
    a(f"- UI 组件库：{det['uiLibrary'] or '未检出'}")
    a(f"- CSS 框架：{det['cssFramework'] or '未检出'}")
    a("")
    a("> 本报告由 `scripts/scan_style.py` 自动生成。置信度含义：high=显式主题变量/配置检出；"
      "medium=频率统计推断；low=推断但不唯一；none=未检出（留给 design 阶段）。")
    a("")

    if snapshot["branch"] == "existing" and snapshot["tokens"]["colors"]:
        a("## 设计 Token")
        a("")
        a("| 角色 | 值 | 置信度 | 来源 |")
        a("| ---- | -- | ------ | ---- |")
        for t in snapshot["tokens"]["colors"]:
            a(f"| {t['role']} | `{t['value'] or '—'}` | {t['confidence']} | {', '.join(t['sources']) or '—'} |")
        a("")

        for title, key in (("圆角", "radius"), ("阴影", "shadows")):
            if snapshot["tokens"][key]:
                a(f"### {title}（按出现频率）")
                a("")
                a("| 值 | 次数 | 来源 |")
                a("| -- | ---- | ---- |")
                for r in snapshot["tokens"][key]:
                    a(f"| `{r['value']}` | {r['count']} | {', '.join(r['sources']) or '—'} |")
                a("")
        fs = snapshot["tokens"]["fontStack"]
        if fs:
            a(f"### 字体栈\n\n`{fs['value']}`\n")
        if snapshot["colorFrequency"]:
            a("## 高频颜色 Top 12")
            a("")
            a("| 值 | 次数 | 来源 |")
            a("| -- | ---- | ---- |")
            for c in snapshot["colorFrequency"]:
                a(f"| `{c['value']}` | {c['count']} | {', '.join(c['sources']) or '—'} |")
            a("")
        if det.get("tailwindNamedColors"):
            a("## Tailwind 命名色")
            a("")
            for c in det["tailwindNamedColors"]:
                a(f"- `{c['name']}`：`{c['value']}`")
            a("")

    if snapshot["notes"]:
        a("## 扫描说明")
        a("")
        for n in snapshot["notes"]:
            a(f"- {n}")
        a("")

    if snapshot["branch"] == "existing":
        a("## 复核清单（AI 必做，完成后删除本段）")
        a("")
        a("1. 打开上方「来源」列的 1-2 个真实页面文件，确认主色/文字色/圆角/阴影判断与页面实际观感一致；")
        a("2. 通读一个列表页 + 一个弹窗/表单组件，将页面骨架提炼到下方「布局模式」段；")
        a("3. 冲突时以页面源码为准修正本报告，并同步修正 style-snapshot.json。")
        a("")
        a("## 布局模式（由 AI 复核后填写）")
        a("")
        a("```")
        a("整体布局：[如 左侧固定侧边栏 220px + 顶部页头 56px + 内容区 padding 24px]")
        a("列表页模式：[如 页头（标题+主操作按钮右对齐）→ 筛选栏 → 表格卡片 → 分页]")
        a("表单/弹窗模式：[如 宽 600px、圆角 16px、底部右对齐按钮]")
        a("按钮模式：[如 主按钮纯色/渐变、次按钮描边、危险按钮红色]")
        a("```")
        a("")
        a("> 用途：prototype.html 的字体与间距尺度、preview.html 的令牌复用均以本快照为据；"
          "视觉决策权仍在 design 阶段。")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="扫描项目源码提取设计令牌，生成 style-snapshot（req-analysis-skill）")
    parser.add_argument("--project", default=".", help="项目根目录（默认当前目录）")
    parser.add_argument("--output", default=".", help="快照输出目录（如 .nds/req-NNN/01-requirements）")
    args = parser.parse_args()

    project_root = Path(args.project).resolve()
    if not project_root.exists():
        print(f"❌ 项目目录不存在: {project_root}")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    snapshot, source_files = scan(project_root)

    json_path = output_dir / "style-snapshot.json"
    json_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 已生成: {json_path}")

    md_path = output_dir / "style-snapshot.md"
    md_path.write_text(render_markdown(snapshot), encoding="utf-8")
    print(f"✅ 已生成: {md_path}")

    branch_label = "已有项目" if snapshot["branch"] == "existing" else "新项目"
    print(f"📁 扫描了 {len(source_files)} 个源文件 → 分支判定：{branch_label}")
    if snapshot["branch"] == "existing":
        primary = next((t for t in snapshot["tokens"]["colors"] if t["role"] == "primary"), None)
        if primary and primary["value"]:
            print(f"🎨 主色: {primary['value']}（置信度 {primary['confidence']}，来源: {', '.join(primary['sources'])}）")
    print("👉 下一步: 按 SKILL.md「原型 HTML」步骤继续（已有项目复核快照后产双稿，新项目走 impeccable 2-B 分支）")


if __name__ == "__main__":
    main()

#!/usr/bin/env node
/**
 * nzw-dev-skills 原型截图脚本（req-analysis-skill 用途）
 *
 * 读取截图清单 shots.json（默认当前目录，可用 --config 指定），用 Puppeteer 2x 截图。
 *
 * 清单格式（数组，每项一个截图任务）：
 *   [
 *     { "file": "prototype.html", "selector": "#page-login",
 *       "output": "screenshots/prototype-login.png", "width": 1440, "height": 900 },
 *     { "file": "preview.html", "fullPage": true,
 *       "output": "screenshots/preview-full.png", "width": 1440, "height": 900 }
 *   ]
 *
 * - selector：只截取该元素（单文件多页原型按页区块截图，需原型内页面容器带 id）
 * - fullPage：整页截图（默认 true）；两者都不给时截视口
 *
 * 首次使用前安装依赖：
 *   cd <本脚本所在目录> && npm install
 *
 * 用法（在 .nds/req-NNN/01-requirements/ 目录下执行）：
 *   node <skill>/scripts/screenshot.mjs
 */
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);

let puppeteer;
try {
  puppeteer = require('puppeteer');
} catch {
  console.error('❌ 未找到 puppeteer，请先安装依赖：');
  console.error(`   cd "${__dirname}" && npm install`);
  process.exit(1);
}

// 解析 --config 参数（默认 ./shots.json）
const configIdx = process.argv.indexOf('--config');
const configPath = configIdx !== -1 ? process.argv[configIdx + 1] : 'shots.json';
const baseDir = path.dirname(path.resolve(configPath));

if (!fs.existsSync(configPath)) {
  console.error(`❌ 截图清单不存在: ${configPath}`);
  console.error('   请按 SKILL.md「截图捕获」步骤先生成 shots.json');
  process.exit(1);
}

let shots;
try {
  shots = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
} catch (e) {
  console.error(`❌ shots.json 解析失败: ${e.message}`);
  process.exit(1);
}
if (!Array.isArray(shots) || shots.length === 0) {
  console.error('❌ shots.json 应为非空数组');
  process.exit(1);
}

const browser = await puppeteer.launch({
  headless: 'new',
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
});

let failed = 0;
for (const shot of shots) {
  const srcFile = path.resolve(baseDir, shot.file);
  const outPath = path.resolve(baseDir, shot.output);

  if (!fs.existsSync(srcFile)) {
    console.error(`  ❌ 源文件不存在，跳过: ${shot.file}`);
    failed += 1;
    continue;
  }

  console.log(`Capturing: ${shot.file}${shot.selector ? ` (${shot.selector})` : ''} -> ${shot.output}`);

  const page = await browser.newPage();
  await page.setViewport({
    width: shot.width || 1440,
    height: shot.height || 900,
    deviceScaleFactor: 2, // 2x 缩放，保证视网膜屏清晰度
  });

  try {
    await page.goto(`file:///${srcFile.replace(/\\/g, '/')}`, {
      waitUntil: 'networkidle0',
      timeout: 20000,
    });
    await new Promise((r) => setTimeout(r, 500));

    fs.mkdirSync(path.dirname(outPath), { recursive: true });

    if (shot.selector) {
      const el = await page.$(shot.selector);
      if (el) {
        await el.screenshot({ path: outPath, type: 'png' });
      } else {
        console.warn(`  ⚠ 未找到选择器 ${shot.selector}，回退整页截图`);
        await page.screenshot({ path: outPath, fullPage: true, type: 'png' });
      }
    } else {
      await page.screenshot({
        path: outPath,
        fullPage: shot.fullPage !== false,
        type: 'png',
      });
    }
    console.log(`  Done: ${shot.output}`);
  } catch (e) {
    console.error(`  ❌ 截图失败 ${shot.file}: ${e.message}`);
    failed += 1;
  } finally {
    await page.close();
  }
}

await browser.close();

if (failed > 0) {
  console.error(`⚠ 完成，但 ${failed} 个任务失败，请修复对应 HTML 后重试`);
  process.exit(1);
}
console.log('All screenshots captured!');

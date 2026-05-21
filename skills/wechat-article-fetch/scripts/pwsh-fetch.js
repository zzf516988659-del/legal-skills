#!/usr/bin/env node
/**
 * 微信公众号文章抓取 - WSL2 + Python subprocess 中转版
 *
 * 原理（已验证可行，2026-05-20 实测）：
 * 1. Node.js 生成 .bat + .js 到 Windows 临时目录
 * 2. Node spawn python3 执行 Python helper 脚本（通过文件路径，无复杂引号）
 * 3. Python helper 内部用 subprocess 调用 bash -c '...cmd.exe /c bat'
 *    （Python Popen 能正确处理 WSL2 interop）
 * 4. .bat 内部 cd → set NODE_PATH → node 执行 Playwright JS
 * 5. 读取 __WX_RESULT__...__WX_END__ 标记解析 JSON 结果
 *
 * 用法: node pwsh-fetch.js <URL> [output.md]
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// WSL2 → Windows 路径映射
const WSL_TEMP = '/mnt/c/Users/Administrator/AppData/Local/Temp';
// WIN_TEMP 在 Node.js 字符串里用双反斜杠，到 Python 文件时用 r"..." raw string 就不会有问题
const WIN_TEMP = 'C:\\Users\\Administrator\\AppData\\Local\\Temp';

// 从 cookie 文件加载（优先使用最新 cookie）
function loadCookies() {
  const cookieDir = '/home/administrator/.openclaw/media/inbound';
  try {
    const files = fs.readdirSync(cookieDir)
      .filter(f => f.startsWith('cookies_') && f.endsWith('.json'))
      .sort()
      .reverse();
    if (files.length === 0) return null;
    const latest = files[0];
    const raw = JSON.parse(fs.readFileSync(path.join(cookieDir, latest), 'utf8'));
    return raw.filter(c => c.domain === 'mp.weixin.qq.com').map(c => ({
      name: c.name,
      value: c.value,
      domain: '.mp.weixin.qq.com',
      path: c.path,
      sameSite: (c.sameSite === 'Strict' || c.sameSite === 'Lax' || c.sameSite === 'None') ? c.sameSite : 'Lax'
    }));
  } catch (e) {
    return null;
  }
}

const WX_COOKIES = loadCookies();

function buildJsCode(url, cookies) {
  const cookiesStr = JSON.stringify(cookies);
  return 'const { chromium } = require(\'playwright\');\n' +
    'const fs = require(\'fs\');\n' +
    'const edgePath = \'C:\\\\Program Files (x86)\\\\Microsoft\\\\Edge\\\\Application\\\\msedge.exe\';\n' +
    'const cookies = ' + cookiesStr + ';\n' +
    '(async () => {\n' +
    '  let browser;\n' +
    '  try {\n' +
    '    const options = { headless: true, args: [\'--no-sandbox\', \'--disable-setuid-sandbox\'] };\n' +
    '    if (fs.existsSync(edgePath)) { options.executablePath = edgePath; console.log("Using Edge"); } else { console.log("Edge not found at " + edgePath); }\n' +
    '    browser = await chromium.launch(options);\n' +
    '    const ctx = await browser.newContext();\n' +
    '    for (const c of cookies) { await ctx.addCookies([c]); }\n' +
    '    const page = await ctx.newPage();\n' +
    '    await page.setExtraHTTPHeaders({ \'Referer\': \'https://mp.weixin.qq.com/\' });\n' +
    '    await page.goto(\'' + url + '\', { waitUntil: \'networkidle\', timeout: 25000 });\n' +
    '    await page.waitForTimeout(5000);\n' +
    '    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));\n' +
    '    await page.waitForTimeout(2000);\n' +
    '    const data = await page.evaluate(() => {\n' +
    '      const a = document.querySelector(\'#js_content\') || document.querySelector(\'.rich_media_content\') || document.body;\n' +
    '      return { title: document.title.replace(\'微信公众平台\',\'\').trim(), html: a.innerHTML, url: window.location.href };\n' +
    '    });\n' +
    '    await browser.close();\n' +
    '    console.log(\'__WX_RESULT__\');\n' +
    '    process.stdout.write(JSON.stringify(data));\n' +
    '    console.log(\'__WX_END__\');\n' +
    '  } catch(e) {\n' +
    '    console.error(\'__WX_ERROR__:\'+e.message);\n' +
    '    if(browser) await browser.close().catch(()=>{});\n' +
    '    process.exit(1);\n' +
    '  }\n' +
    '})();';
}

function parseHtmlToMarkdown(html, url) {
  const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/);
  const title = titleMatch ? titleMatch[1].replace(/微信公众平台/, '').trim() : '无标题';

  const contentMatch = html.match(/id="js_content"[^>]*>([\s\S]*?)<\/div>\s*<div[^>]*id="js_pc_qr_code"/);
  const rawHtml = contentMatch ? contentMatch[1] : html;

  if (rawHtml.includes('参数错误') || rawHtml.includes('访问异常') || rawHtml.includes('此内容无法查看') || rawHtml.includes('诱导关注')) {
    throw new Error('文章不存在、已删除或无法访问');
  }

  const images = [];
  for (const m of rawHtml.matchAll(/data-src="([^"]+)"/g)) {
    images.push({ url: m[1], alt: '图片' + (images.length + 1), index: images.length });
  }

  function imgAlt(idx) { return images[idx] ? images[idx].alt : '图片' + (idx + 1); }

  let content = rawHtml
    .replace(/<img[^>]*>/gi, (match) => {
      const srcMatch = match.match(/data-src=["']([^"']+)["']/);
      if (srcMatch) {
        const idx = images.findIndex(i => i.url === srcMatch[1]);
        return idx >= 0 ? '\n\n![' + imgAlt(idx) + '](' + srcMatch[1] + ')\n\n' : '';
      }
      return '';
    })
    .replace(/<p[^>]*>/gi, '\n\n')
    .replace(/<\/p>/gi, '')
    .replace(/<h[1-6][^>]*>/gi, '\n\n## ')
    .replace(/<\/h[1-6]>/gi, '\n\n')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, '\n\n')
    .replace(/^\n+/, '')
    .replace(/\n+$/, '')
    .trim();

  return {
    title,
    content,
    url: url || '',
    images,
    fetchedAt: new Date().toISOString()
  };
}

function formatMarkdown(article) {
  let md = '# ' + article.title + '\n\n';
  md += '> 来源: ' + article.url + '\n';
  md += '> 抓取时间: ' + article.fetchedAt + '\n\n';
  md += '---\n\n';
  md += article.content + '\n\n';
  if (article.images.length > 0) {
    md += '---\n\n**图片列表**（共 ' + article.images.length + ' 张）:\n\n';
    article.images.forEach((img, i) => {
      md += (i + 1) + '. ' + img.alt + ': ' + img.url + '\n';
    });
  }
  return md;
}

async function fetchViaPythonScript(url) {
  if (!WX_COOKIES || WX_COOKIES.length === 0) {
    throw new Error('未找到有效的微信 cookie，请重新扫码登录获取');
  }

  const ts = Date.now();
  const jsFile = WSL_TEMP + '/wechat_' + ts + '.js';
  const batFile = WSL_TEMP + '/wechat_' + ts + '.bat';
  const pyFile = WSL_TEMP + '/wechat_' + ts + '.py';

  const jsCode = buildJsCode(url, WX_COOKIES);

  // BAT 内容：CRLF 换行，NODE_PATH 用双反斜杠
  const batContent = '@echo off\r\n' +
    'cd /d ' + WIN_TEMP + '\r\n' +
    'set NODE_PATH=C:\\Users\\Administrator\\AppData\\Roaming\\npm\\node_modules\r\n' +
    '"C:\\Program Files\\nodejs\\node.exe" "' + WIN_TEMP + '\\wechat_' + ts + '.js"\r\n' +
    'if errorlevel 1 exit /b 1';

  // Python 内容：bat 路径用 r"..." raw string，避免 \U \A 等被 Python 解释为转义序列
  const pyLines = [
    'import subprocess, sys, os',
    'ts = ' + ts,
    // r"..." raw string：Windows 路径里的 \ 不再被解释为转义
    'bat = r"C:\\Users\\Administrator\\AppData\\Local\\Temp\\wechat_" + str(ts) + ".bat"',
    'sys.stderr.write("DEBUG bat=" + bat + " exists=" + str(os.path.exists(bat)) + "\\n")',
    'cmd = ["/bin/bash", "-c", "cd /mnt/c && /mnt/c/Windows/System32/cmd.exe /c \\"" + bat + "\\""]',
    'sys.stderr.write("DEBUG cmd=" + str(cmd) + "\\n")',
    'ps = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)',
    'out, err = ps.communicate()',
    'sys.stderr.write("DEBUG ps.returncode=" + str(ps.returncode) + " err=" + err.decode("utf-8", errors="replace")[:200] + "\\n")',
    'print(out.decode("utf-8", errors="replace"), end="")',
    'exit(ps.returncode)'
  ];
  const pyContent = pyLines.join('\n');

  fs.writeFileSync(jsFile, jsCode, 'utf8');
  fs.writeFileSync(batFile, batContent, 'utf8');
  fs.writeFileSync(pyFile, pyContent, 'utf8');

  return new Promise((resolve, reject) => {
    const ps = spawn('python3', [pyFile], { stdio: ['pipe', 'pipe', 'pipe'] });

    let stdout = '';
    let stderr = '';
    ps.stdout.on('data', chunk => { stdout += chunk.toString(); });
    ps.stderr.on('data', chunk => { stderr += chunk.toString(); });

    const timer = setTimeout(() => {
      ps.kill('SIGKILL');
      cleanup();
      reject(new Error('执行超时 75s\n' + stderr.slice(0, 500)));
    }, 75000);

    function cleanup() {
      try { fs.unlinkSync(jsFile); } catch {}
      try { fs.unlinkSync(batFile); } catch {}
      try { fs.unlinkSync(pyFile); } catch {}
    }

    ps.on('close', (code) => {
      clearTimeout(timer);
      cleanup();

      if (code !== 0) {
        reject(new Error('执行失败，退出码 ' + code + '\nSTDERR: ' + stderr.slice(0, 500)));
        return;
      }

      const resultMatch = stdout.match(/__WX_RESULT__([\s\S]*?)__WX_END__/);
      if (!resultMatch) {
        const wxError = stdout.match(/__WX_ERROR__:(.*)/);
        if (wxError) {
          reject(new Error('抓取错误: ' + wxError[1].trim()));
        } else {
          reject(new Error('无法解析输出\nSTDOUT: ' + stdout.slice(0, 200) + '\nSTDERR: ' + stderr.slice(0, 300)));
        }
        return;
      }

      let data;
      try {
        data = JSON.parse(resultMatch[1].trim());
      } catch(e) {
        reject(new Error('JSON解析失败: ' + resultMatch[1].slice(0, 100)));
        return;
      }
      resolve(data);
    });

    ps.on('error', (err) => {
      clearTimeout(timer);
      reject(new Error('进程错误: ' + err.message));
    });
  });
}

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error('用法: node pwsh-fetch.js <URL> [output.md]');
    console.error('示例: node pwsh-fetch.js https://mp.weixin.qq.com/s/xxxxx');
    process.exit(1);
  }

  const outputFile = process.argv[3] || null;

  console.log('\u{1F7E2} 正在抓取: ' + url);

  try {
    const data = await fetchViaPythonScript(url);

    if (!data.html) {
      throw new Error('页面 HTML 为空，可能需要更新 cookie');
    }

    const checkStrings = ['无法查看', '此内容已被发布者删除', '诱导关注'];
    if (checkStrings.some(s => data.html.includes(s))) {
      throw new Error('文章不存在、已删除或需微信授权关注');
    }

    const article = parseHtmlToMarkdown(data.html, data.url || url);
    const md = formatMarkdown(article);

    if (outputFile) {
      fs.writeFileSync(outputFile, md, 'utf8');
      console.log('\u2705 已保存: ' + outputFile);
    } else {
      console.log('\n' + md);
    }

    console.log('\n\u2705 抓取成功！标题: ' + article.title);
    console.log('\u{1F4C4} 正文长度: ' + article.content.length + ' 字，图片: ' + article.images.length + ' 张');

  } catch (err) {
    console.error('\u274C 抓取失败: ' + err.message);
    process.exit(1);
  }
}

main();
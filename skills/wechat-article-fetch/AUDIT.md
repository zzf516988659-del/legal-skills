# wechat-article-fetch 安全审核记录

> **审核日期**:2026-06-10
> **审核人**:小法师(信拓集团法务助理)
> **审核结论**:**已通过人工审核,允许使用**

## 一、`child_process` 调用清单

| 文件 | 行号 | 调用 | 用途 | 风险等级 |
|---|---|---|---|---|
| `scripts/fetch.js` | 87 | `spawn(npx, [playwright, install, chromium])` | 首次运行时自动安装 Playwright Chromium 浏览器 | 🟢 低 |
| `scripts/pwsh-fetch.js` | 195 | `spawn(python3, [pyFile])` | 抓取微信公众号文章的 Python 脚本(由 Node 生成的 .py 文件) | 🟢 低 |

## 二、风险评估

### fetch.js
- ✅ 仅运行 `npx playwright install` 单一白名单命令
- ✅ 安装路径固定在 `node_modules/playwright`
- ✅ 无 shell 注入点(使用 argv 数组,非 shell 字符串)
- ✅ 来源:官方 cat-xierluo/legal-skills 上游仓库(v1.3.1)

### pwsh-fetch.js
- ✅ 仅 spawn 本地 `python3` 解释器
- ✅ 执行的 .py 文件由 Node 端通过 `fs.writeFileSync` 写入,**来源受控**
- ✅ URL 已加白名单约束:`^https://mp\.weixin\.qq\.com/s/`
- ✅ 加固日期:2026-06-02(参见 MEMORY.md § 十二)
- ✅ 来源:官方 cat-xierluo/legal-skills 上游仓库

## 三、code_safety 静态扫描误报说明

`openclaw security audit` 报告此技能"包含危险代码模式",**实际为功能性 child_process 调用**,无恶意 payload。

**处置方式**:**白名单化**(本审核记录)——不再要求每次扫描命中后人工复审。

## 四、定期复核

- 下次复核日期:**2026-09-10**(季度复核)
- 复核触发条件:技能升级到 v1.4.x / 上游变更
- 复核内容:重新核对 child_process 调用清单

## 五、不可接受的变更(白名单撤回条件)

- ❌ 新增对未列入白名单的 URL/文件调用
- ❌ 改用 `shell: true` 或字符串拼接命令
- ❌ 新增对外网任意域名的 HTTP 请求
- ❌ 修改 Playwright 安装逻辑(加装其他浏览器内核需复审)

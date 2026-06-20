# 信拓集团法律文书标准格式配置

> 版本：v0.1.0 | 更新：2026-06-06 | 适用：所有对外法律文书

---

## 一、字体规范

| 用途 | 字体 | 字号 | 说明 |
|---|---|---|---|
| 正文（中文） | 仿宋_GB2312 | 14pt（28 half-points） | 标准法律文书正文 |
| 西文/数字 | Times New Roman | 14pt（28 half-points） | 与中文正文等宽 |
| 标题（中文） | 黑体 | 16pt（32 half-points） | 一级标题 |
| 副标题 | 仿宋_GB2312 | 14pt 加粗 | 二级标题 |
| 页眉 | 仿宋_GB2312 | 10pt（20 half-points） | 公司简称 |
| 页脚 | 仿宋_GB2312 | 10pt（20 half-points） | 页码 |

**字体回退规则**：
- 中文字体 fallback：仿宋_GB2312 → 仿宋 → 宋体
- 西文字体 fallback：Times New Roman → Arial → 无衬线
- **弯引号必须与 eastAsia 字体一致**——md2word 生成的 DOCX 中弯引号默认用 ASCII 字体，需修复

---

## 二、页眉规范

| 文书类型 | 页眉内容 | 位置 |
|---|---|---|
| 律师函/催告函 | 江苏信拓建设（集团）股份有限公司 | 居中 |
| 答辩状/上诉状 | 空白（不使用页眉） | — |
| 合同/协议 | 空白或合同编号 | 居左 |
| 审查报告 | 江苏信拓建设（集团）股份有限公司 | 居中 |
| 判决/裁定归档 | 空白 | — |

---

## 三、页脚规范

| 文书类型 | 页脚内容 | 格式 |
|---|---|---|
| 律师函/催告函 | 第 X 页 共 Y 页 | 居中 |
| 答辩状/上诉状 | 第 X 页 共 Y 页 | 居中 |
| 合同/协议 | 第 X 页 共 Y 页 | 居中 |
| 审查报告 | 第 X 页 共 Y 页 | 居中 |
| 判决/裁定归档 | 第 X 页 共 Y 页 | 居中 |

---

## 四、段落规范

| 项目 | 规范 |
|---|---|
| 行距 | 单倍行距（wordDocument默认） |
| 段前间距 | 0pt |
| 段后间距 | 0pt |
| 首行缩进 | 2字符（0.74cm） |
| 页边距 | 上：2.54cm，下：2.54cm，左：2.54cm，右：2.54cm |
| 页面方向 | 纵向（A4） |
| 页码格式 | 第 X 页 共 Y 页，阿拉伯数字 |

---

## 五、标题层级

| 层级 | 格式 | 示例 |
|---|---|---|
| 一级标题 | 黑体 16pt，居中，不加粗 | 一、事实 |
| 二级标题 | 仿宋_GB2312 14pt，左对齐，加粗 | （一）合同签订情况 |
| 三级标题 | 仿宋_GB2312 14pt，左对齐，不加粗 | 1. 合同主体 |
| 正文 | 仿宋_GB2312 14pt，首行缩进2字符 | （正文内容） |

---

## 六、信拓集团固定内容（不得修改）

| 内容 | 固定值 |
|---|---|
| 发函单位全称 | 江苏信拓建设（集团）股份有限公司 |
| 简称 | 信拓集团 |
| 英文名 | Jiangsu Xintuo Construction (Group) Co., Ltd. |
| 注册地址 | 如东县掘港镇泰山路 28 号（如东新税务大楼斜对面） |
| 法务部联系人 | 法务专员 |
| 函件编号格式 | 信拓律函字[YYYY]第 N 号 |

---

## 七、模板文件位置

| 模板类型 | 位置 |
|---|---|
| Markdown 字段化模板 | `~/.openclaw/workspace/skills/legal-skills-github/skills/contract-templates/templates/` |
| DOCX 母版模板（含页眉页脚） | `~/.openclaw/workspace/skills/legal-skills-github/skills/contract-templates/docx_templates/` |
| 标准格式配置 | `~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/references/xintuo-format.md` |

---

## 八、DOCX 模板制作规范（使用 apply_docx_template.py 时）

1. **模板准备**：在 Word 中创建带 `{{KEY}}` 占位符的 DOCX 文件，预先设置好页眉/页脚/字体/段落样式
2. **占位符格式**：必须使用 `{{KEY}}` 格式（无空格），KEY 只能包含字母、数字、下划线
3. **字段填充**：
   ```bash
   python3 ~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/scripts/apply_docx_template.py \
     TEMPLATE.docx OUTPUT.docx \
     --replacements-json /path/to/data.json
   ```
4. **门禁校验**：
   ```bash
   python3 ~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/scripts/format_gate.py \
     --docx OUTPUT.docx
   ```

---

## 九、交付前门禁检查清单

| 检查项 | 标准 |
|---|---|
| 字体 | 仿宋_GB2312 + Times New Roman，无其他中文字体混用 |
| 弯引号字体 | ascii/hAnsi/cs 字体必须与 eastAsia 一致 |
| 标点字体 | 全角标点使用仿宋_GB2312，半角使用 Times New Roman |
| 页眉 | 按文书类型（见第二节） |
| 页脚 | 第 X 页 共 Y 页，居中 |
| 首行缩进 | 2 字符 |
| 行距 | 单倍行距 |
| 页边距 | 上下左右 2.54cm |
| 空段落 | 无连续空行/空段 |
| 页码 | 阿拉伯数字，与页脚联动 |

---

## 十、已知格式风险

| 风险 | 原因 | 解决方案 |
|---|---|---|
| 弯引号 WPS 回退 | md2word 输出时弯引号 run 用了 ASCII 字体 | 在 Markdown 源码中将 `"` `"` 替换为全角引号，或生成后用 wenge 修复 |
| 标点字体混杂 | 同一文档混用多种字体 | 统一 run 的 rFonts 属性 |
| 标题字体不一致 | `# 标题` 用了默认黑体，非标准仿宋 | Markdown 中明确指定或 post-processing 修正 |
| 页眉消失 | 文档分节时页眉断开 | 检查 sectionProperties 中的 headerReference |
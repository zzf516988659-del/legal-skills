# Legacy: md2word-gate 迁移记录

> **创建时间**: 2026-06-20
> **状态**: md2word-gate v0.1.0 已合并入 wenge v0.1.0

## 背景

md2word-gate v0.1.0(本地独有,400 行 Python)曾是小法师律所的"轻量门禁"工具,致敬文格(lilialla/legal-document-format-skill)的"交付前门禁"思想。

设计哲学:**仅做"门禁校验",不做格式转换**。

## 11 项检查清单(已 100% 覆盖)

| # | 检查项 | wenge 对应模块 |
|---|---|---|
| 1 | OpenXML 结构完整性(zip/document.xml/可被 python-docx 解析) | `scripts/audit_docx_structure.py` |
| 2 | 页眉页脚是否存在(信拓集团页眉+页码) | `scripts/audit_docx_structure.py` + `references/format-checklist.md` 页面章节 |
| 3 | 页码字段(使用 PAGE 字段而非硬编码) | `scripts/audit_docx_structure.py` PAGE_FIELD_RE |
| 4 | 标题样式引用(Heading 1 而非字号设置) | `scripts/audit_docx_structure.py` TITLE_STYLE_IDS |
| 5 | 表格边框 | `references/format-checklist.md` 表格条目 |
| 6 | 字体合规(仿宋_GB2312/Times New Roman 配比) | `scripts/audit_docx_structure.py` + `references/format-checklist.md` 字体章节 |
| 7 | 字符数统计(正文+表格) | `scripts/format_gate.py` count_severities |
| 8 | 段落数(总段落/表格数) | `scripts/format_gate.py` |
| 9 | 渲染页门禁(LibreOffice+Poppler,页码/签名/页面) | `scripts/compare_rendered_pages.py` + `references/visual-validation.md` |
| 10 | 中文标点全角(检测半角混入) | `scripts/audit_docx_structure.py` CJK_PUNCTUATION / HALFWIDTH_PUNCTUATION |
| 11 | 空段检测(连续 3+ 个空段) | `scripts/audit_docx_structure.py` |

## wenge 额外能力(md2word-gate 不具备)

| # | 能力 | 描述 |
|---|---|---|
| 12 | 模板比对 | `scripts/compare_docx_template_parity.py` DOCX ↔ 模板等价性 |
| 13 | 视觉验证 | `scripts/compare_rendered_pages.py` 候选 PNG ↔ 基准 PNG |
| 14 | Release 烟测 | `scripts/release_smoke.py` 模板出文端到端验证 |
| 15 | 内容锁定 | `references/content-lock.md` 防止正文被改坏 |
| 16 | 信拓格式规范 | `references/xintuo-format.md` 江苏信拓集团专用格式 |
| 17 | 路由决策 | `references/routing.md` 智能判定走哪条门禁路径 |
| 18 | 失败模式 | `references/failure-modes.md` 已知门禁失败 + 修复模板 |

## 退出码规范(保留)

```
0 - 全部通过
1 - 有警告(非严格模式不视为失败)
2 - 有失败
3 - 文件错误
```

## 历史调用命令(已废弃)

```bash
# 旧命令(已废弃)
python3 skills/md2word-gate/scripts/md2word_gate.py /path/to/output.docx

# 新命令(wenge 替代)
python3 skills/wenge/scripts/format_gate.py --docx /path/to/output.docx
python3 skills/wenge/scripts/format_gate.py --docx /path/to/output.docx --fail-on-warning
```

## 引用方迁移指南

涉及以下脚本/文档的 md2word-gate 引用需更新为 wenge:

- `skills/legal-skill-router/SKILL.md`
- `skills/legal-skill-router/references/快速决策表.md`
- `skills/contract-templates/SKILL.md`
- `skills/contract-templates/scripts/render_template.py`

## 设计哲学保留

md2word-gate 的核心思想"交付前门禁 / 不做格式转换 / 严格检查"已完全融入 wenge 的 format_gate.py 设计与 references/routing.md 路由决策中。

---
name: md2word-gate
version: 0.1.0
author: 杨卫薪律师（微信ywxlaw）
description: md2word 交付前门禁。在 md2word --preset=legal 输出 DOCX 后做 OpenXML 结构校验 + 关键元素检查，输出门禁报告，避免"差不多"的法律文书流入业务流。本 skill 不做格式转换，仅做门禁校验。
license: MIT
---

# md2word-gate（md2word 交付前门禁）

> 致敬：本文格（lilialla/legal-document-format-skill）"交付前门禁"思想。
> 致敬：本文格（lilialla/legal-document-format-skill）"三不原则"。
> 来源学习：https://mp.weixin.qq.com/s/6ayoCO6MovoNurvL8RDZUA

## 一、定位

**md2word-gate 不是一个新转换器，而是 md2word 输出 DOCX 后的"门禁层"。**

- **md2word** 负责：Markdown → DOCX（仿宋_GB2312/1.5 倍行距/页码/标题样式）
- **md2word-gate** 负责：DOCX → 检查清单 → 通过/打回

## 二、门禁检查项（v0.1.0）

| 检查项 | 说明 | 必检/可选 |
|---|---|---|
| OpenXML 结构完整性 | zip 包结构、document.xml 是否存在、是否可被 python-docx 解析 | 必检 |
| 页眉页脚是否存在 | 法律文书通常要求"信拓集团"页眉 + 页码 | 必检 |
| 页码字段 | 是否使用 PAGE 字段（而非硬编码"1"） | 必检 |
| 标题样式引用 | 一级标题是否引用 Heading 1 样式（非直接设置字号） | 必检 |
| 表格边框 | 是否有表格且包含边框 | 必检（如有表格） |
| 字体合规 | 仿宋_GB2312 / Times New Roman 配比是否正确 | 必检 |
| 字符数统计 | 正文+表格的总字符数 | 必检 |
| 段落数 | 总段落数、表格数 | 必检 |
| 渲染页门禁 | 需 LibreOffice + Poppler，PDF → 图片，检查页码/签名区/页面数 | 可选（环境依赖） |
| 中文标点全角 | 检测正文是否混入半角标点 | 必检 |
| 空段检测 | 是否存在连续 3 个以上空段 | 必检 |

## 三、快速开始

### 命令行调用

```bash
# 基本门禁（仅 OpenXML 校验，零依赖）
python3 scripts/md2word_gate.py /path/to/output.docx

# 输出 JSON 报告
python3 scripts/md2word_gate.py /path/to/output.docx --json

# 严格模式（任何警告都视为不通过）
python3 scripts/md2word_gate.py /path/to/output.docx --strict

# 启用渲染页门禁（需 LibreOffice + Poppler）
python3 scripts/md2word_gate.py /path/to/output.docx --enable-render
```

### 输出格式

#### 文本格式（默认）

```
========================================
md2word-gate 交付前门禁报告
========================================
文件: 周世文超龄用工合同_审查报告.docx
检查时间: 2026-06-05 14:40
========================================

✅ OpenXML 结构完整性      通过
✅ 页眉页脚                通过
✅ 页码字段                警告 (使用硬编码页码"1"而非 PAGE 字段)
✅ 标题样式引用            通过
✅ 表格边框                跳过 (无表格)
✅ 字体合规                警告 (正文使用宋体而非仿宋_GB2312)
✅ 字符数统计              通过 (4923 字)
✅ 段落数                  通过 (87 段)
✅ 中文标点全角            通过
✅ 空段检测                通过

========================================
结论: ⚠️ 有警告 (2 项)
建议: 修正警告后重新生成
========================================
```

#### JSON 格式

```json
{
  "file": "周世文超龄用工合同_审查报告.docx",
  "checked_at": "2026-06-05T14:40:00+08:00",
  "overall": "warning",
  "passed": 8,
  "warning": 2,
  "failed": 0,
  "items": [
    {"name": "OpenXML 结构完整性", "status": "pass", "detail": ""},
    {"name": "页眉页脚", "status": "pass", "detail": "页眉=信拓集团, 页脚=页码"},
    {"name": "页码字段", "status": "warning", "detail": "硬编码'1'而非 PAGE 字段"},
    ...
  ]
}
```

## 四、退出码

| 退出码 | 含义 |
|---|---|
| 0 | 全部通过 |
| 1 | 有警告（默认非严格模式不视为失败） |
| 2 | 有失败（结构不完整或关键检查未通过） |
| 3 | 文件不存在或不可读 |

## 五、整合到现有工作流

### 5.1 作为 `md2word --preset=legal` 的后置门禁

在 `MEMORY.md` 的"文书输出"流程中，将：
```bash
# 旧
python3 .../md2word.py <输入.md> --preset=legal -o <输出.docx>

# 新
python3 .../md2word.py <输入.md> --preset=legal -o <输出.docx>
python3 .../md2word_gate.py <输出.docx>  # 门禁
```

### 5.2 与 `legal-proposal-generator` 联动

`legal-proposal-generator` 输出后强制走 `md2word_gate.py`：
- 失败 → 不发送
- 警告 → 法务人工复核后再发送

## 六、依赖

| 依赖 | 必装 | 用途 |
|---|---|---|
| `python-docx` | ✅ | 解析 OpenXML |
| `Pillow` | 可选 | 渲染页门禁（PDF → 图片） |
| `LibreOffice` | 可选 | 渲染页门禁（DOCX → PDF） |
| `poppler-utils` (pdftoppm) | 可选 | 渲染页门禁（PDF → 图片） |

**安装核心依赖**：
```bash
pip install python-docx
```

**安装渲染门禁依赖**（WSL2）：
```bash
sudo apt install libreoffice poppler-utils
```

## 七、设计原则（来自文格）

> **"能执行的执行。能检查的检查。能证明的证明。证明不了的地方，直接报告给人。"**

本 skill 严格遵守此原则：
- 能用 OpenXML 检查的（如样式引用）→ 检查
- 不能检查的（如"页面是否好看"）→ 报告给人
- 不擅自修改原 DOCX，只输出报告

## 八、路线图

| 版本 | 功能 |
|---|---|
| **v0.1.0**（当前） | OpenXML 结构校验 + 关键元素检查 |
| v0.2.0 | 渲染页门禁（LibreOffice + Poppler） |
| v0.3.0 | 与信拓集团模板对齐（自定义检查项） |
| v0.4.0 | 自动修复（如页码字段自动改用 PAGE） |

## 九、相关引用

- **文格**：`github.com/lilialla/legal-document-format-skill`
- **md2word**：`skills/legal-skills-github/skills/md2word/`
- **contract-copilot-engine**：`github.com/maoo8485/contract-copilot-engine`

---
name: wenge
version: 0.1.0
author: 江苏信拓建设（集团）股份有限公司 法务部（封装 lilialla 文格 v2.2.0）
description: 文格（lilialla/legal-document-format-skill）的本地化封装。信拓集团法律文书格式门禁，集成 L0-L4 路由、DOCX 结构审计、文本审计、模板执行、视觉校验。原版地址：https://github.com/lilialla/legal-document-format-skill
license: MIT
---

# 文格（wenge）— 信拓集团法律文书格式门禁

> 致敬作者：**lilialla**（文格原作者）
> 原版地址：`https://github.com/lilialla/legal-document-format-skill`
> 原版版本：v2.2.0（2026-06-05 拉取）
> **本仓库为本地化封装，原版 100% 保留所有脚本与文档；仅追加本地化 SKILL.md**

## 一、定位

**文格 wenge = 信拓集团法律文书格式门禁的"专业版"**。

| 维度 | 我们的 md2word-gate | 文格 wenge |
|---|---|---|
| 版本 | v0.1.1（自研） | v2.2.0（开源） |
| 代码量 | 400 行 | 3089 行（7x） |
| 测试覆盖 | 0 | 65 + 10 步 release smoke |
| DOCX 审计 | 基础 9 项 | 25+ 项（cjk_quote_font_mismatch 等专业检查） |
| 文本审计 | 半角标点 | 半角标点 + 连续空格 + 行尾空格 + 混合宽度 + 空括号 |
| 视觉校验 | ❌ | ✅（需 LibreOffice + Poppler） |
| 模板执行 | ❌ | ✅（apply_docx_template.py） |
| 路由 | 1 层 | L0-L4 五层 |

**结论**：本封装**直接替代** `md2word-gate`，**所有信拓集团的法律文书门禁都走 wenge**。

## 二、L0-L4 路由表（信拓定制）

| 路由 | 任务 | 文格读 | 信拓典型场景 |
|---|---|---|---|
| **L0 文本清理** | 标点/格式清理 | `audit_text.py` | 法条/案例入库前清理 |
| **L1 普通 DOCX** | Markdown→DOCX | `format_gate.py --docx` | 内部讨论稿、草稿 |
| **L2 模板执行** | 按模板生成 | `apply_docx_template.py` | 律师函/催告函批量生成 |
| **L3 裁决书定稿** | 仲裁裁决书格式 | `format_gate.py --require-visual` | 一审/二审判决书归档 |
| **L4 视觉校验** | 渲染 PDF/PNG | `render_docx.sh` + `compare_rendered_pages.py` | 对外发送、归档、盖章文件 |

## 三、与现有 skill 的关系

| 现有 skill | 关系 |
|---|---|
| `md2word` | **上游**：Markdown→DOCX，文格作用于其输出 |
| `md2word-gate` | **被替代**：wenge 是升级版 |
| `contract-templates` | **L2 模板执行**的简化版（仅律师函/催告函等高频） |
| `legal-skill-router` | **总入口**：判定任务后分发 |
| `de-ai-polish` | **L0 文本清理**的简化版（仅标点修正） |

## 四、5 分钟快速上手

### 4.1 单文件门禁

```bash
python3 ~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/scripts/format_gate.py \
  --docx /path/to/output.docx
```

### 4.2 文本审计（无需 DOCX）

```bash
python3 ~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/scripts/audit_text.py \
  /path/to/markdown.md
```

### 4.3 DOCX 结构审计

```bash
python3 ~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/scripts/audit_docx_structure.py \
  /path/to/output.docx
```

### 4.4 模板执行（确定性模式）

```bash
python3 ~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/scripts/apply_docx_template.py \
  --template /path/to/template.docx \
  --data '{...JSON...}' \
  --output /path/to/output.docx
```

### 4.5 视觉校验（需 LibreOffice + Poppler）

```bash
bash ~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/scripts/render_docx.sh \
  /path/to/output.docx /path/to/render_dir
```

### 4.6 完整门禁（推荐用于对外文件）

```bash
python3 ~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/scripts/format_gate.py \
  --docx /path/to/output.docx \
  --require-visual \
  --baseline-png /path/to/baseline_pages \
  --candidate-png /path/to/candidate_pages
```

## 五、退出码语义

| 退出码 | 含义 |
|---|---|
| 0 | 全部通过 |
| 1 | 有 error / 有 warning（`--fail-on-warning` 时） |
| 2 | 调用错误（参数缺失等） |

## 六、与 MEMORY.md 集成

在 MEMORY.md"文书输出"流程中：

```
第一步:去AI化
第二步:转 Word（md2word --preset=legal）
第三步:交付前门禁（wenge / format_gate.py）   ← 用 wenge 替换 md2word-gate
第四步:归档记录
```

**门禁命令**改为：
```bash
# 旧
python3 .../md2word-gate/scripts/md2word_gate.py <输出.docx>

# 新（更专业）
python3 .../wenge/scripts/format_gate.py --docx <输出.docx>
```

## 七、信拓集团本地化建议（v0.2.0 路线图）

| 优先级 | 行动 |
|---|---|
| **P0 立即** | 用 wenge 替换 md2word-gate 写入 MEMORY.md |
| P1 一周 | 安装 LibreOffice + Poppler（WSL2），启用视觉校验 |
| P1 一周 | 整理信拓集团"页眉/页脚/字体"标准配置，写入 references/ |
| P2 月内 | 把律师函/催告函/上诉状模板的页眉用 apply_docx_template 串联 |
| P3 季度 | 训练律师用 wenge 做判决书归档前 L3 校验 |

## 八、依赖

| 依赖 | 必装 | 用途 |
|---|---|---|
| `python-docx` | ✅ | 解析 OpenXML |
| `Pillow` | 可选 | 视觉校验（PNG 处理） |
| `LibreOffice` | 可选 | DOCX→PDF 转换 |
| `poppler-utils` (pdftoppm) | 可选 | PDF→PNG 转换 |

**安装核心依赖**：
```bash
pip install python-docx Pillow
```

**安装视觉校验依赖**（WSL2）：
```bash
sudo apt install libreoffice poppler-utils
```

## 九、相关引用

- **文格原版**：`github.com/lilialla/legal-document-format-skill`
- **文格文章**：`E:\律师事务部\各类工具\文格_法律文书模板执行Skill_lilialla_20260605.md`
- **本封装源代码**：`/tmp/legal-document-format-skill/`
- **本封装安装位置**：`~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/`
- **被替代的 md2word-gate**：`~/.openclaw/workspace/skills/legal-skills-github/skills/md2word-gate/`

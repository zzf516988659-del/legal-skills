---
name: contract-templates
version: 0.1.0
author: 江苏信拓建设（集团）股份有限公司 法务部
description: 信拓集团高频法律文书字段化模板。基于文格（lilialla/legal-document-format-skill）的"确定性模式"思路，提供律师函、催告函、固定格式报告三类高频模板，支持字段化批量生成。
license: MIT
---

# 信拓集团合同文书模板库（contract-templates）

> 设计思想：致敬文格（lilialla/legal-document-format-skill）"模板也是指令"。
> 使用场景：律师函、催告函、固定格式报告的高频批量生成。

## 一、定位

**contract-templates 是信拓集团法律文书的"字段化模板库"**——不替代 `legal-proposal-generator`（它生成非模板类法律服务方案），而是与它**互补**：

| 维度 | contract-templates | legal-proposal-generator |
|---|---|---|
| **场景** | 高频复用、字段化、固定格式 | 非模板类、定制化 |
| **生成方式** | 模板 + 表格数据 → 批量 | Markdown → 自由生成 |
| **适用文书** | 律师函、催告函、固定格式报告 | 诉讼方案、咨询报告、建议书 |
| **典型工作** | 表格驱动 20 份律师函 | 1 份建工分包合同审查报告 |
| **核心优势** | 稳定、快速、零 LLM 调用 | 灵活、深度推理 |

## 二、首批模板（v0.1.0）

| 模板 | 文件 | 字段数 | 适用场景 |
|---|---|---|---|
| **律师函** | `templates/律师函.md` | 11 | 主张权利、催告、警告、要求履行 |
| **催告函** | `templates/催告函.md` | 9 | 工程款催收、债务履行催告 |
| **固定格式报告** | `templates/审查报告.md` | 7 | 简单合同审查报告（无需 Call 3 触发时使用） |

## 三、字段命名规范

| 类型 | 命名 | 示例 |
|---|---|---|
| 案号 | `{{CASE_NO}}` | (2026)苏0623民初123号 |
| 当事人 | `{{CLAIMANT}}` / `{{RESPONDENT}}` | 江苏信拓建设集团 / 周世文 |
| 金额 | `{{AMOUNT}}` | 1,500,000.00 |
| 日期 | `{{YYYY-MM-DD}}` | 2026-06-05 |
| 期限 | `{{DEADLINE}}` | 2026-07-05 |
| 编号 | `{{LETTER_NO}}` | 信拓律函字[2026]第 123 号 |

## 四、批量生成

### 4.1 命令行单份

```bash
python3 scripts/render_template.py templates/律师函.md \
  --data '{"CASE_NO":"(2026)苏0623民初123号","CLAIMANT":"江苏信拓建设集团"}' \
  --output /tmp/律师函_张三.docx
```

### 4.2 表格驱动批量

```bash
# 1. 准备 data.json（每行一份数据）
# 2. 批量渲染
python3 scripts/render_template.py templates/律师函.md \
  --data-file data.json \
  --output-dir ./output/
```

### 4.3 走 md2word 流水线

```bash
# 模板渲染后走标准四步流程
python3 scripts/render_template.py templates/律师函.md --data ... --output /tmp/raw.md
# 去AI化（律师函一般无 AI 痕迹，可跳过）
# 转 Word
python3 .../md2word.py /tmp/raw.md --preset=legal /tmp/律师函.docx
# 交付前门禁
python3 .../wenge/scripts/format_gate.py --docx /tmp/律师函.docx
```

### 4.4 走 DOCX 模板流水线（推荐，用于正式对外文书）

> v0.2.0 新增（2026-06-06）。使用预格式化 DOCX 模板，通过 wenge apply_docx_template.py 填充字段，直接生成带标准页眉/页脚的正式文书，无需经过 md2word。

```bash
# 第一步：准备数据 JSON
cat > /tmp/letter_data.json << 'EOF'
{
  "LETTER_NO": "信拓律函字[2026]第001号",
  "ISSUE_DATE": "2026年6月6日",
  "ISSUER": "江苏信拓建设（集团）股份有限公司",
  "RECIPIENT": "周世文",
  "RECIPIENT_ADDR": "江苏省如东县掘港镇",
  "SUBJECT": "要求立即支付碧水戎城项目工程款",
  "FACT": "贵方承接本公司碧水戎城项目...",
  "DEMAND": "1. 立即支付工程款...",
  "DEADLINE": "2026年6月20日",
  "CONSEQUENCE": "本公司将依法向有管辖权的人民法院提起诉讼..."
}
EOF

# 第二步：用 DOCX 模板生成（页眉/页脚/字体已预置）
python3 ~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/scripts/apply_docx_template.py \
  ~/.openclaw/workspace/skills/legal-skills-github/skills/contract-templates/docx_templates/律师函_template.docx \
  /tmp/律师函_周世文.docx \
  --replacements-json /tmp/letter_data.json \
  --force

# 第三步：交付前门禁（wenge）
python3 ~/.openclaw/workspace/skills/legal-skills-github/skills/wenge/scripts/format_gate.py \
  --docx /tmp/律师函_周世文.docx
```

**DOCX 模板位置**：`docx_templates/律师函_template.docx`

**与 md2word 流水线的对比**：

| 维度 | md2word 流水线 | DOCX 模板流水线（推荐） |
|---|---|---|
| 页眉/页脚 | 依赖 md2word --header 参数 | ✅ 预置在 DOCX 模板中，稳定可靠 |
| 字体控制 | 依赖 --preset=legal | ✅ 完全由模板控制 |
| 弯引号字体 | 需 post-processing 修复 | ✅ 模板中已正确设置 |
| 生成速度 | 慢（需调 LLM） | 快（纯文本替换） |
| 适用场景 | 定制化内容 | 高频标准化文书 |

## 五、模板编写规范

1. **必填字段** 用 `{{XXX}}`，**可选字段** 用 `{{XXX?}}` 或 `{{XXX:default}}`
2. **正文中括号注解** 用 `【注：...】` 在最终输出前删除
3. **不允许包含**：
   - 半角中文标点（必须全角）
   - 半角引号（必须 `"…"`）
   - 列表项 `1. 2. 3.`（必须 ①②③）
4. **页眉设置**：在 YAML frontmatter 中声明：
   ```yaml
   ---
   header: 江苏信拓建设（集团）股份有限公司
   footer: 第 X 页 共 Y 页
   ---
   ```

## 六、路线图

| 版本 | 功能 |
|---|---|
| **v0.1.0**（当前） | 3 份高频模板（律师函/催告函/审查报告） |
| **v0.2.0**（当前，2026-06-06） | ✅ DOCX 模板流水线（apply_docx_template.py + wenge）；律师函 DOCX 母版已完成；催告函/上诉状 DOCX 母版待完成 |
| v0.3.0 | 与 `de-ai-polish` 联动：自动去AI化 |
| v0.4.0 | 与 `legal-proposal-generator` 联动：模板+定制化混合生成 |
| v0.5.0 | 表格驱动批量 + E 盘归档自动化 |

## 七、相关引用

- **文格文章**：`E:\律师事务部\各类工具\文格_法律文书模板执行Skill_lilialla_20260605.md`
- **文格学习笔记**：本笔记上方对话
- **md2word**：`skills/legal-skills-github/skills/md2word/`
- **wenge**：`skills/legal-skills-github/skills/wenge/`（2026-06-06 升级替代 md2word-gate）

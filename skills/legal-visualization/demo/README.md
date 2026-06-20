# Legal Visualization 演示样本

> **创建时间**: 2026-06-20
> **适配场景**: 小法师律所 / 江苏信拓建设(集团)股份有限公司 法律服务方案
> **drawio 版本要求**: drawio CLI ≥ 13.0(导出 PNG/SVG/PDF 三件套)

## 一、演示样本清单

| 序号 | 文件名 | 适配场景 | 来源模板 |
|---|---|---|---|
| 01 | 01-律师服务路线图.drawio | 常年法律顾问服务方案阶段路线图 | `templates/service/service-roadmap.drawio` |
| 02 | 02-争点-证据矩阵.drawio | 诉讼案件争点 × 证据 双向矩阵图 | `templates/litigation/issue-evidence-matrix.drawio` |
| 03 | 03-三线流向图.drawio | 法律关系 / 资金流向 / 责任划分 | `templates/litigation/three-line-flow.drawio` |

## 二、导出三件套

### 前置条件

| 工具 | 用途 | 安装 |
|---|---|---|
| drawio CLI | 把 .drawio 导出为 PNG / SVG / PDF | https://github.com/jgraph/drawio-desktop/releases |

### 导出命令

```bash
# 1. 单文件三件套导出(默认 svg + png)
python3 scripts/export_drawio.py demo/samples/01-律师服务路线图.drawio \
    --output-dir ./output/

# 2. 全套三件套(含 PDF)
python3 scripts/export_drawio.py demo/samples/ \
    --output-dir ./output/ \
    --format svg,png,pdf \
    --png-scale 3.0

# 3. 律师服务方案批量导出
python3 scripts/export_drawio.py --recursive templates/ \
    --output-dir ./output/all-templates/
```

### 三件套产物

每份 `.drawio` 源文件导出后产生:
- `*.svg` — 矢量图,适合 PPT / Word 嵌入
- `*.png` — 位图,适合飞书 / 邮件 / 微信
- `*.pdf` — PDF,适合正式交付归档
- `*.drawio` — 源文件(始终保留,可二次编辑)

## 三、自检(无需 drawio CLI)

```bash
# 校验 .drawio XML 结构
python3 scripts/validate_drawio.py demo/samples/

# 校验并输出 JSON 报告
python3 scripts/validate_drawio.py --json demo/samples/01-律师服务路线图.drawio
```

校验项(6 项):
- [mxgraph_model] mxGraphModel 存在
- [root_cells] id="0" 与 id="1" 保留节点齐备
- [parent_one] 所有顶层元素 parent="1"
- [edge_geometry] 所有 edge 含 mxGeometry relative="1"
- [node_size] 所有节点声明 width/height
- [xml_safe_comments] 未发现破坏 XML 的字符组合

## 四、适配我方场景的典型应用

### A. 律师服务方案(service-roadmap)
- 客户首次咨询 → 案件评估 → 服务方案 → 启动会 → 过程服务 → 结案汇报
- 适用:常年法律顾问合同 / 专项法律服务方案

### B. 争点-证据矩阵(issue-evidence-matrix)
- 列:案件争议焦点(原告主张 / 被告抗辩 / 我方主张)
- 行:证据材料(原告证据 / 被告证据 / 我方证据 / 第三方证据)
- 适用:庭审前质证准备 / 律师内部研究报告

### C. 三线流向图(three-line-flow)
- 三方关系图:原告 / 被告 / 第三方(资金 / 责任 / 货物 / 信息)
- 适用:法律关系图 / 资金流向图 / 责任划分图

## 五、命名规范

详见 `references/naming-conventions.md`,默认采用 `NN-<主题>.drawio` 格式:
- 序号 NN(01-99)
- 中文主题
- 统一 .drawio 扩展名

## 六、与本仓库其他技能联动

| 联动技能 | 用途 |
|---|---|
| `contract-copilot` | 合同审查后生成"合同结构图" |
| `litigation-analysis-external` | 9 阶段诉讼分析中嵌入"证据链图解" |
| `legal-proposal-generator` | 法律服务方案中嵌入"服务路线图" |
| `md2word --preset=legal` | 三件套图嵌入正式 Word 文书 |

## 七、当前状态

- ✅ 18 个上游模板全部 XML 校验通过
- ✅ 3 个适配小法师场景的演示样本创建完成
- ⚠️ drawio CLI 未安装(WSL2 环境),无法导出 PNG/SVG/PDF
- 📝 后续:在 Windows 主机安装 drawio CLI 后可批量导出三件套
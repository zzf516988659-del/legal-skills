# claim_basis_matrix.md - 请求权基础五层矩阵

> 版本：v0.1.0 | 更新：2026-06-06 | 来源：庭前一页纸作战卡（律途修远） + 信拓法务工作流

---

## 一、概念说明

**请求权基础矩阵（claim_basis_matrix）** 是将律师的诉讼请求转化为结构化法律评价框架的工具，使每一个诉讼请求都对应到具体的法条、要件和证据。

**核心价值**：
- 把"案件故事"转化为"法律评价结构"
- 适配法院请求权基础审理思路
- 让每个结论可复核、可追溯

---

## 二、五层结构规范

| 层级 | 字段名 | 说明 | 示例 |
|---|---|---|---|
| 第1层 | `claim` | 具体诉讼请求 | 支付货款 100 万元 |
| 第2层 | `legal_relationship` | 基础法律关系 | 买卖合同关系 |
| 第3层 | `claim_basis` | 请求权名称 | 买卖合同价款请求权 |
| 第4层 | `legal_basis_articles` | 依据法条（编号+名称） | 民法典第595条、第626条 |
| 第5层 | `elements` | 构成要件（逐项） | 合同成立、货物交付、价款到期、买受人未付款 |
| 第6层 | `evidence_refs` | 每要件对应的证据 | 买卖合同（证合同成立）、送货单（证交付）、对账微信（证到期）、付款流水（证未付） |

---

## 三、JSON 结构示例

```json
{
  "claim_basis_matrix": [
    {
      "claim": "支付货款人民币1,250,000元",
      "legal_relationship": "买卖合同关系",
      "claim_basis": "买卖合同价款请求权",
      "legal_basis_articles": [
        {"article": "民法典第595条", "name": "买卖合同定义"},
        {"article": "民法典第626条", "name": "买受人支付价款义务"}
      ],
      "elements": [
        {"element": "合同成立", "satisfied": true, "evidence": "《采购合同》P3-5"},
        {"element": "货物交付", "satisfied": true, "evidence": "送货单P12 + 验收确认书P15"},
        {"element": "价款到期", "satisfied": true, "evidence": "对账微信记录P18"},
        {"element": "买受人未付款", "satisfied": true, "evidence": "付款流水（无付款记录）P20"}
      ]
    },
    {
      "claim": "支付逾期付款利息（按LPR 1.5倍，自2026年5月16日起算）",
      "legal_relationship": "买卖合同关系",
      "claim_basis": "违约责任请求权",
      "legal_basis_articles": [
        {"article": "民法典第577条", "name": "违约责任"},
        {"article": "民法典第585条", "name": "违约金"}
      ],
      "elements": [
        {"element": "合同存在违约金/利息约定", "satisfied": "待核", "evidence": "《采购合同》第7条P8"},
        {"element": "买方违约事实", "satisfied": true, "evidence": "见上方货款请求权要素"},
        {"element": "利息计算方式明确", "satisfied": true, "evidence": "合同约定按LPR 1.5倍P8"}
      ]
    }
  ]
}
```

---

## 四、字段说明

### claim（诉讼请求）
- 必须具体到金额/行为，不能模糊表述
- 涉及多项请求时，每项单独列一个矩阵行

### legal_relationship（法律关系）
- 填写基础法律关系类型（买卖合同/建设工程合同/民间借贷/劳动争议等）
- 需与案由保持一致

### claim_basis（请求权名称）
- 使用法律专业术语
- 如"买卖合同价款请求权""建设工程价款优先受偿权""侵权损害赔偿请求权"

### legal_basis_articles（法条依据）
- 列出具体条文编号和内容摘要
- 必须通过 legal-article-retrieval 核实条文现行有效
- 必须通过 legal-norm-validity-check 校验无冲突

### elements（构成要件）
- 每个要件标注 `satisfied` 状态：`true`（满足）/ `false`（不满足）/ `待核`（证据不足）
- 每要件必须关联到具体证据（含页码）

### evidence_refs（证据映射）
- 格式：`证据名称 + 页码`
- 必须是原始材料中的具体页码
- 支持多条证据共同证明同一要件

---

## 五、输出格式（Markdown 表格版）

### 请求权基础矩阵表

| # | 诉讼请求 | 法律关系 | 请求权基础 | 法条依据 | 构成要件 | 证据映射 | 状态 |
|---|---|---|---|---|---|---|---|
| 1 | 支付货款100万元 | 买卖合同关系 | 买卖合同价款请求权 | 民法典第595条、第626条 | 合同成立✓ 货物交付✓ 价款到期✓ 未付款✓ | 采购合同P3-5 送货单P12 对账微信P18 付款流水P20 | ✅ |
| 2 | 逾期利息 | 买卖合同关系 | 违约责任请求权 | 民法典第577条、第585条 | 约定✓ 违约✓ 计算方式明确✓ | 合同P8 | ✅ |

---

## 六、在 litigation-analysis 中的嵌入位置

```
Stage 3: 法律关系定性
    ↓
Stage 3.5: 法条解释 S04 legal-interpretation-argument
    ↓
Stage 4: 双检索闭环（yuandian-law-search + minimax-coding-plan-tool）
    ↓
【NEW】Stage 4.3: claim_basis_matrix 构建
    → 对每个诉讼请求，按五层结构逐项填写
    → 调用 legal-article-retrieval 核实法条
    → 调用 legal-norm-validity-check 校验有效性
    → 调用 S09 legal-element-extraction 提取构成要件
    → 页码回溯：每条结论标注来源材料页码
    ↓
Stage 4.5: 类案分析 S07 analogical-reasoning
    ↓
Stage 5.5: 攻防强度评估 S03 argument-strength-evaluation
    ↓
Stage 6: 推理链校验 S01 deductive-reasoning
    ↓
Stage 6.5: 后果量化 S10 formal-legal-consequence
    ↓
Stage 7: 答辩状生成
    ↓
Stage 7.5: 庭前一页纸作战卡压缩
```

---

## 七、页码回溯规范（2026-06-06 新增）

> 每条结论必须回溯到原始材料页码，这是 Stage 7.5 的强制要求。

| 内容类型 | 回溯格式 | 示例 |
|---|---|---|
| 事实主张 | [材料名]P[页码] | 送货单P12、验收确认书P15 |
| 法条引用 | [法条编号]（来源：yuandian-law-search 核实） | 民法典第595条 |
| 证据认定 | [证据名]P[页码] | 对账微信记录P18 |
| 争点判断 | 来源：Stage 0 输出 | 争点#1 来自 S05 争点识别 |
| 风险评估 | 来源：Stage 5.5 | 风险#2 来自 S03 攻防评估 |

---

## 八、与原有"争点-证据映射表"的区别

| 维度 | 原争点-证据映射 | claim_basis_matrix |
|---|---|---|
| 维度 | 争点 → 证据 | 请求 → 要件 → 证据 |
| 层级 | 二层 | 六层 |
| 法条关联 | 间接 | 直接（法条→要件→证据） |
| 法院适配性 | 一般 | 高（请求权基础审理思路） |
| 可执行性 | 中 | 高（一页纸作战卡核心） |
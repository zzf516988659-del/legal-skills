---
name: litigation-analysis-external
version: "1.0.0"
author: 法师小助理
license: CC BY-NC-ND 4.0
description: litigation-analysis 8 阶段增强版——外挂 7 技能（THUYRan/Legal-Skills-Chinese）
---

# litigation-analysis-external

**版本**: 1.0.0  
**最后更新**: 2026-06-03  
**说明**: 7 技能外挂 SKILL——把 THUYRan/Legal-Skills-Chinese 的 7 P0 技能外挂到 `litigation-analysis` 工作流

## 7 技能装载清单

| 编号 | 技能 | 装载位置 | 来源路径（E 盘） |
|---|---|---|---|
| S05 | dispute-issue-identification | Stage 0 | `E:\律师事务部\法律技能测试\Legal-Skills-Chinese\skills\dispute-issue-identification\` |
| S06 | evidence-argument-chain | Stage 2.5 | `E:\律师事务部\法律技能测试\Legal-Skills-Chinese\skills\evidence-argument-chain\` |
| S04 | legal-interpretation-argument | Stage 3.5 | `E:\律师事务部\法律技能测试\Legal-Skills-Chinese\skills\legal-interpretation-argument\` |
| S02 | counterfactual-reasoning | Stage 3.7 | `E:\律师事务部\法律技能测试\Legal-Skills-Chinese\skills\counterfactual-reasoning\` |
| S07 | analogical-reasoning | Stage 4.5 | `E:\律师事务部\法律技能测试\Legal-Skills-Chinese\skills\analogical-reasoning\` |
| S03 | argument-strength-evaluation | Stage 5.5 | `E:\律师事务部\法律技能测试\Legal-Skills-Chinese\skills\argument-strength-evaluation\` |
| S01 | deductive-reasoning | Stage 6 | `E:\律师事务部\法律技能测试\Legal-Skills-Chinese\skills\deductive-reasoning\` |

## 调用顺序

```
Stage 0：S05 争点识别（树状分层）
   ↓
Stage 2.5：S06 证据链（P-F-C 链）
   ↓
Stage 3.5：S04 法条解释（四层解释）
   ↓
Stage 3.7：S02 反事实推演（5+ 项）
   ↓
Stage 4.5：S07 类案分析（yuandian-law-search 真实检索）
   ↓
Stage 5.5：S03 攻防强度评估
   ↓
Stage 6：S01 推理链校验（谬误检测）
```

## 使用规范

| 场景 | 建议跑技能 |
|---|---|
| 重大争点（决定胜败）| 跑全套 7 技能 |
| 次级争点 | 跑 S05 + S06 + S07 |
| 背景争点 | 跑 S05 即可 |

## 输出翻译规范

**学术标记 → 法言法语**：
- `[CF-HIGH]` → 删去
- `[CF-LOW]` → 删去
- `[P-F-C]` → 删去
- 其他 `[XXX-XXX]` 形式 → 改为正文叙述

## CC BY-NC-ND 4.0 许可合规

- 仅限内部使用
- 不得对外分发/转赠/商业化
- 7 技能输出必须律师复核

## 试运行验证

- 永天涂料案（建工）：✅ 通过
- 沈美娟案（侵权）：✅ 通过（复盘 100%）
- 周春明案（劳动）：✅ 通过

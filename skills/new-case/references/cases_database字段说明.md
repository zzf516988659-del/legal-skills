# cases_database.json 字段说明

## 数据文件位置

`/home/administrator/.openclaw/workspace/cases_system/cases_database.json`

## 顶层结构

```json
{
  "lastUpdated": "2026-05-18",
  "totalCases": 59,
  "totalAmount": 102804304.31,
  "cases": [ ... ]
}
```

## cases[] 每个案件字段

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `internalId` | string | 内部案号 | `"2026-006"` |
| `caseNumber` | string | 官方案号 | `"（2026）苏0685民初1240号"` |
| `caseName` | string | 案件名称 | `"沈美娟 vs 海安尚鸿酒店侵权纠纷"` |
| `caseType` | string | 案件类型 | `"民事"` |
| `causeOfAction` | string | 案由 | `"侵权纠纷"` |
| `court` | string | 立案法院 | `"海安市人民法院开发区法庭"` |
| `plaintiff` | string | 原告 | `"沈美娟"` |
| `defendant` | string | 被告 | `"海安尚鸿酒店管理有限公司"` |
| `amount` | number | 诉讼金额（元） | `120000` |
| `status` | string | 当前状态 | `"待答辩"` |
| `procedure` | string | 程序阶段 | `"一审"` |
| `filingDate` | string | 立案日期 | `"2026-05-08"` |
| `hearingDate` | string/null | 开庭日期 | `"2026-05-13"` 或 null |
| `分公司` | string | 所属分公司 | `"尚鸿酒店"` |
| `我方代理律师` | string | 代理律师 | `"朱宗锋（特别授权）"` |
| `对方代理律师` | string | 对方律师 | `"徐阳（江苏联盛律师事务所）"` |
| `lastUpdated` | string | 最后更新时间 | `"2026-05-18"` |
| `notes` | string | 备注 | `"开庭已结束，择期宣判"` |

## status 有效值

`待建档` / `待答辩` / `已答辩` / `待开庭` / `已开庭` / `待判决` / `已判决` / `上诉中` / `执行中` / `已归档`

## procedure 有效值

`一审` / `二审` / `再审` / `执行` / `破产`

## 更新规则

- 新案登记：追加至 `cases[]`，`totalCases` +1，`lastUpdated` 更新为当天
- 状态推进：找到对应 internalId，修改 status + procedure + 期限相关字段 + lastUpdated
- 删除案件：物理删除（不常用），totalCases -1
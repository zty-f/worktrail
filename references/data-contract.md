# 数据合同

## 工作区

workflow.json记录来源与所选产出，默认summary。配置、范围变化与输出行为见[来源与产出选择](workflow.md)。brief.json记录person.name/role、report_type（halfyear/annual/probation）、period.start/end/label、minutes、projects和rubric。projects.rubric引用考核维度ID。可设置title覆盖标题。disclosure说明模拟性质或材料范围。minutes是叙事规划输入，当前导出器不自动证明讲述时长；逐页提示不等于精确计时配音。

state/ledger.sqlite3包括sources、versions、facts、decisions和events。packet导出的evidence-packet.json是Agent阅读的原文资料包。source_id按provider+locator稳定，版本为正文单元SHA256。旧版本不覆盖。

## facts.json

顶层为schema_version和facts数组。单条示例：

```json
{
  "id": "F01", "project_id": "P1", "kind": "action", "subject": "self",
  "event_date": "2026-03-20", "status": "done",
  "statement": "我完成业务验收并整理上线问题清单",
  "role_level": "contributor", "dedupe_key": "P1-business-acceptance-20260320",
  "evidence": [{"source_id":"从packet复制实际ID","version":"完整版本哈希","unit":"L3","quote":"该位置含本人姓名的逐字原文"}],
  "review": {"status":"checked","reviewer":"实际核对者","note":"核对主体、范围和状态"}
}
```

- kind：action工作动作、outcome整体结果、role角色、metric指标、plan计划。
- subject：self本人、team团队、other他人。整体指标通常归team。
- status：done、in_progress、planned。
- event_date：事件日期，不用文件更新时间代替；不明先补问。
- 日期未知可显式填null，同时提供date_status=unknown与date_note。brief.report_type=evidence为所选资料核查，不按报告期归档；正式halfyear/annual/probation会排除未知日期记录并提出补证问题。证据核查不能冒充已完成的正式周期汇报。
- attribution_basis=self_report表示独立保存的本人补充，不能包装成平台文档独立证明。completion_basis=document_checkbox表示原文done/勾选记录；design_only只证明方案内容，完成待核实。
- role_level：contributor或lead。lead需明确属于本人的整体负责人引文。
- dedupe_key：同一交付的稳定键，不能把整个项目所有事实设为同一个键。
- review：实际看过原文的语义复核，不是解析脚本自动盖章。

指标另加：

```json
{"metric":{"key":"平均处理时长","stage":"result","value":25,"unit":"分钟","population":"全量已结售后工单","comparison_id":"H1-ticket","window":"2026-04-01至2026-06-30","direction":"lower"}}
```

同一比较定义允许基线和观察窗口不同，但群体、统计量、单位、业务含义需可比。不同comparison_id不混算。stage只允许baseline/result；目标保留为plan或背景。direction为lower/higher。不自动换算单位，不把中位数当平均数；Agent先核对归一化依据。

import-facts为增量upsert，不删除本次未提交的旧事实。改已有事实保留事件历史；停用用exclude_fact决议。

## 核查说明与精简演示

brief.review_notes为Agent核对后的说明，review_note_fact_ids附对应事实定位；review_questions列补证问题。它们不是自动发现或自动证明的语义结论。

可选brief.presentation_outline精简演示内容。每页需要title、fact_ids和body（文字）或kind=table、values、widths（表格）。fact_ids必须来自当前有效事实；脚本附加统一来源位置及备注。提纲文字仍由Agent核对语义，不能用有效编号给无关陈述背书。省略则采用自动提纲。

```json
{"presentation_outline":[{"title":"已确认的参与范围","body":["本人参与后端开发，分工来自本人补充，完成月份待核实。"],"fact_ids":["实际事实编号"]}]}
```

## 原文定位

MD/TXT为L行；CSV为R数据行（从2起）；DOCX为P段落或T表R行；PDF为PAGE实际页；XLSX为工作表!R行；PPTX为SLIDE实际页。不声称保留全部图片、样式或公式。XLSX读取保存的公式缓存，缺缓存先由表格工具重算或提供计算值。

平台Markdown的L是本次CLI正文行号，不是云文档原生段落ID。附件签名查询参数在入库前去除，保留路径和行号，避免临时凭据落盘与无改动文档产生假版本。图片和链接指向的其他材料未被读取。DOCX摘录可去除排版标记，精确引文和完整快照在证据页及账本中保留。

## 手工平台资料包

官方平台技能可把听记、表格和日志读成统一格式，再ingest-packet：

```json
{"sources":[{"provider":"dingtalk","locator":"原始文档或听记链接","title":"项目复盘听记","units":[{"unit":"TRANSCRIPT-00:12:30","text":"该位置实际转写"}]}]}
```

只放实际读取的正文。摘要和二手转述需标注，不冒充逐字原文。资料包由Agent按回包核对，不代表额外自动适配已经实现。

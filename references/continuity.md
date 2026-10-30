# 长期账本和修正

## 增量

同一工作区反复ingest-local/platform-sync，正文未变不新建版本。变化保留旧版本，旧引用在analyze中失效并阻止build。重新看原文、更新事实version/quote后import-facts。只改哈希不看变化内容不算复核。

本地选定目录中消失或读取失败的来源停用；平台选定文档读取失败也停用旧缓存。历史仍在库中。移除sources.json某项不会抹掉已积累资料；要撤出范围，使用source-disable并排除/修正相关事实。不同来源选择建议建不同工作区，明确混合时再合并。

## 平时记录

```bash
python3 scripts/review.py note /absolute/workspace --project P1 --date 2026-07-10 --text '我完成第二轮业务验收，遗留问题已交负责人跟进。'
```

note写入记录人、日期及本人补充标识，不自动变成已核实业务结果。让Agent读新增packet、抽事实并保留自述说明。

## 指标确认

analyze得到实际conflict_id，从候选选择selected_fact_id。decision文件需要id、type=metric_resolution、conflict_id、selected_fact_id、reason、reviewer和evidence。evidence与事实结构相同，引用当前有效来源。示例见examples/halfyear-demo/decisions。

```bash
python3 scripts/review.py decision /absolute/workspace /absolute/decision.json
python3 scripts/review.py analyze /absolute/workspace
```

冲突ID包含成员和事实版本；数据变后旧决议不自动生效。不能把模拟确认用于真实数据。

## 修正或停用事实

fact_patch需要fact_id、expected_hash、patch。expected_hash为原始事实规范JSON的SHA256，可用prs_core.digest计算。patch只允许statement、subject、role_level、status、event_date、evidence、review。改指标值应依据真实来源重新import-facts，不能补丁硬改。

```json
{"id":"D02","type":"fact_patch","fact_id":"F02","expected_hash":"实际事实哈希","reason":"本人确认职责表述","reviewer":"实际确认人","patch":{"statement":"我完成需求说明与异常流程清单"}}
```

停用用type=exclude_fact，也需fact_id、expected_hash、reason和reviewer。已有决议ID不能覆盖，新增ID保留审计。补丁后重新验证证据。

## 跨周期

修改brief的report_type和period复用数据库，按事件日期筛选历史事实。导入下半年资料后可生成年度报告，原修正继续保留。源或事实变化时先核对旧决议。

history显示最近100条事件，完整记录在SQLite。原文快照属于工作资料，按公司策略存储备份。撤权后不用于新报告；历史快照保留/清除按公司资料要求处理。

本版提供可被调度器调用的增量命令。默认不注册后台任务。用户明确要求后另配自动化，OAuth失效时停止同步并报告缺口。

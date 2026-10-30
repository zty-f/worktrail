# 平台资料接入与类型边界

核对日期2026-10-30。安装与授权见[飞书](setup-feishu.md)、[钉钉](setup-dingtalk.md)、[企业微信](setup-wecom.md)，失败处理见[共同排障](setup-troubleshooting.md)。本文件只说明正文适配、选择范围和采集后的验收，不重复安装步骤。

## 共同流程

1. 用户选本地、某个平台或混合资料，以及summary等所需产出，configure保存到workflow.json。本地不安装平台CLI。
2. 平台仅在选中时检查安装/应用配置/本人登录。auth-check只返回脱敏认证判断；unknown不当成未登录，也不当成成功。
3. 有明确文档链接就直接选择；只有个人空间、文件夹名或关键词时，Agent用官方CLI只读取得有限候选，展示可读标题/路径供选择。不会默认扫描整个企业。
4. 把真正选定的文档写进sources.json，再collect或platform-sync。每批每平台最多30篇，不接受空文档范围冒充完成。
5. 查看state/last-platform-sync.json的mode、read、failed、complete_for_selection，并核对正文覆盖。搜索结果、目录、缩略图和页面树不是正文。
6. 由Agent实际读取evidence-packet.json，按合同抽取事实、分析，再仅生成所选格式。来源访问能力不代表成果归属。

source.mode为单平台时，collect拒绝其他平台配置；mixed允许明确列出的本地目录和平台文档。切换范围后未选旧来源停用，历史保留，manual/journal本人补充仍独立保留。旧事实若引用已停用来源必须重新核对。

## 当前自动适配

| 平台 | CLI | 搜索 | 正文 |
|---|---|---|---|
| 飞书/Lark | lark-cli | drive +search | docs +fetch，Docx/Wiki文字，显式--as user |
| 钉钉 | dws | drive search | doc read，alidocs.dingtalk.com/i/nodes/在线文字文档 |
| 企业微信 | wecom-cli | doc search | doc contents get，以及smartpage页面树后逐页读取正文 |

链接域名/路径按白名单校验。飞书适配当前支持.feishu.cn/.larksuite.com/.larkoffice.com的/docx/或/wiki/；其他文档域名不是因为官方CLI可能支持就自动放开。钉钉表格、PDF、听记、日志、旧URL等需先按官方产品Skill读取成资料包或本地导出。企微表格、PPT、PDF、微盘文件等不作为当前doc/smartpage自动读取能力。

内嵌图片、表格数据、附件、链接内PRD和接口页面并未自动读取。需要时单独选定这些来源，使用对应官方只读能力转为带定位的ingest-packet，或由用户获准导出后本地导入。不能用搜索高亮填充正文。

## 配置例子

下面仅表示结构，链接必须替换为实际选定值，不能调用占位链接：

```json
{"providers":[{"provider":"dingtalk","documents":[{"title":"选定文档标题","url":"https://alidocs.dingtalk.com/i/nodes/实际节点"}]}]}
```

```bash
python scripts/review.py configure /absolute/workspace --source dingtalk --sources-config /absolute/workspace/sources.json --outputs summary
python scripts/review.py collect /absolute/workspace
```

也保留discover/platform-sync/ingest-local高级入口。discover只有关键词检索和分页上限，不内置三家任意文件夹树递归，也不支持断点续搜；has_more=true必须说明候选未列完。增大max-pages会从第一页重读。

## 回包与文件路径

飞书ok/data、钉钉success/body或success/data、企微errcode等需区分HTTP成功与业务成功。未知回包形状、未知搜索结构、缺正文或有截断标志时按失败处理。失败来源停用旧缓存，不把上次内容冒充本次读取。

企微大正文可能返回file_path。只有对应provider显式设置cli_output_dir为本次可信CLI输出目录时，才允许读取该目录内实际正文；不能按不可信回包任意读取本机文件。smartpage逐页读不能只拿页面树就标完成。

平台Markdown中图片等资源的临时签名查询参数入库前去除，保留资源路径与行号，不下载图片；避免临时凭据落盘和未修改正文产生假版本。证据页L为采集时CLI Markdown行号，不是平台原生段落ID。

## 已验证范围

2026-10-30：钉钉dws v1.0.52已真实验证设备授权、个人空间/TechDoc目录分页、选定三篇adoc正文，以及未修改文档复读不新增版本。真实内容及本人补充位于单独私有工作区，未放入可分发Skill。

飞书和企微按官方main文档与源码核对安装、授权、状态及读取接口，并做回包/身份/范围/失败测试；未完成真实租户端到端验证。不同组织、特殊文档、大规模分页和跨平台运行不能由钉钉这次实测代替。

## 数据流向

凭据留在官方CLI，不写sources.json、Skill、报告或共享压缩包。原文与证据快照保存在用户工作区；Agent读取时内容进入当前Agent配置的模型，所以本地账本不等于推理全部离线。

本项目仅使用白名单读命令，默认不发消息、不改协作者、不回写文档、不启用全量聊天存档。CLI诊断保留保守错误类别与提示，不把可能含凭据的原始stderr写入项目输出。

# 安装与首次使用

本Skill供能读取文件、执行Python脚本的AI Agent使用。单独下载文件夹不会启动一个后台应用，也不会自行调用模型。默认只生成工作内容与成效总结；PDF和PPT是用户另选的产出。

## 1 解压和交给Agent

解压桌面压缩包，保持worktrail目录完整，不要只复制SKILL.md。可以把整目录放进目标Agent支持的skills目录，也可以直接要求Agent读取此目录的SKILL.md；无需为了试用改全局配置。

首次可以这样说：

> 读取这个目录的SKILL.md。先让我选择本地文件夹、飞书、钉钉、企业微信或混合资料，再确认需要的产出。我现在只要工作内容和成效总结，不要PPT。

用户已说明来源和产出时，直接沿用，不重复询问。只说“帮我整理工作”时默认summary；不自动调用三家平台，不生成全套格式。

## 2 按实际需要准备环境

| 要做的事 | 需要什么 |
|---|---|
| 查看内置示例 | 浏览器；Word/PPT用对应办公软件打开 |
| MD/TXT/CSV本地采集；总结、汇报底稿、证据页、自评、讲述提示 | Python >=3.10，所选这些产出不需要Node或第三方Python包 |
| 读取DOCX、文本PDF、XLSX | 分别需要python-docx、pypdf、openpyxl；PPTX文字解析使用标准库 |
| 读取平台资料 | 对应平台CLI及用户自己的授权；三家指南分别列前置条件 |
| 生成并验收Word/PDF | python-docx及可用的文档渲染运行时/LibreOffice |
| 生成可编辑PPT | Node、@oai/artifact-tool及配套演示校验运行时 |

当前完整排版使用Codex提供的文档/演示运行时，本压缩包不包含这些运行时，也不宣称可以从公共npm安装同名私有组件。没有该运行时的其他Agent仍可走轻量总结/证据流程；选择PPT/PDF时先doctor检查，缺依赖不能交付一个冒充成品的空文件。此版本没有把完整导出引擎改成所有机器均可公开安装的实现。

## 3 Python与解析依赖

在项目目录运行。macOS/Linux：

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/review.py doctor --outputs summary
```

Windows PowerShell：

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/review.py doctor --outputs summary
```

后续示例中的python代表同一个可用解释器；替换为你的.venv/bin/python或.venv\Scripts\python.exe。只读MD/TXT/CSV并做轻量产出时，可省略venv和pip安装，直接用满足版本的Python。完整模拟案例包含DOCX，因此重新生成整份模拟资料需安装requirements。

使用当前Codex环境时，Agent优先通过load_workspace_dependencies定位已有Python和Node，不再向全局环境重复安装依赖。所有运行路径动态发现，不绑定本开发者的用户名。

## 4 用所选产出做环境检查

```bash
python scripts/review.py doctor --outputs summary
python scripts/review.py doctor --outputs summary,evidence
python scripts/review.py doctor --outputs docx,pdf,pptx
```

看environment_checks_passed与missing_for_selection。summary不应因没有PPT引擎而失败。此检查不代表原文读取、登录、事实语义或实际渲染已通过；额外资料格式仍需对应解析包。

可通过PRS_NODE、PRS_NODE_MODULES、PRS_PRESENTATIONS_SKILL、PRS_DOCX_RENDERER指定目标电脑已经存在的运行时路径；不会替用户下载或复制Codex内部运行时。文档字体随包提供并含OFL许可。PPT默认PingFang SC，当前已在Mac验证；其他系统需选择可用中文字体并实际渲染验收，不能承诺跨平台相同效果。

## 5 新建工作区并选来源

工作区应在资料目录外；不同人的资料分工作区保存。

```bash
python scripts/review.py init /absolute/my-review
python scripts/review.py configure /absolute/my-review --interactive
```

向导询问资料来源、本地文件夹/平台配置和需要的产出。支持：本地、飞书、钉钉、企微、混合。工作区workflow.json保存选择；brief.json填写本人姓名、分工/岗位、报告周期、项目和考核标准。不会修改Skill内的模拟案例。

本地资料示例：

```bash
python scripts/review.py configure /absolute/my-review --source local --local-folder /absolute/my-materials --outputs summary
python scripts/review.py collect /absolute/my-review
```

多个本地资料目录重复传--local-folder。路径有空格时加引号。不能把工作区放进要采集的资料目录，以免再次读入输出或数据库。

平台资料：只安装和授权选中的一家，先看[飞书](setup-feishu.md)、[钉钉](setup-dingtalk.md)或[企微](setup-wecom.md)。选择文件夹、标题、链接或项目关键词后，Agent先展示有限候选，用户选正文，再写sources.json。目录发现由官方CLI完成，collect不自动递归整个企业空间。

```bash
python scripts/review.py configure /absolute/my-review --source dingtalk --sources-config /absolute/my-review/sources.json --outputs summary,evidence
python scripts/review.py collect /absolute/my-review
```

混合资料：

```bash
python scripts/review.py configure /absolute/my-review --source mixed --local-folder /absolute/my-materials --sources-config /absolute/my-review/sources.json --outputs summary
```

sources.json格式参考assets/sources.example.json；只保留选定平台和真实文档，示例占位链接不能调用。collect会拒绝与所选平台不一致的配置。切换采集范围后，未选旧来源会停用并保留历史；引用旧来源的事实需Agent重新核对，不能混入新报告。本人手工补充/journal保留为补充来源。

## 6 选择要生成什么

| 输出键 | 生成的用户文件 |
|---|---|
| summary（默认） | 工作总结.md，梳理工作内容、个人/团队产出、成效与缺口 |
| report | 汇报底稿.md，按半年/年度/转正框架组织 |
| evidence | 交互证据页、来源快照、CSV及分析数据 |
| docx | Word报告；PDF只在内部用于渲染验收，不作为所选交付 |
| pdf | PDF报告；中间Word留在私有构建目录 |
| pptx | 可编辑PPT，不额外交付Word/PDF |
| self-eval | 绩效自评草稿，不自动给分 |
| speaker-notes | 逐页讲述提示，不意味着已经导出PPT |
| all | 明确选择全部 |

可多选逗号分隔。需要摘要和PPT，不需要PDF：--outputs summary,pptx。需要直接在聊天中总结时，Agent可以先给核对后的文字；落盘只生成summary，不强制执行排版导出。

## 7 先理解资料 再按选择生成

采集完成不会自动抽事实。Agent必须实际阅读state/evidence-packet.json，按数据合同制作facts.json，再运行：

```bash
python scripts/review.py import-facts /absolute/my-review /absolute/my-review/facts.json
python scripts/review.py analyze /absolute/my-review
python scripts/review.py build /absolute/my-review
python scripts/review.py verify /absolute/my-review
```

build采用workflow.json中的产出选择，也可单次覆盖：

```bash
python scripts/review.py build /absolute/my-review --outputs summary
python scripts/review.py build /absolute/my-review --outputs evidence
python scripts/review.py build /absolute/my-review --outputs pdf
```

每次成功构建将output切换为这次所选产出；旧成功版本保存在builds。未选择的Word/PPT不会遗留在新output中冒充本次生成。manifest.json是核验记录，不是额外报告。失败时保留上一份output，不把缺依赖当作已完成。

日期不明按数据合同保留unknown，使用evidence报告模式作专项核查；正式周期不强行计入。没有业务成效数据时可以整理已有工作产出，但不编造增长、人效、贡献比例或绩效等级。

## 8 验收和交付

只验收所选格式。summary/evidence不要求PPT存在；证据页仅显示实际选定的下载项。Word/PDF和PPT仍需逐页视觉检查，可编辑对象和Office实机兼容性分别说明。真实平台资料不随公开Skill打包，账号凭据留在官方CLI。

## 9 模拟案例与检查

```bash
python scripts/review.py build examples/halfyear-demo --outputs all
python scripts/review.py verify examples/halfyear-demo
python -m unittest discover -s tests -q
```

内置完整模拟示例保持全部格式。另有examples/summary-only展示仅工作总结的实际轻量输出。平台登录诊断与范围路由采用隔离测试，不能替代飞书/企微真实租户验收；钉钉已验证的范围见对应指南。

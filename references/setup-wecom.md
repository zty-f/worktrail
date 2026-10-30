# 企业微信 CLI 安装与授权

核对日期：2026-10-30。依据企业微信官方WecomTeam套件。当前项目已核对官方安装、状态与读取命令，并用结构化回包测试；尚未在真实企微账号完成端到端读取。初次使用先用一篇用户允许的文档验收。

## 1 安装和版本检查

官方前置条件为Node.js >=18、企业微信账号；官方列出的CLI平台为macOS x64/arm64、Linux x64/arm64、Windows x64。项目自己的Windows/Linux导出仍须单独检查，不能把CLI支持平台等同于整套PDF/PPT渲染已验证。

```bash
node --version
npm --version
wecom-cli --version
```

没有CLI或低于当前官方Skill要求的1.2.1时：

```bash
npm install -g @wecom/cli
wecom-cli --version
```

企业已有固定版本时先与企业管理员核对，避免擅自替换。安装完成但Agent仍找不到命令时，重开终端/Agent，检查npm全局bin路径；见[共同排障](setup-troubleshooting.md)。

可选安装官方业务套件：

```bash
npx skills add WecomTeam/wecom-unified -y -g
```

它会检测Agent目录并安装Skill，先核对目标位置；不会因为你安装了本绩效Skill就自动具备所有账号权限。首次安装官方业务套件的任务并不授权发送消息、创建机器人通知或上传资料。本项目默认只读所选文档。

## 2 先查认证，不反复扫码

```bash
wecom-cli auth show --status
```

- 明确输出authorized：凭证已配置，可以继续确认身份和文档权限。
- 明确输出unauthorized：进入下一步初始化。
- 命令报错或其他输出：状态未知，按排障处理；不能仅凭退出码0或含有authorized字样推定成功。

本项目提供受控摘要，不显示原始认证内容：

```bash
python scripts/review.py auth-check --provider wecom
```

此处authenticated=true只表示官方CLI报告已配置授权，不代表目标文档可读。

## 3 扫码初始化

仅在未授权且用户选择企微资料时执行：

```bash
wecom-cli auth init --noninteractive
```

命令会输出本次授权链接/二维码，并等待用户完成验证。Agent需要在进程等待期间及时将当前链接或二维码展示给用户，保留进程；用户使用本人企业微信扫码并确认正确企业和身份。不要在输出真正传给用户前等待整个命令结束。

用户回复成功后检查原进程是否成功退出，再执行：

```bash
wecom-cli auth show --status
python scripts/review.py auth-check --provider wecom
```

只有明确authorized才进入业务读取。链接/二维码失效后，不复用截图或旧链接；先结束旧流程，再发起一次新的auth init。不要同时启动多个初始化进程，也不通过手工编辑配置文件塞入他人的cookie或token。

若向导提示需要管理员启用对应能力，或账号/企业不在可用范围，用户在官方页面完成申请，由管理员处理。Skill不能代批、伪造企业身份或承诺所有企业都能立即开通。

## 4 确认本人和资料类型

需要按本人筛选时，使用当前官方命令取得实际身份：

```bash
wecom-cli identity whoami
wecom-cli doc search --help
wecom-cli doc contents get --help
wecom-cli smartpage pages get --help
```

Agent只给用户展示可读姓名、企业、文件标题和链接，内部ID用于调用传递，不凭姓名猜userid。sources.json只写所选文档定位，不写凭证。

支持用户直接给文档链接、精确标题或项目关键词。微盘空间/文件夹的发现由Agent按官方disk域能力取有限候选；本项目platform-sync不内置任意微盘递归和二进制文件下载。找不到文件夹时先说明当前范围，不能自动改为全企业搜索。

当前自动正文适配：

| 类型 | 处理 |
|---|---|
| doc.weixin.qq.com/doc/... | doc contents get，读取Markdown文字 |
| doc.weixin.qq.com/smartpage/...或page.weixin.qq.com/smartpage/... | 先取页面树，再按实际page_id取各页面正文 |
| 在线表格、智能表格、微盘二进制 | 官方对应技能转为带位置的资料包，或用户获准导出后本地采集 |
| PPT、journal汇报、collect、mind、flow等搜索命中 | 搜索命中不算正文读取；按官方能力边界告知用户在客户端查看/导出，不能假装已解析 |

标题摘要、页面树、长正文文件路径、表格元信息都不能替代实际正文。长正文落到CLI输出文件时，只能在用户指定可信cli_output_dir内读取，不能接受回包任意本地路径。

## 5 选择并读取一篇资料

```bash
python scripts/review.py discover /absolute/workspace --provider wecom --query '项目关键词' --max-pages 3
```

若是“与我有关”的范围，应让Agent按真实whoami结果提供--identity；不能编造标识或用空查询扫描全库。先展示候选标题和可读链接，由用户选择后写sources.json。单平台单批最多30篇。

```bash
python scripts/review.py configure /absolute/workspace --source wecom --sources-config /absolute/workspace/sources.json --outputs summary
python scripts/review.py collect /absolute/workspace
```

检查last-platform-sync.json的read/failed/complete_for_selection和evidence-packet正文覆盖。authenticated不等于业务权限，必须以实际所选正文读取成功为判据。失败来源列为缺口，不取其他无关文件替代。

## 6 常见失败

| 现象 | 处理顺序 |
|---|---|
| npm安装后找不到wecom-cli | 核对npm当前安装目录、PATH与执行Agent的账号；重新打开终端，再查版本 |
| 输出unauthorized | 初始化一次，用户扫码；原进程结束后再查status |
| 扫码成功但status仍unauthorized | 检查二维码是否属于当前进程，是否选了不同企业/账号，进程是否已经超时；再开一次新流程 |
| 状态不是authorized/unauthorized | 当作未知；看当前版本help，不把近似文字或空输出算成功 |
| authorized但文档报no authority/permission denied | 用同一企微身份在客户端打开；确认文档分享权限、企业或应用可用范围，由拥有者/管理员在平台内处理 |
| 搜索不到、但客户端能看见 | 确认账号、企业、标题和搜索过滤条件；用精确已选链接验证，不断言文件不存在 |
| 搜索到不支持的类型 | 说明只完成定位，按官方限制请求客户端导出；不把搜索高亮作为证据 |
| 网络、证书或链接过期 | 修复网络/信任链，重新签发本次初始化链接；不关闭TLS验证或复用旧二维码 |

本项目不会通过给机器人发消息、创建Webhook、修改文档成员或把资料公开来“修复”只读权限。需要这些额外动作时属于另一个明确任务。

## 官方依据

- [企业微信套件及安装说明](https://github.com/WecomTeam/wecom-unified)
- [前置检查和凭证初始化](https://github.com/WecomTeam/wecom-unified/blob/main/skills/wecom-unified/SKILL.md)
- [文档正文读取](https://github.com/WecomTeam/wecom-unified/blob/main/skills/wecom-unified/references/wecomcli-doc.md)
- [搜索与范围限制](https://github.com/WecomTeam/wecom-unified/blob/main/skills/wecom-unified/references/wecomcli-doc-manage.md)

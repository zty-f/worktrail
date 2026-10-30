# 飞书与 Lark 的安装和授权

核对日期：2026-10-30。用于读取本人选定的工作资料。CLI和账号授权由飞书管理；本Skill不保存应用密钥或令牌。使用前先读[共同排障](setup-troubleshooting.md)。

## 1 先检查环境和现有安装

仅选择飞书资料时执行；本地模式跳过全部步骤。需要Node.js和npm/npx。macOS、Linux用终端，Windows用PowerShell，命令中的路径替换为实际路径。

```bash
node --version
npm --version
lark-cli --version
```

如果最后一条命令能运行，先核对版本与帮助，复用现有安装和账号，不默认升级或重新配置。没有Node/npm时先从[Node.js官网](https://nodejs.org/)安装适用于本机的受支持版本，重新打开终端再检查。

未安装CLI时使用官方安装入口：

```bash
npx @larksuite/cli@latest install
lark-cli --version
lark-cli config --help
lark-cli auth login --help
```

这会下载官方安装器；先看它列出的安装位置和Agent Skill目录，按提示完成。已经存在的配置不覆盖。若企业统一提供CLI和应用，使用企业版本与已有应用，先向管理员确认适用身份和可用范围。

安装成功判据是当前执行Agent的终端能找到lark-cli，不是仅看到安装器下载成功。PATH或npm权限问题见共同排障。

## 2 首次应用配置

```bash
lark-cli config init
```

在终端按照向导配置应用。Agent远程协助首次新建配置时，官方另提供：

```bash
lark-cli config init --new
```

只有确实需要新配置时才用--new；不要因为授权失败就反复新建应用。命令会给出配置页面，用户在浏览器完成应用配置、组织选择和需要的审批；保留原进程直到完成或退出。企业环境可能需要应用发布、可用成员范围和管理员开通权限。不是所有账号都能自行批准这些权限；无法操作时由企业管理员处理。

密钥在官方向导和CLI配置中录入，不粘贴到聊天、sources.json、截图或Skill目录。用户说网页“完成了”后仍需检查CLI的配置和认证状态。

## 3 用户登录和范围授权

本项目读取个人资料使用--as user。应用bot身份可用不代表本人登录成功。

先查看帮助，使用明确范围发起授权，不使用不带范围的auth login，也不默认使用--recommend或--domain all：当前官方实现可能据此申请全部业务域。

用户在自己的终端操作时，可限定本项目涉及的文档和云空间域：

```bash
lark-cli auth login --domain docs --domain drive
lark-cli auth status --json --verify
```

域授权可能包含多种能力，并不等于“仅只读scope”。要严格收窄时，Agent先检查所选读取命令的当前帮助、schema或missing_scopes，再仅请求实际需要的读取scope：

```bash
lark-cli auth login --scope "<当前读取命令实际要求的scope>"
```

当前官方drive +search参考将搜索权限列为search:docs:read；这不覆盖全部正文读取权限。尖括号不是可执行值，不能照抄或编造scope名称。应用后台开通的scope和用户实际授予的scope都需要满足；增加后台权限后，按当前CLI提示完成发布或审批，再补做用户授权。

## 4 Agent协助时避免用户收不到授权链接

官方支持分步设备授权：

```bash
lark-cli auth login --domain docs --domain drive --no-wait --json
```

Agent只向用户展示本次返回的verification_url/verification_uri_complete，并按官方Skill用auth qrcode生成二维码。链接视为不透明字符串，原样转发，不改query。device_code只在当前授权流程内保管，不写进项目、聊天回复或公开日志。先把链接展示给用户，等待用户完成；不要在用户看见链接前阻塞轮询。

用户完成后，Agent恢复本次流程：

```bash
lark-cli auth login --device-code "<本次返回的device_code>"
lark-cli auth status --json --verify
```

用户不需要手工拼device_code。授权码过期或拒绝后，本次流程结束；重新带相同所需范围生成新链接，不能复用旧码。

若当前安装版本不支持分步参数，按它的--help保留交互登录进程，并及时把当前链接交给用户。参数不兼容时停止核对版本，不猜替代参数。

## 5 登录成功后选资料

```bash
python scripts/review.py auth-check --provider feishu
```

该命令仅返回经过筛选的认证判断，不展示原始令牌。authenticated=true仍不证明某篇文档可读。CLI本机状态中应确认identity=user；只有bot可用时不能当作个人资料接通。

可以给Agent文档链接、文件夹链接或名称、项目关键词。先列出有限候选供选择，再读取正文。文件夹浏览由Agent使用官方lark-drive的drive files list能力；先读其files-list参考及当前schema，按真实folder_token和分页游标调用。项目的platform-sync不自动递归整个云空间。

只读搜索入口：

```bash
python scripts/review.py discover /absolute/workspace --provider feishu --query '项目关键词' --max-pages 3
```

把用户选定的Docx/Wiki链接放入sources.json，执行：

```bash
python scripts/review.py configure /absolute/workspace --source feishu --sources-config /absolute/workspace/sources.json --outputs summary
python scripts/review.py collect /absolute/workspace
```

成功判据是state/last-platform-sync.json的mode=live、failed为空、complete_for_selection=true，且正文非空；不是搜索命中或缩略图可见。先用一篇用户允许的文档验证，再扩大到其他选定资料。

## 6 登录和权限失败怎么处理

| 现象 | 应按什么顺序处理 |
|---|---|
| 没有应用配置、config init提示缺配置 | 先完成第2步；企业已有应用时复用，避免反复--new |
| 浏览器显示成功，但CLI仍无user身份 | 检查原进程是否已退出/过期；分步流程要恢复--device-code；重新验证状态 |
| scope不足、missing_scopes | 区分user/bot身份；user补授实际scope，bot由管理员开通应用权限；不以重新扫码替代后台审批 |
| user身份正常但某篇permission denied | 用同一账号在飞书客户端打开该文档；由拥有者通过原平台授予所需阅读权限；CLI授权不能绕过文档分享权限 |
| 读取空结果，bot可用 | 确认业务命令使用--as user；不能把bot资源为空当成“本人没有文档” |
| 组织外文档、密级、企业安全策略拦截 | 遵循租户策略，找管理员确认或在获准前提下本地导出；不自动调低安全设置 |
| 登录链接过期、取消或网络失败 | 结束旧流程，检查网络后只重试一次新的登录；沿用所需scope范围 |
| 新版命令或回包变化 | 查看--help和官方参考；未知结构按失败处理，不能把元数据当正文 |

共享账号、在聊天中粘贴token或把文档设为公开都不是修复方法。本项目不自动调整协作者、发布文档或发送管理员消息。

## 参考依据

- [官方安装与首次配置](https://github.com/larksuite/cli/blob/main/README.zh.md)
- [官方身份和权限参考](https://github.com/larksuite/cli/blob/main/skills/lark-shared/references/lark-shared-identity-and-permissions.md)
- [应用配置参考](https://github.com/larksuite/cli/blob/main/skills/lark-shared/references/lark-shared-config-init.md)
- [云空间及文件夹路由](https://github.com/larksuite/cli/blob/main/skills/lark-drive/SKILL.md)

这些命令按官方资料核对，当前项目未完成真实飞书租户端到端验证。目标电脑先核对当前版本；安装成功、登录成功、文档可读、产出完成分别验收。

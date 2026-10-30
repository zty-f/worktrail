# 钉钉 CLI 安装与授权

核对日期：2026-10-30。本机dws v1.0.52已真实验证设备授权、个人空间目录与三篇选定adoc正文读取；其他机器、组织和文档类型需要现场检查。当前官方main的部分新参数与本机旧版不同，以目标电脑--help为准。

## 1 安装所选平台的CLI

```bash
dws --version --format json
```

已有可用CLI就复用，不默认退出当前账号或升级。没有dws时，具备Node/npm的电脑可用官方npm安装方式，macOS、Linux、Windows均使用同一个包名：

```bash
npm install -g dingtalk-workspace-cli
dws --version --format json
dws auth login --help --format json
```

没有Node/npm时，官方另提供系统安装器：

macOS/Linux：

```bash
curl -fsSL https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.sh -o dws-install.sh
sh dws-install.sh
```

Windows PowerShell：

```powershell
Invoke-WebRequest https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.ps1 -OutFile dws-install.ps1
powershell -File ./dws-install.ps1
```

先确认下载来源与安装器显示的目标位置，保留企业自定义版本和已有配置。官方还提供GitHub Releases、Homebrew及国内镜像入口，网络或架构问题见[共同排障](setup-troubleshooting.md)及[官方安装说明](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/blob/main/README_zh.md)。Linux安装器当前声明不支持musl/Alpine。不要下载架构不匹配的文件后忽略启动错误。

安装器可能同时安装官方钉钉Skills；本Skill内已有安装和取数说明，不要求目标机器预先存在本开发者的私有Skill。涉及额外文档类型时优先读取目标机器安装的官方产品Skill和对应leaf schema。

## 2 本机浏览器登录

```bash
dws auth login --format json
```

原进程保持运行，用户在浏览器选择自己的账号和目标组织，再完成授权。浏览器回跳127.0.0.1时，接收回调的必须是启动CLI的那台机器。网页显示“登录了”不是CLI持久化成功的判据。

命令成功退出后检查：

```bash
dws auth status --format json
python scripts/review.py auth-check --provider dingtalk
```

确认authenticated=true，并在本机确认组织和账号正确。不要把完整认证JSON转发到群聊或复制进报告。官方新版本可能支持auth status --readonly，它读取本地快照而不刷新；先看help，本机v1.0.52不支持此参数，不能强加。带reason的不可判定结果不能仅凭authenticated=false认定未登录。

## 3 设备码登录

SSH、远程Agent、回调不通或用户浏览器不在CLI所在机器时用设备授权：

```bash
dws auth login --device --no-browser --timeout 600 --format json
```

1. Agent读取本次进程输出，仅展示验证页面和user_code，不展示底层device_code或令牌。
2. 用户打开当前页面，输入该user_code，选择正确组织并授权。
3. 保留发码的原进程，直到它成功退出、明确失败或过期。不要同时启动多个登录进程。
4. 用户回复完成后，检查原进程，再运行auth-check确认状态。

--timeout是CLI帮助中的HTTP请求超时参数，不是延长服务端授权码寿命的开关；有效期以本次输出为准。Agent应及时展示链接并保留后台进程，不能等阻塞超时后才交给用户。任何演示文档都不应内置一个“通用授权码”。

### Invalid or expired user code

确认用户打开的是当前进程生成的页面且输入的是当前user_code。旧页面可能还在浏览器，不能因网页刷新就认为换成了新码。先检查旧进程是否结束；结束或过期后重新执行一次设备登录，明确提示新旧码已切换，不重复使用旧码。

新码立即失败时，记录无敏感信息的错误文字，核对CLI版本和系统时间；按官方指引排查。若设备链路仍不可用且用户浏览器和CLI在同一机器，可明确切换到第2步的本机回调登录。不要反复发码或宣称浏览器成功就已接通。

## 4 组织访问与单项行为权限

官方CLI企业数据访问可能受组织开关控制。若提示组织尚未开启CLI访问，用户可在官方授权页点“立即申请”；管理员在钉钉开发者平台的CLI访问管理中审批或开启。审批通过后重跑登录，再检查状态。这是由用户在平台内操作的流程，Skill不会自行给管理员发送消息。

登录后还可能遇到PAT行为授权或单项scope缺失：先查看本机dws pat --help、官方PAT参考与实际失败提示，按具体只读行为申请；用户完成授权后重试这一项。不默认批量永久授权所有能力，不使用--recommend替代文档最小读取需求。

PAT与应用权限是两层不同的授权。dws pat chmod若按产品批量展开权限，先用--dry-run核对scope、授权类型和有效期，再由用户明确确认；不把批量或永久授权静默执行。官方退出码4表示PAT拦截，本项目会提示行为授权而非让用户重复登录。

凭据存储出错时，先检查当前auth migrate-keychain --help。支持该迁移的Mac环境可先做预检：

```bash
env -u DWS_DISABLE_KEYCHAIN dws auth migrate-keychain --to file-dek --dry-run --format json
```

只在预检通过、用户核对迁移范围并确认后，按官方帮助执行实际迁移。不因Keychain失败就全局关闭密钥链或清空所有账号。

多组织时先用当前版本的profile list帮助和结果确认目标；业务调用可用实际返回的profile参数。名称、ID和profile格式可能随版本变化，不凭记忆编造，不自动切换到其他组织尝试访问。

## 5 选择个人空间或文件夹

```bash
dws schema 'wiki space list' --compact --format json
dws wiki space list --help --format json
dws wiki space list --type myWikiSpace --format json
```

从真实结果取得workspaceId，再列直接目录：

```bash
dws drive list --workspace <实际workspaceId> --limit 20 --format json
dws drive list --workspace <实际workspaceId> --folder <实际nodeId> --limit 20 --format json
```

尖括号必须替换为真实返回值，Agent负责传递，用户只需选可读名称。分页使用返回的nextPageToken/nextCursor对应--cursor；每批不超过30项。我的文件钉盘根目录可用：

```bash
dws drive list --limit 20 --format json
```

先展示目录、再由用户选择要读的文件。只默认浏览个人或明确选定空间，不扫描全企业。目录能列出不代表所有正文均可读。

按官方URL分流识别类型：/i/nodes/在线文字adoc可自动同步；表格、PDF、听记、旧链接等按官方产品技能转资料包或导出到本地。/i/p/分享短链不能直接假定为doc read支持的节点链接。不得把网页标题、搜索高亮、缩略图或表格元数据当成完整正文。

## 6 一篇文档读取验收

用用户选定链接配置sources.json，然后：

```bash
python scripts/review.py configure /absolute/workspace --source dingtalk --sources-config /absolute/workspace/sources.json --outputs summary
python scripts/review.py collect /absolute/workspace
```

检查last-platform-sync.json：mode=live、failed为空、complete_for_selection=true，且evidence-packet有正文。失败时缺口保留，不用旧缓存冒充新读取。正常status只证明本地账号可用，实际读取才证明这一篇具有所需权限。

## 7 失败处理

| 现象 | 处理 |
|---|---|
| 浏览器已授权，CLI未登录 | 检查原进程是否超时/退出；回调是否在另一台机器；重新开启一个正确流程 |
| authenticated=false并伴reason | 先判定本地状态能否读取，不直接reset或宣称未登录 |
| ciphertext_key_mismatch | 先参照官方auth migrate-keychain帮助做dry-run预检，再由用户按提示确认迁移；不要auth reset清空全部账号 |
| 组织CLI访问关闭 | 由用户走官方申请，管理员批准后重新登录 |
| 已登录但缺单项行为权限 | 按实际PAT/scope提示申请所需只读能力，再重试该项 |
| 只有某篇文档无权限 | 同账号在钉钉客户端验证，找文档拥有者授予阅读权限；登录授权不会绕过文档ACL |
| 命令不存在或unknown flag | 用本机help和leaf schema核对版本；不要schema --all或尝试猜参数 |
| 有RECOVERY_EVENT_ID | 按官方recovery plan/execute/finalize指南核对恢复计划，避免无范围重试 |
| 搜索成功，正文为空或类型不支持 | 保留为未读取，按类型路由或请求本地导出；不生成该来源的完成业绩 |

本机实测路径仅是所选三篇adoc，不推广为所有组织、平台类型均已验证。

参考：[官方项目](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli)、[认证及参数参考](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/blob/main/docs/reference.md)。

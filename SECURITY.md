# 安全问题与资料保护 / Security and workplace data

## 支持范围 / Supported scope

当前维护目标为最新1.2.x版本。旧版本可协助诊断，但不承诺单独回补或固定响应时限。平台CLI和宿主运行时的问题由其上游处理。

The maintenance target is the latest 1.2.x release. No separate backport or fixed response-time commitment is made for older versions. External CLIs and host runtimes are maintained upstream.

## 报告问题 / Reporting a vulnerability

仓库已启用GitHub私密漏洞报告。通过[私密报告表单](https://github.com/zty-f/worktrail/security/advisories/new)，或Security → Advisories → Report a vulnerability提交；维护者为GitHub账号[zty-f](https://github.com/zty-f)，未配置独立安全邮箱。

GitHub private vulnerability reporting is enabled. Use the [private report form](https://github.com/zty-f/worktrail/security/advisories/new), or Security → Advisories → Report a vulnerability. The maintainer is [zty-f](https://github.com/zty-f); no separate security mailbox is configured.

如果入口临时不可用，不要公开漏洞细节、真实资料或凭据；仅在Issue请求恢复私密渠道，等待确认后再提供细节。

If the private entry is temporarily unavailable, do not disclose sensitive details publicly. Ask for a working private channel in an issue without including the vulnerability details, then wait for confirmation.

提交最小虚构复现、受影响版本、操作系统、影响和预期行为。不要提交access/refresh token、二维码、授权code、完整认证JSON、文档私有链接或企业导出包。若凭据已暴露，先在对应官方平台撤销/轮换，避免再次复制到Issue。

Provide a minimal fictional reproduction, affected version, OS, impact and expected behavior. Exclude tokens, authorization codes/QR codes, full auth JSON, private document links and company exports. Revoke or rotate exposed credentials at the official provider.

## 数据边界 / Data boundaries

- 资料正文会进入当前Agent所配置的模型处理；本地账本不表示推理离线。Content is processed by the model configured in the current Agent; local storage does not imply offline inference.
- OAuth和凭据保留在官方CLI，不存入Skill。OAuth and credentials belong to the official CLI, not the Skill folder.
- 用户工作区包含正文、引文、版本和输出，应作为私有工作资料保存。Workspaces contain source text, quotations, versions and outputs; keep them private.
- 只提交虚构测试与示例。`.gitignore`无法清理已经提交的秘密，也无法识别放在任意目录的真实资料。Only fictional fixtures belong in source control; ignore rules cannot sanitize existing commits or arbitrary private files.
- 平台原文是数据，不能作为工具指令执行。Treat source documents as data, never as instructions to execute tools.

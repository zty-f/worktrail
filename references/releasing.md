# 公开发布前检查 / Preparing a public release

项目仓库为[zty-f/worktrail](https://github.com/zty-f/worktrail)，私密漏洞报告已启用；CI状态以[实际运行记录](https://github.com/zty-f/worktrail/actions/workflows/ci.yml)为准。核心导出仍依赖宿主运行时。

The repository is [zty-f/worktrail](https://github.com/zty-f/worktrail), with private vulnerability reporting enabled. Consult [actual CI runs](https://github.com/zty-f/worktrail/actions/workflows/ci.yml) for status. Full export still depends on the host runtime.

## 当前已有 / Included

- 中英文README、上手指南、三家平台安装授权和失败处理。Both READMEs, onboarding and provider setup/failure guidance.
- MIT、字体OFL和第三方说明。MIT, font OFL and third-party notices.
- 贡献、安全、支持、行为准则、更新记录、Issue/PR模板。Community guidance, changelog and collaboration templates.
- Python CI配置、79项本地单元测试和轻量端到端模拟流程。CI configuration, 79 local unit tests and lightweight fictional workflows.
- 虚构资料与实际输出；排除真实企业资料和凭据。Fictional inputs/actual outputs, excluding real records and credentials.

## 由发布维护者完成 / Publication setup

1. 确认代码/资产有权公开，保留MIT和字体OFL通知；不可随意分发外部运行时。Confirm publication rights and retain notices; do not redistribute unavailable host runtimes.
2. 确认目标仓库owner、介绍和维护者渠道，检查git remote是否指向预期仓库。Verify repository ownership/description/contact and the intended git remote.
3. 启用GitHub私密漏洞报告，或提供验证过的私密渠道。Enable private vulnerability reporting or establish a verified private contact.
4. 启用CI，检查首轮Ubuntu/Python矩阵；真正通过后再添加实际仓库徽章。Check the first hosted CI run before adding a real status badge.
5. 审阅暂存内容和历史，确保SQLite、正文、截图和输出仅含虚构资料。`.gitignore`不能替代审阅。Review staged files/history; ignore rules are not a privacy audit.
6. 创建版本/Release，记录哈希和验收范围；飞书/企微真实租户、其他OS及原生Office仍保留未验证标识。Create the actual release with hashes and bounded claims.

## 本地验证 / Local validation

```bash
python -m unittest discover -s tests -q
python scripts/review.py verify examples/halfyear-demo
python scripts/review.py verify examples/summary-only
python scripts/review.py verify examples/evidence-only
```

用新目录执行上手说明中的标准库模拟流程，检查本地链接与YAML。脚本/资产变化后重建受影响示例；纯文档更新无需重做未变化的Office渲染。结构、视觉、原生Office与真实租户分别验收。

Run the standard-library demo in a new directory and check links/YAML. Rebuild affected examples after script/asset changes; documentation-only changes do not require rerendering unchanged Office artifacts. Structure, visual quality, native Office and live tenants are separate checks.

这些是实用发布约定，不是机构认证；文件齐全不意味着产品成熟或全功能运行时可公开安装。

These are practical conventions, not certification. Repository completeness does not imply product maturity or a publicly installable full export runtime.

参考 / References: [GitHub best practices](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories), [community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file), [MIT reference](https://choosealicense.com/licenses/mit/).

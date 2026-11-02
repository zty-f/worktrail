# 更新记录 / Changelog

## 1.2.2 — 2026-11-02

- 项目正式命名为“职迹 WorkTrail”，Skill标识和目录名统一为worktrail。Rename the project to WorkTrail and use worktrail as the Skill/directory name.
- 增加真实仓库、贡献和私密漏洞报告入口。Add actual repository, contribution and private-report links.
- 固定Git换行规则，CI核验克隆后的完整/轻量随包示例。Preserve byte-exact fixtures and verify bundled examples after checkout in CI.
- PRS_*运行时环境变量继续兼容，避免破坏已有本地配置。Retain PRS_* runtime environment compatibility.
- 中英文README提供“GitHub链接安装 → 开始使用”的通用Agent话术，由对应Agent按自身机制安装，无需指定专属安装器。Provide generic Agent installation/first-use prompts in both READMEs, without requiring an Agent-specific installer.
- 首次GitHub Release提供完整项目压缩包、中英文安装说明、更新记录及SHA-256校验文件。The first GitHub Release provides the full project archive, Chinese/English installation guides, changelog and SHA-256 checksums.

## 1.2.1 — 2026-10-30

文档与开源协作更新 / Documentation and community update:

- 增加英文README、英文首次使用与平台安装排障指引；中文README增加目录、架构、预览及公开发布边界。Add English onboarding and expand the Chinese README.
- 增加贡献、安全、支持、行为准则、Issue/PR模板及Python CI配置。Add contribution/security/support/conduct guidance, templates and Python CI configuration.
- 补充发布前检查、依赖与字体许可说明；保留标准MIT正文，字体使用OFL。Clarify release checks and external notices; retain canonical MIT text and the font's OFL.
- 核心采集、事实规则和导出脚本未改变。Core ingestion, evidence and export code is unchanged.
- CI配置已做本地结构检查及等效命令验证，尚未在GitHub运行。CI is locally checked; no hosted run is claimed.

## 1.2.0 — 2026-10-30

- 来源选择支持本地文件夹、飞书、钉钉、企微和混合范围。Selectable local/Feishu/DingTalk/WeCom/mixed sources.
- 默认summary，多选产出；未选择的Office文件不会生成或留在本次output。Summary by default with selectable exports and no stale unselected files in output.
- 三家安装授权与排障、脱敏认证诊断、范围校验和失败保留旧输出。Platform onboarding, sanitized auth checks, scoped collection and preservation of the previous successful output on failure.
- 79项单元测试；实际轻量总结、证据、PDF、PPT及完整导出验证。79 unit tests plus actual selected-output checks.

更早版本材料见已有本地发行包；此记录不补造未知提交或Release历史。Earlier local packages are retained separately; no unknown commit or release history is reconstructed.

# 贡献指南 / Contributing

欢迎改进资料解析、证据核验、平台适配、文档及公开可安装的导出能力。中文和英文均可用于讨论与PR。请先阅读[README](README.md)、[行为准则](CODE_OF_CONDUCT.md)和[安全说明](SECURITY.md)。

Contributions to parsing, evidence validation, adapters, documentation and portable export are welcome. Chinese and English issues and PRs are accepted. Start with the [English README](README.en.md), [code of conduct](CODE_OF_CONDUCT.md) and [security policy](SECURITY.md).

## 本地开发 / Local development

Python >=3.10. No platform account, Node runtime or model API key is needed for unit tests. In the project directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -q
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
```

轻量端到端验证请创建一个不存在的新目录，命令中的python指当前虚拟环境解释器。`-S`用于验证不加载第三方site-packages的路径。夹具中的事实预设且为虚构，不代表模型自动理解新资料。

For a lightweight end-to-end check, choose a new directory that does not exist. Use your active Python interpreter. `-S` checks the standard-library path. The fixture contains fictional, pre-reviewed facts; it is not an extraction model.

```bash
python -S scripts/create_light_demo.py /absolute/new-smoke-workspace --outputs summary,evidence
python -S scripts/review.py build /absolute/new-smoke-workspace
python -S scripts/review.py verify /absolute/new-smoke-workspace
```

## 修改约定 / Change expectations

- 真实文档、账号身份、OAuth链接、密钥、cookie和令牌不得进入Issue、PR、测试或示例。使用最小虚构样例。Never submit real workplace material or credentials; use minimal fictional fixtures.
- 平台默认只读，搜索和目录不冒充正文。未知回包明确失败，保持选定资料范围。Keep adapters read-only, scoped and explicit about unsupported responses.
- 本人归因、团队结果、未知日期、在途工作及指标口径必须分别保留。Preserve attribution, completion status, unknown dates and metric comparability.
- 新增依赖时说明适用功能及安装方式；保持summary轻量路径可用。Explain new dependencies and preserve the lightweight summary path.
- README功能、默认值和限制变更同步更新中英文版本；操作指南若仅有某种语言，要明确标识。Update both READMEs when behavior or limits change; identify untranslated guides.
- 为具体行为变化增加有意义的回归检查。无需为拼写修改机械加测试。Add meaningful regression coverage for behavior changes.
- 修改scripts或assets会改变recipe_hash；随包示例须重新构建并verify。Changes under scripts/assets require rebuilding and verifying affected bundled examples.

## 提交与评审 / Pull requests

在[项目仓库](https://github.com/zty-f/worktrail)中提交Issue或PR。PR说明问题、改动后行为、测试方法、平台/运行时验收边界及新增依赖。AI辅助贡献同样需要提交者核对事实、许可与测试结果，不用AI生成结果替代验证。

Use the [project repository](https://github.com/zty-f/worktrail) to open issues and PRs. Explain the problem, resulting behavior, validation, platform/runtime limits and any new dependency. Authors remain responsible for reviewing AI-assisted contributions.

GitHub CI配置只测试公开Python依赖、单元测试和轻量模拟流程。Office视觉质量、真实平台授权与原生PowerPoint/WPS兼容性需独立验证，不由CI通过自动推定。

The CI configuration covers public Python dependencies, unit tests and lightweight fictional workflows. It does not validate Office visual quality, live tenant permissions or native PowerPoint/WPS compatibility.

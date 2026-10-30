# 外部组件与来源 / Third-party notices

原创代码与说明按[MIT](LICENSE)提供。外部CLI、运行时、Python包和字体保留各自许可，不因本项目MIT重新授权。除字体外，以下外部软件未随包分发；安装时以实际版本许可为准。

Original code and documentation use [MIT](LICENSE). External software/fonts retain their own licenses. Apart from the font, external software below is not redistributed; consult the installed version's license.

## 随包字体 / Bundled font

**Noto Sans CJK SC Regular** — unmodified font from [notofonts/noto-cjk](https://github.com/notofonts/noto-cjk), [source OTF](https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf).

文件为assets/fonts/NotoSansCJKsc-Regular.otf，许可[SIL OFL 1.1](assets/fonts/OFL.txt)，版权信息保留在未修改字体元数据中；仅用于本地渲染，不自动安装系统。PPT默认PingFang SC为宿主系统字体，本项目不分发。

The unmodified OTF retains copyright metadata and uses [SIL OFL 1.1](assets/fonts/OFL.txt). It is not automatically installed into the OS. PPT's default PingFang SC is a host system font and is not bundled.

## 用户安装的依赖 / User-installed dependencies

| Component | Purpose | Upstream |
|---|---|---|
| python-docx | DOCX parsing/generation | [python-openxml/python-docx](https://github.com/python-openxml/python-docx) |
| pypdf | PDF text extraction | [py-pdf/pypdf](https://github.com/py-pdf/pypdf) |
| openpyxl | XLSX parsing | [openpyxl documentation](https://openpyxl.readthedocs.io/) |
| Node.js | CLI installation and optional export host | [nodejs.org](https://nodejs.org/) |
| Feishu/Lark CLI | Selected document access | [larksuite/cli](https://github.com/larksuite/cli) |
| DingTalk DWS | Selected document access | [DingTalk workspace CLI](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli) |
| WeCom CLI/Skill suite | Selected document access | [WecomTeam/wecom-unified](https://github.com/WecomTeam/wecom-unified) |

## 宿主组件 / Host components

Word/PDF使用宿主文档渲染器及可用组件；PPT使用宿主@oai/artifact-tool和演示校验器；浏览器QA使用宿主Playwright/Chromium。运行时、浏览器和上游Skill源文件未复制进公开包，也不声称都能从公共包管理器获取。

Word/PDF use the host document renderer; PPT uses host @oai/artifact-tool and validators; browser QA uses host Playwright/Chromium. These components and upstream Skill sources are not bundled or claimed to be publicly installable.

CI按核对提交SHA引用[actions/checkout](https://github.com/actions/checkout)和[actions/setup-python](https://github.com/actions/setup-python)，没有复制其源码。CI references official action commits without bundling their source.

## 核对范围 / Reference scope

平台命令参考核对日期2026-10-30，revision见[platform-sources.json](references/platform-sources.json)。DWS实测v1.0.52，飞书/企微尚无真实租户验收。账号、权限和依赖许可需按目标版本核对。本项目与服务商无官方隶属或背书关系。

Provider references were checked on 2026-10-30; see the [source record](references/platform-sources.json). Local DWS acceptance used v1.0.52; Feishu/WeCom live acceptance is pending. Check target-version permissions/licenses. No official affiliation or endorsement is implied.

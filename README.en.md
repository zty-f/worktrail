# WorkTrail

[简体中文](README.md) | **English** · Version **1.2.2** · Python **>=3.10** · [MIT](LICENSE)

A Skill for work summaries, annual summaries, year-end reports, personal annual work reports, mid-year presentations, probation reports and performance self-evaluation/review preparation. Turn local files or selected authorized DingTalk, WeCom (Enterprise WeChat) and Feishu/Lark records into evidence-backed accounts of your work, contributions and observed results. Export a report, evidence explorer, self-evaluation, Word, PDF or editable PowerPoint only when requested. **The default output is a work summary.**

This Agent Skill includes CLI helpers for source collection, evidence checks and selected exports, and can also support project retrospectives. You supply an AI Agent that can read files and execute Python. Downloading the folder alone does not analyze new documents. [Repository](https://github.com/zty-f/worktrail) · [CI runs](https://github.com/zty-f/worktrail/actions/workflows/ci.yml).

This independent open-source project is not affiliated with worktrail.app, worktrail.net or other products sharing the name.

**Contents:** [Quick start](#quick-start) · [Preview](#preview) · [Features](#features) · [Command-line workflow](#command-line-workflow) · [Requirements](#requirements) · [Platform access](#platform-access) · [How it works](#how-it-works) · [Examples and validation](#examples-and-validation) · [Limits and roadmap](#limits-and-roadmap) · [Contributing and license](#contributing-and-license)

## Quick start

### 1. Install the Skill

Send this prompt to your Agent that supports Agent Skills, letting it use its own installation mechanism. It is a chat instruction, not a terminal command:

```text
Please install the Skill from this GitHub repository: https://github.com/zty-f/worktrail.
The Skill is in the repository root and is named worktrail. Follow your Agent's installation procedure and include all supporting files.
```

Keep the scripts, references, assets, examples and other supporting directories. Installing SKILL.md alone is insufficient.

### 2. Start using it

Once installation is complete and your Agent recognizes the Skill, send:

```text
Please use the worktrail Skill to organize the work records in the folder I specify.
I only need a summary of work content and observed results, with evidence and open questions. Do not generate a PPT.
```

Then provide the actual local folder path, your role and the relevant time period as needed. If the Skill is not recognized, follow your Agent's instructions to refresh its Skill list, start a new session or restart.

Local MD/TXT/CSV input and lightweight summaries require Python >=3.10. Install a provider CLI and authorize your own account only when selecting platform sources; check [requirements](#requirements) when selecting PDF/PPT. For manual script execution, see the [command-line workflow](#command-line-workflow).

## Preview

This screenshot is from the included fictional half-year example. The evidence explorer supports personal/team filters, metric conflicts and exact quotations. It contains no real workplace records.

![Evidence explorer from fictional half-year records](examples/halfyear-demo/qa/evidence-desktop-top.png)

[Summary example](examples/summary-only/output/工作总结.md) · [PDF](examples/halfyear-demo/output/汇报文档.pdf) · [Editable PPTX](examples/halfyear-demo/output/汇报演示.pptx) · [Slide preview](examples/halfyear-demo/qa/deck-montage.webp)

Download the project and open [the evidence HTML](examples/halfyear-demo/output/index.html) in a browser. GitHub's file viewer does not run the interactive page. Examples and default exported filenames/headings are currently Chinese.

## Features

- Choose specific local folders or platform documents; browse a bounded set of candidates before selecting document bodies.
- Keep personal actions, team results, plans, in-progress work and completed delivery separate. File ownership alone does not establish personal contribution.
- Preserve source versions, exact quotations and location references. Unknown event dates remain unknown.
- Compare metrics only when definition, unit, population and comparison scope match. Unresolved conflicting values do not become quantitative achievements.
- Select only the outputs you need. A failed export preserves the previous successful output; a new successful build removes unselected formats from the current output directory.

| Output key | Result |
|---|---|
| `summary` — default | Work content, personal/team results, observed effects and gaps in Markdown |
| `report` | Structured report draft in Markdown |
| `evidence` | Interactive evidence page, source snapshots, CSV and analysis data |
| `docx` / `pdf` / `pptx` | Word / PDF / editable PowerPoint |
| `self-eval` | Self-evaluation draft without an automatic performance rating |
| `speaker-notes` | Slide-by-slide speaking notes; no PPT export is implied |
| `all` | All formats, only when explicitly selected |

## Command-line workflow

Download the complete project or clone the repository:

```bash
git clone https://github.com/zty-f/worktrail.git
cd worktrail
```

See the [English installation guide](references/installation.en.md) for Windows commands and detailed steps. Keep the entire project folder together and ask your Agent to read `SKILL.md`:

> Read this project's SKILL.md. Use my selected local folder. I only need a summary of work and observed results, with evidence and open questions. Do not generate Word, PDF or PPT.

Run commands in the project directory. Replace `python` with the interpreter used by your Agent and use real paths; keep your private workspace outside the source-material folder.

```bash
python scripts/review.py init /absolute/my-review
python scripts/review.py configure /absolute/my-review --interactive
python scripts/review.py doctor --outputs summary
python scripts/review.py collect /absolute/my-review
python scripts/review.py packet /absolute/my-review
```

Fill `brief.json` with the person, role, period and projects. The wizard saves selected sources and outputs in `workflow.json`. For platform input, install and authorize only the selected provider and prepare `sources.json` from the documents you chose.

**Your Agent must actually read `state/evidence-packet.json`, extract and semantically review facts, then create `facts.json`.** Collection alone does not perform this step. The [data contract](references/data-contract.md) and [reasoning guide](references/reasoning.md) are currently Chinese.

```bash
python scripts/review.py import-facts /absolute/my-review /absolute/my-review/facts.json
python scripts/review.py analyze /absolute/my-review
python scripts/review.py build /absolute/my-review
python scripts/review.py verify /absolute/my-review
```

Build uses your saved output selection. Override a single build with `--outputs summary,pptx`, for example. Summary-only output contains `工作总结.md` and `manifest.json`; it does not require Node or an Office renderer.

To try a fictional example without platform accounts or third-party Python packages, create a new path that does not already exist:

```bash
python -S scripts/create_light_demo.py /absolute/new-demo --outputs summary
python -S scripts/review.py build /absolute/new-demo
python -S scripts/review.py verify /absolute/new-demo
```

This fixture contains pre-reviewed fictional facts. It demonstrates the pipeline, not automatic understanding of arbitrary files.

## Requirements

| Capability | Requirements |
|---|---|
| MD/TXT/CSV input; summary, report, evidence, self-evaluation and notes | Python >=3.10 standard library |
| Read DOCX / text PDF / XLSX | `python-docx` / `pypdf` / `openpyxl`, listed in `requirements.txt` |
| Read selected cloud documents | The relevant official CLI and your own account/organization authorization |
| Generate and validate Word/PDF | `python-docx` and an available host document-rendering runtime |
| Export editable PPTX | Node, host `@oai/artifact-tool` and presentation validation helpers |

Full export currently uses the host Codex document/presentation runtime, which is **not bundled** and is not claimed to be a publicly installable npm dependency. Other Agent environments can use lightweight outputs; full exports require separately available compatible runtimes. Mac export was checked; Windows/Linux export and native PowerPoint/WPS rendering have not been accepted.

Run `doctor --outputs <selection>` before exporting. Runtime overrides are `PRS_NODE`, `PRS_NODE_MODULES`, `PRS_PRESENTATIONS_SKILL` and `PRS_DOCX_RENDERER`; they point to compatible runtimes that already exist on the target host.

## Platform access

Use the [English setup and troubleshooting guide](references/platform-setup.en.md). Detailed Chinese guides: [Feishu/Lark](references/setup-feishu.md), [DingTalk](references/setup-dingtalk.md), [WeCom](references/setup-wecom.md), [common failures](references/setup-troubleshooting.md), [supported document types](references/platforms.md).

```bash
python scripts/review.py auth-check --provider dingtalk
python scripts/review.py doctor --provider dingtalk --check-auth --outputs summary
```

Diagnostics do not install software, start OAuth or expose raw credentials. The official CLI may refresh existing credentials. Login success does not establish permission to a document: read one user-approved document first. App scopes, organization access and document ACLs are separate checks.

As of 2026-10-30, DingTalk personal-space pagination, three selected adoc bodies and an unchanged reread were validated in an earlier authorized run. Feishu and WeCom commands were checked against official references and tested with isolated responses/routing; **no live tenant acceptance has been completed**. Real DingTalk material and credentials are excluded from this project.

Automatic body adapters cover Feishu Docx/Wiki, DingTalk nodes text documents and WeCom doc/smartpage. Search snippets, document titles and page trees are not body evidence. Other types require an authorized official export or a located text packet; there is no default enterprise-wide scan.

## How it works

Selected read-only input → versioned source ledger → Agent-reviewed facts → deterministic attribution/reference/metric checks → selected exports.

The Agent reads and interprets source material. Python handles ingestion, SQLite history, explicit revisions, reference validation and comparable-metric calculation. Native objects are used for editable PPT tables and charts. Rules cannot prove semantic truth, causality or a performance rating.

```text
worktrail/
├── SKILL.md                 Agent entrypoint
├── agents/openai.yaml       Agent UI metadata
├── scripts/                 Ingestion, ledger, checks and selected exports
├── references/              Setup, provider guides and data/quality contracts
├── assets/                  Evidence UI assets and OFL font
├── examples/                Fictional inputs, outputs and QA evidence
├── tests/                   Unit and browser checks
├── .github/                 CI configuration and collaboration templates
├── CONTRIBUTING.md
└── LICENSE
```

Keep real workspaces private. They contain source bodies, quotations and outputs. Source text is processed by the model configured in your Agent; local ledger storage does not imply offline inference. No independent model API/key is required by these scripts, but your Agent account and model usage are your own. The default workflow does not send messages, write back to platforms, submit reviews or schedule jobs.

## Examples and validation

The full fictional example has 13 sources, 20 extracted facts and 18 retained facts after duplicate merging and period checks. It resolves 23/25 minutes using a fictional confirmation, computes 40→25 as a 37.5% duration reduction, leaves 48/60 unresolved, keeps a pilot figure separate and does not present unfinished work as launched results.

`examples/summary-only` and `examples/evidence-only` each use three fictional Markdown records and five pre-reviewed facts. They demonstrate selected output without Office dependencies.

```bash
python -m unittest discover -s tests -q
python scripts/review.py verify examples/halfyear-demo
python scripts/review.py build examples/halfyear-demo --outputs all
```

The last command requires the full host export runtime. Local evidence records 79 passing unit tests, 24 full-evidence browser checks, 14 evidence-only browser checks and actual summary/evidence/PDF-only/PPT-only/full builds. See the [QA record](examples/halfyear-demo/qa/output-selection-report.json).

[GitHub CI](https://github.com/zty-f/worktrail/actions/workflows/ci.yml) targets Ubuntu and Python 3.10/3.12/3.13 with public Python dependencies, bundled-example verification after checkout and lightweight fixtures. Consult actual runs for status. CI does not prove live platform access or Office visual compatibility.

## Limits and roadmap

- Actual semantic extraction is performed by your Agent; CLI collection is not a built-in language model.
- Full PDF/PPT export still depends on the host runtime. A publicly installable export backend is a future direction.
- Feishu/WeCom live acceptance, cross-platform font/rendering checks and native Office QA remain to be done.
- Scans, images, attachments and unsupported tables need separate recognition or an authorized export.
- Both READMEs, an English quick start and an English platform summary are provided. Some detailed references and default output headings/filenames remain Chinese; full localization is not claimed.

These are current limits and possible next steps, not delivery-date promises.

## Contributing and license

[Contributing](CONTRIBUTING.md) · [Support](SUPPORT.md) · [Security](SECURITY.md) · [Code of conduct](CODE_OF_CONDUCT.md) · [Changelog](CHANGELOG.md) · [Release preparation](references/releasing.md)

Original code and documentation use [MIT](LICENSE). The bundled Noto font retains [SIL OFL 1.1](assets/fonts/OFL.txt). External dependencies, CLIs and host runtimes retain their own licenses and are not redistributed here; see [third-party notices](THIRD_PARTY.md).

This is an independent project, not an official Feishu, DingTalk, WeCom or OpenAI product. Use [issues](https://github.com/zty-f/worktrail/issues) and [pull requests](https://github.com/zty-f/worktrail/pulls) for fictional reproductions and contributions. Private vulnerability reporting is enabled: use the [private report form](https://github.com/zty-f/worktrail/security/advisories/new), not public issues, for sensitive security details.

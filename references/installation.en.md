# Installation and first use

[English README](../README.en.md) · [中文完整版](installation.md) · [Platform setup](platform-setup.en.md)

## 1. Install from GitHub or use the archive

Send this prompt to an Agent that supports Agent Skills and let it follow its own installation procedure:

```text
Please install the Skill from this GitHub repository: https://github.com/zty-f/worktrail.
The Skill is in the repository root and is named worktrail. Follow your Agent's installation procedure and include all supporting files.
```

Once installed and recognized:

```text
Please use the worktrail Skill to organize the work records in the folder I specify.
I only need a summary of work content and observed results, with evidence and open questions. Do not generate a PPT.
```

Then provide the actual folder path, your role and the relevant period. If the Skill is not recognized, follow your Agent's instructions to refresh its list, start a new session or restart.

Alternatively, extract the package and keep the entire `worktrail` directory. Give it to an Agent that can read files and run Python, either through the host's supported Skill installation mechanism or by asking the Agent to read its `SKILL.md` directly. There is no standalone GUI or background service to start.

Tell the Agent which folders/platform you want and which output you need. If output is unspecified, use `summary`. Do not install all three platform CLIs for local input.

## 2. Python and optional parsing packages

Python >=3.10 is required. In the project directory, macOS/Linux:

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/review.py doctor --outputs summary
```

Windows PowerShell:

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/review.py doctor --outputs summary
```

For MD/TXT/CSV input and lightweight output, you may skip pip and use a compatible Python directly. Reading DOCX/text PDF/XLSX requires the corresponding package in `requirements.txt`. Image-only scans require separate recognized text with source locations.

In commands below, `python` means your chosen interpreter. Paths with spaces must be quoted. On Windows, use an absolute path such as `C:\Users\you\Documents\my-review` instead of `/absolute/my-review`.

## 3. Create a private workspace and choose input

Use a new private workspace outside the source-material folder:

```bash
python scripts/review.py init /absolute/my-review
python scripts/review.py configure /absolute/my-review --interactive
```

The wizard accepts local, Feishu, DingTalk, WeCom or mixed sources and multiple output selections. It saves configuration only; it does not start OAuth, install software or collect data.

Local selection:

```bash
python scripts/review.py configure /absolute/my-review --source local --local-folder /absolute/materials --outputs summary
```

Repeat `--local-folder` for multiple folders. Fill the workspace's `brief.json` with the person, role, period and projects. A simple summary does not require a complete performance rubric or a presentation length.

For platform input, first follow [platform setup](platform-setup.en.md), list a bounded set of candidates, then choose the documents. Copy the structure of [sources.example.json](../assets/sources.example.json), remove unselected providers and replace placeholders with actual selected document links. It must not contain credentials.

```bash
python scripts/review.py configure /absolute/my-review --source dingtalk --sources-config /absolute/my-review/sources.json --outputs summary,evidence
```

For mixed input, use `--source mixed`, the selected local folders and selected platform configuration together. `collect` rejects mismatched platform configurations. After a successful scope change, unselected old sources are deactivated with history retained; facts referencing them need another review.

## 4. Collect, review and build

```bash
python scripts/review.py doctor --outputs summary
python scripts/review.py collect /absolute/my-review
python scripts/review.py packet /absolute/my-review
```

The Agent must read `state/evidence-packet.json` and produce reviewed `facts.json` according to the [data contract, Chinese](data-contract.md). Do not reuse example facts for real files. Collection alone does not extract facts.

```bash
python scripts/review.py import-facts /absolute/my-review /absolute/my-review/facts.json
python scripts/review.py analyze /absolute/my-review
python scripts/review.py build /absolute/my-review
python scripts/review.py verify /absolute/my-review
```

Unknown dates, unresolved metric conflicts and unclear attribution remain gaps; do not invent outcomes. The `evidence` report type permits explicit unknown-date review without forcing it into a formal reporting period.

## 5. Select outputs and check dependencies

Output keys: `summary`, `report`, `evidence`, `docx`, `pdf`, `pptx`, `self-eval`, `speaker-notes`; use `all` only for an explicit full selection. Comma-separate multiple outputs.

```bash
python scripts/review.py doctor --outputs summary,pptx
python scripts/review.py build /absolute/my-review --outputs summary,pptx
```

This generates a summary and PPTX, without delivering a Word/PDF report. PDF-only keeps its intermediate Word inside the private build directory. Every output includes a manifest for integrity checks. A successful build replaces current `output`; history is retained under `builds`. An export failure preserves the previous successful output.

Full Word/PDF validation requires the compatible host document renderer. Editable PPT requires Node, host `@oai/artifact-tool` and the presentation validators. These Codex runtimes are not bundled or publicly installed by this package. If absent, use lightweight outputs or provide an existing compatible runtime via `PRS_NODE`, `PRS_NODE_MODULES`, `PRS_PRESENTATIONS_SKILL`, `PRS_DOCX_RENDERER`. Never substitute empty files for failed exports.

The bundled font is OFL-licensed. PPT uses PingFang SC by default; Mac export was checked. Other systems need appropriate fonts and actual rendering checks. Native PowerPoint/WPS acceptance has not been completed.

## 6. Try the standard-library demo

Choose a new nonexistent directory:

```bash
python -S scripts/create_light_demo.py /absolute/new-demo --outputs summary,evidence
python -S scripts/review.py build /absolute/new-demo
python -S scripts/review.py verify /absolute/new-demo
```

All people and records are fictional; facts are preset and reviewed only for the fixture. This path does not need platform login, third-party Python packages or the full Office runtime.

For failures, see [English platform troubleshooting](platform-setup.en.md) or the [detailed Chinese troubleshooting guide](setup-troubleshooting.md). Treat real workspaces as private and never commit them to a public repository.

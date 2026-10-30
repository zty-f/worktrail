# Platform installation, authorization and troubleshooting

[English README](../README.en.md) · [English installation](installation.en.md)

Checked against official references on 2026-10-30. Install only the selected provider. Reuse an existing working CLI/account; do not overwrite configuration or upgrade a company-managed installation by default. Check the target version and `--help` first. Detailed Chinese guides: [Feishu](setup-feishu.md), [DingTalk](setup-dingtalk.md), [WeCom](setup-wecom.md).

## Feishu / Lark

Official source: [larksuite/cli](https://github.com/larksuite/cli).

Check `node --version`, `npm --version` and `lark-cli --version`. If missing, use the official installer:

```bash
npx @larksuite/cli@latest install
lark-cli --version
lark-cli config --help
lark-cli auth login --help
```

For a genuinely new setup, run `lark-cli config init` and follow the official application configuration flow. Reuse a company app when applicable. `config init --new` creates a new configuration and is not a generic login repair. App visibility, scopes, publishing or approval may require an administrator. Enter secrets only in the official local flow, never in chat or `sources.json`.

Personal records require `user` identity; a working bot is not your login. Use explicit domains rather than bare login, `--recommend` or all domains:

```bash
lark-cli auth login --domain docs --domain drive
lark-cli auth status --json --verify
```

Domain grants can include more than read-only capabilities. For strict minimal grants, inspect command help/schema or `missing_scopes`, then use `auth login --scope "<actual required scope>"`. Do not guess a scope or copy a placeholder. App approval and user grants are separate requirements.

An assisting Agent can use the split device flow when supported:

```bash
lark-cli auth login --domain docs --domain drive --no-wait --json
```

Show the current verification URL immediately. Keep `device_code` only in the active authorization session. Once the user finishes, resume with `lark-cli auth login --device-code "<current device_code>"`, then verify status. A canceled/expired flow needs a fresh link. If split parameters are unsupported, follow local help and keep the interactive process alive.

Run `python scripts/review.py auth-check --provider feishu`. After user login, search selected keywords or browse the selected folder using official drive references and actual returned IDs. Choose bounded candidates, then read one selected document before expanding. This project does not recursively scan the enterprise.

If scopes are missing, address both app permission and user grant rather than repeatedly scanning login QR codes. If user identity works but a document is denied, open it with the same account and ask its owner for reading access. A CLI grant cannot bypass document ACLs. Feishu live tenant acceptance is pending.

## DingTalk

Official source: [DingTalk workspace CLI](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli). Version 1.0.52 was used for the earlier selected-adoc live validation; newer flags may differ.

```bash
dws --version --format json
```

If missing and Node/npm are available:

```bash
npm install -g dingtalk-workspace-cli
dws --version --format json
dws auth login --help --format json
```

Official macOS/Linux and Windows installers are also available; commands are in the detailed Chinese guide. The Linux installer does not declare musl/Alpine support. Preserve company-managed versions and settings.

With a browser on the same computer as the CLI:

```bash
dws auth login --format json
```

Keep the process running through the callback. A `127.0.0.1` callback must reach the machine running the CLI. After successful exit:

```bash
dws auth status --format json
python scripts/review.py auth-check --provider dingtalk
```

For a remote Agent or unavailable callback:

```bash
dws auth login --device --no-browser --timeout 600 --format json
```

Show the current verification page and `user_code` immediately; preserve the issuing process until success or expiry. Do not run multiple login processes. `--timeout` is an HTTP timeout, not an extension of the server's code lifetime. For “Invalid or expired user code”, check the current page/code, end the old expired flow and issue one fresh flow. Do not recycle screenshots or repeatedly issue codes without checking the original process.

`authenticated=false` with a `reason` can indicate unreadable local state rather than proven logout. The diagnostic preserves indeterminate status. Newer versions may offer `auth status --readonly`; v1.0.52 does not, so inspect help before adding it.

Organization CLI access may require a user request and administrator approval on the official page. PAT behavior authorization is separate from login/app permissions. Exit code 4 is a PAT block: inspect `dws pat --help` and authorize only the selected reading behavior. Preview batch `pat chmod` with `--dry-run` and have the user confirm scope/expiry; do not silently grant all actions.

For `ciphertext_key_mismatch`, inspect `auth migrate-keychain --help` and follow the official dry-run migration path before confirmed migration. Do not default to clearing accounts, disabling the keychain globally or `auth reset`.

Browse the selected personal space with real returned IDs:

```bash
dws wiki space list --type myWikiSpace --format json
dws drive list --workspace <actual-workspaceId> --limit 20 --format json
dws drive list --workspace <actual-workspaceId> --folder <actual-nodeId> --limit 20 --format json
```

Placeholders are not runnable values. Use returned pagination cursors, show titles and let the user select at most 30 documents per batch. Only supported nodes text/adoc links enter the automatic body adapter. Short sharing links, tables, recordings and binary files require their official path or an authorized export.

## WeCom / Enterprise WeChat

Official source: [WecomTeam/wecom-unified](https://github.com/WecomTeam/wecom-unified). The checked official Skill requires Node >=18 and CLI >=1.2.1. Live WeCom tenant acceptance is pending.

```bash
node --version
npm --version
wecom-cli --version
```

If missing, install the official package; confirm before replacing a managed version:

```bash
npm install -g @wecom/cli
wecom-cli --version
wecom-cli auth show --status
```

Exact output `authorized` means credentials are configured; `unauthorized` means initialization is needed. Any other output is unknown. Substring matching is unsafe because `unauthorized` contains `authorized`.

For an unauthorized account:

```bash
wecom-cli auth init --noninteractive
```

The command emits the current link/QR and waits. Show it promptly, keep the process alive and have the user scan with their own account and correct organization. After successful exit:

```bash
wecom-cli auth show --status
python scripts/review.py auth-check --provider wecom
wecom-cli identity whoami
```

Do not reuse expired QR codes or another person's cookies. Organization eligibility/admin enablement follows the official flow; the Skill cannot approve it.

Use actual identity results for “my documents”. Select a folder, title, link or project keyword and enumerate bounded candidates. Folder discovery uses official disk capabilities, not unrestricted recursive ingestion. Automatic adapters cover `doc` Markdown and `smartpage` page bodies. A page tree is not body evidence. Tables, binary files and unsupported types need an official export or authorized local input. CLI response file paths are trusted only inside the explicit `cli_output_dir`.

## First-document acceptance

After selecting documents and making a credential-free `sources.json`, use provider `feishu`, `dingtalk` or `wecom`:

```bash
python scripts/review.py configure /absolute/my-review --source dingtalk --sources-config /absolute/my-review/sources.json --outputs summary
python scripts/review.py collect /absolute/my-review
```

Check `state/last-platform-sync.json`: `mode=live`, no failed selected items, `complete_for_selection=true`, and nonempty bodies in the evidence packet. Directory/search success, browser completion and `authenticated=true` do not establish document access. Failed items remain gaps; do not call cached text newly read.

## Shared failures

| Symptom | Next step |
|---|---|
| CLI missing | Check Agent account/PATH, reopen its terminal, verify OS/CPU support |
| npm EACCES / PowerShell policy | Use an approved user-level setup or installer; avoid automatic sudo/global policy changes |
| Download timeout | Enable the user's configured trusted proxy in the actual shell, retry once, then report continued failure |
| TLS error | Check system time/trusted roots; do not disable TLS verification |
| Browser success but CLI failure | Check process, callback machine, device polling, account and organization |
| Expired code/QR | End the old flow, create one fresh current flow and display it promptly |
| Unknown status/credential lock | Preserve unknown; inspect help/storage repair rather than resetting accounts |
| Scope/organization blocked | Resolve specific grants or the official admin request; repeated login is insufficient |
| DingTalk PAT block | Authorize the required selected behavior after preview, rather than logging in again |
| One document denied | Check native-client access with the same account and document ACL |
| Unsupported type | Report discovery only; use the allowed export/type path |

Never attach raw auth JSON, tokens, codes, private links or company exports to public issues. Do not change sharing settings, message administrators or publish documents to bypass read permissions. Reference revisions are in [platform-sources.json](platform-sources.json).

#!/usr/bin/env python3
"""职迹 WorkTrail：资料同步、证据账本、成果归因与报告导出。"""
import argparse, importlib.util, json, os, shutil, subprocess, sys
from pathlib import Path
from prs_core import *
from prs_outputs import build,verify,runtime
from prs_platforms import discover,sync,BINS
from prs_workflow import configure,collect,workflow,parse_outputs,OUTPUT_LABELS,SOURCE_LABELS
from prs_setup import auth_check,GUIDES

def doctor(outputs=None,provider=None,check_auth=False):
    rt=runtime();selected=parse_outputs(outputs);packages={p:importlib.util.find_spec(p) is not None for p in ['docx','pypdf','openpyxl']}
    artifact=(Path(rt['modules'])/'@oai/artifact-tool').is_dir();base=Path.home()/'.codex/plugins/cache/openai-primary-runtime'
    renderer=os.environ.get('PRS_DOCX_RENDERER')
    renderer_ok=Path(renderer).is_file() if renderer else bool(list((base/'documents').glob('*/skills/documents/render_docx.py')))
    ppt_skill=os.environ.get('PRS_PRESENTATIONS_SKILL')
    ppt_helpers=(Path(ppt_skill)/'container_tools/artifact_tool_utils.mjs').is_file() if ppt_skill else bool(list((base/'presentations').glob('*/skills/presentations/container_tools/artifact_tool_utils.mjs')))
    missing=[]
    if {'docx','pdf'}&set(selected):
        if not packages['docx']:missing.append('python-docx')
        if not renderer_ok:missing.append('文档渲染运行时，见references/installation.md')
    if 'pptx' in selected:
        if not rt['node']:missing.append('Node.js')
        if not artifact or not ppt_helpers:missing.append('Codex演示运行时与校验器，见references/installation.md')
    if provider and not shutil.which(BINS[provider]):missing.append(BINS[provider])
    if check_auth and not provider:raise ValueError('--check-auth需要明确--provider，不自动检查三家账号')
    result={'python':sys.executable,'python_supported':sys.version_info>=(3,10),'selected_outputs':selected,'missing_for_selection':missing,'environment_checks_passed':not missing and sys.version_info>=(3,10),'node':rt['node'],'artifact_tool':artifact,'docx_renderer':renderer_ok,'python_packages':packages,'platform_cli':{p:shutil.which(b) for p,b in BINS.items()},'authentication':auth_check(provider) if check_auth else '未检查账号；加--provider及--check-auth可诊断所选平台','scope':'仅环境检查，不代表已读正文、资料充分或已通过实际渲染。MD/TXT/CSV采集与summary/evidence/report不需要Node或第三方Python包。'}
    return result
def add_note(w,project,day,text):
    b=load(w/'brief.json')
    if project not in {p['id'] for p in b['projects']}:raise ValueError('项目不存在')
    date.fromisoformat(day)
    body=f"本人补充记录，未由外部资料独立核实。\n日期：{day}\n项目：{project}\n记录人：{b['person']['name']}\n{text}"
    item=put_source(w,'journal','journal:'+digest([project,day,text]),day+'工作记录',[{'unit':'NOTE1','text':body}]);packet(w);return item
def ingest_packet(w,path):
    result=[]
    for s in load(path)['sources']:
        if s.get('provider') not in {'feishu','dingtalk','wecom','manual'}:raise ValueError('导入包来源平台无效')
        result.append(put_source(w,s['provider'],s['locator'],s['title'],s['units']))
    packet(w);return {'ok':True,'sources':result,'note':'导入包需由Agent按平台原始回包核对，不能导入搜索摘要冒充正文。'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('doctor');p.add_argument('--outputs');p.add_argument('--provider',choices=list(BINS));p.add_argument('--check-auth',action='store_true')
    p=sub.add_parser('auth-check');p.add_argument('--provider',choices=list(BINS),required=True)
    p=sub.add_parser('init');p.add_argument('workspace',type=Path)
    p=sub.add_parser('configure');p.add_argument('workspace',type=Path);p.add_argument('--source',choices=list(SOURCE_LABELS));p.add_argument('--local-folder',action='append');p.add_argument('--sources-config');p.add_argument('--outputs');p.add_argument('--interactive',action='store_true')
    for name in ['packet','analyze','build','verify','history']:
        p=sub.add_parser(name);p.add_argument('workspace',type=Path)
        if name=='build':
            p.add_argument('--outputs',help='逗号分隔summary,evidence,report,docx,pdf,pptx,self-eval,speaker-notes，或all；默认workflow选择，首次仅summary')
            p.add_argument('--skip-ppt',action='store_true',help='兼容旧开发命令；优先使用--outputs明确选择')
    p=sub.add_parser('collect');p.add_argument('workspace',type=Path)
    for name in ['ingest-local','import-facts','decision','ingest-packet']:
        p=sub.add_parser(name);p.add_argument('workspace',type=Path);p.add_argument('file',type=Path)
    p=sub.add_parser('discover');p.add_argument('workspace',type=Path);p.add_argument('--provider',choices=list(BINS),required=True);p.add_argument('--query',required=True);p.add_argument('--max-pages',type=int,default=3);p.add_argument('--identity')
    p=sub.add_parser('platform-sync');p.add_argument('workspace',type=Path);p.add_argument('--config',type=Path,required=True)
    p=sub.add_parser('note');p.add_argument('workspace',type=Path);p.add_argument('--project',required=True);p.add_argument('--date',required=True);p.add_argument('--text',required=True)
    p=sub.add_parser('source-disable');p.add_argument('workspace',type=Path);p.add_argument('--source-id',required=True)
    args=ap.parse_args()
    try:
        cmd=args.command;w=args.workspace.resolve() if hasattr(args,'workspace') else None
        if cmd=='doctor':result=doctor(args.outputs,args.provider,args.check_auth)
        elif cmd=='auth-check':result=auth_check(args.provider)
        elif cmd=='init':result=init_workspace(w)
        elif cmd=='configure':result=configure(w,args.source,args.local_folder,args.outputs,args.sources_config,args.interactive or not any([args.source,args.local_folder,args.outputs,args.sources_config]))
        elif cmd=='collect':result=collect(w)
        elif cmd=='ingest-local':result=ingest_local(w,args.file)
        elif cmd=='packet':
            p=packet(w);result={'path':str(w/'state/evidence-packet.json'),'sources':len(p['sources']),'note':'Agent读取此文件完成事实抽取；本命令不把原文塞进终端。'}
        elif cmd=='import-facts':result=import_facts(w,args.file)
        elif cmd=='decision':result=add_decision(w,load(args.file))
        elif cmd=='analyze':
            a=analyze(w);result={'path':str(w/'state/analysis.json'),'facts':len(a['facts']),'duplicates':a['duplicates'],'conflicts':a['conflicts'],'invalid_facts':a['invalid_facts'],'decision_errors':a['decision_errors'],'questions':a['questions']}
        elif cmd=='build':result=build(w,args.skip_ppt,args.outputs)
        elif cmd=='verify':result=verify(w)
        elif cmd=='discover':result=discover(w,args.provider,args.query,args.max_pages,args.identity)
        elif cmd=='platform-sync':result=sync(w,load(args.config))
        elif cmd=='note':result=add_note(w,args.project,args.date,args.text)
        elif cmd=='ingest-packet':result=ingest_packet(w,args.file)
        elif cmd=='source-disable':
            with connect(w) as db:
                found=db.execute('SELECT 1 FROM sources WHERE id=?',(args.source_id,)).fetchone()
                if not found:raise ValueError('来源不存在')
                db.execute('UPDATE sources SET active=0 WHERE id=?',(args.source_id,));event(db,'source_disabled',{'source_id':args.source_id})
            packet(w);result={'disabled':args.source_id,'note':'历史快照保留审计。引用此来源的事实现在失效，需排除或改用其他证据后重新生成。'}
        else:
            with connect(w) as db:result=rows(db,'SELECT seq,at,kind,payload FROM events ORDER BY seq DESC LIMIT 100')
        print(json.dumps(result,ensure_ascii=False,indent=2));return 1 if isinstance(result,dict) and result.get('ok') is False else 0
    except (ValueError,KeyError,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as e:
        print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())

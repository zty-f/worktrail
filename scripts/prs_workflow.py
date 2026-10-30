"""Explicit source and deliverable selection; standard-library-only onboarding."""
from pathlib import Path
from prs_core import load, save

OUTPUT_LABELS={
    'summary':'工作内容与成效总结', 'report':'汇报底稿 Markdown',
    'evidence':'交互证据页与CSV清单', 'docx':'Word报告', 'pdf':'PDF报告',
    'pptx':'可编辑PPT', 'self-eval':'绩效自评草稿', 'speaker-notes':'逐页讲述提示'
}
SOURCE_LABELS={'local':'本地文件夹','feishu':'飞书','dingtalk':'钉钉','wecom':'企业微信','mixed':'本地与平台混合'}
DEFAULT_OUTPUTS=['summary']

def parse_outputs(value):
    if value is None:return list(DEFAULT_OUTPUTS)
    values=value.split(',') if isinstance(value,str) else value
    if isinstance(values,set):values=[key for key in OUTPUT_LABELS if key in values]
    if not isinstance(values,(list,tuple)) or not values:raise ValueError('至少选择一种产出')
    if values==['all']:return list(OUTPUT_LABELS)
    result=[]
    for item in values:
        if not isinstance(item,str) or item.strip() not in OUTPUT_LABELS:raise ValueError('未知产出；可选 '+','.join(OUTPUT_LABELS)+' 或 all')
        if item.strip() not in result:result.append(item.strip())
    return result

def workflow(w):
    p=Path(w)/'workflow.json'
    data=load(p) if p.exists() else {'schema_version':'1.0','source':{'mode':'local','local_folders':[]},'outputs':DEFAULT_OUTPUTS}
    if data.get('source',{}).get('mode') not in SOURCE_LABELS:raise ValueError('资料来源无效，请运行configure')
    data['outputs']=parse_outputs(data.get('outputs'))
    return data

def configure(w,source=None,folders=None,outputs=None,sources_config=None,interactive=False,input_fn=input):
    w=Path(w).resolve()
    if not (w/'brief.json').exists():raise ValueError('请先init创建工作区')
    previous=workflow(w)
    if interactive:
        choices=list(SOURCE_LABELS)
        prompt='资料来源：'+ '；'.join(str(i+1)+' '+SOURCE_LABELS[k] for i,k in enumerate(choices))+'。输入序号 [1]：'
        reply=input_fn(prompt).strip() or '1'
        if not reply.isdigit() or not 1<=int(reply)<=len(choices):raise ValueError('资料来源序号无效，原配置未修改')
        source=choices[int(reply)-1]
        if source in {'local','mixed'}:
            raw=input_fn('本地资料文件夹完整路径（多个用 | 分隔；可留空稍后选择）：').strip()
            folders=[x.strip() for x in raw.split('|') if x.strip()]
        else:folders=[]
        if source!='local':sources_config=input_fn('已选平台文档的sources.json路径（可留空，授权并选资料后再填）：').strip() or None
        keys=list(OUTPUT_LABELS)
        raw=input_fn('需要的产出：'+'；'.join(str(i+1)+' '+OUTPUT_LABELS[k] for i,k in enumerate(keys))+'。输入逗号分隔序号，默认1，全部填all：').strip() or '1'
        if raw=='all':outputs='all'
        else:
            indexes=[x.strip() for x in raw.split(',')]
            if any(not x.isdigit() or not 1<=int(x)<=len(keys) for x in indexes):raise ValueError('产出序号无效，原配置未修改')
            outputs=[keys[int(x)-1] for x in indexes]
    mode=source or previous['source']['mode']
    if mode not in SOURCE_LABELS:raise ValueError('未知资料来源')
    selected_folders=folders if folders is not None else (previous['source'].get('local_folders',[]) if mode in {'local','mixed'} else [])
    if mode not in {'local','mixed'} and selected_folders:raise ValueError('平台单来源不能同时选择本地文件夹；请选择mixed')
    normalized=[]
    for folder in selected_folders:
        p=Path(folder).expanduser().resolve()
        if not p.is_dir():raise ValueError('本地资料文件夹不存在：'+str(p))
        if w.is_relative_to(p):raise ValueError('工作区必须放在资料文件夹外，避免把生成文件再次采集')
        if str(p) not in normalized:normalized.append(str(p))
    config_path=sources_config or (previous['source'].get('platform_config') if mode!='local' and mode==previous['source']['mode'] else None)
    if config_path:
        config_path=str(Path(config_path).expanduser().resolve())
        if not Path(config_path).is_file():raise ValueError('平台sources.json不存在')
        validate_platform_selection(mode,load(config_path))
    data={'schema_version':'1.0','source':{'mode':mode,'local_folders':normalized},'outputs':parse_outputs(outputs if outputs is not None else previous['outputs'])}
    if config_path:data['source']['platform_config']=config_path
    save(w/'workflow.json',data)
    return {'ok':True,'workflow':data,'next':'编辑brief中的身份与周期；按需安装授权所选平台；运行collect采集，再由Agent阅读原文生成facts。'}

def validate_platform_selection(mode,config):
    providers=config.get('providers')
    if not isinstance(providers,list) or not providers:raise ValueError('sources.json需明确列出选定平台及文档')
    for entry in providers:
        provider=entry.get('provider')
        if provider not in {'feishu','dingtalk','wecom'}:raise ValueError('sources.json包含未知平台')
        if mode!='mixed' and provider!=mode:raise ValueError('平台配置与所选资料来源不一致；不会自动扩大范围')
        if not isinstance(entry.get('documents'),list) or not entry['documents']:raise ValueError('先选定文档，再采集正文；不进行空范围全库扫描')
        if len(entry['documents'])>30:raise ValueError('单平台单批最多30篇，请分批')

def collect(w):
    from prs_core import ingest_local
    from prs_platforms import sync
    w=Path(w);data=workflow(w);scope=data['source'];mode=scope['mode'];local=scope.get('local_folders',[])
    config=None
    # Validate the whole selection before any read or ledger mutation.
    if mode in {'local','mixed'} and not local:raise ValueError('尚未选择本地资料文件夹，请运行configure --local-folder')
    for folder in local:
        p=Path(folder).resolve()
        if not p.is_dir() or w.resolve().is_relative_to(p):raise ValueError('资料目录已失效，或工作区位于资料目录内，请重新选择')
    if mode!='local':
        if not scope.get('platform_config'):raise ValueError('尚未选定平台文档，请先授权并浏览候选，再配置--sources-config')
        config=load(scope['platform_config']);validate_platform_selection(mode,config)
    reports=[]
    if mode in {'local','mixed'}:
        for folder in local:reports.append(ingest_local(w,folder))
    if config is not None:reports.append(sync(w,config))
    from prs_core import connect,rows,event,packet
    selected_ids={entry['source_id'] for report in reports for entry in report.get('read',[])}
    disabled=[]
    with connect(w) as db:
        for source in rows(db,'SELECT * FROM sources WHERE active=1'):
            if source['provider'] not in {'manual','journal'} and source['id'] not in selected_ids:
                db.execute('UPDATE sources SET active=0 WHERE id=?',(source['id'],));disabled.append(source['id'])
        event(db,'collection_scope',{'mode':mode,'selected_sources':sorted(selected_ids),'disabled_sources':disabled})
    packet(w)
    result={'ok':all(not r.get('failed') for r in reports),'source_mode':mode,'reports':reports,'next':'采集不会自动理解原文。由Agent读取state/evidence-packet.json，核对后import-facts，再build；只生成所选产出。'}
    save(w/'state/last-collection.json',result);return result

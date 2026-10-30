"""Read-only CLI adapters. Explicit selection, bounded paging, no shell evaluation."""
import json, re, shutil, subprocess
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl
from prs_core import save, now, put_source, packet, connect, event, digest
from prs_setup import classify_error,GUIDES

BINS={'feishu':'lark-cli','dingtalk':'dws','wecom':'wecom-cli'}
ALLOWED={
 'feishu':{('drive','+search'),('docs','+fetch')},
 'dingtalk':{('drive','search'),('doc','read')},
 'wecom':{('doc','search'),('doc','contents','get'),('smartpage','pages','get')}
}
class PlatformError(ValueError):
    def __init__(self,message,category='platform_error'):
        super().__init__(message);self.category=category
def clean_url(url):
    p=urlparse(url)
    if p.scheme!='https' or p.username or p.password:raise PlatformError('平台链接必须为HTTPS文档链接')
    return urlunparse((p.scheme,p.netloc,p.path,'','',''))
def unwrap(r):
    if not isinstance(r,dict):return r
    if r.get('ok') is False or r.get('success') is False or r.get('errcode',0) not in (0,None) or r.get('code',0) not in (0,200,None,'0'):
        error=classify_error(r)
        raise PlatformError('平台返回失败：'+error['hint']+' 详见references/setup-troubleshooting.md；响应正文未写入日志。',error['category'])
    payload=r.get('data',r.get('body',r.get('result',r)))
    return unwrap(payload) if payload is not r else r
def run(provider,args,runner=None):
    prefix=next((x for x in ALLOWED[provider] if tuple(args[:len(x)])==x),None)
    if not prefix:raise PlatformError('拒绝未列入只读白名单的命令')
    argv=[BINS[provider],*args]
    if runner:return unwrap(runner(argv))
    if not shutil.which(argv[0]):raise PlatformError('未安装 '+argv[0]+'；请按'+GUIDES[provider]+'安装并授权','not_installed')
    # Confirm the installed command surface without executing business calls.
    help_result=subprocess.run([argv[0],*prefix,'--help',*(['--format','json'] if provider=='dingtalk' else [])],capture_output=True,text=True,timeout=20)
    if help_result.returncode:raise PlatformError('当前CLI不支持所需命令，请核对版本','unsupported_cli')
    result=subprocess.run(argv,capture_output=True,text=True,timeout=60,shell=False)
    if result.returncode:
        error=({'category':'behavior_authorization_required','hint':'请按钉钉指南完成所选只读行为的PAT授权；不重新扫码或批量永久授权。'} if provider=='dingtalk' and result.returncode==4 else classify_error(result.stderr or result.stdout))
        raise PlatformError('CLI调用失败：'+error['hint']+' 详见references/setup-troubleshooting.md；原始stderr未写入日志。',error['category'])
    try:return unwrap(json.loads(result.stdout))
    except json.JSONDecodeError:raise PlatformError('CLI返回非JSON，不能当成成功正文','unknown_response')
def normalize_body(text):
    # Expiring signed asset queries change on every fetch and contain temporary credentials.
    # Preserve the asset path and Markdown line positions; do not fetch embedded resources.
    def clean_match(match):
        value=match.group(0);p=urlparse(value)
        if any(re.search(r'^(signature|ossaccesskeyid|expires|x-amz-.+|x-oss-.+|access_token|authcode)$',k,re.I) for k,_ in parse_qsl(p.query)):
            return urlunparse((p.scheme,p.netloc,p.path,p.params,'',''))
        return value
    return re.sub(r'https?://[^\s<>"\)]+',clean_match,text)
def lines(text,prefix='L'):
    return [{'unit':prefix+str(n),'text':x} for n,x in enumerate(normalize_body(text).splitlines(),1) if x.strip()]
def member(obj,keys,default=None):
    if not isinstance(obj,dict):return default
    for k in keys:
        if k in obj:return obj[k]
    return default
def search_page(provider,q,cursor='',identity=None,runner=None):
    if provider=='feishu':
        args=['drive','+search','--query',q,'--page-size','20','--as','user','--format','json']
        if cursor:args+=['--page-token',cursor]
        data=run(provider,args,runner)
    elif provider=='dingtalk':
        args=['drive','search','--query',q,'--limit','30','--format','json']
        if cursor:args+=['--cursor',cursor]
        data=run(provider,args,runner)
    else:
        body={'keywords':[q] if q else [],'limit':30,'search_scope':'title_content'}
        if cursor:body['cursor']=cursor
        if identity:body['visitor_userids']=[identity]
        if not q and not identity:raise PlatformError('企微纯范围搜索需本人身份过滤；不能无范围浏览')
        data=run(provider,['doc','search','--json',json.dumps(body,ensure_ascii=False)],runner)
    if isinstance(data,dict) and isinstance(data.get('data'),dict):data=data['data']
    items=member(data,['docs','items','files','results','nodes'])
    if not isinstance(items,list):raise PlatformError('未知搜索结果结构，需更新适配器')
    more=bool(member(data,['has_more','hasMore','hasNext'],False));next_cursor=member(data,['next_cursor','nextCursor','page_token','nextPageToken'],'')
    normalized=[]
    for item in items:
        # Search metadata only locates candidates. Never treat highlights as body evidence.
        meta=item.get('result_meta',item) if isinstance(item,dict) else {}
        url=member(item,['url','doc_url','docUrl','link']) or member(meta,['url','doc_url','docUrl'])
        ident=member(item,['docid','document_id','nodeId','dentryUuid','fileId','token','id']) or member(meta,['token','doc_token'])
        normalized.append({'title':member(item,['doc_name','title','name'],member(meta,['title','name'],'未命名文档')),'url':url,'id':ident,'type':str(member(item,['doc_type','type','fileType'],'unknown')).lower()})
    return normalized,more,next_cursor

def discover(w,provider,query,max_pages=3,identity=None,runner=None):
    if provider not in BINS:raise PlatformError('未知平台')
    if not 1<=max_pages<=20:raise PlatformError('max-pages必须为1至20')
    if len(query)>30 and provider=='feishu':raise PlatformError('飞书关键词不能超过30字符')
    cursor='';seen=set();items=[];more=False;errors=[]
    for n in range(max_pages):
        page,more,nxt=search_page(provider,query,cursor,identity,runner)
        for x in page:
            key=x['url'] or x['id']
            if key and key not in seen:items.append(x);seen.add(key)
        if not more:break
        if not nxt or nxt==cursor:errors.append('服务端表示有下一页，但没有新的游标');break
        cursor=nxt
    result={'provider':provider,'query':query,'at':now(),'candidates':items,'pages_read':n+1,'complete_for_query':not more and not errors,'has_more':more,'errors':errors,'next_cursor':cursor if more else None,'note':'仅发现候选，尚未读取正文；请把选定链接写入sources.json。创建/修改时间不等于事件发生日期。'}
    save(Path(w)/'state'/f'{provider}-discovery.json',result);return result

def fetch(provider,item,runner=None,import_root=None):
    url=clean_url(item['url']);host=urlparse(url).hostname or '';path=urlparse(url).path
    if provider=='feishu':
        if not (host.endswith('.feishu.cn') or host.endswith('.larksuite.com') or host.endswith('.larkoffice.com')):raise PlatformError('不是支持的飞书/Lark域名')
        if not re.match(r'^/(docx|wiki)/[^/]+',path):raise PlatformError('当前自动适配仅支持飞书Docx/Wiki正文；表格请导出或通过官方表格Skill读成带位置的资料包')
        data=run(provider,['docs','+fetch','--doc',url,'--doc-format','markdown','--detail','with-ids','--as','user','--format','json'],runner)
        doc=member(data,['document'],data)
        content=member(doc,['content','markdown'])
        if not isinstance(content,str) or not content.strip():raise PlatformError('没有取得完整文档正文')
        if '<fragment' in content or '<excerpt' in content:raise PlatformError('返回节选，需要完整正文，未将片段标为已完成')
        return lines(content),member(doc,['title','name'],item.get('title',path))
    if provider=='dingtalk':
        if host!='alidocs.dingtalk.com' or not path.startswith('/i/nodes/'):raise PlatformError('当前钉钉自动适配支持/i/nodes/在线文字文档。旧链接、听记或表格请由官方dws技能转为资料包')
        data=run(provider,['doc','read','--node',url,'--format','json'],runner)
        content=data if isinstance(data,str) else member(data,['content','markdown','text','documentContent'])
        if isinstance(content,dict):content=member(content,['content','markdown','text'])
        if not isinstance(content,str) or not content.strip():raise PlatformError('钉钉返回体未识别到正文，需按实际schema更新，未当作成功')
        if isinstance(data,dict) and member(data,['has_more','hasMore','truncated'],False):raise PlatformError('正文尚未完整返回，请补齐分页后导入')
        return lines(content),item.get('title',path)
    if not (host=='doc.weixin.qq.com' or host=='page.weixin.qq.com'):raise PlatformError('不是支持的企微文档域名')
    parts=path.strip('/').split('/')
    if len(parts)<2:raise PlatformError('无法识别文档类型')
    kind,ident=parts[:2]
    if kind=='doc':
        data=run(provider,['doc','contents','get','--json',json.dumps({'docid':ident,'content_type':'markdown'})],runner)
        content=member(data,['content'])
        if not content and data.get('file_path'):
            # Large CLI bodies may point to disk. Only explicitly selected directories may be read.
            p=Path(data['file_path']).resolve()
            if not import_root or not p.is_relative_to(Path(import_root).resolve()):raise PlatformError('长文档写入本地文件；请设置cli_output_dir为该CLI受信输出目录后重试')
            content=p.read_text(encoding='utf-8')
        if not isinstance(content,str) or not content.strip():raise PlatformError('企微未返回正文')
        return lines(content),member(data,['name'],item.get('title',ident))
    if kind=='smartpage':
        data=run(provider,['smartpage','pages','get','--json',json.dumps({'docid':ident})],runner)
        units=[];pages=data.get('pages',[])
        if not pages:raise PlatformError('智能文档没有页面')
        for p in pages:
            pid=p.get('page_id')
            if not pid:raise PlatformError('智能文档页面缺少定位')
            detail=run(provider,['smartpage','pages','get','--json',json.dumps({'docid':ident,'page_id':pid,'content_type':'markdown'})],runner)
            dp=detail.get('pages',[])
            if not dp:raise PlatformError('页面正文读取失败')
            body=dp[0].get('content_file_inner')
            if not body and dp[0].get('file_path'):
                f=Path(dp[0]['file_path']).resolve()
                if not import_root or not f.is_relative_to(Path(import_root).resolve()):raise PlatformError('页面正文路径不在cli_output_dir')
                body=f.read_text(encoding='utf-8')
            if not isinstance(body,str):raise PlatformError('页面未返回正文')
            units+=lines(body,'PAGE-'+str(pid)+'-L')
        return units,data.get('doc_title',item.get('title',ident))
    raise PlatformError('该企微文档类型尚无正文适配，请导出本地文件；搜索命中不算读取成功')

def sync(w,config,runner=None):
    providers=config.get('providers',[]);report={'at':now(),'read':[],'failed':[],'mode':'fixture' if runner else 'live','complete_for_selection':True}
    if not providers:raise PlatformError('先选择平台及具体文档，再同步；未选择来源不能标为读取成功')
    for provider_config in providers:
        provider=provider_config['provider']
        if provider not in BINS:raise PlatformError('未知平台')
        selected=provider_config.get('documents',[])
        if len(selected)>30:raise PlatformError('单批最多30篇，分批同步')
        for item in selected:
            try:
                units,title=fetch(provider,item,runner,provider_config.get('cli_output_dir'))
                r=put_source(w,provider,clean_url(item['url']),title,units)
                report['read'].append({'provider':provider,'title':title,**r})
            except (PlatformError,OSError,subprocess.TimeoutExpired) as e:
                report['complete_for_selection']=False;report['failed'].append({'provider':provider,'title':item.get('title','所选文档'),'error':str(e),'category':getattr(e,'category','read_failed')})
                with connect(w) as db:
                    sid='S'+digest([provider,clean_url(item['url'])])[:12]
                    db.execute('UPDATE sources SET active=0 WHERE id=?',(sid,))
    with connect(w) as db:event(db,'platform_sync',report)
    save(Path(w)/'state/last-platform-sync.json',report);packet(w);return report

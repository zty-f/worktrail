"""Read-only CLI login diagnostics. Never install, start OAuth, or expose raw auth output. Official CLIs may refresh stored credentials."""
import json,re,shutil,subprocess

AUTH_COMMANDS={'feishu':['lark-cli','auth','status','--json'],'dingtalk':['dws','auth','status','--format','json'],'wecom':['wecom-cli','auth','show','--status']}
GUIDES={'feishu':'references/setup-feishu.md','dingtalk':'references/setup-dingtalk.md','wecom':'references/setup-wecom.md'}

def classify_error(payload):
    raw=json.dumps(payload,ensure_ascii=False) if not isinstance(payload,str) else payload
    text=raw.lower()
    rules=[
        ('credential_repair',r'ciphertext_key_mismatch|local_state_requires_repair|local_state_unreadable'),
        ('organization_blocked',r'组织.{0,20}(?:未开启|未开通)|cli.{0,16}访问.{0,10}(?:关闭|未开启)|organization.{0,15}(?:disabled|blocked)'),
        ('missing_scope',r'missing_scopes|insufficient_scope|scope.{0,16}(?:missing|denied)|缺少.{0,12}(?:scope|权限范围)'),
        ('login_required',r'unauthorized|not logged|未登录|未授权|auth_token_expired|user_token_illegal|token.{0,15}(?:expired|invalid)|authentication_required'),
        ('access_denied',r'forbidden|permission.denied|access.denied|no authority|权限不足|无权限|没有权限'),
        ('network_timeout',r'timed?\s*out|timeout|超时|connection refused|certificate|tls|ssl'),
        ('unsupported_cli',r'unknown.flag|unknown.command|unknown runtime schema|unknown option|unrecognized argument'),
        ('configuration_required',r'config.{0,15}(?:missing|not found|init)|未配置|缺少.{0,10}应用'),
    ]
    hints={'credential_repair':'参照平台指南修复凭证存储，不自动重置全部账号。','organization_blocked':'由用户在官方页面申请组织CLI访问，管理员批准后重试。','missing_scope':'核对缺少的只读scope，完成应用审批及用户重新授权。','login_required':'按平台指南重新登录，保留新授权流程直到退出，再验证状态。','access_denied':'核对登录账号、应用scope和该文档的分享权限；不自动改权限。','network_timeout':'检查网络、系统证书和代理；不关闭TLS验证，不把网络错误当作未登录。','unsupported_cli':'查看当前--help及官方版本；先核对命令差异。','configuration_required':'先完成该平台应用或凭证配置，再做用户登录。','unknown_error':'错误类型尚不明确。按平台排障指南在本机核对，不输出原始认证回包。'}
    category=next((kind for kind,pattern in rules if re.search(pattern,text)),'unknown_error')
    return {'category':category,'hint':hints[category]}

def auth_check(provider,runner=None):
    if provider not in AUTH_COMMANDS:raise ValueError('未知平台')
    args=AUTH_COMMANDS[provider]
    result={'provider':provider,'guide':GUIDES[provider],'authenticated':None,'document_permission':'未验证；需读取一篇用户选定文档才能确认','raw_credentials_exposed':False}
    if runner is None and not shutil.which(args[0]):return {**result,'ok':False,'state':'not_installed','hint':'先按指南安装所选平台CLI；其他平台无需安装。'}
    try:
        response=runner(args) if runner else subprocess.run(args,capture_output=True,text=True,timeout=30,shell=False)
    except (OSError,subprocess.TimeoutExpired):return {**result,'ok':False,'state':'diagnostic_failed','hint':'状态查询未完成；不能判定未登录。检查网络或凭证锁后再查。'}
    raw=response.stdout.strip();parsed=None
    if provider=='wecom' and response.returncode==0 and raw in {'authorized','unauthorized'}:
        authenticated=raw=='authorized'
        return {**result,'ok':True,'authenticated':authenticated,'state':'authenticated' if authenticated else 'login_required'}
    try:parsed=json.loads(raw)
    except (json.JSONDecodeError,TypeError):pass
    if response.returncode!=0:
        error=classify_error(response.stderr or raw)
        return {**result,'ok':False,'state':error['category'],'hint':error['hint']}
    if not isinstance(parsed,dict):return {**result,'ok':False,'state':'unknown_response','hint':'未识别登录状态，不能把命令成功当成登录成功。请在本机参照当前CLI帮助核对。'}
    data=parsed.get('data',parsed.get('body',parsed))
    if not isinstance(data,dict):return {**result,'ok':False,'state':'unknown_response'}
    if parsed.get('ok') is False or parsed.get('success') is False:
        error=classify_error(parsed);return {**result,'ok':False,'state':error['category'],'hint':error['hint']}
    authenticated=None
    if provider=='dingtalk':
        if data.get('reason'):return {**result,'ok':False,'state':'indeterminate','hint':'本地凭证快照不可确定；参照钉钉指南核对修复，不直接判定未登录。'}
        if isinstance(data.get('authenticated'),bool):authenticated=data['authenticated']
    elif provider=='feishu':
        user=data.get('identities',{}).get('user',{}) if isinstance(data.get('identities'),dict) else {}
        if isinstance(user,dict) and isinstance(user.get('available'),bool):authenticated=user['available']
        elif data.get('identity') in {'user','bot','none'}:authenticated=data['identity']=='user'
        if data.get('verified') is False and data.get('identity')=='user':authenticated=False
    elif data.get('status') in {'authorized','unauthorized'}:authenticated=data['status']=='authorized'
    if authenticated is None:return {**result,'ok':False,'state':'unknown_response','hint':'输出结构不兼容，请按官方CLI帮助核对；不猜测登录状态。'}
    return {**result,'ok':True,'authenticated':authenticated,'state':'authenticated' if authenticated else 'login_required'}

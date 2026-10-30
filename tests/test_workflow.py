import copy,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prs_core import *
from prs_workflow import *
from prs_setup import auth_check,classify_error
from prs_outputs import build,verify
from create_demo import create

class SelectionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmpbase=tempfile.TemporaryDirectory();cls.fixture=Path(cls.tmpbase.name)/'fixture';create(cls.fixture)
 @classmethod
 def tearDownClass(cls):cls.tmpbase.cleanup()
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.w=Path(self.tmp.name)/'workspace';shutil.copytree(self.fixture,self.w)
 def tearDown(self):self.tmp.cleanup()
 def test_fresh_workspace_defaults_to_summary_only(self):
  w=Path(self.tmp.name)/'new';init_workspace(w);self.assertEqual(workflow(w)['outputs'],['summary']);self.assertEqual(workflow(w)['source']['local_folders'],[])
 def test_empty_workspace_cannot_be_reported_as_finished_summary(self):
  w=Path(self.tmp.name)/'empty';init_workspace(w)
  with self.assertRaises(ValueError):build(w)
  self.assertFalse((w/'output').exists())
 def test_interactive_choice_is_persisted(self):
  materials=Path(self.tmp.name)/'raw';materials.mkdir();replies=iter(['1',str(materials),'1,3'])
  configure(self.w,interactive=True,input_fn=lambda _:next(replies));p=workflow(self.w);self.assertEqual(p['outputs'],['summary','evidence']);self.assertEqual(p['source']['local_folders'],[str(materials.resolve())])
 def test_invalid_choice_does_not_modify_previous_configuration(self):
  before=(self.w/'workflow.json').read_bytes()
  with self.assertRaises(ValueError):configure(self.w,outputs='invalid')
  self.assertEqual(before,(self.w/'workflow.json').read_bytes())
 def test_workspace_cannot_be_inside_material_directory(self):
  with self.assertRaises(ValueError):configure(self.w,source='local',folders=[self.tmp.name])
 def test_selected_platforms_are_not_implicitly_expanded(self):
  p=Path(self.tmp.name)/'sources.json';save(p,{'providers':[{'provider':'wecom','documents':[{'url':'https://doc.weixin.qq.com/doc/test'}]}]})
  with self.assertRaises(ValueError):configure(self.w,source='feishu',sources_config=str(p))
 def test_scope_is_checked_before_any_collection(self):
  p=Path(self.tmp.name)/'sources.json';save(p,{'providers':[{'provider':'dingtalk','documents':[{'url':'https://alidocs.dingtalk.com/i/nodes/test'}]}]})
  configure(self.w,source='dingtalk',sources_config=str(p));save(p,{'providers':[{'provider':'feishu','documents':[{'url':'https://demo.feishu.cn/docx/t'}]}]})
  with patch('prs_platforms.sync',side_effect=AssertionError('must not read')):
   with self.assertRaises(ValueError):collect(self.w)
 def test_each_platform_routes_only_to_its_selected_config(self):
  for provider in ['feishu','dingtalk','wecom']:
   p=Path(self.tmp.name)/(provider+'.json');config={'providers':[{'provider':provider,'documents':[{'url':'https://example.test/selected'}]}]};save(p,config);configure(self.w,source=provider,sources_config=str(p))
   with patch('prs_platforms.sync',return_value={'read':[],'failed':[]}) as run:
    result=collect(self.w);self.assertTrue(result['ok']);self.assertEqual(run.call_args.args[1],config)
 def test_local_collection_disables_out_of_selection_sources(self):
  raw=Path(self.tmp.name)/'new-materials';raw.mkdir();(raw/'note.md').write_text('仅选定的新资料')
  put_source(self.w,'manual','conversation:clarification','本人补充',[{'unit':'N1','text':'本人补充参与范围'}])
  configure(self.w,source='local',folders=[str(raw)]);self.assertTrue(collect(self.w)['ok'])
  active=[s for s in packet(self.w)['sources'] if s['active']];self.assertEqual(len(active),2);self.assertEqual({s['provider'] for s in active},{'local','manual'})
 def test_mixed_collects_selected_local_and_platform(self):
  raw=Path(self.tmp.name)/'mixed-local';raw.mkdir();(raw/'note.md').write_text('本地补充')
  p=Path(self.tmp.name)/'mixed.json';save(p,{'providers':[{'provider':'wecom','documents':[{'url':'https://doc.weixin.qq.com/doc/t'}]}]});configure(self.w,source='mixed',folders=[str(raw)],sources_config=str(p))
  with patch('prs_platforms.sync',return_value={'read':[],'failed':[]}) as run:
   r=collect(self.w);self.assertEqual(len(r['reports']),2);run.assert_called_once()
 def test_summary_runs_without_document_or_presentation_runtime(self):
  configure(self.w,outputs='summary')
  with patch('prs_outputs.runtime',side_effect=AssertionError('Node not needed')),patch('prs_outputs.render_document',side_effect=AssertionError('PDF not requested')),patch('prs_outputs.docx',side_effect=AssertionError('Word not requested')),patch('prs_outputs.make_deck',side_effect=AssertionError('PPT not requested')):
   result=build(self.w)
  self.assertEqual(result['slides'],0);self.assertEqual({p.name for p in (self.w/'output').iterdir()},{'工作总结.md','manifest.json'});self.assertIn('37.5%',(self.w/'output/工作总结.md').read_text());self.assertTrue(verify(self.w)['ok']);self.assertFalse(verify(self.w)['editable_pptx_created'])
 def test_evidence_only_has_no_missing_download_links(self):
  with patch('prs_outputs.runtime',side_effect=AssertionError('Node not needed')),patch('prs_outputs.docx',side_effect=AssertionError('Word not needed')):
   build(self.w,outputs='evidence')
  text=(self.w/'output/index.html').read_text();self.assertNotIn(' download>',text);self.assertFalse((self.w/'output/汇报文档.docx').exists());self.assertTrue(verify(self.w)['ok'])
 def test_plain_outputs_can_be_selected_individually(self):
  for output,filename in [('report','汇报底稿.md'),('self-eval','绩效自评草稿.txt'),('speaker-notes','逐页讲述提示.txt')]:
   with patch('prs_outputs.runtime',side_effect=AssertionError('Node not needed')),patch('prs_outputs.docx',side_effect=AssertionError('Word not needed')):build(self.w,outputs=output)
   self.assertEqual({p.name for p in (self.w/'output').iterdir()},{filename,'manifest.json'});self.assertTrue(verify(self.w)['ok'])
 def test_pdf_only_keeps_intermediate_word_private(self):
  def render(folder,qa): (Path(folder)/'汇报文档.pdf').write_bytes(b'%PDF-1.7 test-routing-only')
  with patch('prs_outputs.render_document',side_effect=render),patch('prs_outputs.runtime',side_effect=AssertionError('PPT not needed')):build(self.w,outputs='pdf')
  self.assertEqual({p.name for p in (self.w/'output').iterdir()},{'汇报文档.pdf','manifest.json'});self.assertTrue(verify(self.w)['ok'])
 def test_word_only_does_not_export_pdf(self):
  with patch('prs_outputs.render_document') as renderer:build(self.w,outputs='docx')
  renderer.assert_called_once();self.assertEqual({p.name for p in (self.w/'output').iterdir()},{'汇报文档.docx','manifest.json'})
 def test_ppt_only_does_not_create_word_or_pdf(self):
  def export(args,**kwargs): (Path(args[-1])/'output/汇报演示.pptx').write_bytes(b'unit-routing-placeholder')
  with patch('prs_outputs.subprocess.run',side_effect=export),patch('prs_outputs.render_document',side_effect=AssertionError('PDF not requested')),patch('prs_outputs.docx',side_effect=AssertionError('Word not requested')):build(self.w,outputs='pptx')
  self.assertEqual({p.name for p in (self.w/'output').iterdir()},{'汇报演示.pptx','manifest.json'})
 def test_failed_selected_export_keeps_previous_success(self):
  build(self.w,outputs='summary');before=(self.w/'output/manifest.json').read_bytes()
  with patch('prs_outputs.render_document',side_effect=ValueError('renderer missing')):
   with self.assertRaises(ValueError):build(self.w,outputs='pdf')
  self.assertEqual(before,(self.w/'output/manifest.json').read_bytes());self.assertTrue(verify(self.w)['ok'])
 def test_workflow_change_invalidates_deliverable(self):
  configure(self.w,outputs='summary');build(self.w);configure(self.w,outputs='summary,evidence');self.assertFalse(verify(self.w)['ok'])

class AuthDiagnosticTests(unittest.TestCase):
 def response(self,stdout,code=0,stderr=''):
  return lambda argv:subprocess.CompletedProcess(argv,code,stdout if isinstance(stdout,str) else json.dumps(stdout),stderr)
 def test_wecom_exact_states(self):
  self.assertTrue(auth_check('wecom',self.response('authorized'))['authenticated']);self.assertFalse(auth_check('wecom',self.response('unauthorized'))['authenticated']);self.assertIsNone(auth_check('wecom',self.response('maybe authorized'))['authenticated'])
 def test_feishu_bot_is_not_user_login(self):
  self.assertFalse(auth_check('feishu',self.response({'identity':'bot','identities':{'user':{'available':False}}}))['authenticated'])
  self.assertTrue(auth_check('feishu',self.response({'identity':'user','identities':{'user':{'available':True}}}))['authenticated'])
 def test_dingtalk_indeterminate_is_not_reported_as_logged_out(self):
  r=auth_check('dingtalk',self.response({'success':True,'authenticated':False,'reason':'local_state_requires_repair'}));self.assertIsNone(r['authenticated']);self.assertEqual(r['state'],'indeterminate')
 def test_unknown_success_cannot_prove_login(self):
  self.assertIsNone(auth_check('dingtalk',self.response({'success':True}))['authenticated'])
 def test_status_output_never_returns_raw_credentials(self):
  r=auth_check('dingtalk',self.response({'success':True,'authenticated':True,'access_token':'TEST-SECRET-NOT-A-REAL-CREDENTIAL','refresh_token':'TEST-SECRET-NOT-A-REAL-CREDENTIAL'}));self.assertNotIn('TEST-SECRET',canonical(r));self.assertEqual(r['document_permission'].split('；')[0],'未验证')
 def test_failure_reports_action_without_raw_stderr(self):
  r=auth_check('feishu',self.response('',1,'missing_scopes private-secret-test'));self.assertEqual(r['state'],'missing_scope');self.assertNotIn('private-secret',canonical(r))
 def test_timeout_is_not_unauthenticated(self):
  def runner(_):raise subprocess.TimeoutExpired('auth status',30)
  r=auth_check('feishu',runner);self.assertIsNone(r['authenticated']);self.assertEqual(r['state'],'diagnostic_failed')
 def test_missing_cli_does_not_install(self):
  with patch('prs_setup.shutil.which',return_value=None),patch('prs_setup.subprocess.run',side_effect=AssertionError('no install or login')):self.assertEqual(auth_check('wecom')['state'],'not_installed')
 def test_permission_and_login_are_distinguished(self):
  self.assertEqual(classify_error({'error':'insufficient_scope'})['category'],'missing_scope');self.assertEqual(classify_error('AUTH_TOKEN_EXPIRED')['category'],'login_required');self.assertEqual(classify_error('document forbidden')['category'],'access_denied')
 def test_dingtalk_pat_exit_does_not_recommend_logging_in_again(self):
  from prs_platforms import run,PlatformError
  responses=[subprocess.CompletedProcess([],0,'help',''),subprocess.CompletedProcess([],4,'','PAT authorization private-test-secret')]
  with patch('prs_platforms.shutil.which',return_value='/fake/dws'),patch('prs_platforms.subprocess.run',side_effect=responses):
   with self.assertRaises(PlatformError) as caught:run('dingtalk',['doc','read','--node','https://alidocs.dingtalk.com/i/nodes/test','--format','json'])
  self.assertEqual(caught.exception.category,'behavior_authorization_required');self.assertNotIn('private-test-secret',str(caught.exception))

if __name__=='__main__':unittest.main()

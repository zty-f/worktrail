import copy,json,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prs_core import *
from prs_outputs import compose,make_deck,build_content
from prs_platforms import *
from create_demo import create

class ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=tempfile.TemporaryDirectory();cls.fixture=Path(cls.base.name)/'fixture';create(cls.fixture)
    @classmethod
    def tearDownClass(cls):cls.base.cleanup()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.w=Path(self.tmp.name)/'work';shutil.copytree(self.fixture,self.w)
        self.a=analyze(self.w);self.b=load(self.w/'brief.json');self.sm={s['id']:s for s in packet(self.w)['sources']};self.fm={f['id']:f for f in load(self.w/'facts.json')['facts']}
    def tearDown(self):self.tmp.cleanup()
    def test_personal_contribution_keeps_other_leader(self):
        a,r=compose(self.w);p=next(s for s in r['sections'] if s['id']=='P1');text=''.join(p['paragraphs'])
        self.assertIn('周岚负责项目整体推进',text);self.assertIn('团队完成',text);self.assertNotIn('我主导',text)
    def test_lead_cannot_be_borrowed_from_other_person(self):
        f=copy.deepcopy(self.fm['F01']);f['role_level']='lead';f['statement']='我主导项目'
        self.assertTrue(validate_fact(f,self.sm,self.b))
    def test_self_without_named_source_is_rejected(self):
        f=copy.deepcopy(self.fm['F05']);f['subject']='self';self.assertTrue(validate_fact(f,self.sm,self.b))
    def test_duplicate_is_merged_once(self):
        self.assertEqual(self.a['duplicates'],[{'kept':'F02','merged':'F03'}]);f=next(f for f in self.a['facts'] if f['id']=='F02');self.assertEqual(len(f['evidence']),2)
    def test_cross_period_excluded(self):self.assertIn('F07',self.a['outside_period']);self.assertNotIn('F07',{f['id'] for f in self.a['facts']})
    def test_unknown_event_date_is_not_placed_in_reporting_period(self):
        f=copy.deepcopy(self.fm['F02']);f.update(event_date=None,date_status='unknown',date_note='来源未记录完成时间')
        save(self.w/'undated.json',{'facts':[f]});import_facts(self.w,self.w/'undated.json')
        a=analyze(self.w);self.assertIn('F02',a['undated_facts']);self.assertNotIn('F02',{x['id'] for x in a['facts']});self.assertTrue(any('日期' in q['question'] for q in a['questions']))
        self.b['report_type']='evidence';save(self.w/'brief.json',self.b)
        a,r=compose(self.w);self.assertIn('F02',{x['id'] for x in a['facts']});self.assertIsNone(next(x for x in a['facts'] if x['id']=='F02')['event_date']);self.assertNotIn('None',canonical(r))
    def test_missing_date_cannot_silently_become_unknown(self):
        f=copy.deepcopy(self.fm['F02']);f.pop('event_date');self.assertTrue(validate_fact(f,self.sm,self.b))
    def test_real_evidence_page_is_not_labelled_as_mock(self):
        from prs_outputs import write_html
        self.b.update(report_type='evidence',disclosure='真实授权资料，仅核查所选范围。');save(self.w/'brief.json',self.b)
        a,r=compose(self.w);out=self.w/'real-html';out.mkdir();write_html(a,r,out)
        self.assertNotIn('所有案例人物、项目及数据均为模拟',(out/'index.html').read_text())
    def test_long_text_sections_are_paginated_in_deck(self):
        self.b['review_notes']=['原文已核查。'*15]*7;save(self.w/'brief.json',self.b)
        a,r=compose(self.w);deck=make_deck(a,r);self.assertTrue(any(s['title']=='工作复盘 续页' for s in deck['slides']))
    def test_curated_deck_requires_existing_facts_and_keeps_source_locations(self):
        self.b['presentation_outline']=[{'title':'所选工作','body':['参与范围'],'fact_ids':['F02']}];save(self.w/'brief.json',self.b)
        a,r=compose(self.w);deck=make_deck(a,r);self.assertEqual(len(deck['slides']),2);self.assertIn('F02',deck['slides'][1]['sources']);self.assertIn('版本',deck['slides'][1]['speaker_notes'])
        self.b['presentation_outline'][0]['fact_ids']=['UNKNOWN'];save(self.w/'brief.json',self.b)
        a,r=compose(self.w)
        with self.assertRaises(ValueError):make_deck(a,r)
    def test_unlaunched_project_keeps_preparation_and_pending_separate(self):
        p=next(p for p in self.a['projects'] if p['id']=='P3');self.assertIn('F11',p['self_facts']);self.assertIn('F12',p['ongoing_facts']);self.assertEqual(p['team_facts'],[])
    def test_conflicts_detected_before_confirmation(self):
        before=load(self.w/'qa/analysis-before-resolution.json');self.assertEqual(sum(c['status']=='unresolved' for c in before['conflicts']),2)
    def test_resolution_adopts_25_and_correct_relative_change(self):
        m=next(m for m in self.a['metrics'] if m['status']=='usable');self.assertEqual((m['baseline'],m['result'],m['change_pct']),(40,25,-37.5))
    def test_population_mismatch_not_used_as_full_cohort(self):
        pilot=next(m for m in self.a['metrics'] if '5个' in m['group'][2]);self.assertEqual(pilot['status'],'observed');self.assertEqual(pilot['result'],18);self.assertIsNone(pilot['change_pct'])
    def test_unresolved_number_withheld_from_achievement(self):
        _,r=compose(self.w);p=next(s for s in r['sections'] if s['id']=='P2');self.assertNotIn('60篇',''.join(p['paragraphs']));self.assertNotIn('48篇',''.join(p['paragraphs']))
    def test_goal_28_is_not_a_result(self):self.assertNotIn(28,[m.get('result') for m in self.a['metrics']])
    def test_missing_quote_is_rejected(self):
        f=copy.deepcopy(self.fm['F02']);f['evidence'][0]['quote']='用户从未说过的独立业绩';self.assertTrue(validate_fact(f,self.sm,self.b))
    def test_source_revision_invalidates_facts_and_decisions(self):
        s=next(s for s in self.sm.values() if s['title']=='12_工单指标导出.csv');units=copy.deepcopy(s['units']);units[0]['text']+=' 修订';put_source(self.w,s['provider'],s['locator'],s['title'],units)
        a=analyze(self.w);self.assertTrue(a['invalid_facts']);self.assertTrue(a['decision_errors'])
    def test_partial_source_failure_deactivates_cache(self):
        conf={'providers':[{'provider':'feishu','documents':[{'url':'https://demo.feishu.cn/docx/doc1','title':'项目'}]}]}
        sync(self.w,conf,lambda argv:{'ok':True,'data':{'document':{'content':'林知夏负责验收'}}})
        report=sync(self.w,conf,lambda argv:{'ok':False,'error':{'message':'denied'}})
        self.assertFalse(report['complete_for_selection']);self.assertEqual(next(s for s in packet(self.w)['sources'] if s['provider']=='feishu')['active'],0)
    def test_numeric_substring_does_not_validate(self):
        f=copy.deepcopy(self.fm['M01']);f['metric']['value']=4;self.assertTrue(validate_fact(f,self.sm,self.b))
    def test_invalid_selected_candidate_does_not_resolve(self):
        with connect(self.w) as db:db.execute('DELETE FROM decisions')
        a=analyze(self.w);c=next(c for c in a['conflicts'] if c['group'][0]=='平均处理时长')
        add_decision(self.w,{'id':'X','type':'metric_resolution','conflict_id':c['id'],'selected_fact_id':'F02','reason':'测试','reviewer':'测试','evidence':self.fm['M01']['evidence']})
        after=analyze(self.w);self.assertTrue(after['decision_errors']);self.assertEqual(next(x for x in after['conflicts'] if x['id']==c['id'])['status'],'unresolved')
    def test_decision_cannot_overwrite_audit(self):
        with self.assertRaises(ValueError):add_decision(self.w,load(self.w/'decisions/01_工单指标口径确认.json'))
    def test_stale_patch_is_not_silently_reused(self):
        add_decision(self.w,{'id':'X','type':'fact_patch','fact_id':'F02','expected_hash':'old','reason':'修正','reviewer':'本人','patch':{'statement':'新陈述'}})
        self.assertTrue(analyze(self.w)['decision_errors'])
    def test_reimport_does_not_duplicate_facts_or_erase_decisions(self):
        import_facts(self.w,self.w/'facts.json');a=analyze(self.w);self.assertEqual(len(a['facts']),18);self.assertIn('D01',a['applied_decisions'])
    def test_unchanged_source_does_not_create_revision(self):
        s=next(iter(self.sm.values()))
        with connect(self.w) as db:before=db.execute('SELECT count(*) FROM versions').fetchone()[0]
        put_source(self.w,s['provider'],s['locator'],s['title'],s['units'])
        with connect(self.w) as db:self.assertEqual(before,db.execute('SELECT count(*) FROM versions').fetchone()[0])
    def test_fact_patch_survives_report_rebuild(self):
        f=self.fm['F02'];add_decision(self.w,{'id':'X','type':'fact_patch','fact_id':f['id'],'expected_hash':digest(f),'reason':'本人修正文案','reviewer':'林知夏','patch':{'statement':'我整理需求说明和异常流程'}})
        self.assertEqual(next(f for f in analyze(self.w)['facts'] if f['id']=='F02')['statement'],'我整理需求说明和异常流程')
        self.assertEqual(next(f for f in analyze(self.w)['facts'] if f['id']=='F02')['statement'],'我整理需求说明和异常流程')
    def test_three_report_modes(self):
        for kind,title in [('halfyear','半年工作汇报'),('annual','年度绩效述职'),('probation','转正工作报告')]:
            self.b['report_type']=kind;save(self.w/'brief.json',self.b);_,r=compose(self.w);self.assertIn(title,r['title'])
    def test_company_rubric_used_in_deck(self):
        a,r=compose(self.w);p=make_deck(a,r);self.assertTrue(any('跨团队协作' in canonical(s) for s in p['slides']))
    def test_doc_and_deck_share_metric_values(self):
        a,r=compose(self.w);chart=next(s for s in make_deck(a,r)['slides'] if s['kind']=='chart');self.assertEqual(chart['values'],[40,25]);self.assertIn('37.5%',canonical(r))
    def test_resolution_owner_evidence_is_in_report_sources(self):
        from prs_outputs import reference_text
        self.assertIn('09_指标负责人确认.md',reference_text(self.a,['M03']))
    def test_html_escapes_source_script(self):
        from prs_outputs import write_html
        a,r=compose(self.w);a['facts'][0]['statement']='<script>alert(1)</script>';out=self.w/'html';out.mkdir();write_html(a,r,out);text=(out/'index.html').read_text();self.assertIn('&lt;script&gt;alert',text);self.assertNotIn('<script>alert(1)',text)
    def test_no_conflict_workspace_builds_content(self):
        with connect(self.w) as db:
            db.execute('DELETE FROM decisions');db.execute("DELETE FROM facts WHERE id IN ('M02','M05')")
        out=self.w/'no-conflict';out.mkdir();a,r=build_content(self.w,out)
        self.assertEqual(a['conflicts'],[]);self.assertTrue((out/'汇报文档.docx').exists())
    def test_inactive_sources_are_not_exported(self):
        sid=next(s['id'] for s in self.sm.values() if s['title']=='11_协作反馈.md')
        with connect(self.w) as db:db.execute('UPDATE sources SET active=0 WHERE id=?',(sid,))
        self.assertNotIn(sid,{s['id'] for s in analyze(self.w)['sources']})
    def test_standalone_metric_does_not_invent_percentage(self):
        m=next(m for m in self.a['metrics'] if m['status']=='observed')
        self.assertIsNone(m['change_pct']);self.assertIn('不计算改善幅度',metric_text(m))

class PlatformTests(unittest.TestCase):
    def test_rotating_signed_asset_queries_do_not_create_new_evidence_version(self):
        first='正文\n![图](https://assets.example/a.png?Expires=1&OSSAccessKeyId=temporary&Signature=one)\n后文'
        second=first.replace('Expires=1','Expires=2').replace('Signature=one','Signature=two')
        a=lines(first);b=lines(second);self.assertEqual(a,b);self.assertEqual(a[-1]['unit'],'L3');self.assertNotIn('temporary',canonical(a));self.assertNotIn('Signature',canonical(a))
        self.assertIn('dentryKey=real',normalize_body('https://alidocs.dingtalk.com/document/preview?dentryKey=real&type=d'))
    def test_dws_body_envelope(self):
        units,_=fetch('dingtalk',{'url':'https://alidocs.dingtalk.com/i/nodes/test'},lambda a:{'success':True,'body':{'content':'完整文档正文'}})
        self.assertEqual(units[0]['text'],'完整文档正文')
    def test_nested_body_error_is_rejected(self):
        with self.assertRaises(PlatformError):unwrap({'success':True,'body':{'success':False,'message':'denied'}})
    def test_unknown_search_shape_is_not_empty_success(self):
        with self.assertRaises(PlatformError):search_page('dingtalk','测试',runner=lambda a:{'success':True,'body':{'unknownResults':[]}})
    def test_dws_search_native_identifiers(self):
        items,more,_=search_page('dingtalk','测试',runner=lambda a:{'success':True,'body':{'items':[{'fileId':'real-returned-id','name':'测试文档','docUrl':'https://alidocs.dingtalk.com/i/nodes/test'}],'hasMore':False}})
        self.assertEqual(items[0]['id'],'real-returned-id');self.assertEqual(items[0]['url'],'https://alidocs.dingtalk.com/i/nodes/test');self.assertFalse(more)
    def test_feishu_user_identity_and_body(self):
        calls=[]
        def runner(argv):calls.append(argv);return {'ok':True,'data':{'document':{'content':'正文，不是搜索高亮','title':'文档'}}}
        units,_=fetch('feishu',{'url':'https://demo.feishu.cn/docx/t'},runner);self.assertEqual(units[0]['text'],'正文，不是搜索高亮');self.assertIn('--as',calls[0]);self.assertIn('user',calls[0])
    def test_dingtalk_document_body(self):
        units,_=fetch('dingtalk',{'url':'https://alidocs.dingtalk.com/i/nodes/abc'},lambda a:{'success':True,'data':{'content':'工单正文'}});self.assertEqual(units[0]['text'],'工单正文')
    def test_wecom_doc_body(self):
        units,_=fetch('wecom',{'url':'https://doc.weixin.qq.com/doc/abc'},lambda a:{'errcode':0,'content':'文档正文'});self.assertEqual(units[0]['text'],'文档正文')
    def test_wecom_smartpage_reads_each_page_not_just_tree(self):
        calls=[]
        def runner(argv):
            body=json.loads(argv[-1]);calls.append(body)
            return {'pages':[{'page_id':'p1'}],'doc_title':'智能文档'} if 'page_id' not in body else {'pages':[{'page_id':'p1','content_file_inner':'页面正文'}]}
        units,_=fetch('wecom',{'url':'https://doc.weixin.qq.com/smartpage/a1_demo'},runner);self.assertEqual(len(calls),2);self.assertIn('页面正文',units[0]['text'])
    def test_unsupported_type_is_explicit(self):
        with self.assertRaises(PlatformError):fetch('wecom',{'url':'https://doc.weixin.qq.com/ppt/abc'},lambda a:{})
    def test_search_does_not_adopt_highlights_as_evidence(self):
        with tempfile.TemporaryDirectory() as t:
            result=discover(t,'wecom','项目',runner=lambda a:{'docs':[{'docid':'x','doc_name':'项目','url':'https://doc.weixin.qq.com/doc/x','text_highlight':['高亮摘要']}],'has_more':False})
            self.assertNotIn('高亮摘要',canonical(result));self.assertFalse((Path(t)/'state/ledger.sqlite3').exists())
    def test_search_pages_report_incomplete_at_cap(self):
        with tempfile.TemporaryDirectory() as t:
            counter=[0]
            def runner(a):counter[0]+=1;return {'ok':True,'data':{'items':[{'url':'https://demo.feishu.cn/docx/'+str(counter[0]),'title':'项目'}],'has_more':True,'page_token':str(counter[0])}}
            result=discover(t,'feishu','项目',max_pages=2,runner=runner);self.assertEqual(len(result['candidates']),2);self.assertFalse(result['complete_for_query'])
    def test_business_error_is_not_http_success(self):
        with self.assertRaises(PlatformError):unwrap({'errcode':48002,'errmsg':'denied'})
    def test_unknown_body_does_not_count_as_success(self):
        with self.assertRaises(PlatformError):fetch('dingtalk',{'url':'https://alidocs.dingtalk.com/i/nodes/a'},lambda a:{'data':{'title':'只有标题'}})
    def test_write_command_not_whitelisted(self):
        with self.assertRaises(PlatformError):run('wecom',['doc','delete'],lambda a:{})
    def test_untrusted_response_file_path_is_not_read(self):
        with self.assertRaises(PlatformError):fetch('wecom',{'url':'https://doc.weixin.qq.com/doc/x'},lambda a:{'file_path':'/etc/passwd'})
    def test_shell_metacharacters_remain_one_argument(self):
        seen=[]
        def runner(a):seen.append(a);return {'items':[],'has_more':False}
        search_page('dingtalk','$(touch /tmp/should-not-run)',runner=runner);self.assertIn('$(touch /tmp/should-not-run)',seen[0])

if __name__=='__main__':unittest.main()

#!/usr/bin/env python3
"""Standard-library-only fictional corpus for selected-output onboarding examples."""
import argparse
from pathlib import Path
from prs_core import init_workspace,save,packet,load,import_facts
from prs_workflow import configure,collect

def create(w,outputs='summary'):
 w=Path(w).resolve();init_workspace(w);raw=w/'materials';raw.mkdir()
 brief={'schema_version':'1.0','person':{'name':'林知夏','role':'产品经理'},'report_type':'halfyear','period':{'start':'2026-01-01','end':'2026-06-30','label':'2026年上半年'},'minutes':5,'disclosure':'轻量模拟案例。人物、项目、数据均为虚构；只演示所选产出，不使用真实企业资料。','projects':[{'id':'P1','name':'售后工单改版','rubric':['R1','R2']}],'rubric':[{'id':'R1','name':'业务结果'},{'id':'R2','name':'协作与交付'}]};save(w/'brief.json',brief)
 docs={
 '01_分工.md':'# 项目分工\n2026-01-08 项目由周岚负责整体推进；林知夏参与需求梳理和业务验收，不负责研发排期及总体交付。\n',
 '02_交付.md':'# 阶段交付\n2026-03-20 林知夏完成需求说明与业务验收，整理上线问题清单。\n2026-03-20 团队完成售后工单改版上线。\n',
 '03_指标.md':'# 同口径指标\n2026-01-30 全量已结售后工单平均处理时长40分钟，包含退回重开单，窗口为2026-01-01至2026-01-31。\n2026-06-30 全量已结售后工单平均处理时长25分钟，包含退回重开单，窗口为2026-04-01至2026-06-30。\n这些是团队前后观察数据，不能据此证明个人独立因果贡献。\n'}
 for name,text in docs.items():(raw/name).write_text(text,encoding='utf-8')
 configure(w,source='local',folders=[str(raw)],outputs=outputs);collect(w)
 sources={s['title']:s for s in packet(w)['sources']};facts=[]
 def add(fid,kind,subject,day,text,title,unit,**extra):
  s=sources[title];quote=next(u['text'] for u in s['units'] if u['unit']==unit)
  facts.append({'id':fid,'project_id':'P1','kind':kind,'subject':subject,'event_date':day,'status':'done','statement':text,'role_level':'contributor','evidence':[{'source_id':s['id'],'version':s['version'],'unit':unit,'quote':quote}],'review':{'status':'checked','reviewer':'轻量虚构案例预设核对','note':'只用于模拟测试；真实资料需由Agent重新理解核对。'},**extra})
 add('F01','role','self','2026-01-08','我参与需求梳理与业务验收，周岚负责整体推进','01_分工.md','L2')
 add('F02','action','self','2026-03-20','我完成需求说明、业务验收与上线问题清单','02_交付.md','L2')
 add('F03','outcome','team','2026-03-20','团队完成工单改版上线','02_交付.md','L3')
 for fid,stage,value,day,window,unit in [('M01','baseline',40,'2026-01-30','2026-01-01至2026-01-31','L2'),('M02','result',25,'2026-06-30','2026-04-01至2026-06-30','L3')]:
  add(fid,'metric','team',day,'平均处理时长观测记录','03_指标.md',unit,metric={'key':'平均处理时长','stage':stage,'value':value,'unit':'分钟','population':'全量已结售后工单 含退回重开单','comparison_id':'ticket-H1','window':window,'direction':'lower'})
 save(w/'facts.json',{'schema_version':'1.0','facts':facts});import_facts(w,w/'facts.json')
 return {'workspace':str(w),'sources':3,'facts':5,'outputs':load(w/'workflow.json')['outputs'],'next':'运行review.py build；这份模拟夹具不使用第三方Python包。'}

if __name__=='__main__':
 import json
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('workspace',type=Path);p.add_argument('--outputs',default='summary');a=p.parse_args();print(json.dumps(create(a.workspace,a.outputs),ensure_ascii=False,indent=2))

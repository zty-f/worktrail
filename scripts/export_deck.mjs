#!/usr/bin/env node
// Native editable objects authored with the Codex presentation runtime.
import fs from 'node:fs/promises';
import {existsSync,readdirSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const [planFile,runArg]=process.argv.slice(2),run=path.resolve(runArg),out=path.join(run,'output'),qa=path.join(run,'qa');
await fs.mkdir(qa,{recursive:true});
const modules=process.env.PRS_NODE_MODULES||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
process.env.RUNTIME_NODE_MODULES=modules;
process.env.RUNTIME_NODE=process.execPath;
const require=createRequire(path.join(modules,'package.json'));
const {Presentation,PresentationFile,FileBlob}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
function skillDir(){if(process.env.PRS_PRESENTATIONS_SKILL)return process.env.PRS_PRESENTATIONS_SKILL;const base=path.join(os.homedir(),'.codex/plugins/cache/openai-primary-runtime/presentations');const version=readdirSync(base).filter(x=>existsSync(path.join(base,x,'skills/presentations/container_tools/artifact_tool_utils.mjs'))).sort().at(-1);if(!version)throw Error('缺少Codex演示文稿校验运行时');return path.join(base,version,'skills/presentations');}
const skill=skillDir();
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const plan=JSON.parse(await fs.readFile(planFile,'utf8')),font=plan.font,ink='#172F44',muted='#566779',blue='#236B91';
const p=Presentation.create({slideSize:{width:1280,height:720}});
const tableOwners=[],chartOwners=[];
function text(s,value,x,y,w,h,size=30,color=ink,bold=false,name='body'){
 const shape=s.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=value;shape.text.style={typeface:font,fontSize:size,color,bold,verticalAlignment:'top',autoFit:'none',wrap:'square',insets:0};return shape;
}
for(const item of plan.slides){
 const s=p.slides.add();s.background.fill='#FFFFFF';
 if(item.kind==='cover'){
  text(s,plan.cover_label||'个人工作述职',70,70,1120,35,22,muted);
  text(s,item.title,70,175,1140,160,62,ink,true,'title');
  text(s,item.subtitle,74,380,1100,55,30);
  text(s,item.body.filter(Boolean).join('\n\n'),74,470,1100,120,23,muted);
 }else{
  text(s,String(item.number).padStart(2,'0')+'  '+plan.disclosure.split('。')[0],70,32,1140,28,17,muted);
  text(s,item.title,70,92,1140,90,46,ink,true,'title');
  if(item.kind==='table'){
   const rows=item.values.length,heights=Math.min(435,Math.max(250,rows*76));
   const t=s.tables.add({rows,columns:item.values[0].length,left:70,top:205,width:1140,height:heights,columnWidths:item.widths,values:item.values});
   t.borders.assign({style:'solid',fill:'#D5DFE7',width:1});
   for(let r=0;r<rows;r++)for(let c=0;c<item.values[0].length;c++){
    const cell=t.getCell(r,c);cell.fill=r===0?'#E7EDF2':(r%2?'#FFFFFF':'#F6F8FA');
    cell.text.style={typeface:font,fontSize:item.title.includes('证据索引')?23:25,color:ink,bold:r===0,verticalAlignment:'middle',wrap:'square',insets:12};
   }
   tableOwners.push(item.number);
  }else if(item.kind==='chart'){
   const chart=s.charts.add('bar',{position:{left:70,top:205,width:690,height:390},categories:item.categories,series:[{name:item.unit,values:item.values,fill:blue}],hasLegend:false,barOptions:{direction:'column',grouping:'clustered',gapWidth:150},dataLabels:{showValue:true,position:'outEnd',textStyle:{typeface:font,fontSize:26}},xAxis:{textStyle:{typeface:font,fontSize:23}},yAxis:{minimumScale:Math.min(0,Math.floor(Math.min(...item.values)*1.2/10)*10),maximumScale:Math.max(10,Math.ceil(Math.max(...item.values)*1.2/10)*10),textStyle:{typeface:font,fontSize:20},numberFormatCode:'0',majorGridlines:{fill:'#DEE5EA',width:1,style:'solid'}},chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF'});
   applyPresentationChartFont(chart,{fontFamily:font});
   text(s,'单位 '+item.unit,90,190,500,30,20,muted);
   text(s,`${item.values[0]} ${item.unit}${item.values[1]<item.values[0]?'降至':'变为'} ${item.values[1]} ${item.unit}`,825,240,365,65,29);
   text(s,item.change_pct===null?'基线为0，不计算相对变化':`较基线${item.change_pct<0?'下降':'变化'} ${Math.abs(item.change_pct)}%`,825,315,365,65,30,ink,true);
   text(s,'统计范围\n'+item.population,825,405,365,90,24);
   text(s,'基线 '+item.baseline_window+'\n观察 '+item.result_window,825,525,365,88,18,muted);
   chartOwners.push(item.number);
  }else{
   let y=205;
   for(const para of item.body){
    const lineCount=Math.max(1,Math.ceil(para.length/39));const h=Math.max(70,lineCount*43+14);
    if(y+h>625)throw Error('正文过多，需拆页 '+item.title);
    text(s,para,74,y,1125,h,30);y+=h+22;
   }
  }
  const refs=item.sources.split('\n').filter(Boolean).slice(0,2).join('；');
  text(s,refs.length>119?refs.slice(0,116)+'…':refs,74,657,1090,38,14,muted);
 }
 text(s,String(item.number).padStart(2,'0'),1190,662,45,25,16,muted);
 s.speakerNotes.text=item.speaker_notes;
}
for(const [i,s] of p.slides.items.entries()){
 const png=await p.export({slide:s,format:'png',scale:1});await fs.writeFile(path.join(qa,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const montage=await p.export({format:'webp',montage:true});await fs.writeFile(path.join(qa,'deck-montage.webp'),new Uint8Array(await montage.arrayBuffer()));
const candidate=path.join(run,'candidate.pptx');await (await PresentationFile.exportPptx(p)).save(candidate);
await finalizePresentation({workspaceDir:run,candidatePath:candidate,finalPath:path.join(out,'汇报演示.pptx'),pythonExecutable:process.env.PRS_PYTHON||'python3',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],explicitTotalSlideCount:plan.slides.length,requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:chartOwners,materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,receiptPath:path.join(qa,'pptx-validation.json')});
const finalDeck=await PresentationFile.importPptx(await FileBlob.load(path.join(out,'汇报演示.pptx')));
for(const [i,s] of finalDeck.slides.items.entries()){
 const png=await finalDeck.export({slide:s,format:'png',scale:1});await fs.writeFile(path.join(qa,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const finalMontage=await finalDeck.export({format:'webp',montage:true});await fs.writeFile(path.join(qa,'deck-montage.webp'),new Uint8Array(await finalMontage.arrayBuffer()));
await fs.writeFile(path.join(qa,'editability.json'),JSON.stringify({nativeText:true,nativeTables:tableOwners,nativeCharts:chartOwners,slideCount:plan.slides.length,font,applicationTest:'未在PowerPoint/WPS实机中测试；已由Artifact Tool导入和渲染。'},null,2));
console.log(JSON.stringify({pptx:path.join(out,'汇报演示.pptx'),slides:plan.slides.length,tableOwners,chartOwners}));

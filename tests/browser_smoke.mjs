import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const project=path.resolve(process.argv[2]||'examples/halfyear-demo'),out=path.join(project,'output'),qa=path.join(project,'qa');await fs.mkdir(qa,{recursive:true});
const modules=process.env.PRS_NODE_MODULES||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
const {chromium}=createRequire(path.join(modules,'package.json'))('playwright');
const data=JSON.parse(await fs.readFile(path.join(out,'analysis.json'),'utf8')),passed=[],errors=[];
const check=(name,value)=>{assert.ok(value,name);passed.push(name);};
const server=http.createServer(async(req,res)=>{try{const file=path.resolve(out,'.'+decodeURIComponent(new URL(req.url,'http://local').pathname==='/'?'/index.html':new URL(req.url,'http://local').pathname));if(!file.startsWith(out+path.sep))throw Error();const buf=await fs.readFile(file);res.setHeader('content-type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.pdf')?'application/pdf':'application/octet-stream');res.end(buf);}catch{res.statusCode=404;res.end('missing');}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=`http://127.0.0.1:${server.address().port}`;let browser;
try{
 browser=await chromium.launch({...process.env.PRS_CHROME?{executablePath:process.env.PRS_CHROME}:{channel:'chrome'},headless:true});
 const ctx=await browser.newContext({viewport:{width:1440,height:1000}}),page=await ctx.newPage();page.on('pageerror',e=>errors.push(e.message));await page.goto(base);
 check('all analyzed facts displayed',await page.locator('#facts article:visible').count()===data.facts.length);
 check('one resolved and one unresolved conflict visible',await page.locator('.conflict.resolved').count()===1&&await page.locator('.conflict.unresolved').count()===1);
 check('desktop fits viewport',await page.evaluate(()=>document.documentElement.scrollWidth<=1440));
 await page.screenshot({path:path.join(qa,'evidence-desktop-top.png')});await page.screenshot({path:path.join(qa,'evidence-desktop.png'),fullPage:true});
 await page.locator('[data-filter=self]').click();check('self filter excludes team',await page.locator('#facts article:visible').count()===data.facts.filter(f=>f.subject==='self').length);
 check('filter accessible state',await page.locator('[data-filter=self]').getAttribute('aria-pressed')==='true');
 await page.locator('[data-filter=unfinished]').click();check('unfinished filter separates plans and in-progress',await page.locator('#facts article:visible').count()===data.facts.filter(f=>f.status!=='done').length);
 await page.locator('[data-filter=all]').click();await page.locator('#search').fill('F02');check('search narrows evidence',await page.locator('#facts article:visible').count()===1);
 await page.locator('#F02 details').first().locator('summary').focus();await page.keyboard.press('Enter');check('keyboard expands exact quote',await page.locator('#F02 details').first().getAttribute('open')!==null);
 check('quote includes named attribution',(await page.locator('#F02 blockquote').first().innerText()).includes('林知夏'));
 const href=await page.locator('#F02 details a').first().getAttribute('href');const response=await ctx.request.get(base+'/'+href.split('#')[0]);check('source snapshot opens',response.ok());const source=await response.text();check('source page contains exact location',source.includes('id="'+href.split('#')[1]+'"'));
 await page.locator('#search').fill('');await page.locator('[data-filter=self]').click();await page.locator('#conflicts a[href="#M02"]').click();await page.locator('#M02').waitFor({state:'visible'});check('following evidence link reveals hidden team fact',await page.locator('#M02').isVisible());
 await page.locator('[data-filter=self]').click();await page.locator('#conflicts a[href="#M02"]').click();await page.locator('#M02').waitFor({state:'visible'});check('same evidence link reveals target after refiltering',await page.locator('#M02').isVisible());
 const downloads=await page.locator('a[download][href]').evaluateAll(a=>a.map(x=>x.getAttribute('href')));
 for(const href of downloads){const r=await ctx.request.get(base+'/'+href);check('download works '+href,r.ok()&&(await r.body()).length>100);}
 const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true}),mp=await mobile.newPage();mp.on('pageerror',e=>errors.push(e.message));await mp.goto(base);
 check('mobile fits actual 390px device',await mp.evaluate(()=>document.documentElement.scrollWidth<=390));await mp.screenshot({path:path.join(qa,'evidence-mobile-top.png')});await mp.screenshot({path:path.join(qa,'evidence-mobile.png'),fullPage:true});
 await mp.locator('[data-filter=team]').click();check('mobile filtering works',await mp.locator('#facts article:visible').count()===data.facts.filter(f=>f.subject==='team').length);
 const offline=await browser.newContext();await offline.setOffline(true);const op=await offline.newPage();await op.goto('file://'+path.join(out,'index.html'));await op.locator('[data-filter=self]').click();check('offline file works',await op.locator('#facts article:visible').count()>0);
 check('no runtime errors',errors.length===0);
 await fs.writeFile(path.join(qa,'browser-report.json'),JSON.stringify({ok:true,checks:passed.length,passed,errors,browser:await browser.version()},null,2));console.log(JSON.stringify({ok:true,checks:passed.length,qa}));
}finally{await browser?.close();await new Promise(r=>server.close(r));}

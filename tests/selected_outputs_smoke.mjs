import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const w=path.resolve(process.argv[2]||'examples/evidence-only'),out=path.join(w,'output'),qa=path.join(w,'qa');await fs.mkdir(qa,{recursive:true});
const modules=process.env.PRS_NODE_MODULES||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
const {chromium}=createRequire(path.join(modules,'package.json'))('playwright');
const data=JSON.parse(await fs.readFile(path.join(out,'analysis.json'),'utf8')),passed=[],errors=[];const check=(name,ok)=>{assert.ok(ok,name);passed.push(name);};let browser;
try{
 browser=await chromium.launch({channel:'chrome',headless:true});const ctx=await browser.newContext({viewport:{width:1440,height:1000}});await ctx.setOffline(true);const page=await ctx.newPage();page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.join(out,'index.html')).href);
 check('offline evidence-only page opens',await page.locator('#facts article').count()===data.facts.length);
 check('no unrequested downloads',await page.locator('a[download]').count()===0);
 check('no nonexistent Office links',await page.locator('a[href$=".docx"],a[href$=".pdf"],a[href$=".pptx"]').count()===0);
 check('desktop fits viewport',await page.evaluate(()=>document.documentElement.scrollWidth<=1440));
 await page.locator('[data-filter=self]').click();check('personal filter works',await page.locator('#facts article:visible').count()===data.facts.filter(f=>f.subject==='self').length);
 const target=data.facts.find(f=>f.subject==='team');const hashChanged=page.evaluate(()=>new Promise(resolve=>addEventListener('hashchange',()=>resolve(true),{once:true})));await page.locator(`#report a[href="#${target.id}"]`).first().click();await hashChanged;check('source link clears incompatible filter',await page.locator('#'+target.id).isVisible());
 await page.locator('#search').fill('F02');check('search finds selected record',await page.locator('#facts article:visible').count()===1);
 const detail=page.locator('#F02 details').first();await detail.locator('summary').focus();await page.keyboard.press('Enter');check('keyboard opens exact quotation',await detail.getAttribute('open')!==null);
 const f=data.facts.find(f=>f.id==='F02'),ref=f.evidence[0];check('quote equals ledger',await detail.locator('blockquote').innerText()===ref.quote);
 const href=await detail.locator('a').getAttribute('href');const source=await fs.readFile(path.join(out,href.split('#')[0]),'utf8');check('source snapshot contains exact unit',source.includes('id="'+ref.unit+'"'));check('source snapshot contains current hash',source.includes(ref.version));
 await page.locator('#evidence').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(qa,'evidence-only-desktop.png')});
 const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true});await mobile.setOffline(true);const mp=await mobile.newPage();await mp.goto(pathToFileURL(path.join(out,'index.html')).href);check('mobile fits viewport',await mp.evaluate(()=>document.documentElement.scrollWidth<=390));await mp.locator('[data-filter=team]').click();check('mobile filtering works',await mp.locator('#facts article:visible').count()===data.facts.filter(f=>f.subject==='team').length);await mp.locator('#evidence').scrollIntoViewIfNeeded();await mp.screenshot({path:path.join(qa,'evidence-only-mobile.png')});
 check('no runtime errors',errors.length===0);await fs.writeFile(path.join(qa,'browser-report.json'),JSON.stringify({ok:true,checks:passed.length,passed,errors},null,2));console.log(JSON.stringify({ok:true,checks:passed.length}));
}finally{await browser?.close();}

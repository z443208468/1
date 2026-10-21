#!/usr/bin/env node
'use strict';
/* Prerequisites: npm playwright, Chromium, a Chinese-capable system font.
   CHROMIUM_PATH may point to an existing executable. No browser/font is bundled. */
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url'),{chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..'),draft=process.argv.includes('--draft');
const OUT=process.env.R8_PRINT_OUT?path.resolve(process.env.R8_PRINT_OUT):(draft?path.join(ROOT,'qa_work','print_draft'):path.join(ROOT,'print'));
const names=['Player_ZH','Player_EN','Designer_Guide'].filter(n=>fs.existsSync(path.join(OUT,n+'.html')));
(async()=>{
const options={headless:true,args:['--no-sandbox']};
if(process.env.CHROMIUM_PATH)options.executablePath=process.env.CHROMIUM_PATH;
const browser=await chromium.launch(options),results=[];
for(const name of names){
 const page=await browser.newPage({viewport:{width:1000,height:1300},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.join(OUT,name+'.html')).href,{waitUntil:'load'});
 await page.evaluate(()=>window.R8PrintReady||document.fonts.ready);
 const geometry=await page.evaluate(()=>Array.from(document.querySelectorAll('.page')).map((s,i)=>{
  const c=s.querySelector('.content'),r=c.getBoundingClientRect(),f=s.querySelector('.footer').getBoundingClientRect();
  const children=Array.from(c.children).map(x=>x.getBoundingClientRect());
  const bottom=Math.max(r.top,...children.map(x=>x.bottom));
  return {page:i+1,title:s.querySelector('h2')?.textContent,overflowPx:Math.max(0,bottom-r.bottom),footerOverlapPx:Math.max(0,bottom-f.top),horizontalOverflowPx:Math.max(0,...children.map(x=>x.right-r.right),...children.map(x=>r.left-x.left)),bodyWidth:r.width,contentHeight:r.height,pageHeight:s.getBoundingClientRect().height};
 }));
 const bad=geometry.filter(g=>g.overflowPx>2||g.footerOverlapPx>2||g.horizontalOverflowPx>2||Math.abs(g.pageHeight-297*96/25.4)>2||Math.abs(g.contentHeight-240*96/25.4)>2);
 if(bad.length&&!draft){await browser.close();throw new Error(name+' layout overflow: '+JSON.stringify(bad));}
 await page.pdf({path:path.join(OUT,name+'.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false});
 results.push({file:name+'.pdf',expectedSections:geometry.length,geometry,overflow:bad,errors});await page.close();
}
await browser.close();
const report={draft,generatedAt:new Date().toISOString(),results,allFixedPageLayoutsFit:results.every(x=>!x.overflow.length&&!x.errors.length)};
fs.writeFileSync(path.join(OUT,'print_geometry.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({draft,generatedAt:report.generatedAt,results:results.map(r=>({file:r.file,pages:r.expectedSections,overflow:r.overflow,errors:r.errors})),allFixedPageLayoutsFit:report.allFixedPageLayoutsFit}));
})().catch(e=>{console.error(e.stack||e);process.exit(1)});

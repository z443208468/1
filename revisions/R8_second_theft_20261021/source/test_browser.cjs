'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert'),{chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..'),checks=[];
const ok=(name,value)=>{assert(value,name);checks.push({name,result:'PASS'});};
async function range(page,selector,value){await page.locator(selector).evaluate((el,v)=>{el.value=String(v);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));},value);}
async function click(page,action,extra=''){await page.locator(`[data-act="${action}"]${extra}`).first().click();}
async function proveEarly(page){await click(page,'screen','[data-screen="case"]');await click(page,'contact','[data-who="maker"]');await click(page,'contact','[data-who="handler"]');for(const [k,v]of Object.entries({theft:'d17',custody:'loan_production',conclusion:'subject_not_title'}))await page.locator(`select[data-kind="claim"][data-key="${k}"]`).selectOption(v);await click(page,'prove');}
(async()=>{
 const launch={headless:true,args:['--no-sandbox']};if(process.env.CHROMIUM_PATH)launch.executablePath=process.env.CHROMIUM_PATH;
 const browser=await chromium.launch(launch);let allErrors=[];
 const open=async(width=390)=>{const context=await browser.newContext({viewport:{width,height:844}});const page=await context.newPage();page.on('pageerror',e=>allErrors.push(String(e)));await page.goto('file://'+ROOT+'/R8_Offline.html');return {context,page};};
 let {context,page}=await open();
 ok('offline file loads and title is present',await page.locator('#game-title').innerText());
 ok('default is field mode',await page.locator('#mode').inputValue()==='field');
 await click(page,'stage','[data-id="S03"]');
 ok('field S03 hides canonical source chain',await page.locator('.source-chain').count()===0);
 ok('field S03 history cannot expand without a source action',await page.locator('[data-act="source"][data-id="S03"]').count()===1&&await page.locator('details').count()===0);
 await click(page,'source','[data-id="S03"]');
 ok('opening historical source permanently records fallback reference',await page.evaluate(()=>R8_TEST.state().questions.S03.reference)==='fallback');
 ok('backup source chain becomes visible',await page.locator('.source-chain').count()===1);
 ok('backup source is recorded',await page.evaluate(()=>R8_TEST.state().questions.S03.reference)==='fallback');
 await click(page,'hint','[data-id="S03"]');await click(page,'hint','[data-id="S03"]');
 ok('answer hint permanently records assistance',await page.evaluate(()=>R8_TEST.state().questions.S03.reference)==='assisted_reference');
 await click(page,'stage','[data-id="S02"]');
 ok('empty bridge slots contain no preplaced solution',await page.locator('[data-bridge]').count()===0);
 await page.locator('#field-S02-mainBridge').selectOption('yanagi');
 ok('bridge input moves a real strip into the selected diagram slot',await page.locator('[data-bridge="yanagi"]').count()===1);
 await click(page,'stage','[data-id="S01"]');
 for(const item of ['tower','viaduct','willow'])await click(page,'order-add',`[data-item="${item}"]`);
 await range(page,'#mask-slider',0);await range(page,'#mask-slider',100);
 await page.locator('#field-S01-inference').selectOption('occlusion_possible');await click(page,'submit');
 ok('S01 ordering plus actual screen manipulation validates',await page.evaluate(()=>!R8_TEST.state().questions.S01.dirty));
 await click(page,'order-down','[data-item="tower"]');
 ok('editing an accepted draft clears its current success state',await page.evaluate(()=>R8_TEST.state().questions.S01.dirty));
 ok('prior evidence survives draft change',await page.evaluate(()=>!!R8_TEST.state().questions.S01.accepted));
 await click(page,'stop');
 ok('early refusal has its own truthful outcome',await page.evaluate(()=>R8_TEST.state().earlyStopped&&!R8_TEST.state().caseProven));
 await click(page,'spoiler');ok('spoiler does not mark proof',await page.evaluate(()=>R8_TEST.state().spoilerViewed&&!R8_TEST.state().caseProven));
 await context.close();
 const branchResults=[];
 for(const disclosure of ['quiet','announce'])for(const resolution of ['expose','replay']){
  ({context,page}=await open());await proveEarly(page);
  ok(disclosure+'/'+resolution+' early proof needs no stage or A date',await page.evaluate(()=>R8_TEST.state().caseProven&&!Object.values(R8_TEST.state().questions).some(q=>q.accepted)&&!R8Engine.sourceDateVerified(R8_TEST.state())));
  if(disclosure==='announce')await click(page,'disclosure','[data-value="announce"]');
  await click(page,'resolution',`[data-value="${resolution}"]`);
  if(resolution==='replay'){
   await click(page,'secure');await click(page,'insert');await range(page,'#replay-mask',100);
   ok(disclosure+' replay keeps marked disc in actual SVG',await page.locator('#replay-figure [data-demo-disk]').count()===1);
   await click(page,'replay-view','[data-value="side"]');
   ok(disclosure+' side manipulation completed',await page.evaluate(()=>R8Engine.replayReady(R8_TEST.state())));
  }
  await click(page,'finalize');
  const result=await page.evaluate(()=>({state:R8_TEST.state(),world:R8Engine.world(R8_TEST.state())}));
  ok(disclosure+'/'+resolution+' actual return and cancellation',result.state.completed&&result.world.coreHolder==='akari'&&result.world.frameHolder==='akari'&&result.world.transfer==='cancelled');
  ok(disclosure+'/'+resolution+' broker knows completed disposition',result.world.brokerKnowsChallenge);
  await page.reload();ok(disclosure+'/'+resolution+' local reload preserves resolution',await page.evaluate(()=>R8_TEST.state().completed&&R8_TEST.state().coreHolder==='akari'));
  await page.locator('#language').click();ok(disclosure+'/'+resolution+' English preserves completed state',await page.evaluate(()=>R8_TEST.state().lang==='en'&&R8_TEST.state().completed));
  ok(disclosure+'/'+resolution+' mobile has no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  branchResults.push({disclosure,resolution,world:result.world});
  if(disclosure==='quiet'&&resolution==='replay'){fs.mkdirSync(path.join(ROOT,'qa/screenshots'),{recursive:true});await page.screenshot({path:path.join(ROOT,'qa/screenshots/mobile_resolution.png'),fullPage:true});}
  await context.close();
 }
 ({context,page}=await open(1100));await page.locator('#mode').selectOption('desk');await click(page,'stage','[data-id="S04"]');
 ok('desk mode shows its distinct reference board',await page.locator('.backup').count()>=1);
 ok('desk provenance is recorded',await page.evaluate(()=>R8_TEST.state().questions.S04.reference)==='desk');
 await page.screenshot({path:path.join(ROOT,'qa/screenshots/desktop_puzzle.png'),fullPage:true});
 await click(page,'screen','[data-screen="contacts"]');await click(page,'contact','[data-who="handler"]');
 ok('D17 original record shows entering, covering, withdrawing and side frames',await page.locator('#person-handler .d17-grid figure').count()===6);
 await page.screenshot({path:path.join(ROOT,'qa/screenshots/original_record.png'),fullPage:true});
 await context.close();
 const blocked=await browser.newContext({viewport:{width:390,height:844}});await blocked.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw new Error('Blocked by test');}});});page=await blocked.newPage();page.on('pageerror',e=>allErrors.push(String(e)));await page.goto('file://'+ROOT+'/R8_Offline.html');
 ok('storage-denied browser warns without crashing',await page.locator('#storage-warning').isVisible());
 await click(page,'hold');ok('game acts despite unavailable localStorage',await page.evaluate(()=>R8_TEST.state().transfer==='paused'));
 await blocked.close();await browser.close();
 ok('no JavaScript exceptions during all flows',allErrors.length===0);
 fs.writeFileSync(path.join(ROOT,'qa/browser_results.json'),JSON.stringify({version:'R8.1',run_date:'2026-10-21',checks,branches:branchResults,javascript_errors:allErrors,scope:'Actual file navigation, authored UI interactions, current local Chromium, 390px/1100px. No human blind playtest, field validation or commercial authorisation.'},null,2));
 console.log(JSON.stringify({checks:checks.length,passed:checks.length,branches:branchResults.length}));
})().catch(e=>{console.error(e);process.exit(1)});

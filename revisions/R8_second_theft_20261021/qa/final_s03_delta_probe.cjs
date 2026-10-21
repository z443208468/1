'use strict';

// Focused follow-up after the full independent run: two neutral S03 instruction
// changes only. This preserves final_independent_results.json and its old SHA.
// Run from any directory with Playwright and a Chromium executable installed.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { chromium } = require('playwright');
const ROOT = path.resolve(__dirname, '..');
const SHOTS = process.env.REVIEW_SCREENSHOT_DIR || (process.env.WORK_DIR
  ? path.resolve(process.env.WORK_DIR, 'final_independent_review')
  : fs.mkdtempSync(path.join(os.tmpdir(), 'tokyo-r8-s03-delta-')));
const OUT = process.env.REVIEW_RESULTS_FILE ? path.resolve(process.env.REVIEW_RESULTS_FILE)
  : path.join(__dirname, 'final_s03_delta_results.rerun.json');
const baseline = JSON.parse(fs.readFileSync(path.join(__dirname, 'final_independent_results.json')));
const file = path.join(ROOT, 'R8_Offline.html');
const html = fs.readFileSync(file, 'utf8');
const hash = x => crypto.createHash('sha256').update(x).digest('hex');
const checks = [], errors = [], observations = [];
const check = (id, passed, evidence) => checks.push({id, passed:!!passed, evidence});
const changes = [
  ['按图像被转制的先后连接四张载体卡。', '连接四张载体卡。'],
  ['Connect the four image-carrier cards in the order the image was transformed into successive forms.', 'Connect the four image-carrier cards.']
];
const beforeHash = hash(html);
const metadata = {
  scope:'Only the S03 bilingual task-direction clarification after the independent full focused run. No human or field test.',
  artifact:'R8_Offline.html', artifactSha256:beforeHash,
  artifactBytes:Buffer.byteLength(html), baselineArtifactSha256:baseline.artifactSha256,
  sourceHashes:Object.fromEntries(['content.json','app.js','engine.js','figures.js'].map(f=>[f,hash(fs.readFileSync(path.join(ROOT,'source',f)))])),
  screenshotDirectory:SHOTS
};
fs.mkdirSync(SHOTS,{recursive:true});
let reversed = html;
for (const [now,old] of changes) reversed = reversed.replace(now,old);
check('only_two_neutral_task_sentences_changed_in_built_artifact', hash(reversed)===baseline.artifactSha256,
  {reversedHash:hash(reversed),baselineHash:baseline.artifactSha256,changes});
check('app_engine_and_figures_unchanged_since_full_focused_run',
  ['app.js','engine.js','figures.js'].every(f=>metadata.sourceHashes[f]===baseline.sourceHashes[f]),
  {current:metadata.sourceHashes,baseline:baseline.sourceHashes});
const embedded = JSON.parse(html.match(/window\.R8Content=(.*?);<\/script>/s)[1]);
const source = JSON.parse(fs.readFileSync(path.join(ROOT,'source/content.json'),'utf8'));
check('built_content_matches_delivered_source',JSON.stringify(embedded)===JSON.stringify(source),{});

(async()=>{
  const options={headless:true,args:['--no-sandbox']};
  if(process.env.CHROMIUM_PATH) options.executablePath=process.env.CHROMIUM_PATH;
  const browser=await chromium.launch(options);
  try{
    for(const lang of ['zh','en']){
      const context=await browser.newContext({viewport:{width:1100,height:900}});
      const page=await context.newPage();
      page.on('pageerror',e=>errors.push(String(e)));
      await page.goto('file://'+file);
      if(lang==='en') await page.locator('#language').click();
      await page.locator('[data-act="stage"][data-id="S03"]').first().click();
      const text=await page.locator('#main').innerText();
      const labels={date:await page.locator('label[for="field-S03-dateObject"]').innerText(),
        range:await page.locator('label[for="field-S03-rangeObject"]').innerText()};
      const state=await page.evaluate(()=>R8_TEST.state());
      const q=source.stages.find(q=>q.id==='S03');
      check(`S03_${lang}_clarifies_forward_transformation_without_answer_order`,
        text.includes(q.task[lang]) && q.task[lang].startsWith(changes[lang==='zh'?0:1][0]) &&
        !/1995|原画.*模写.*铜像.*照片|portrait.*copy.*bronze.*photograph/i.test(q.task[lang]),
        {task:q.task[lang]});
      check(`S03_${lang}_default_labels_and_source_gate_remain_neutral`,
        !/1995/.test(labels.date) && !/最早|earliest|lower bound/i.test(labels.range) &&
        await page.locator('.source-chain').count()===0 &&
        await page.locator('#main details').count()===0 &&
        await page.locator('#main > .panel > .diagram svg text').count()===0 &&
        state.questions.S03.reference==='field' && !state.records.includes('date_source'),
        {labels,reference:state.questions.S03.reference,records:state.records});
      const screenshot=path.join(SHOTS,`s03_final_delta_${lang}.png`);
      await page.screenshot({path:screenshot,fullPage:true});
      observations.push({language:lang,screenshot,task:q.task[lang],labels});
      await context.close();
    }
    check('no_uncaught_browser_errors',errors.length===0,{errors});
    check('artifact_unchanged_during_delta_check',hash(fs.readFileSync(file))===beforeHash,{});
  }catch(e){errors.push(String(e.stack||e));check('delta_probe_completed',false,{error:String(e)});}
  finally{
    await browser.close();
    const result={...metadata,checks,observations,errors,passed:checks.filter(c=>c.passed).length,failed:checks.filter(c=>!c.passed).length};
    fs.writeFileSync(OUT,JSON.stringify(result,null,2)+'\n');
    console.log(JSON.stringify({output:OUT,artifactSha256:beforeHash,passed:result.passed,failed:result.failed,errors}));
    if(result.failed)process.exitCode=1;
  }
})();

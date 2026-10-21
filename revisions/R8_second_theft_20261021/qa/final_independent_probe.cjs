'use strict';

// Final independent focused review, not the author's whole regression suite.
// From the release root:
// CHROMIUM_PATH=/path/to/chrome-headless-shell node qa/final_independent_probe.cjs
// Optional REVIEW_SCREENSHOT_DIR or WORK_DIR keeps screenshots in a chosen location.
// Otherwise use a fresh OS temporary directory, independent of the checkout path.
// Reruns write a separate result by default, preserving the reviewed evidence.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { chromium } = require('playwright');
const ROOT = path.resolve(__dirname, '..');
const SHOTS = process.env.REVIEW_SCREENSHOT_DIR || (process.env.WORK_DIR
  ? path.resolve(process.env.WORK_DIR, 'final_independent_review')
  : fs.mkdtempSync(path.join(os.tmpdir(), 'tokyo-r8-independent-')));
const OUT = process.env.REVIEW_RESULTS_FILE ? path.resolve(process.env.REVIEW_RESULTS_FILE)
  : path.join(__dirname, 'final_independent_results.rerun.json');
const artifact = path.join(ROOT, 'R8_Offline.html');
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const E = require(path.join(ROOT, 'source/engine.js'));
const checks = [], flows = [], observations = [], errors = [];
const check = (id, passed, evidence) => checks.push({ id, passed: !!passed, evidence });
const step = (s, a) => E.act(s, a).state;
const hashAtStart = sha(artifact);
fs.mkdirSync(SHOTS, { recursive: true });
const metadata = {
  reviewer: '/root/game_design_research',
  scope: 'Independent source/design inspection and targeted actual-browser actions. The reviewer already knows the answers; this is not a blind playtest, a human test or fieldwork.',
  artifact: 'R8_Offline.html', artifactSha256: hashAtStart,
  artifactBytes: fs.statSync(artifact).size,
  sourceHashes: Object.fromEntries(['content.json','app.js','engine.js','figures.js'].map(f => [f, sha(path.join(ROOT,'source',f))])),
  screenshotDirectory: SHOTS
};

async function click(page, action, extra='') {
  await page.locator(`[data-act="${action}"]${extra}`).first().click();
}
async function range(page, selector, value) {
  await page.locator(selector).evaluate((el, v) => {
    el.value = String(v);
    el.dispatchEvent(new Event('input', {bubbles:true}));
    el.dispatchEvent(new Event('change', {bubbles:true}));
  }, value);
}
async function state(page) { return page.evaluate(() => R8_TEST.state()); }
async function world(page) { return page.evaluate(() => R8Engine.world(R8_TEST.state())); }
async function shot(page, name, selector) {
  const file = path.join(SHOTS, name + '.png');
  if (selector) await page.locator(selector).screenshot({path:file});
  else await page.screenshot({path:file, fullPage:true});
  return file;
}

(async () => {
  const options = {headless:true, args:['--no-sandbox']};
  if (process.env.CHROMIUM_PATH) options.executablePath = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(options);
  const open = async (width=1100) => {
    const context = await browser.newContext({viewport:{width,height:900}});
    const page = await context.newPage();
    page.on('pageerror', e => errors.push(String(e)));
    await page.goto('file://' + artifact);
    return {context, page};
  };
  try {
    // Default field materials and actual access provenance, in both languages.
    for (const lang of ['zh', 'en']) {
      const {context,page} = await open();
      if (lang === 'en') await page.locator('#language').click();
      await click(page,'stage','[data-id="S03"]');
      const dateLabel = await page.locator('label[for="field-S03-dateObject"]').innerText();
      const rangeLabel = await page.locator('label[for="field-S03-rangeObject"]').innerText();
      const mainText = await page.locator('#main').innerText();
      check(`S03_${lang}_default_labels_do_not_assign_date_or_bound`,
        !/1995/.test(dateLabel) && !/最早|earliest|lower bound/i.test(rangeLabel), {dateLabel,rangeLabel});
      check(`S03_${lang}_default_recognition_figure_is_not_solution_chain`,
        await page.locator('.source-chain').count() === 0 &&
        await page.locator('#main > .panel > .diagram svg text').count() === 0,
        {sourceChainCount:await page.locator('.source-chain').count(), defaultText:mainText});
      const before = await state(page);
      check(`S03_${lang}_history_is_explicit_recorded_source_action`,
        await page.locator('[data-act="source"][data-id="S03"]').count() === 1 &&
        await page.locator('#main details').count() === 0 && before.questions.S03.reference === 'field',
        {reference:before.questions.S03.reference});
      await shot(page,`s03_default_${lang}`);
      await click(page,'source','[data-id="S03"]');
      const after = await state(page);
      check(`S03_${lang}_history_open_records_fallback_and_displays_source`,
        after.questions.S03.reference === 'fallback' && after.records.includes('date_source') &&
        await page.locator('.source-chain').count() === 1,
        {reference:after.questions.S03.reference,records:after.records});
      await shot(page,`s03_source_${lang}`);
      await context.close();
    }
    {
      const {context,page} = await open();
      await click(page,'stage','[data-id="S03"]');
      await click(page,'hint','[data-id="S03"]');
      const h1 = (await state(page)).questions.S03.reference;
      await click(page,'hint','[data-id="S03"]');
      const h2 = (await state(page)).questions.S03.reference;
      check('S03_direction_hint_vs_answer_hint_provenance', h1==='field' && h2==='assisted_reference', {h1,h2});
      await click(page,'stage','[data-id="S05"]');
      const t = await page.locator('#main').innerText();
      check('S05_default_task_does_not_supply_core_matching_answers',
        !/B失窃图配给D-17|失主.*配给L\+D|B→D-17|owner-return.*L\+D|match B to D-17/i.test(t),
        {defaultText:t});
      await shot(page,'s05_default_zh');
      // S05 is openly a supplied-history stop: its explanatory history is
      // available normally, while the complete dated timeline uses backup.
      await click(page,'backup','[data-id="S05"]');
      check('S05_supplied_timeline_remains_accessible_and_logged',
        (await state(page)).questions.S05.reference==='fallback' &&
        /1873/.test(await page.locator('#main').innerText()),
        {reference:(await state(page)).questions.S05.reference});
      await context.close();
    }

    // A genuine early refusal, including save/reload and an explicit spoiler.
    {
      const {context,page} = await open();
      await click(page,'stop');
      await shot(page,'early_refusal');
      await click(page,'spoiler');
      await page.reload();
      const s = await state(page), w = await world(page);
      check('early_refusal_and_spoiler_survive_reload_without_proving_case',
        s.earlyStopped && s.spoilerViewed && !s.caseProven && !s.completed &&
        s.coreHolder==='player' && s.transfer==='paused' && !s.alerted && w.earlyRefusal,
        {earlyStopped:s.earlyStopped,spoilerViewed:s.spoilerViewed,world:w});
      await context.close();
    }

    let commonEntryHash = null;
    // Two operational routes at the same entry, plus the two disclosure variants.
    for (const disclosure of ['quiet','announce']) for (const resolution of ['expose','replay']) {
      const {context,page} = await open();
      const flow = {disclosure,resolution,actions:[],screenshots:[]};
      const act = async (label, action, extra='') => { await click(page,action,extra); flow.actions.push(label); };
      const openingFrames = await page.locator('.film-pair svg').evaluateAll(x=>x.map(y=>y.outerHTML));
      await act('Open contact records','screen','[data-screen="contacts"]');
      await act('Request and read L+D from Akari','contact','[data-who="maker"]');
      flow.makerRecordVisible = /L|借用单|Loan record/.test(await page.locator('#main').innerText());
      await act('Request and read original D-17 from Narumi','contact','[data-who="handler"]');
      if (disclosure==='quiet' && resolution==='expose') {
        const frames = await page.locator('.d17-grid figure').evaluateAll(figures=>figures.map(f=>({
          label:f.querySelector('figcaption').textContent,
          svg:f.querySelector('svg').outerHTML,
          diskCount:f.querySelectorAll('[data-demo-disk]').length,
          cx:f.querySelector('[data-demo-disk]').getAttribute('cx'),
          cy:f.querySelector('[data-demo-disk]').getAttribute('cy'),
          screenX:f.querySelector('[data-occluder]').getAttribute('x'),
          nick:f.querySelector('[data-frame-nick]').getAttribute('d'),
          crease:f.querySelector('[data-cloth-crease]').getAttribute('d')
        })));
        check('D17_six_frames_match_opening_and_keep_original_disk_features',
          frames.length===6 && frames.every(f=>f.diskCount===1 && f.cx==='160' && f.cy==='90') &&
          frames[0].svg===openingFrames[0] && frames[2].svg===openingFrames[1] &&
          frames.every(f=>f.nick===frames[0].nick && f.crease===frames[0].crease) &&
          [20,72.2,136,72.2,20,20].every((x,i)=>Math.abs(+frames[i].screenX-x)<0.001),
          {frames:frames.map(({svg,...f})=>f), openingB1Matches:frames[0].svg===openingFrames[0],openingB2Matches:frames[2].svg===openingFrames[1]});
        flow.screenshots.push(await shot(page,'d17_six_frames','.d17-grid'));
      }
      await act('Open core-claim comparison','screen','[data-screen="case"]');
      for (const [key,value] of Object.entries({theft:'d17',custody:'loan_production',conclusion:'subject_not_title'})) {
        await page.locator(`select[data-kind="claim"][data-key="${key}"]`).selectOption(value);
        flow.actions.push('Match '+key+' → '+value);
      }
      await act('Check core case with A left unchecked','prove');
      const entry = await state(page);
      const entryHash=crypto.createHash('sha256').update(JSON.stringify(entry)).digest('hex');
      if (!commonEntryHash) commonEntryHash=entryHash;
      check(`${disclosure}_${resolution}_same_entry_and_early_proof`,
        entryHash===commonEntryHash && entry.caseProven && entry.claims.date==='' &&
        !Object.values(entry.questions).some(q=>q.accepted),
        {entryHash,records:entry.records,acceptedStages:Object.values(entry.questions).filter(q=>q.accepted).length});
      flow.entryHash=entryHash;
      if (disclosure==='announce') await act('Send explicit challenge before resolving','disclosure','[data-value="announce"]');
      flow.beforeResolution=await world(page);
      check(`${disclosure}_${resolution}_opponent_request_reads_actual_disclosure`,
        flow.beforeResolution.brokerRequest===(disclosure==='announce'?'REQUEST_CONTINUOUS':'REQUEST_FRONT'), flow.beforeResolution);
      await act('Choose '+resolution,'resolution',`[data-value="${resolution}"]`);
      if (resolution==='replay') {
        await act('Try ending before physical demonstration (must remain unresolved)','finalize');
        check(`${disclosure}_replay_cannot_finish_without_actions`, !(await state(page)).completed,
          {feedback:await page.locator('#feedback').innerText()});
        await act('Keep real sheets outside demonstration','secure');
        await act('Insert striped demonstration disk only','insert');
        await range(page,'#replay-mask',100); flow.actions.push('Move screen across fixed disk');
        const front=await page.locator('#replay-figure').evaluate(el=>({
          disks:el.querySelectorAll('[data-demo-disk]').length,
          screenX:+el.querySelector('[data-occluder]').getAttribute('x'),
          cx:+el.querySelector('[data-demo-disk]').getAttribute('cx'),
          r:+el.querySelector('[data-demo-disk]').getAttribute('r')
        }));
        check(`${disclosure}_replay_actual_occlusion_keeps_disk`,
          front.disks===1 && front.screenX<=front.cx-front.r && front.screenX+48>=front.cx+front.r,front);
        if (disclosure==='quiet') flow.screenshots.push(await shot(page,'replay_front_hidden','#replay-figure'));
        await act('Open separated side view','replay-view','[data-value="side"]');
        check(`${disclosure}_replay_side_shows_same_disk_on_separate_layer`,
          await page.locator('#replay-figure [data-demo-disk]').count()===1 &&
          await page.locator('#replay-figure [data-layer="base"]').count()===1 &&
          await page.locator('#replay-figure [data-layer="screen"]').count()===1 &&
          (await state(page)).replay.sideSeen,
          {replay:(await state(page)).replay,feedback:await page.locator('.record .notice').last().innerText()});
        if (disclosure==='quiet') flow.screenshots.push(await shot(page,'replay_side_visible','#replay-figure'));
      }
      await act('Execute return of inserts and frame','finalize');
      const completed=await state(page), w=await world(page);
      flow.finalWorld=w;
      flow.actualEventLog=completed.log;
      flow.receiptText=await page.locator('.receipt').innerText();
      check(`${disclosure}_${resolution}_completed_outcome_reads_correct_route`,
        completed.completed && completed.completion.disclosure===disclosure && completed.completion.resolution===resolution &&
        completed.completion.alertedBefore===(disclosure==='announce') && w.coreHolder==='akari' && w.frameHolder==='akari' &&
        w.brokerKnowsChallenge && !w.sourceDateVerified,
        {completion:completed.completion,world:w,receiptText:flow.receiptText});
      if (disclosure==='quiet') flow.screenshots.push(await shot(page,'ending_'+resolution));
      if (disclosure==='quiet' && resolution==='expose') {
        const downloadEvent=page.waitForEvent('download');
        await click(page,'export');
        const download=await downloadEvent;
        const save=path.join(SHOTS,'completed_progress.json');
        await download.saveAs(save);
        await page.reload();
        const reloaded=await world(page);
        const second=await open();
        await second.page.locator('#import-file').setInputFiles(save);
        const imported=await world(second.page);
        await click(second.page,'stage','[data-id="S01"]');
        await second.page.locator('#field-S01-inference').selectOption('theft_proved');
        const edited=await world(second.page);
        const stable=x=>x.coreHolder==='akari'&&x.frameHolder==='akari'&&x.transfer==='cancelled'&&x.brokerRequest==='SALE_WITHDRAWN';
        check('completed_save_reload_import_and_old_draft_edit_preserve_events',
          stable(reloaded)&&stable(imported)&&stable(edited)&&
          JSON.stringify(edited.recordRecipients)===JSON.stringify(w.recordRecipients),
          {reloaded,imported,edited});
        await second.context.close();
      }
      flows.push(flow);
      await context.close();
    }

    // A new reenactment cannot substitute for the original record's provenance.
    let withoutOriginal=E.initial();
    withoutOriginal=step(withoutOriginal,{type:'CONTACT',who:'maker'});
    for(const [key,value] of Object.entries({theft:'d17',custody:'loan_production',conclusion:'subject_not_title'}))
      withoutOriginal=step(withoutOriginal,{type:'CLAIM',key,value});
    for(const action of [{type:'SECURE_CORE'},{type:'INSERT_DEMO'},{type:'REPLAY_MASK',value:100},{type:'REPLAY_VIEW',value:'side'}])
      withoutOriginal=step(withoutOriginal,action);
    const rejected=E.act(withoutOriginal,{type:'PROVE'});
    check('new_reenactment_does_not_prove_B_without_D17',
      E.replayReady(withoutOriginal)&&!rejected.result.ok&&rejected.result.wrong.includes('record_d17'),
      {replayReady:E.replayReady(withoutOriginal),proof:rejected.result});
    observations.push({id:'site_deletion_limit',kind:'DESIGN_COUNTEREXAMPLE',
      finding:'All four witnessed browser resolutions used no stage submission and no A verification. This verifies the legitimate early path, not that every normal field task is useless. S01/S04/S05 replacement and historical-causality judgments remain in the human-readable independent report.'});
    check('no_uncaught_browser_errors',errors.length===0,errors);
    check('reviewed_artifact_unchanged_during_run',sha(artifact)===hashAtStart,{start:hashAtStart,end:sha(artifact)});
  } catch(error) {
    errors.push(error.stack||String(error));
    check('probe_completed',false,error.stack||String(error));
  } finally {
    await browser.close();
    const result={...metadata,checks,flows,observations,errors,
      passed:checks.filter(x=>x.passed).length,failed:checks.filter(x=>!x.passed).length};
    fs.writeFileSync(OUT,JSON.stringify(result,null,2)+'\n');
    process.stdout.write(JSON.stringify({output:OUT,artifactSha256:metadata.artifactSha256,passed:result.passed,failed:result.failed,errors})+'\n');
    process.exitCode=result.failed?1:0;
  }
})().catch(error=>{process.stderr.write(String(error.stack||error)+'\n');process.exitCode=1;});

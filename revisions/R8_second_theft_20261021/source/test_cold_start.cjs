'use strict';
// Run against a freshly extracted release, never the author's open browser.
// node source/test_cold_start.cjs /absolute/extracted/root /absolute/report.json
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const assert = require('assert');
const {pathToFileURL} = require('url');
const {chromium} = require('playwright');
const root = path.resolve(process.argv[2] || path.join(__dirname, '..'));
const reportPath = path.resolve(process.argv[3] || path.join(root, 'qa', 'cold_start_results.json'));
const entry = path.join(root, 'R8_Offline.html');
const checks = [], errors = [], requests = [];
const ok = (name, value) => { assert(value, name); checks.push({name, result: 'PASS'}); };
const click = (page, action, suffix = '') => page.locator(`[data-act="${action}"]${suffix}`).first().click();
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async () => {
  const launch = {headless: true, args: ['--no-sandbox']};
  if (process.env.CHROMIUM_PATH) launch.executablePath = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(launch);
  const context = await browser.newContext({viewport: {width: 390, height: 844}});
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(String(error)));
  page.on('request', request => { if (/^https?:/.test(request.url())) requests.push(request.url()); });
  await page.goto(pathToFileURL(entry).href);
  ok('fresh file starts at opening without prior completion', (await page.locator('#main').innerText()).includes('你手里已经有什么'));
  ok('default observation mode is field', await page.locator('#mode').inputValue() === 'field');
  await click(page, 'hold');
  ok('refusal immediately pauses transfer', (await page.locator('#sidebar').innerText()).includes('已暂停'));
  await click(page, 'stop');
  ok('early result does not pretend full proof', (await page.locator('#main').innerText()).includes('未检验原始记录'));
  await click(page, 'continue');
  await click(page, 'stage', '[data-id="S03"]');
  ok('final S03 observed-date label is neutral', await page.locator('label[for="field-S03-dateObject"]').innerText() === '所读纪年对应哪一载体？');
  ok('final S03 range label does not preselect lower bound', await page.locator('label[for="field-S03-rangeObject"]').innerText() === '这项纪年可约束哪种材料？');
  ok('initial S03 has no complete reference chain', await page.locator('.source-chain').count() === 0);
  await click(page, 'screen', '[data-screen="case"]');
  await click(page, 'contact', '[data-who="maker"]');
  await click(page, 'contact', '[data-who="handler"]');
  for (const [key, value] of Object.entries({theft: 'd17', custody: 'loan_production', conclusion: 'subject_not_title'})) {
    await page.locator(`select[data-kind="claim"][data-key="${key}"]`).selectOption(value);
  }
  await click(page, 'prove');
  ok('core evidence permits disposition without five solved stops', (await page.locator('#feedback').innerText()).includes('不必补齐五站'));
  await click(page, 'resolution', '[data-value="expose"]');
  await click(page, 'finalize');
  const outcome = await page.locator('#main').innerText();
  ok('visible outcome records the return', outcome.includes('第二次失窃没有发生'));
  ok('unverified A stays separately unverified', outcome.includes('本轮未独立核验'));
  ok('previous refusal remains in the result', outcome.includes('已发生并保留'));
  ok('sidebar shows actual game-world object return', (await page.locator('#sidebar').innerText()).includes('已由鸣海归还'));
  await page.reload();
  ok('reload preserves executed disposition', (await page.locator('#main').innerText()).includes('已经发生的处置'));
  await page.locator('#language').click();
  ok('English switch preserves completed outcome', (await page.locator('#main').innerText()).includes('RESOLUTION'));
  ok('mobile page has no horizontal overflow', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
  ok('no runtime HTTP requests', requests.length === 0);
  ok('no JavaScript exceptions', errors.length === 0);
  await browser.close();
  const components = {};
  for (const relative of ['R8_Offline.html', 'play/index.html', 'print/Player_ZH.pdf', 'print/Player_EN.pdf', 'print/Designer_Guide.pdf']) {
    components[relative] = hash(path.join(root, relative));
  }
  const report = {version: 'R8-20261021', run_date: new Date().toISOString(), extracted_root: root,
    entry_sha256: components['R8_Offline.html'], component_sha256: components,
    checks, passed: checks.length, failed: 0, javascript_errors: errors, runtime_http_requests: requests,
    scope: 'Actual file navigation from a fresh ZIP extraction in a new Chromium browser context, using visible UI. Tests early refusal, optional A, early proof, executed return, reload and English switch. Component hashes identify the tested bytes; packaging later adds this report and updates manifest only. Not a human, field or physical assembly test.'};
  fs.mkdirSync(path.dirname(reportPath), {recursive: true});
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(JSON.stringify({passed: checks.length, failed: 0, entry_sha256: report.entry_sha256, report: reportPath}));
})().catch(error => { console.error(error); process.exit(1); });

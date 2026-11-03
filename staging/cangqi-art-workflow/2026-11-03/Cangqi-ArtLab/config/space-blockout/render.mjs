import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const [file, cam, state, destination] = process.argv.slice(2);
if (!destination) throw Error('node render.mjs <scene.json> <camera_id> <state_id> <new-output-directory>');
const source = fs.readFileSync(file);
const data = JSON.parse(source.toString('utf8').replace(/^\uFEFF/, ''));
const hash = createHash('sha256').update(source).digest('hex');
const root = path.dirname(fileURLToPath(import.meta.url));
const output = path.resolve(destination);
if (fs.existsSync(output)) throw Error('Output exists: ' + output);
const require = createRequire(import.meta.url);
const threeDir = path.dirname(require.resolve('three'));
const { chromium } = require('playwright');
const browser = await chromium.launch({ executablePath:process.env.BLOCKOUT_CHROMIUM || undefined, args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
let temp;
try {
  fs.mkdirSync(path.dirname(output), {recursive:true});
  temp = fs.mkdtempSync(path.join(path.dirname(output), '.blockout-'));
  const page = await browser.newPage();
  const html = '<script type="importmap">{"imports":{"three":"/three/three.module.js"}}</script><script type="module">import {render} from "/passes.js";window.render=render;</script>';
  await page.route('**/*', async route => {
    const name = new URL(route.request().url()).pathname;
    if (name === '/') return route.fulfill({contentType:'text/html',body:html});
    const local = name === '/passes.js' ? path.join(root, 'passes.js')
      : /^\/three\/three\.[a-z.]+\.js$/.test(name) ? path.join(threeDir, path.basename(name)) : null;
    if (!local || !fs.existsSync(local)) return route.abort();
    return route.fulfill({contentType:'text/javascript', body:fs.readFileSync(local)});
  });
  const passHashes = {};
  await page.exposeFunction('savePNG', (name, uri) => {
    if (!['clay','depth','normal','line','semantic','top'].includes(name)) throw Error('Bad pass');
    const png = Buffer.from(uri.split(',')[1], 'base64');
    fs.writeFileSync(path.join(temp, name + '.png'), png);
    passHashes[name] = createHash('sha256').update(png).digest('hex');
  });
  await page.goto('http://blockout.local/');
  await page.waitForFunction(() => typeof window.render === 'function');
  const facts = await page.evaluate(async args => window.render(...args), [data,cam,state]);
  fs.writeFileSync(path.join(temp,'visibility.json'), JSON.stringify({...facts, scene_sha256:hash, pass_sha256:passHashes},null,2));
  fs.writeFileSync(path.join(temp, 'scene-snapshot.json'), source);
  fs.renameSync(temp,output); temp = undefined;
  console.log(output);
} finally {
  await browser.close();
  if (temp) fs.rmSync(temp,{recursive:true,force:true});
}

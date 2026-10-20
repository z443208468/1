from pathlib import Path
import json
import os
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
checks=[]
def ok(name,cond):
 if not cond:raise AssertionError(name)
 checks.append({'name':name,'result':'PASS'})
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1100,'height':850});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 # Navigation is blocked by the environment. Test the exact self-contained bundle by content injection.
 page.set_content((R/'R3_Offline.html').read_text(),wait_until='load')
 ok('initial rendered',page.locator('#submit').count()==1)
 page.locator('#submit').click();ok('empty answer gives feedback',page.locator('.error').count()==1)
 page.locator('#team').fill('R3 Test Team')
 for c in ['tower','sign','roof']:page.locator(f'[data-card="{c}"]').click()
 page.locator('#f-reading').select_option('occlusion');page.locator('#submit').click();ok('S01 solved',page.evaluate('R3_TEST.getState().passed[0]') is True)
 page.locator('#next').click();page.locator('#flip').click();page.locator('#rotate').click()
 page.locator('#f-stage').select_option('inase');page.locator('#f-place').select_option('sumida');page.locator('#submit').click();ok('S02 solved by controls',page.evaluate('R3_TEST.getState().passed[1]') is True)
 page.locator('#next').click();ok('S03 has a visible memorial reference',page.locator('svg[aria-label]').count()>=1);page.locator('#f-life').select_option('1680');page.locator('#f-earliest').select_option('1995');page.locator('#f-dateMeaning').select_option('exact');page.locator('#submit').click();ok('exact-year overclaim rejected',page.locator('.error').count()==1)
 page.locator('#f-dateMeaning').select_option('lower_bound');page.locator('#submit').click();page.locator('#share').click();page.locator('#next').click();ok('share has orientation help',page.evaluate('R3_TEST.getState().inputs[3].rotation')==0 and page.evaluate('R3_TEST.getState().inputs[3].mirror') is False)
 for k,v in {'camera':'playground','building':'sports','purpose':'capture'}.items():page.locator('#f-'+k).select_option(v)
 page.locator('#submit').click();ok('S04 still requires interpretation',page.evaluate('R3_TEST.getState().passed[3]') is True)
 page.locator('#next').click()
 for c in ['kisho','hisamatsu','chitose','meiji']:page.locator(f'[data-card="{c}"]').click()
 page.locator('#f-move').select_option('location');page.locator('#submit').click();ok('S05 solved',page.evaluate('R3_TEST.getState().passed[4]') is True)
 page.locator('#next').click()
 answer=json.loads((R/'play/data.json').read_text())['finalAnswer']
 for k,v in answer.items():page.locator('#f-'+k).select_option(v)
 page.locator('#submit').click();ok('solo receipt rendered',page.locator('#receipt').count()==1)
 page.locator('#ending').select_option('joint');ok('joint receipt changes response','联合签收' in page.locator('#receipt').inner_text())
 page.locator('#language').click();ok('language toggle preserves completion',page.evaluate('R3_TEST.getState().completed') is True and 'Joint delivery' in page.locator('#receipt').inner_text())
 page.screenshot(path=str(R/'qa/browser_final.png'),full_page=True)
 final=page.evaluate('R3_TEST.getState()')
 page.evaluate("R3_TEST.setState({...R3_ENGINE.initial(),stage:3,choice:'challenge'})")
 ok('challenge has unsolved orientation',page.evaluate('R3_TEST.getState().inputs[3].mirror') is True)
 for _ in range(4):page.locator('#hint').click()
 ok('hint level capped at three',page.evaluate('R3_TEST.getState().hints[3]')==3)
 page.on('dialog',lambda d:d.accept());page.locator('#assist').click();ok('assistance is recorded',page.evaluate('R3_TEST.getState().assisted[3]') is True)
 ok('desktop session does not auto-claim field evidence',not any(page.evaluate('R3_TEST.getState().observed').values()))
 page.evaluate('s=>R3_TEST.setState(s)',final)
 page.set_viewport_size({'width':390,'height':844});ok('mobile has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
 page.screenshot(path=str(R/'qa/browser_mobile.png'),full_page=True)
 ok('no JavaScript exceptions',not errors)
 storage_warning=page.locator('#storageWarning').is_visible()
 for lang in ['zh','en']:
  pr=b.new_page();pr.set_content((R/f'play/print_{lang}.html').read_text(),wait_until='load');pr.emulate_media(media='print');pr.pdf(path=str(R/f'R3_Player_Kit_{lang.upper()}.pdf'),format='A4',print_background=True,prefer_css_page_size=True)
  ok(f'{lang} print DOM pages=13',pr.locator('.page').count()==13);pr.close()
 b.close()
report={'date':'2026-10-20','checks':checks,'javascript_errors':errors,'scope':'Chromium /usr/bin/chromium; exact standalone HTML injected via set_content because file navigation is blocked. Actual hosted navigation, native persistent storage, and field play not validated.','storage_warning_visible':storage_warning}
(R/'qa/browser_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'checks':len(checks),'passed':len(checks),'storage_warning_visible':storage_warning},ensure_ascii=False))

"""Exercise the actual standalone file in Chromium using visible controls.

Requires playwright. Set CHROMIUM_PATH if the executable is not managed by Playwright.
This is software verification, never a visitor blind test or a field test.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, tempfile, sys
_runtime=Path(__file__).resolve().parents[3]/"runtime-python"
if _runtime.is_dir():sys.path.insert(0,str(_runtime))
from playwright.sync_api import sync_playwright

R = Path(__file__).resolve().parents[1]
D = json.loads((R / 'play/data.json').read_text(encoding='utf-8'))
checks, errors, network_requests = [], [], []

def ok(name, condition, detail=None):
    if not condition:
        raise AssertionError(name)
    checks.append({'name': name, 'result': 'PASS', 'detail': detail})

def state(page):
    return page.evaluate('R7_TEST.getState()')

def pick_fields(page, answers):
    for k, value in answers.items():
        if k not in ('order', 'rotation', 'mirror'):
            page.locator('#f-' + k).select_option(str(value))

def open_game(browser, mobile=False, disable_storage=False):
    context = browser.new_context(viewport={'width': 390 if mobile else 1120, 'height': 844 if mobile else 900}, accept_downloads=True)
    if disable_storage:
        context.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('storage unavailable')}})")
    context.set_offline(True)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('request', lambda request: network_requests.append(request.url) if request.url.startswith(('http:', 'https:')) else None)
    page.goto((R / 'R7_Offline.html').as_uri(), wait_until='load')
    return context, page

def solve_s3(page, choice):
    page.locator('[data-nav="2"]').click()
    pick_fields(page, D['stages'][2]['answer'])
    page.locator('#submit').click()
    page.locator('#' + choice).click()

def finish(page, ending):
    page.locator('[data-nav="5"]').click()
    pick_fields(page, D['finalAnswer'])
    page.locator('#ending').select_option(ending)
    page.locator('#submit').click()

with sync_playwright() as p:
    launch = {'headless': True, 'args': ['--no-sandbox']}
    _local=Path(__file__).resolve().parents[3]/'runtime-browsers/chromium_headless_shell-1161/chrome-linux/headless_shell'
    if os.environ.get('CHROMIUM_PATH') or _local.exists():
        launch['executable_path'] = os.environ.get('CHROMIUM_PATH') or str(_local)
    browser = p.chromium.launch(**launch)
    browser_version = browser.version
    context, page = open_game(browser)
    ok('standalone file renders actual title', page.locator('#title').inner_text() == D['title']['zh'])
    ok('opening makes fictional status explicit', D['fictionNotice']['zh'] in page.locator('.fiction-notice').inner_text())
    page.locator('#submit').click()
    ok('empty submission rejected visibly', page.locator('.feedback.bad').count() == 1)
    page.locator('#team').fill('UI Verification Team')
    page.reload(wait_until='load')
    ok('file URL localStorage survives reload', page.locator('#team').input_value() == 'UI Verification Team')
    for card in ['tower', 'sign', 'roof']:
        page.locator('[data-card="' + card + '"]').click()
    pick_fields(page, D['stages'][0]['answer'])
    page.locator('#submit').click()
    ok('S01 solved with card controls', state(page)['passed'].get('0') is True and page.locator('#stageReveal').is_visible())
    page.locator('#next').click()
    page.locator('#flip').click()
    page.locator('#rotate').click()
    pick_fields(page, D['stages'][1]['answer'])
    page.locator('#submit').click()
    ok('S02 solved with rotation and flip controls', state(page)['passed'].get('1') is True)
    page.locator('#next').click()
    ok('S03 memorial identification diagram visible', page.locator('.diagram.memorial svg').count() == 1)
    pick_fields(page, D['stages'][2]['answer'])
    page.locator('#f-dateMeaning').select_option('exact')
    page.locator('#submit').click()
    ok('exact 1995 overclaim rejected', page.locator('.feedback.bad').count() == 1)
    page.locator('#f-dateMeaning').select_option('lower_bound')
    page.locator('#submit').click()
    page.locator('#share').click()
    page.locator('#next').click()
    s = state(page)
    ok('share calibrates first park entry', s['inputs']['3']['rotation'] == 0 and s['inputs']['3']['mirror'] is False)
    page.locator('.sources summary').click()
    source_text = page.locator('.sources').inner_text()
    ok('S04 sources are directly available without a later-stage gate', all(token in source_text for token in D['stages'][3]['sources']))
    page.locator('#submit').click()
    ok('calibration does not solve park interpretation', page.locator('.feedback.bad').count() == 1 and not state(page)['passed'].get('3'))
    pick_fields(page, D['stages'][3]['answer'])
    page.locator('#submit').click()
    ok('S04 camera building and purpose accepted', state(page)['passed'].get('3') is True)
    page.locator('#next').click()
    for card in ['kisho', 'hisamatsu', 'chitose', 'meiji']:
        page.locator('[data-card="' + card + '"]').click()
    pick_fields(page, D['stages'][4]['answer'])
    page.locator('#submit').click()
    ok('S05 name chain and relocation accepted', state(page)['passed'].get('4') is True)
    finish(page, 'solo')
    ok('full route reaches ending with receipt closed by default', state(page)['completed'] and not page.locator('#receipt').is_visible())
    page.locator('#receiptDisclosure summary').click()
    ok('receipt opens only after explicit request', page.locator('#receipt').is_visible())
    if D.get('finale'):
        for index in range(1, len(D['finale'])):
            page.locator('#nextScene').click()
            ok('finale scene ' + str(index + 1) + ' accessible', page.evaluate('R7_TEST.getScene()') == index)
        page.locator('#replayScenes').click()
        ok('finale can be replayed without new answers', page.evaluate('R7_TEST.getScene()') == 0 and state(page)['completed'])
    page.locator('#ending').select_option('joint')
    page.locator('#receiptDisclosure summary').click()
    ok('ending selection updates completed receipt', D['ending']['joint']['zh'] in page.locator('#receipt').inner_text())
    page.locator('#language').click()
    page.locator('#receiptDisclosure summary').click()
    ok('English retains completion and uses translated ending', state(page)['completed'] and D['ending']['joint']['en'] in page.locator('#receipt').inner_text())
    page.screenshot(path=str(R / 'qa/runtime_desktop.png'), full_page=True)
    for width in [390, 320]:
        page.set_viewport_size({'width': width, 'height': 844})
        ok('no horizontal overflow at ' + str(width), page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
    page.set_viewport_size({'width': 390, 'height': 844})
    page.screenshot(path=str(R / 'qa/runtime_mobile.png'), full_page=True)
    with page.expect_download() as download_info:
        page.locator('#saveFile').click()
    download = download_info.value
    exported = json.loads(Path(download.path()).read_text())
    ok('export contains release and all progress', exported['product'] == D['version'] and exported['state']['completed'])
    context.close()

    for choice in ['challenge', 'share']:
        for ending in ['solo', 'joint']:
            context, page = open_game(browser)
            solve_s3(page, choice)
            page.locator('#next').click()
            pose = state(page)['inputs']['3']
            expected = (0, False) if choice == 'share' else (3, True)
            ok(choice + '+' + ending + ' correct park initial state', (pose['rotation'], pose['mirror']) == expected)
            finish(page, ending)
            s = state(page)
            ok(choice + '+' + ending + ' gets full early ending', s['completed'] and s['choice'] == choice and s['ending'] == ending and len(s['passed']) == 1)
            ok(choice + '+' + ending + ' all seven facts and souvenir retained', page.locator('#receipt dd').count() == 7 and page.locator('#receipt svg').count() == 1)
            for index,scene in enumerate(D['finale']):
                ok(choice + '+' + ending + ' full scene ' + str(index+1), page.locator('#finale h3').first.inner_text() == scene['title']['zh'])
                ok(choice + '+' + ending + ' receipt hidden while reading scene ' + str(index+1), not page.locator('#receipt').is_visible())
                if index < len(D['finale'])-1: page.locator('#nextScene').click()
            context.close()

    context, page = open_game(browser)
    solve_s3(page, 'share')
    page.locator('#next').click()
    page.locator('#rotate').click()
    page.locator('[data-nav="2"]').click()
    page.locator('#challenge').click()
    page.locator('[data-nav="3"]').click()
    ok('strategy change does not reset begun park work', state(page)['inputs']['3']['rotation'] == 1)
    for _ in range(4):
        page.locator('#hint').click()
    ok('hints are free and capped at three', state(page)['hints']['3'] == 3)
    page.on('dialog', lambda dialog: dialog.accept())
    page.locator('#assist').click()
    ok('stage assistance is recorded and story remains complete', state(page)['assisted'].get('3') is True and page.locator('#stageReveal').is_visible())
    page.locator('[data-nav="5"]').click()
    page.locator('#assist').click()
    ok('final assistance retains full receipt and finale', state(page)['completed'] and state(page)['assisted'].get('5') is True and page.locator('#receiptDisclosure').is_visible())
    ok('desktop never auto-claims on-site evidence', not any(state(page)['observed'].values()))
    context.close()

    context, page = open_game(browser)
    for card in ['tower', 'sign', 'roof']:
        page.locator('[data-card="' + card + '"]').click()
    pick_fields(page, D['stages'][0]['answer'])
    page.locator('#submit').click()
    page.locator('#clearOrder').click()
    ok('editing solved answer removes stale success display', page.locator('#stageReveal').count() == 0 and not state(page)['passed'].get('0'))
    with tempfile.TemporaryDirectory() as folder:
        bad = Path(folder) / 'malformed.json'
        bad.write_text(json.dumps({'version':'R3.1','inputs':{'0':{'order':['unknown_card']}}}))
        page.locator('#fileInput').set_input_files(str(bad))
        page.wait_for_function("document.querySelector('#importMessage').hidden===false")
        ok('unknown imported card is safely filtered', state(page)['inputs']['0'].get('order') == [] and page.locator('#submit').is_visible())
        valid = Path(folder) / 'valid.json'
        valid.write_text(json.dumps(exported))
        page.locator('#fileInput').set_input_files(str(valid))
        page.wait_for_function('R7_TEST.getState().completed===true')
        ok('export imports completion without automatically exposing receipt', state(page)['completed'] and not page.locator('#receipt').is_visible())
    context.close()
    context, page = open_game(browser, disable_storage=True)
    page.locator('#team').fill('No-storage test')
    ok('storage unavailable gives truthful export fallback', page.locator('#storageWarning').is_visible() and page.locator('#saveFile').is_enabled())
    context.close()
    ok('no automatic network requests', not network_requests, network_requests)
    ok('no JavaScript exceptions', not errors, errors)
    browser.close()

report = {'generated_at':datetime.now(timezone.utc).isoformat(),'version':D['version'],'data_sha256':hashlib.sha256((R/'play/data.json').read_bytes()).hexdigest(),'bundle_sha256':hashlib.sha256((R/'R7_Offline.html').read_bytes()).hexdigest(),'app_sha256':hashlib.sha256((R/'play/app.js').read_bytes()).hexdigest(),'browser':'Chromium '+browser_version,'load_method':'actual local file:// URL with browser network forcibly offline','checks':checks,'javascript_errors':errors,'automatic_network_requests':network_requests,'scope':'UI controls, offline file loading, local persistence, hints, assistance, independent branches, early solution, import/export and responsive layout. No tourist blind test or on-site validation.'}
(R / 'qa/browser_results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'checks':len(checks),'passed':len(checks),'browser':browser_version},ensure_ascii=False))

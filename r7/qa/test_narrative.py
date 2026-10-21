"""Inspect actual narrative presentation and spoiler boundaries in both languages."""
from pathlib import Path
import hashlib,json,os,sys
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];scratch=R.parents[1]
if (scratch/'runtime-python').exists():sys.path.insert(0,str(scratch/'runtime-python'))
from playwright.sync_api import sync_playwright
D=json.loads((R/'content/game.json').read_text());checks=[];errors=[];screenshots=[]
proofdir=R/'qa/narrative_screenshots';proofdir.mkdir(exist_ok=True)
def ok(n,c):
    if not c:raise AssertionError(n)
    checks.append({'name':n,'result':'PASS'})
with sync_playwright() as p:
    launch={'headless':True,'args':['--no-sandbox']};exe=os.environ.get('CHROMIUM_PATH') or scratch/'runtime-browsers/chromium_headless_shell-1161/chrome-linux/headless_shell'
    if Path(exe).exists():launch['executable_path']=str(exe)
    browser=p.chromium.launch(**launch)
    for lang in ['zh','en']:
        context=browser.new_context(viewport={'width':390,'height':844});context.set_offline(True);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((R/'R7_Offline.html').as_uri())
        if lang=='en':page.locator('#language').click()
        for fig_id,spec in D.get('figures',{}).items():
            if spec.get('kind')!='handoff':continue
            # This presentation-only fixture uses the actual loaded module and content.
            context2=browser.new_context(viewport={'width':800,'height':600},reduced_motion='reduce');context2.set_offline(True)
            preview=context2.new_page();preview.goto((R/'R7_Offline.html').as_uri())
            preview.evaluate('(x)=>{document.querySelector("#main").innerHTML=R7_NARRATIVE.render(x.id,x.lang);R7_NARRATIVE.activate(document)}',{'id':fig_id,'lang':lang})
            image=preview.locator('#main svg[data-narrative]').first
            target=proofdir/(lang+'_'+fig_id+'_static.png');image.screenshot(path=str(target));screenshots.append(str(target.relative_to(R)))
            ok(lang+' '+fig_id+' reduced-motion static panels visible',image.is_visible() and preview.locator('.handoff-run').count()==0)
            context2.close()
        # Observe the real CSS animation at its beginning and completed state.
        # Pausing an existing browser animation makes the two proof images
        # deterministic without replacing the SVG or faking a motion class.
        motion_context=browser.new_context(viewport={'width':900,'height':900});motion_context.set_offline(True)
        motion=motion_context.new_page();motion.goto((R/'R7_Offline.html').as_uri())
        motion.evaluate('(lang)=>{document.querySelector("#main").innerHTML=R7_NARRATIVE.render("replay_uncut",lang);R7_NARRATIVE.activate(document)}',lang)
        motion.wait_for_function('document.querySelector(".handoff-lower").getAnimations().length>0')
        untouched=motion.evaluate('JSON.stringify(R7_TEST.getState())')
        dy=[]
        for point,time in [('start',0),('end',4000)]:
            value=motion.evaluate('(time)=>{const g=document.querySelector(".handoff-lower");const a=g.getAnimations()[0];a.pause();a.currentTime=time;return new DOMMatrix(getComputedStyle(g).transform).m42}',time)
            dy.append(value)
            target=proofdir/(lang+'_replay_uncut_animated_'+point+'.png')
            motion.locator('#main svg[data-narrative]').first.screenshot(path=str(target));screenshots.append(str(target.relative_to(R)))
        ok(lang+' actual put-back animation lowers frame by 58px',abs(dy[0]+58)<.1 and abs(dy[1])<.1)
        motion.locator('[data-story-replay]').click()
        ok(lang+' replay leaves all gameplay progress unchanged',untouched==motion.evaluate('JSON.stringify(R7_TEST.getState())'))
        motion_context.close()
        ok(lang+' opening contains no ending prose',not any(s['text'][lang] in page.locator('#main').inner_text() for s in D['finale']))
        for i,q in enumerate(D['stages']):
            page.evaluate('(x)=>{let s=R7_TEST.getState();s.stage=x;R7_TEST.setState(s)}',i)
            ok(lang+f' stage {i+1} before result hidden',page.locator('#stageReveal').count()==0)
            page.evaluate('(x)=>{let s=R7_TEST.getState();s.inputs[x.i]=x.answer;s.passed[x.i]=true;R7_TEST.setState(s)}',{'i':i,'answer':q['answer']})
            ok(lang+f' stage {i+1} authored result visible',q['success'][lang] in page.locator('#stageReveal').inner_text())
            ok(lang+f' stage {i+1} fits 390px',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        page.evaluate('(a)=>{let s=R7_TEST.getState();s.stage=5;s.inputs[5]=a;s.completed=true;R7_TEST.setState(s)}',D['finalAnswer'])
        for i,scene in enumerate(D['finale']):
            ok(lang+f' final scene {i+1} text correct',scene['text'][lang] in page.locator('#finale').inner_text())
            ok(lang+f' final scene {i+1} receipt default closed',not page.locator('#receipt').is_visible())
            for width in [390,320]:
                page.set_viewport_size({'width':width,'height':844});ok(lang+f' scene {i+1} fits {width}px',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
            if i<len(D['finale'])-1:page.locator('#nextScene').click()
        page.locator('#receiptDisclosure summary').click();ok(lang+' explicit receipt shows complete seven facts',page.locator('#receipt').is_visible() and page.locator('#receipt dd').count()==7)
        context.close()
    # Print source follows the visible page order, not a secret traversal gate.
    for lang in ['zh','en']:
        page=browser.new_page();page.goto((R/f'play/print_{lang}.html').as_uri());prep=page.locator('#rules').inner_text();first=page.locator('#opening').inner_text()
        ok(lang+' preparation excludes ending prose',not any(x['text'][lang] in prep+first for x in D['finale']))
        ok(lang+' midgame page excludes ending responses',not any(x[lang] in page.locator('#choices').inner_text() for x in D['ending'].values()))
        ok(lang+' fifteen hints initially folded',page.locator('[id^="h"] details.hint-fold:not([open])').count()==15)
        order=page.locator('.page').evaluate_all('(xs)=>xs.map(x=>x.id)')
        ok(lang+' souvenir appears after all finale scenes',order.index('souvenir')>order.index('ending'+str(len(D['finale']))))
        page.close()
    browser.close()
ok('no JavaScript presentation errors',not errors)
out={'generated_at':datetime.now(timezone.utc).isoformat(),'version':D['version'],'checks':checks,'javascript_errors':errors,'screenshots':screenshots,'visual_review':'Rendered screenshots require independent visual inspection; this test does not certify image readability.','scope':'Actual UI text, responsive narrative display and print spoiler boundaries only; no claim of story quality, physical usability or field testing.'}
for key,name in [('data_sha256','play/data.json'),('bundle_sha256','R7_Offline.html'),('app_sha256','play/app.js')]:out[key]=hashlib.sha256((R/name).read_bytes()).hexdigest()
(R/'qa/narrative_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':len(checks),'passed':len(checks)}))

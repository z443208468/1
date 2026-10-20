"""Render and check narrative visuals in the actual offline game.
The output is technical/visual verification, not an audience or field test.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'play/data.json').read_text(encoding='utf-8'))
OUT=R/'qa/caper_screenshots';OUT.mkdir(exist_ok=True)
checks=[];errors=[]
def ok(name,condition,detail=None):
    if not condition:raise AssertionError(name)
    checks.append({'name':name,'result':'PASS','detail':detail})
def snap(page,selector,name):
    page.locator(selector).first.screenshot(path=str(OUT/(name+'.png')),animations='allow')
def fill(page,answer):
    for k,v in answer.items():
        if k not in ('order','rotation','mirror'):page.locator('#f-'+k).select_option(str(v))
with sync_playwright() as p:
    opts={'headless':True,'args':['--no-sandbox']}
    if os.getenv('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
    b=p.chromium.launch(**opts)
    c=b.new_context(viewport={'width':1120,'height':900});page=c.new_page()
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('dialog',lambda d:d.accept())
    page.goto((R/'R6_Offline.html').as_uri(),wait_until='load')
    ok('opening graphic is data-bound',page.locator('[data-caper-figure="caper_open"]').count()==1)
    page.evaluate("document.querySelector('.caper-motion svg').getAnimations({subtree:true}).forEach(a=>{a.pause();a.currentTime=0})")
    snap(page,'[data-caper-figure="caper_open"] .caper-motion','opening_narrow_start')
    initial_river=page.locator('[data-caper-figure="caper_open"] .caper-motion [data-river-source]').inner_html()
    page.evaluate("document.querySelector('.caper-motion svg').getAnimations({subtree:true}).forEach(a=>{a.pause();a.currentTime=3600})")
    snap(page,'[data-caper-figure="caper_open"] .caper-motion','opening_narrow_covered')
    ok('opening masks without deleting river source',page.locator('[data-caper-figure="caper_open"] .caper-motion [data-river-source]').inner_html()==initial_river)
    ok('opening ends with pale blank sheet back',page.locator('.caper-motion .sheet-surface').evaluate("e=>getComputedStyle(e).fill")=='rgb(231, 220, 200)')
    for i,s in enumerate(D['stages']):
        page.locator('[data-nav="'+str(i)+'"]').click()
        before=s.get('beforeFigure');after=s.get('afterFigure')
        ok(s['id']+' before graphic is displayed',bool(before) and page.locator('[data-caper-figure="'+before+'"]').count()==1)
        snap(page,'[data-caper-figure="'+before+'"]',str(i+1)+'_before_'+before)
        page.locator('#assist').click()
        ok(s['id']+' successful action changes graphic',bool(after) and page.locator('#stageReveal [data-caper-figure="'+after+'"]').count()==1)
        snap(page,'#stageReveal [data-caper-figure="'+after+'"]',str(i+1)+'_after_'+after)
    page.locator('[data-nav="5"]').click();fill(page,D['finalAnswer']);page.locator('#submit').click()
    ok('finale has exactly six data-driven scenes',len(D.get('finale',[]))==6)
    for i in range(6):
        name='caper'+str(i)
        ok(name+' is visible after existing final answer',page.locator('#finale [data-caper="'+name+'"]').count()==1)
        page.locator('#finale .caper-figure').scroll_into_view_if_needed()
        page.wait_for_timeout(120)
        # Pause each animation at its meaningful end or bow keyframe for review.
        page.evaluate("""(i)=>document.querySelector('#finale svg').getAnimations({subtree:true}).forEach(a=>{a.pause();a.currentTime=i===5?2400:4000})""",i)
        snap(page,'#finale .caper-figure',name)
        if i==1:
            same=page.locator('#finale [data-river-source]').inner_html()==initial_river
            ok('same river source survives the repeated wide-frame move',same)
            ok('wide-frame repetition shows same pale back',page.locator('#finale .sheet-surface').evaluate("e=>getComputedStyle(e).fill")=='rgb(231, 220, 200)')
            ok('wide frame includes holder and feet with no narrow matte',page.locator('#finale [data-person="utsuro"]').count()==1 and page.locator('#finale [mask]').count()==0)
        if i<5:page.locator('#nextScene').click()
    page.locator('#replayScenes').click()
    ok('six-scene performance can restart without new input',page.evaluate('R6_TEST.getScene()')==0 and page.evaluate('R6_TEST.getState().completed'))
    for width in (390,320):
        page.set_viewport_size({'width':width,'height':844})
        for idx in (0,1,3,5):
            page.locator('[data-nav="'+str(idx)+'"]').click()
            ok(str(width)+'px stage '+str(idx+1)+' has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        page.locator('#finale .caper-figure').scroll_into_view_if_needed()
        page.wait_for_timeout(120)
        page.evaluate("document.querySelector('#finale svg').getAnimations({subtree:true}).forEach(a=>{a.pause();a.currentTime=4000})")
        snap(page,'#finale','finale_'+str(width)+'px')
    c.close()
    c=b.new_context(viewport={'width':390,'height':844},reduced_motion='reduce');page=c.new_page()
    page.goto((R/'R6_Offline.html').as_uri(),wait_until='load')
    ok('reduced motion displays explicit opening before/covered frames',page.locator('.caper-still').is_visible() and not page.locator('.caper-motion').is_visible())
    snap(page,'[data-caper-figure="caper_open"]','opening_reduced_motion_390px')
    ok('reduced opening has no active animations',page.evaluate("document.querySelector('[data-caper-figure]').getAnimations({subtree:true}).filter(a=>a.playState==='running').length===0"))
    page.locator('[data-nav="5"]').click();fill(page,D['finalAnswer']);page.locator('#submit').click()
    for i in range(6):
        ok('reduced motion '+str(i+1)+' retains visible illustration',page.locator('#finale .caper-figure svg').is_visible())
        ok('reduced motion '+str(i+1)+' has no active animations',page.evaluate("document.querySelector('#finale').getAnimations({subtree:true}).filter(a=>a.playState==='running').length===0"))
        if i<5:page.locator('#nextScene').click()
    snap(page,'#finale','finale_bow_reduced_motion_390px')
    page.locator('#language').click()
    for width in (390,320):
        page.set_viewport_size({'width':width,'height':844})
        ok('English reduced finale at '+str(width)+'px has no overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        snap(page,'#finale','finale_bow_en_'+str(width)+'px')
    ok('narrative visuals introduce no JavaScript errors',not errors,errors)
    c.close();b.close()
# Contact sheets are review conveniences; the individual screenshots remain the evidence.
try:
    from PIL import Image, ImageDraw
    pairs=['opening_narrow_start','opening_narrow_covered','1_before_fragments','1_after_joined','2_before_riverWrong','2_after_riverBoth','3_before_oldClaim','3_after_modernReference','4_before_parkCrop','4_after_parkFull','5_before_oldExit','5_after_lineageJoined']
    for output,names in [('before_after_contact',pairs),('finale_contact',['caper'+str(i) for i in range(6)])]:
        rows=[];height=0
        for i in range(0,len(names),2):
            images=[]
            for name in names[i:i+2]:
                im=Image.open(OUT/(name+'.png')).convert('RGB');im.thumbnail((540,440));images.append((name,im))
            row_height=max(im.height for _,im in images)+36;rows.append((images,row_height));height+=row_height
        sheet=Image.new('RGB',(1100,height),(225,229,225));draw=ImageDraw.Draw(sheet);y=0
        for images,row_height in rows:
            for j,(name,im) in enumerate(images):
                x=10+j*550;draw.text((x,y+7),name,fill='black');sheet.paste(im,(x,y+29))
            y+=row_height
        sheet.save(OUT/(output+'.png'))
except ImportError:
    pass
report={'generated_at':datetime.now(timezone.utc).isoformat(),'version':D['version'],'data_sha256':hashlib.sha256((R/'play/data.json').read_bytes()).hexdigest(),'bundle_sha256':hashlib.sha256((R/'R6_Offline.html').read_bytes()).hexdigest(),'app_sha256':hashlib.sha256((R/'play/app.js').read_bytes()).hexdigest(),'checks':checks,'screenshots':str(OUT.relative_to(R)),'scope':'Narrative graphic binding, opening/repeated action identity, six-scene navigation, 320/390px layout and reduced motion in actual file:// runtime. This does not establish story quality or visitor response.'}
(R/'qa/caper_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'version':D['version'],'data_sha256':hashlib.sha256((R/'play/data.json').read_bytes()).hexdigest(),'bundle_sha256':hashlib.sha256((R/'R6_Offline.html').read_bytes()).hexdigest(),'app_sha256':hashlib.sha256((R/'play/app.js').read_bytes()).hexdigest(),'checks':len(checks),'passed':len(checks),'screenshots':str(OUT)},ensure_ascii=False))

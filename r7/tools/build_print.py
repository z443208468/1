#!/usr/bin/env python3
"""Generate content-driven, bilingual paper kits from the R7 authored source.

Only the original five puzzle mechanisms and physical material categories are
used. Hints, post-answer scenes, and final spoilers occupy separate leaves.
"""
from __future__ import annotations
import html, hashlib, json, os, re, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'content/game.json'
CSS=(ROOT/'tools/print_style.css').read_text()+'''\n.story-page .dialogue{font-size:10pt}.hint-fold{border-top:.3mm dashed #82958f;padding:5mm 2mm;min-height:46mm}.hint-fold summary{font-weight:bold}.spoiler-page{border-top:2mm solid #a3442e}.original-art{max-width:135mm;margin:4mm auto}.original-art svg{width:100%;height:auto}.finale-page .original-art{max-width:139mm}.souvenir-face svg{height:44mm}.finale-page h2{margin-top:2mm}.paper-hint{display:none;border-top:.3mm dashed #82958f;padding:5mm 2mm;min-height:46mm}@media print{details.hint-fold{display:none!important}.paper-hint{display:block!important}}\n'''
def esc(x):return html.escape(str(x))
def txt(x,l):
    if isinstance(x,dict):
        if l not in x:raise ValueError(f'Missing {l} translation: {x}')
        return str(x[l])
    return str(x or '')
class Kit:
    def __init__(self,d,f,l):self.d,self.f,self.l,self.pages=d,f,l,[];self.src={x['id']:x for x in d['sources']}
    def T(self,z,e):return z if self.l=='zh' else e
    def text(self,x):return txt(x,self.l)
    def p(self,x,cls=''):return ''.join(f'<p class="{cls}">{esc(v)}</p>' for v in self.text(x).split('\n') if v)
    def art(self,n,cls='original-art'):
        svg=self.f.get(self.l,{}).get(n) or self.f.get(n,'')
        return f'<div class="{cls}">{svg}</div>' if svg else ''
    def talk(self,rows):return '<div class="dialogue">'+''.join('<p>'+('<b>'+esc(self.text(r['speaker']))+'</b>' if r.get('speaker') else '')+esc(self.text(r['text']))+'</p>' for r in rows or [])+'</div>'
    def add(self,key,title,body,sub='',cls=''):
        if any(x['key']==key for x in self.pages):raise ValueError('duplicate page '+key)
        self.pages.append(dict(key=key,title=title,body=body,sub=sub,cls=cls))
    def ref(self,key):return self.T('第','p. ')+'{{page:'+key+'}}'+self.T('页','')
    def fields(self,fs):
        return '<table class="fields compact">'+''.join('<tr><th>'+esc(self.text(f['label']))+'</th><td>'+''.join('<div class="field-option"><span class="field-check"></span>'+esc(self.text(l))+'</div>' for _,l in f['options'])+'</td></tr>' for f in fs)+'</table>'
    def facts(self,ids):
        out=''
        for sid in ids:
            s=self.src[sid];out+='<div class="source"><b>'+esc(sid)+' · '+esc(self.text(s['title']))+'</b>'+self.p(s['fact'])+('<div class="url">'+esc(s['url'])+'</div>' if s.get('url') else '')+'</div>'
        return out
    def source_ref(self,q):return '<p class="quiet">'+self.T('本关随身史料：','History cards for this stop: ')+', '.join(q['sources'])+' · '+self.ref('sources1')+self.T('起。资料已印在包内，无需联网。',' onward. All necessary facts are printed; no network is required.')+'</p>'
    def fold(self,title,body):return '<details class="hint-fold"><summary>'+esc(title)+'</summary><div>'+body+'</div></details><div class="paper-hint"><b>'+esc(title)+'</b>'+body+'</div>'
    def help_ref(self,n):return '<div class="note small">'+self.T('需要帮助时才翻到','For optional help, turn to ')+self.ref('h'+str(n))+self.T('；先按需打开提示1、2、3。完成后到',' and open hints 1, 2 and 3 only as needed. After answering, use ')+self.ref('r'+str(n))+self.T('核对并读结果。',' to check and read the consequence.')+'</div>'
    def answer(self,q):
        a=q['answer'];ls=[]
        if 'order' in a:
            labels={c['id']:self.text(c['label']) for c in q['cards']};ls.append(' → '.join(labels[i] for i in a['order']))
        if 'rotation' in a:ls.append(self.T('图卡基准：朝向0、正面；按本关示意锚点核对。','Card reference: orientation 0, unmirrored; verify against the diagram anchors.'))
        for f in q['fields']:ls.append(self.text(f['label'])+': '+self.text(next(t for v,t in f['options'] if v==a[f['id']])))
        return '<div class="answer"><b>'+self.T('完整核对','Complete solution')+'</b>'+''.join('<p>'+esc(s)+'</p>' for s in ls)+'</div>'
    def build(self):
        d=self.d;paper=d.get('paper',{});qs=d['stages'];T=self.T
        cover=self.p(d['subtitle'],'sub')+self.art(d.get('openingFigure'))+self.p(d['opening'])+self.p(d['fictionNotice'],'quiet')
        cover+='<div class="note small">'+T('从下一页准备，再按章节阅读。提示与结果分开放置，终章材料留在最后，准备时不需要翻看。','Prepare on the next page, then follow the chapters. Hints and outcomes are on separate leaves. Ending materials stay at the back and need not be viewed during preparation.')+'</div>'
        self.add('cover',self.text(d['title']),cover,cls='cover')
        prep=T('一组2—4人，每组仅打印一种语言。A4单面、100%原尺寸，关闭“适合页面”。带笔、夹板、纸夹；出发前剪好标注的原谜题活动件。终章的回执与纪念片在结束后再取用和裁剪，不用于通关。','For 2–4 people, print one language per team. Use A4, single-sided, at 100%; disable fit-to-page. Bring a pen, clipboard and clips. Cut the marked puzzle pieces before leaving. The receipt and souvenir at the end are used and cut only after the ending; they are not needed to solve the game.')
        rules=self.p(paper.get('preparation',prep))+'<ol>'+''.join('<li>'+esc(self.text(r))+'</li>' for r in d.get('rules',[]))+'</ol>'+self.p(d['safety'],'small')
        rules+='<h2>'+T('准备清单','Preparation checklist')+'</h2><p class="small">'+T('只准备下列原机制材料：街景三卡、三条横景与原框；河图两面及双标签；双时间轨与下界条；公园两面图、四相机片、两用途片、外墙参照；四剧院名条与1928迁址条。','Prepare only these original mechanism materials: three view cards, three horizontal scene strips and frame; two river-map faces and two labels; two timelines and a lower-bound strip; two park-map faces, four camera markers, two purpose labels and facade reference; four theatre-name strips and the 1928 relocation strip.')+'</p>'
        rules+='<p>'+T('纸包使用：任务页和活动件在前，史料随时可查；提示页按折线遮住后续提示，结果页在作答后阅读。','Paper play: keep tasks and pieces in front, consult sources freely, fold the hint page to cover later hints, and read the outcome page after answering.')+'</p><p>'+T('小组／日期：________________','Team / date: ________________')+'</p>'
        self.add('rules',T('出发前准备','Before you leave'),rules)
        opening=self.talk(d.get('openingDialogue',[]))+self.p(paper.get('openingInstruction',''))
        for key in ['originalCaption','parkAnnotation']:
            if d.get(key):opening+='<div class="claim">'+self.p(d[key])+'</div>'
        self.add('opening',self.text(d.get('openingTitle',d['title'])),opening,T('故事开始 · 阅读页','The story begins · reading page'))
        for n,s in enumerate(qs,1):
            body=self.talk(s.get('before',[]))+self.p(s['intro'])+self.art(s.get('beforeFigure'))+self.p(s['operation'],'action')+self.p(s.get('prompt',''),'small')+self.source_ref(s)
            actions=paper.get('stageActions',[])
            if len(actions)>=n:body+=self.p(actions[n-1],'small')
            self.add('s'+str(n),self.text(s['title']),body,self.text(s['site']),'story-page')
            getattr(self,'materials_'+str(n))(s)
        self.add('finalintro',self.text(d['finalTitle']),self.p(d['finalIntro'])+self.p(paper.get('finalInstruction','')),T('最后的行动','The final action'))
        choices='<div class="choice">'+''.join('<p>□ '+esc(self.text(d['endingLabels'][k]))+'</p>' for k in ['solo','joint'])+'</div>'
        self.add('final',T('完整判断单','Your complete account'),self.fields(d['finalFields'])+choices+'<p class="small">'+T('七项判断成立即可进入终章。没有五章印章要求，正确早解同样有效。核对页：','All seven conclusions lead to the ending. No chapter stamps are required; a correct early solution is accepted. Solution check: ')+self.ref('finalcheck')+'</p>')
        ids=list(self.src)
        for start in range(0,len(ids),4):self.add('sources'+str(start//4+1),T('随身史料','History cards')+' · '+str(start//4+1),self.facts(ids[start:start+4]),T('事实与角色主张分别阅读','Distinguish facts from fictional claims'),'sources-page')
        mid='<div class="spoiler-header">'+T('仅在第三关完成后读取你选择的回应','After Stop 3, read only the response you selected')+'</div>'
        for k in ['challenge','share']:mid+='<h2>'+esc(self.text(d['choiceLabels'][k]))+'</h2>'+self.p(d['choiceResponses'][k])
        self.add('choices',T('第三关之后的选择','Your choice after Stop 3'),mid)
        for n,s in enumerate(qs,1):
            hints='<div class="spoiler-header">'+T('按需揭开；完整答案在另一页','Reveal as needed; the full solution is on a separate page')+'</div><p class="small">'+T('纸上沿虚线向后折，遮住下面尚未使用的提示；电子版逐个展开。三个提示全部免费。','On paper, fold backward at the dashed lines to cover unused hints below. On screen, expand them individually. All three are free.')+'</p>'
            for i,h in enumerate(s['hints'],1):hints+=self.fold(T('免费提示 ','Free hint ')+str(i),self.p(h))
            hints+='<p class="quiet">'+T('答案与行动结果：','Solution and consequence: ')+self.ref('r'+str(n))+'</p>'
            self.add('h'+str(n),T('提示 ','Hints ')+str(n).zfill(2),hints,cls='hint-page')
            result='<div class="spoiler-header">'+T('作答后阅读 · 含本关答案与故事结果','Read after answering · contains this stop’s solution and consequence')+'</div>'+self.answer(s)+self.p(s['success'])+self.art(s.get('afterFigure'))+self.talk(s.get('after',[]))+'<div class="note">'+self.p(s['lead'])+'</div>'
            if n==3:result+='<p class="small">'+T('中段选择回应：','Midgame responses: ')+self.ref('choices')+'</p>'
            self.add('r'+str(n),T('行动结果 ','Consequence ')+str(n).zfill(2),result,cls='hint-page spoiler-page')
        rows=[]
        for f in d['finalFields']:rows.append('<tr><th>'+esc(self.text(f['label']))+'</th><td>'+esc(self.text(next(t for v,t in f['options'] if v==d['finalAnswer'][f['id']])))+'</td></tr>')
        finalcheck='<div class="spoiler-header">'+T('终章核对 · 含最终答案','Finale solution · contains final answers')+'</div><table>'+''.join(rows)+'</table><p>'+T('需要时可直接使用完整答案作为辅助，完整真相、终章与纪念内容不减少。接着从','Use the complete answer as assistance if needed; the truth, ending and souvenir remain complete. Continue at ')+self.ref('ending1')+T('顺序阅读。',' and read in order.')+'</p>'
        self.add('finalcheck',T('终章入口','The finale'),finalcheck,cls='spoiler-page')
        for n,scene in enumerate(d['finale'],1):
            body='<div class="spoiler-header">'+T('终章 · 按顺序阅读','FINALE · Read in order')+'</div>'+self.art(scene.get('figure'))+self.p(scene['text'])+self.talk(scene.get('dialogue',[]))
            for key,labels in [('byChoice',d['choiceLabels']),('byEnding',d['endingLabels'])]:
                for k,v in scene.get(key,{}).items():body+='<h3>'+esc(self.text(labels[k]))+'</h3>'+self.p(v,'small')
            if scene.get('paperAction'):body+='<div class="note">'+self.p(scene['paperAction'])+'</div>'
            self.add('ending'+str(n),self.text(scene['title']),body,cls='finale-page spoiler-page')
        ending='<div class="spoiler-header">'+T('完整终章之后再使用；无需提前准备','Use after the complete ending; no advance preparation required')+'</div>'+self.p(d['paperEnding'],'small')
        for k in ['solo','joint']:ending+='<h3>'+esc(self.text(d['endingLabels'][k]))+'</h3>'+self.p(d['ending'][k],'small')
        self.add('endingresponses',T('留下最后的回应','The closing response'),ending,cls='spoiler-page')
        receipt='<div class="receipt" data-material="receipt"><h2>'+T('案件回执','CASE RECEIPT')+'</h2>'
        for f in d['finalFields']:receipt+='<p>'+esc(self.text(f['label']))+': ______________________________</p>'
        receipt+='<p>'+T('小组／落款：________________','Team / signature: ________________')+'</p></div>'
        souvenir_title=self.text(paper.get('souvenirTitle',d['title']))
        receipt+='<h2>'+T('可折叠纪念片','Foldable souvenir')+'</h2><div class="souvenir" data-material="souvenir"><div class="souvenir-face"><b>'+esc(souvenir_title)+'</b>'+self.f['scene']+'</div><div class="souvenir-face"><b>'+T('我们留下的记录','OUR RECORD')+'</b>'+self.p(paper.get('souvenirText',T('小组：________\n日期：________','Team: ________\nDate: ________')),'small')+'</div></div><p class="cut-label">'+T('单面打印；此时再沿外框剪下，中线对折。图面朝外，折后约86×67毫米。','Single-sided print. Cut the outside border now and fold the centre line, faces outward. Folded size about 86 × 67 mm.')+'</p>'
        self.add('souvenir',T('回执与纪念','Receipt and souvenir'),receipt,cls='spoiler-page')
    def materials_1(self,s):
        T=self.T
        cards='<div class="cards">'+''.join('<div class="card"><b>'+esc(self.text(c['label']))+'</b>'+self.f[c['icon']]+'</div>' for c in s['cards'])+'</div>'
        self.add('s1work',T('01A · 街景识别卡','01A · View cards'),cards+'<div class="track">'+T('顺序','Order')+': ______ → ______ → ______</div>'+self.fields(s['fields'])+self.help_ref(1),T('物料与作答','Materials and answers'))
        inner=self.f['scene'].split('>',1)[1].rsplit('</svg>',1)[0];pieces=[]
        for c in s['cards']:
            x={'tower':0,'sign':200,'roof':400}[c['id']];svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} 0 200 180">{inner}</svg>'
            pieces.append('<div class="scene-piece" data-material="scene-strip"><div class="scene-piece-label">'+esc(self.text(c['label']))+'</div>'+svg+'</div>')
        body='<p>'+T('沿虚线剪下三条横景，按识别卡顺序横向接合，不剪开画面内部物件。','Cut the three scene strips and join them horizontally in the view-card order. Do not cut objects out of the illustration.')+'</p><div class="material-scene-row">'+''.join(pieces)+'</div><div class="assembly-frame" data-material="frame"><div class="assembly-area">'+T('将三条横景接入原框','JOIN THE THREE STRIPS INSIDE THIS FRAME')+'</div></div>'
        if self.d.get('originalCaption'):body+='<div class="claim">'+self.p(self.d['originalCaption'])+'</div>'
        self.add('s1pieces',T('01B · 原景与画框','01B · Scene and frame'),body)
    def materials_2(self,s):
        T=self.T
        a='<div class="diagram" data-material="river-A">'+self.f['riverA']+'</div><p class="small">'+T('转动图卡，与主河、支流、桥及北向核对。另一面在下一页；两面分开打印，无需双面套准。','Rotate the card and compare the main river, tributary, bridges and north. The alternate face is on the next page; no duplex registration is needed.')+'</p>'+self.fields(s['fields'])+self.help_ref(2)
        self.add('s2work',T('02A · 河图','02A · River card'),a)
        b='<div class="diagram" data-material="river-B">'+self.f['riverB']+'</div><div class="half"><div class="strip" data-material="river-label">稲瀬川 / INASE</div><div class="strip" data-material="river-label">隅田川 / SUMIDA</div></div><div class="track">'+T('舞台称呼','STAGE NAME')+': ________________</div><div class="track">'+T('真实借景地','REAL SCENERY')+': ________________</div><p class="quiet">'+T('N北；YANAGI柳桥；NOW现两国桥；OLD旧桥示意。只在允许停留且不挡通行处铺开纸件。','N north; YANAGI Yanagi Bridge; NOW present Ryogoku Bridge; OLD symbolic old bridge. Spread pieces only where stopping is permitted and traffic stays clear.')+'</p>'
        self.add('s2pieces',T('02B · 另一面与两张标签','02B · Alternate face and labels'),b)
    def materials_3(self,s):
        T=self.T
        body=self.art('memorial')+'<div class="track" data-material="life-track">'+T('人物生活：芭蕉迁居深川','PERSON: Basho moves to Fukagawa')+' ________</div><div class="track" data-material="facility-track">'+T('纪念设施：此庭园可以被拍到','SETTING: this garden can be photographed')+' ________</div><div class="strip" data-material="lower-bound">'+T('摄影下界：不早于 ______；确切年份仍未知。','LOWER BOUND: no earlier than ______; exact year unknown.')+'</div>'+self.fields(s['fields'])
        body+='<div class="choice"><b>'+T('完成核对后选择','Choose after checking')+'</b>'+''.join('<p>□ '+esc(self.text(self.d['choiceLabels'][k]))+'</p>' for k in ['challenge','share'])+'</div>'+self.help_ref(3)
        self.add('s3work',T('03A · 双时间轨','03A · Two timelines'),body,cls='timeline-work')
    def materials_4(self,s):
        T=self.T
        self.add('s4work',T('04A · 外墙参照与取景','04A · Facade and viewpoint'),self.art('facade')+self.fields(s['fields'])+self.help_ref(4))
        body='<p class="small">'+T('A、B卡背靠背夹起模拟翻面，或分别转动。先对照河边、大场地、体育中心；线条不代表现实通道。','Clip A and B back-to-back to simulate turning, or rotate them separately. Compare river edge, field and sports centre. Diagram lines are not real access routes.')+'</p><div class="half"><div data-material="park-A"><h3>A</h3>'+self.f['parkA']+'</div><div data-material="park-B"><h3>B</h3>'+self.f['parkB']+'</div></div>'
        names=[T('游乐区侧','PLAYGROUND SIDE'),T('河岸侧','RIVER SIDE'),T('圆形入口侧','CIRCULAR ENTRANCE'),T('大场地侧','FIELD SIDE')]
        for i in [0,2]:body+='<div class="half">'+''.join('<div class="strip" data-material="camera-marker">□ '+x+'</div>' for x in names[i:i+2])+'</div>'
        body+='<div class="half"><div class="strip" data-material="purpose-label">CAPTURE AT<br>'+T('从这里取景','VIEW FROM HERE')+'</div><div class="strip" data-material="purpose-label">DELIVER TO<br>'+T('向这里交付','DELIVER HERE')+'</div></div>'+self.fold(T('仅选择交换校准时展开','Open only if you selected shared calibration'),'<p>'+T('B面顺时针转四分之一圈：河边在上、大场地在左、体育中心在右。相机侧和用途仍需自行判断。','Turn Face B a quarter-turn clockwise: river edge above, field left, sports centre right. You still determine camera side and purpose.')+'</p>')
        self.add('s4pieces',T('04B · 公园图与相机片','04B · Park cards and camera markers'),body)
    def materials_5(self,s):
        T=self.T
        body=''.join('<div class="strip theatre-strip" data-material="theatre-name">'+esc(self.text(c['label']))+'</div>' for c in s['cards'])+'<div class="strip theatre-strip" data-material="move-1928">1928 · '+T('迁址与重新开场','RELOCATION & REOPENING')+'</div><div class="track">'+T('名字沿革','NAME HISTORY')+': ______ → ______ → ______ → ______</div><div class="track">'+T('位置变化','LOCATION HISTORY')+': __________________</div>'+self.fields(s['fields'])+self.help_ref(5)
        self.add('s5work',T('05A · 名字与位置','05A · Names and location'),body)
    def html(self):
        lookup={p['key']:i+1 for i,p in enumerate(self.pages)};out=[];brand=esc(self.text(self.d['title']))+' · R7'
        for i,p in enumerate(self.pages,1):
            b=f'<section class="page {p["cls"]}" id="{p["key"]}"><div class="page-content"><header><span>{brand}</span><span>{self.T("玩家题包 · 中文","PLAYER KIT · ENGLISH")}</span></header><h1>{esc(p["title"])}</h1>'+(f'<p class="sub">{esc(p["sub"])}</p>' if p['sub'] else '')+p['body']+f'</div><footer class="page-foot"><span>A4 · 100% · {self.T("单面 · 原创游戏材料","SINGLE-SIDED · ORIGINAL GAME MATERIAL")}</span><span>{i} / {len(self.pages)}</span></footer></section>'
            out.append(re.sub(r'\{\{page:([^}]+)\}\}',lambda m:str(lookup[m.group(1)]),b))
        return '<!doctype html><html lang="'+self.l+'"><head><meta charset="utf-8"><title>'+brand+'</title><style>'+CSS+'</style></head><body class="'+self.l+'"><div class="no-print"><button onclick="window.print()">'+self.T('打印题包','Print kit')+'</button> · A4 · 100% · '+str(len(self.pages))+' '+self.T('页','pages')+'</div>'+''.join(out)+'</body></html>'
def main():
    if not DATA.exists():raise SystemExit('Missing current authored content/game.json')
    d=json.loads(DATA.read_text());node=os.environ.get('CODEX_PRIMARY_RUNTIME_NODE') or shutil.which('node')
    js="""const fs=require('fs'),D=JSON.parse(fs.readFileSync('./content/game.json')),F=require('./play/figures.js'),N=require('./play/narrative.js');N.configure(D);const r={tower:F.icon('tower'),sign:F.icon('sign'),roof:F.icon('roof'),riverA:F.river({rotation:1,mirror:true}),riverB:F.river({rotation:0,mirror:false}),parkA:F.park({rotation:3,mirror:true}),parkB:F.park({rotation:3,mirror:false}),facade:F.facade(),memorial:F.memorial(),scene:F.scene()};for(const l of ['zh','en'])r[l]=Object.fromEntries(N.supported.map(n=>[n,N.svg(n,l,{static:true})]));process.stdout.write(JSON.stringify(r));"""
    figs=json.loads(subprocess.check_output([node,'-e',js],cwd=ROOT,text=True));meta={'content_source':'content/game.json','content_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),'figures_sha256':hashlib.sha256((ROOT/'play/figures.js').read_bytes()).hexdigest(),'narrative_sha256':hashlib.sha256((ROOT/'play/narrative.js').read_bytes()).hexdigest(),'required_material_categories_unchanged':True,'spoiler_policy':'Preparation has no ending material; hints and outcomes are separate; souvenir only after finale.','materials':{'view_cards':3,'horizontal_scene_strips':3,'frame':1,'river_map_faces':2,'river_labels':2,'timeline_tracks':2,'lower_bound_strip':1,'park_map_faces':2,'camera_markers':4,'purpose_labels':2,'facade_reference':1,'theatre_name_strips':4,'move_1928':1,'receipt':1,'folded_souvenir':1},'languages':{}}
    for l in ['zh','en']:
        k=Kit(d,figs,l);k.build();(ROOT/f'play/print_{l}.html').write_text(k.html());meta['languages'][l]={'pages':len(k.pages),'page_index':[{'page':i+1,'key':p['key'],'title':p['title']}for i,p in enumerate(k.pages)]};print(l,len(k.pages),'pages')
    title=esc(d['title']['zh'])+'<br><small>'+esc(d['title']['en'])+'</small>'
    (ROOT/'play/print.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R7 · Print</title><style>body{font:18px/1.7 sans-serif;max-width:760px;margin:50px auto;padding:0 24px;color:#173b46}a{display:block;padding:16px;margin:16px 0;background:#eef3ef;border:1px solid #9ab0b8;color:inherit}</style><h1>'+title+'</h1><p>每组打印一种语言，A4单面100%。<br>Print one language per team, A4 single-sided at 100%.</p><a href="print_zh.html">中文玩家题包</a><a href="print_en.html">English player kit</a><details><summary>主持／设计者材料（含完整剧透） · Host/designer materials (spoilers)</summary><a href="guide.html">设计指南 / Designer guide</a></details></html>')
    (ROOT/'qa/print_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()

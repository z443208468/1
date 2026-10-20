(function(root){
'use strict';
// Original code-drawn performance. These figures have no puzzle inputs or state.
const F=root.R3_FIG||(typeof require==='function'?require('./figures.js'):null);
if(!F)throw new Error('caper.js requires the unchanged figures.js');
const esc=F.esc, W=800,H=480;let serial=0;
const pick=(lang,zh,en)=>lang==='en'?en:zh;
const inner=s=>s.replace(/^<svg\b[^>]*>/,'').replace(/<\/svg>\s*$/,'');
const sourceScene=inner(F.scene());
const ink='#193c42',paper='#fff8e8',red='#ad482f',gold='#d7ab63',blue='#7195a4';
const text=(x,y,s,size=25,extra='')=>`<text x="${x}" y="${y}" font-size="${size}" ${extra}>${esc(s)}</text>`;
const line=(x1,y1,x2,y2,extra='')=>`<path d="M${x1} ${y1} L${x2} ${y2}" fill="none" stroke="${ink}" stroke-width="4" ${extra}/>`;
const captions={
 caper_open:['窄窗再亮时，只剩空白。河和空舟都不见了。','The narrow window brightens again, but it is blank. The river and Utsuro are gone.'],
 caper0:['同一条河、同一张遮片。这次保留宽框。','The same river and the same sheet. This time the wide frame stays.'],
 caper1:['遮片照旧横移。脚步、片边和持片者都没有出框。','The sheet moves across again. Its edge, the footsteps and its holder stay in the frame.'],
 caper2:['他躲到片后，鞋和身体边缘仍在宽框中。河底景一直在。','He slips behind the sheet. His shoes and body edge remain visible. The river backdrop stays in place.'],
 caper3:['旧题签留下；当代对应和迁址分栏。演出没有切黑。','The old title stays, with its current counterpart and relocation on separate lines. No blackout.'],
 caper4:['同一张遮片落下。原来的三条河景全部归还。','The same sheet comes down. All three original strips of river scenery are returned.'],
 caper5:['完整鞠躬，可见退场。景留在观众前。','A complete bow and a visible exit. The scenery remains with the audience.'],
 fragments:['三条原景错开。被遮住的部分仍留在原条上。','The three original strips are apart. Occluded details remain on their original strips.'],
 joined:['同样三条原景接合。遮挡被保留，底景连成全幅。','The same three strips join. Occlusion remains part of the scene; the backdrop is whole.'],
 riverWrong:['按一个舞台名换景，原河景被搁在显示框外。','A stage name is being used to swap the scene; the original river sits outside the display frame.'],
 riverBoth:['保留同一河景，同时记录舞台名和真实取景来源。','The same river scene stays, with separate labels for its stage name and real source.'],
 oldClaim:['空舟的“1930原始摄影”题签正在给现代庭园参照背书。','Utsuro’s “original photograph, 1930” label claims authority for a modern garden reference.'],
 modernReference:['撤下1930背书，保留参照。证据只给出1995或以后。','The 1930 claim is withdrawn; the reference stays. The evidence establishes 1995 or later only.'],
 parkCrop:['按所谓古公园景裁切，游乐近景和搬景动作一起被排除。','The supposed old-park crop excludes both the playground foreground and the scenery-moving action.'],
 parkFull:['同一近景和后景都留下。箭头从游乐区的观察端开始。','The same foreground and background stay. The viewing arrow begins on the playground side.'],
 oldExit:['同一千歳座题签尚未完成当代对应；请求切黑仍是请求。','The same Chitose-za title lacks its current counterpart. The request for a blackout remains a request.'],
 lineageJoined:['同一旧题签接到明治座；1928迁址另列，不是同一机位。','The same old title connects to Meiji-za. The 1928 relocation is separate; this is not one camera position.']
};
function tag(x,y,w,label,fill=paper,color=ink,size=25){return `<g><rect x="${x}" y="${y}" width="${w}" height="44" rx="3" fill="${fill}" stroke="${color}" stroke-width="2"/>${text(x+w/2,y+30,label,size,`fill="${color}" text-anchor="middle"`)}</g>`;}
function backdrop(){return `<g data-river-source="r3-scene-unchanged" transform="translate(75 144) scale(1.08)">${sourceScene}</g>`;}
function sheet(x=45,y=120,w=330,h=230,classes=''){return `<g class="${classes}" data-prop="same-sheet"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="2" fill="${ink}" stroke="${gold}" stroke-width="4" class="sheet-surface"/><path d="M${x+12} ${y+12} H${x+w-12} V${y+h-12} H${x+12}Z" fill="none" stroke="${paper}" stroke-opacity=".6" stroke-width="2"/><path class="sheet-mark" d="M${x+18} ${y+36} l18 -18 l18 18 l-18 18Z" fill="${gold}"/><path d="M${x+w-20} ${y+13} V${y+h-13}" stroke="${gold}" stroke-width="3"/></g>`;}
function puppet(x=409,pose='hold',classes=''){
 const head=`<path d="M-22 -169 Q0 -196 22 -169 L29 -165 H-29Z" fill="${ink}"/><circle cy="-151" r="19" fill="${red}"/><path d="M-13 -155 h9 m8 0 h9" stroke="${paper}" stroke-width="3"/>`;
 const torso=`<path d="M-17 -131 Q0 -139 17 -131 L28 -66 L-28 -66Z" fill="${ink}"/><path d="M-19 -94 H23" stroke="${red}" stroke-width="11"/>`;
 const arms=pose==='sign'?'<path d="M-13 -125 L-48 -157 L-57 -211 M15 -124 L27 -87"/>':pose==='behind'?'<path d="M-12 -124 L-43 -108 M14 -124 L42 -96 L29 -68"/>':'<path d="M-13 -125 L-47 -115 L-41 -140 M15 -124 L27 -85"/>';
 const upper=`<g class="${pose==='bow'?'bow-torso':''}" transform="${pose==='bow'?'rotate(53 0 -67)':''}">${head}${torso}<g fill="none" stroke="${ink}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round">${arms}</g></g>`;
 return `<g class="caper-puppet ${classes}" data-person="utsuro" transform="translate(${x} 391)">${upper}<path d="M-12 -65 L-17 -13 L-33 -3 M12 -65 L19 -13 L34 -3" fill="none" stroke="${ink}" stroke-width="15" stroke-linecap="round"/></g>`;
}
function frameBorder(){return '<rect x="31" y="74" width="738" height="345" rx="2" fill="none" stroke="'+gold+'" stroke-width="8"/><path d="M44 405 H756" stroke="'+gold+'" stroke-width="3"/>';}
function narrowMatte(uid,mode='narrow'){
 const aperture=`<rect x="245" y="120" width="330" height="230" fill="black"/>`;
 return `<defs><mask id="${uid}-aperture"><rect width="800" height="480" fill="white"/>${aperture}</mask></defs><g class="${mode==='expand'?'aperture-expand':''}"><rect x="30" y="74" width="740" height="345" fill="#112d33" mask="url(#${uid}-aperture)"/><rect x="245" y="120" width="330" height="230" fill="none" stroke="${gold}" stroke-width="8"/></g>`;
}
function stageBase(lang,uid){return `<rect width="800" height="480" rx="4" fill="#112d33"/><rect x="35" y="78" width="730" height="337" fill="${paper}"/><path d="M35 350 H765 V415 H35Z" fill="#e8dcc3"/>${backdrop()}${text(42,39,pick(lang,'借 景 影 戏','BORROWED SCENERY'),25,`fill="${gold}" letter-spacing="3"`)}${text(758,39,pick(lang,'原创舞台','ORIGINAL STAGE'),19,`fill="${paper}" text-anchor="end"`)}${text(400,458,pick(lang,'原创影戏 · 非现场画面','Original shadow play · not a view of the real sites'),20,`fill="${paper}" text-anchor="middle"`)}`;}
function theatre(name,lang,uid,isStatic){
 let body=stageBase(lang,uid),n=name==='caper_open'?-1:Number(name.slice(5));
 if(n===-1){
  if(isStatic){
   const one=(end,id)=>stageBase(lang,id)+`<g class="${end?'sheet-back':''}" transform="translate(${end?200:0} 0)">${puppet()}${sheet()}</g>`+narrowMatte(id)+frameBorder();
   return `<rect width="800" height="480" fill="${paper}"/><svg x="7" y="40" width="386" height="340" viewBox="0 0 800 480">${one(false,uid+'a')}</svg><svg x="407" y="40" width="386" height="340" viewBox="0 0 800 480">${one(true,uid+'b')}</svg>${text(200,380,pick(lang,'遮挡之前','BEFORE'),30,'text-anchor="middle"')}${text(600,380,pick(lang,'窄窗再亮','THE WINDOW BRIGHTENS'),30,'text-anchor="middle"')}${line(374,396,426,396,'marker-end="url(#'+uid+'-arrow)"')}${text(400,441,pick(lang,'河和空舟都不见了。','The river and Utsuro are gone.'),22,'text-anchor="middle"')}`;
  }
  body+=`<g class="opening-move">${puppet()}${sheet(45,120,330,230,'opening-sheet')}</g>`+narrowMatte(uid)+frameBorder();
 }else if(n===0){
  body+=puppet()+sheet()+(!isStatic?narrowMatte(uid,'expand'):'<rect x="245" y="120" width="330" height="230" fill="none" stroke="'+red+'" stroke-width="3" stroke-dasharray="10 8"/>')+frameBorder();
 }else if(n===1){
  body+=`<g class="${isStatic?'sheet-back':'wide-move'}" transform="translate(200 0)">${puppet()}${sheet()}</g>`+frameBorder();
  body+=`<path d="M142 386 H533" fill="none" stroke="${red}" stroke-width="3" stroke-dasharray="8 9" marker-end="url(#${uid}-arrow)"/>`;
 }else if(n===2){
  body+=puppet(571,'behind')+sheet(245,120,330,230,'sheet-back')+frameBorder();
  body+=`<path d="M535 404 H611" stroke="${red}" stroke-width="5"/><circle cx="604" cy="290" r="19" fill="none" stroke="${red}" stroke-width="3"/>`;
 }else if(n===3){
  body+=sheet(245,120,330,230,'sheet-back')+puppet(644,'sign')+line(587,127,587,180)+tag(481,83,202,pick(lang,'千歳座','CHITOSE-ZA'),paper,ink,24)+frameBorder();
  body+=tag(56,355,260,pick(lang,'当代对应：明治座','TODAY: MEIJI-ZA'),paper,ink,22)+tag(334,355,214,pick(lang,'1928：迁址','1928: RELOCATION'),paper,red,19);
 }else if(n===4){
  body+=`<g class="${isStatic?'':'sheet-lower'}">${sheet(245,372,330,23,'sheet-back')}</g>`+puppet(632,'hold')+frameBorder();
  body+=`<path d="M291 349 V362 M409 349 V362 M527 349 V362" stroke="${red}" stroke-width="3"/>`;
 }else{
  body+=`<g class="${isStatic?'':'bow-exit'}">${puppet(594,'bow')}${sheet(486,363,142,19,'sheet-back')}</g>`+frameBorder();
  body+=`<path d="M641 397 H747" fill="none" stroke="${red}" stroke-width="4" stroke-dasharray="8 7" marker-end="url(#${uid}-arrow)"/>${text(745,347,pick(lang,'侧边退场','EXIT'),21,`fill="${red}" text-anchor="end"`)}`;
 }
 return body;
}
function miniScene(x,y,w){return `<g transform="translate(${x} ${y}) scale(${w/600})" data-river-source="r3-scene-unchanged">${sourceScene}</g>`;}
function stripScene(name,lang,uid){let b='';
 const positions=name==='fragments'?[[54,155,-7],[287,118,5],[526,170,-4]]:[[100,160,0],[300,160,0],[500,160,0]];
 positions.forEach(([x,y,r],i)=>{b+=`<defs><clipPath id="${uid}-strip${i}"><rect width="200" height="180"/></clipPath></defs><g transform="translate(${x} ${y}) rotate(${r} 100 90)"><rect x="-3" y="-3" width="206" height="186" fill="${paper}" stroke="${ink}" stroke-width="3"/><g clip-path="url(#${uid}-strip${i})"><g transform="translate(${-i*200} 0)" data-river-source="r3-scene-unchanged">${sourceScene}</g></g>${text(100,217,'0'+(i+1),24,'text-anchor="middle"')}</g>`;});
 if(name==='joined')b+='<rect x="89" y="148" width="622" height="207" fill="none" stroke="'+gold+'" stroke-width="7"/>';
 return b;
}
function riverScene(name,lang,uid){
 const ok=name==='riverBoth';let b=`<rect x="170" y="120" width="600" height="210" fill="#f2ead8" stroke="${gold}" stroke-width="7"/><path d="M170 131 H770" stroke="${ink}" stroke-width="2"/>`;
 if(ok)b+=miniScene(185,144,570);
 else b+=`${text(470,215,pick(lang,'另一条河：空白占位','OTHER RIVER: EMPTY'),27,'text-anchor="middle" fill="#8a847a"')}${text(470,258,pick(lang,'题签决定了换景','THE LABEL TRIGGERS A SWAP'),20,'text-anchor="middle" fill="#8a847a"')}<g transform="rotate(-7 115 276)"><rect x="14" y="232" width="247" height="94" fill="${paper}" stroke="${ink}" stroke-width="3"/>${miniScene(18,235,240)}</g>${text(142,358,pick(lang,'原河景在框外','ORIGINAL OUTSIDE'),21,'text-anchor="middle"')}`;
 b+=tag(208,60,265,pick(lang,'舞台名：稲瀬川','STAGE: INASE'),ok?paper:'#e8d7c7',ink,26);
 b+=ok?tag(411,360,350,pick(lang,'真实来源：隅田川','SOURCE: SUMIDA'),paper,ink,26):`<path d="M339 106 V136" stroke="${red}" stroke-width="5" marker-end="url(#${uid}-arrow)"/>`;
 if(ok)b+=`<path d="M341 106 V124 M588 334 V358" stroke="${red}" stroke-width="4"/>${text(78,285,pick(lang,'同','SAME'),25,'text-anchor="middle"')}${text(78,317,pick(lang,'景','SCENE'),25,'text-anchor="middle"')}`;
 return b;
}
function memorialScene(name,lang,uid){
 const ok=name==='modernReference';let b=`<g transform="translate(120 132) scale(1.55)">${inner(F.memorial())}</g>`;
 b+=tag(122,66,510,ok?pick(lang,'参照：1995或以后','REFERENCE: 1995 OR LATER'):pick(lang,'空舟题签：1930原始摄影','UTSURO: ORIGINAL PHOTO, 1930'),ok?paper:'#ead5c8',ok?ink:red,ok?29:24);
 if(ok){b+=`<path d="M644 82 l40 25 m0 -25 l-40 25" stroke="${red}" stroke-width="6"/>${text(664,134,'1930',25,'text-anchor="middle" fill="'+red+'"')}${text(400,428,pick(lang,'1680 人物史  ≠  1995 设施史','1680: PERSON  ≠  1995: FACILITY'),25,'text-anchor="middle"')}`;}
 return b;
}
function parkScene(name,lang,uid){
 const ok=name==='parkFull';let b=`<rect x="55" y="100" width="690" height="291" fill="${paper}" stroke="${gold}" stroke-width="6"/><g transform="translate(88 110) scale(2.08 1.4)">${inner(F.facade()).replace(/\bfc\b/g,uid+'-fc')}</g>`;
 // The view always contains the same background and playground. Cropping masks only the foreground.
 if(!ok)b+=`<rect x="58" y="266" width="684" height="122" fill="${ink}"/><path d="M63 265 H738" stroke="${red}" stroke-width="5" stroke-dasharray="12 8"/>${text(400,356,pick(lang,'近景被裁去','FOREGROUND CUT'),29,`fill="${paper}" text-anchor="middle"`)}`;
 else b+=`<g><rect x="101" y="335" width="44" height="31" rx="4" fill="${red}"/><circle cx="124" cy="350" r="10" fill="${paper}"/><path d="M110 333 l6 -8 h17 l6 8" fill="${red}"/><path d="M155 351 C245 350 335 318 407 259" stroke="${red}" stroke-width="5" fill="none" marker-end="url(#${uid}-arrow)"/></g>`;
 b+=tag(94,48,610,ok?pick(lang,'保留近景 + 后景 · 当代取景','KEEP BOTH PLANES · CONTEMPORARY VIEW'):pick(lang,'空舟要求：只留“古景”','UTSURO ASKS FOR AN “OLD SCENE”'),paper,ink,ok?27:25);
 b+=text(400,438,ok?pick(lang,'观察端：游乐区 → 体育中心在后','CAMERA: PLAYGROUND → CENTRE BEHIND'):pick(lang,'裁切的历史理由尚未成立','THE HISTORICAL REASON FOR THE CROP IS UNPROVEN'),ok?25:23,'text-anchor="middle"');
 return b;
}
function lineageScene(name,lang,uid){
 const ok=name==='lineageJoined';let b=miniScene(112,156,576)+tag(76,75,270,pick(lang,'千歳座景','CHITOSE-ZA SCENE'),paper,ink,27);
 if(ok){b+=tag(434,75,290,pick(lang,'当代对应：明治座','NOW: MEIJI-ZA'),paper,ink,24)+`<path d="M354 97 H422" stroke="${red}" stroke-width="4" marker-end="url(#${uid}-arrow)"/>`+tag(144,358,512,pick(lang,'位置轨：1928年迁址','LOCATION TRACK: RELOCATED IN 1928'),paper,red,25);}
 else{b+=tag(434,75,290,pick(lang,'当代对应：未整理','COUNTERPART: UNFILED'),paper,ink,22)+`<path d="M354 97 H422" stroke="${red}" stroke-width="4" stroke-dasharray="7 7"/><path d="M618 188 H731 V325 H618Z" fill="${ink}"/>${text(674,249,pick(lang,'切黑？','CUT?'),25,`fill="${paper}" text-anchor="middle"`)}${text(400,402,pick(lang,'只是请求；汐还没有切。','A REQUEST ONLY. SHIO HAS NOT CUT.'),26,'text-anchor="middle"')}`;}
 return b;
}
function svg(name,lang='zh',options={}){
 if(!captions[name])return '';const uid='cp'+(++serial),isStatic=options.static===true;
 const cap=captions[name][lang==='en'?1:0];
 const defs=`<defs><marker id="${uid}-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0 0 L6 3 L0 6" fill="none" stroke="${red}" stroke-width="1.5"/></marker></defs>`;
 const anim=`<style>text{font-family:system-ui,'Noto Sans CJK SC',sans-serif}.opening-move{animation:cp-open 3.6s ease-in-out both}.opening-sheet .sheet-surface,.wide-move .sheet-surface{animation:cp-back 3.6s ease-in-out both}.opening-sheet .sheet-mark,.wide-move .sheet-mark{animation:cp-mark 3.6s ease-in-out both}.sheet-back .sheet-surface{fill:#e7dcc8}.sheet-back .sheet-mark{opacity:0}.wide-move{animation:cp-wide 3.6s ease-in-out both}.aperture-expand{animation:cp-aperture 2.2s ease-out both}.sheet-lower{animation:cp-lower 2s ease-out both}.bow-exit{animation:cp-exit 7s ease-in-out both}.bow-torso{transform-origin:0px -67px;animation:cp-bow 7s ease-in-out both}@keyframes cp-open{0%,12%{transform:translateX(0)}80%,100%{transform:translateX(200px)}}@keyframes cp-back{0%,25%{fill:${ink}}70%,100%{fill:#e7dcc8}}@keyframes cp-mark{0%,25%{opacity:1}70%,100%{opacity:0}}@keyframes cp-wide{0%,12%{transform:translateX(0)}80%,100%{transform:translateX(200px)}}@keyframes cp-aperture{0%,15%{opacity:1}100%{opacity:0}}@keyframes cp-lower{0%{transform:translateY(-252px) scaleY(10);transform-origin:410px 372px;opacity:1}100%{transform:none;opacity:1}}@keyframes cp-exit{0%,63%{transform:translateX(0)}100%{transform:translateX(196px)}}@keyframes cp-bow{0%{transform:rotate(0deg)}22%,49%{transform:rotate(53deg)}64%,100%{transform:rotate(0deg)}}@media(prefers-reduced-motion:reduce){.opening-move,.opening-sheet .sheet-surface,.opening-sheet .sheet-mark,.wide-move,.wide-move .sheet-surface,.wide-move .sheet-mark,.aperture-expand,.sheet-lower,.bow-exit,.bow-torso{animation:none!important}.opening-move{transform:translateX(200px)}.opening-sheet .sheet-surface,.wide-move .sheet-surface{fill:#e7dcc8}.opening-sheet .sheet-mark,.wide-move .sheet-mark{opacity:0}.aperture-expand{opacity:0}.bow-torso{transform:rotate(53deg)}}${isStatic?'#'+uid+' *{animation:none!important}':''}</style>`;
 let b;
 if(name.startsWith('caper'))b=theatre(name,lang,uid,isStatic);
 else{b=`<rect width="800" height="480" rx="4" fill="${paper}"/>${text(40,28,pick(lang,'原创调度图 · 非实景画面','ORIGINAL STAGING DIAGRAM · NOT A REAL-SITE VIEW'),17,'fill="#607572"')}`;
 if(['fragments','joined'].includes(name))b+=stripScene(name,lang,uid);
 else if(name.startsWith('river'))b+=riverScene(name,lang,uid);
 else if(['oldClaim','modernReference'].includes(name))b+=memorialScene(name,lang,uid);
 else if(name.startsWith('park'))b+=parkScene(name,lang,uid);
 else b+=lineageScene(name,lang,uid);
 }
 return `<svg xmlns="http://www.w3.org/2000/svg" id="${uid}" viewBox="0 0 ${W} ${H}" fill="${ink}" role="img" aria-label="${esc(cap)}" data-caper="${esc(name)}" data-static="${isStatic}">${anim}${defs}${b}</svg>`;
}
function render(name,lang='zh',options={}){
 if(!captions[name])return '';const cap=captions[name][lang==='en'?1:0],staticMode=options.static===true;
 const content=name==='caper_open'&&!staticMode?`<div class="caper-motion">${svg(name,lang)}</div><div class="caper-still">${svg(name,lang,{static:true})}</div>`:svg(name,lang,options);
 return `<figure class="caper-figure" data-caper-figure="${name}">${content}<figcaption>${esc(cap)}<span>${esc(pick(lang,'原创影戏与调度示意；不是历史影像或现场演出。','Original shadow play and staging diagrams; not historical footage or a performance at the sites.'))}</span></figcaption>${['caper_open','caper0','caper1','caper4','caper5'].includes(name)&&!staticMode?`<div class="caper-playback"><button type="button" data-caper-replay>${esc(pick(lang,'重演这段动作','Replay this action'))}</button></div>`:''}</figure>`;
}
let watchers=[];
function activate(host){
 watchers.forEach(x=>x.disconnect());watchers=[];
 host.querySelectorAll('.caper-figure').forEach(fig=>{
  const animated=fig.querySelector('svg[data-static="false"]');if(!animated)return;
  const animations=()=>animated.getAnimations({subtree:true});
  const run=()=>animations().forEach(a=>{a.cancel();a.play();});
  const button=fig.querySelector('[data-caper-replay]');if(button)button.onclick=run;
  if(typeof IntersectionObserver!=='undefined'){
   animations().forEach(a=>a.pause());
   const observer=new IntersectionObserver(entries=>{if(entries.some(x=>x.isIntersecting)){animations().forEach(a=>a.play());observer.disconnect();}},{threshold:.25});
   observer.observe(fig);watchers.push(observer);
  }
 });
}
const api={render,svg,activate,frame:(n,lang='zh',options={static:true})=>svg('caper'+n,lang,options),supported:Object.keys(captions),width:W,height:H};
root.R6_CAPER=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);

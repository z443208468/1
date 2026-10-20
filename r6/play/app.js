(function(){
'use strict';
const D=window.R6_DATA,E=window.R3_ENGINE,F=window.R3_FIG,$=id=>document.getElementById(id);
const key='tokyo-five-sites-r6-progress';let S,feedback=null,reelIndex=0;
const i18n=(zh,en)=>({zh,en});
const t=x=>x&&typeof x==='object'&&!Array.isArray(x)?String(x[S?.lang||'zh']??x.zh??x.en??''):String(x??'');
const e=F.esc;
const textHTML=x=>e(t(x)).replace(/\n/g,'<br>');
const dialogue=items=>Array.isArray(items)&&items.length?'<ol class="dialogue">'+items.map(x=>`<li>${x.speaker?`<strong>${e(t(x.speaker))}</strong>`:''}<p>${textHTML(x.text)}</p></li>`).join('')+'</ol>':'';
function clean(raw){
 let a=raw;
 if(typeof a==='string'){try{a=JSON.parse(a);}catch(_){return E.initial();}}
 if(a?.format==='tokyo-five-sites-progress'){
  if(a.product!==D.version)return E.initial();
  a=a.state;
 }
 const s=E.restore(a),inputs={};
 for(let k=0;k<=5;k++){
  const p=s.inputs[k];if(!p||typeof p!=='object'||Array.isArray(p))continue;
  const q=k<5?D.stages[k]:null,fs=q?q.fields:D.finalFields,out={};
  if(q?.cards&&Array.isArray(p.order))out.order=p.order.filter((v,j,arr)=>q.cards.some(c=>c.id===v)&&arr.indexOf(v)===j).slice(0,q.cards.length);
  if(q&&['river','park'].includes(q.type)){
   if(Number.isInteger(p.rotation)&&p.rotation>=0&&p.rotation<4){out.rotation=p.rotation;out.mirror=p.mirror===true;}
  }
  for(const f of fs){const pair=f.options.find(([v])=>v===p[f.id]);if(pair)out[f.id]=pair[0];}
  inputs[k]=out;
 }
 s.inputs=inputs;
 for(const name of ['passed','hints','observed','assisted']){
  const original=s[name];s[name]={};
  for(let k=0;k<=(name==='assisted'?5:4);k++){
   if(name==='hints'){const v=Number(original[k]);if(Number.isFinite(v)&&v>0)s[name][k]=Math.min(3,Math.floor(v));}
   else if(original[k]===true)s[name][k]=true;
  }
 }
 for(let k=0;k<5;k++)if(s.passed[k]&&!E.check(D.stages[k].answer,s.inputs[k]).ok)delete s.passed[k];
 s.completed=s.completed&&E.check(D.finalAnswer,s.inputs[5]).ok;
 return s;
}
try{S=clean(localStorage.getItem(key));}catch(_){S=E.initial();}
function persist(){try{localStorage.setItem(key,JSON.stringify({format:'tokyo-five-sites-progress',product:D.version,state:S}));}catch(_){$('storageWarning').hidden=false;$('storageWarning').textContent=t(i18n('此浏览器不能自动保存。请用“导出进度”保留文件。','Automatic saving is unavailable in this browser. Use Export progress to keep your work.'));}}
function initInput(index){
 if(!S.inputs[index])S.inputs[index]={};
 const q=D.stages[index],p=S.inputs[index];
 if(q&&['river','park'].includes(q.type)&&p.rotation===undefined){
  Object.assign(p,{rotation:index===1?1:3,mirror:true});
  if(index===3&&S.choice==='share')Object.assign(p,{rotation:0,mirror:false});
 }
 return p;
}
function invalidate(){if(S.stage<5)delete S.passed[S.stage];S.completed=false;feedback=null;reelIndex=0;}
function fields(fs,input){return fs.map(f=>{
 const selected=f.options.find(([v])=>v===input[f.id]);
 return `<div class="row"><label for="f-${e(f.id)}">${e(t(f.label))}</label><select id="f-${e(f.id)}" data-field="${e(f.id)}"><option value="">${t(i18n('请选择','Select'))}</option>${f.options.map(([v,label])=>`<option value="${e(v)}" ${selected&&selected[0]===v?'selected':''}>${e(t(label))}</option>`).join('')}</select><div class="selectedText quiet">${selected?e(t(selected[1])):''}</div></div>`;
 }).join('');}
function sources(ids){return `<details class="sources"><summary>${t(i18n('随身史料卡与来源 · 免费查看','History cards and sources · free to consult'))}</summary>${ids.map(id=>{
 const x=D.sources.find(y=>y.id===id);if(!x)return '';
 return `<div class="source"><strong class="source-heading">${e(id)} · ${e(t(x.title))}</strong><p>${textHTML(x.fact)}</p>${x.url?`<a href="${e(x.url)}" target="_blank" rel="noopener">${e(x.url)}</a>`:''}</div>`;
 }).join('')}</details>`;}
function figure(name){if(window.R6_CAPER?.supported.includes(name))return window.R6_CAPER.render(name,S.lang);if(name==='scene')return F.scene();if(name==='river')return F.river({rotation:0,mirror:false});if(name==='park')return F.park({rotation:0,mirror:false});if(name==='memorial')return F.memorial();if(name==='facade')return F.facade();return '';}
function renderFinale(){
 const scenes=Array.isArray(D.finale)?D.finale:[];if(!scenes.length)return '';
 reelIndex=Math.max(0,Math.min(reelIndex,scenes.length-1));const x=scenes[reelIndex];
 return `<section class="finale no-print" id="finale" aria-live="polite"><div class="finale-progress">${t(i18n('终局演出','FINALE'))} · ${reelIndex+1} / ${scenes.length}</div><h3>${e(t(x.title))}</h3>${x.figure?`<div class="wide">${figure(x.figure)}</div>`:''}${x.text?`<p>${textHTML(x.text)}</p>`:''}${dialogue(x.dialogue)}${x.byChoice?.[S.choice]?`<p>${textHTML(x.byChoice[S.choice])}</p>`:''}${x.byEnding?.[S.ending]?`<p>${textHTML(x.byEnding[S.ending])}</p>`:''}<div class="controls"><button id="previousScene" ${reelIndex===0?'disabled':''}>${t(i18n('上一幕','Previous scene'))}</button><button id="nextScene" ${reelIndex===scenes.length-1?'disabled':''}>${t(i18n('下一幕','Next scene'))}</button><button id="replayScenes">${t(i18n('从头重看','Replay from the beginning'))}</button></div></section>`;
}
function render(){
 document.documentElement.lang=S.lang==='zh'?'zh-CN':'en';document.title=t(D.title);$('title').textContent=t(D.title);$('subtitle').textContent=t(D.subtitle);$('release').textContent=D.version;
 $('language').textContent=S.lang==='zh'?'English':'中文';$('saveFile').textContent=t(i18n('导出进度','Export progress'));$('loadFile').textContent=t(i18n('导入进度','Import progress'));$('reset').textContent=t(i18n('重新开始','Restart'));$('printKit').textContent=t(i18n('打印题包','Print kit'));$('footer').textContent=t(D.safety);$('privacy').textContent=t(i18n('离线运行，无需登录；不会上传定位、照片或进度。现场场馆不参与本游戏。','Runs offline without login. No location, photographs or progress are uploaded. The venues are not participants in this game.'));
 $('nav').innerHTML=D.stages.map((x,i)=>`<button data-nav="${i}" class="${S.stage===i?'active':''}" aria-label="${e(t(x.title))}"><span class="num">${String(i+1).padStart(2,'0')}${S.passed[i]?' ✓':''}</span><span class="chapter-label">${e(t(x.shortTitle||x.site))}</span></button>`).join('')+`<button data-nav="5" class="${S.stage===5?'active':''}"><span class="num">${S.completed?'✓':'◇'}</span><span class="chapter-label">${t(i18n('终局','Finale'))}</span></button>`;
 $('statusline').textContent=t(i18n(`已整理 ${Object.values(S.passed).filter(Boolean).length}/5 组证据 · 可随时查看任一章节`,`Evidence assembled: ${Object.values(S.passed).filter(Boolean).length}/5 · All chapters remain accessible`));
 document.querySelectorAll('[data-nav]').forEach(b=>b.onclick=()=>{S.stage=Number(b.dataset.nav);feedback=null;persist();render();});
 const input=initInput(S.stage);let html='';
 if(S.stage===0){html+=`<section class="panel opening"><div class="eyebrow">${t(i18n('案件开始','THE CASE BEGINS'))}</div><h2>${e(t(D.openingTitle||i18n('出发之前','Before you begin')))}</h2>${D.fictionNotice?`<aside class="fiction-notice">${textHTML(D.fictionNotice)}</aside>`:''}${D.openingFigure?`<div class="story-figure">${figure(D.openingFigure)}</div>`:''}<p class="lead-prose">${textHTML(D.opening)}</p>${dialogue(D.openingDialogue)}${D.originalCaption||D.parkAnnotation?`<aside class="opening-instruction"><strong>${t(i18n('开场留在桌上的工作页','THE WORK PAGE LEFT AT THE OPENING'))}</strong>${D.originalCaption?`<p>${textHTML(D.originalCaption)}</p>`:''}${D.parkAnnotation?`<p>${textHTML(D.parkAnnotation)}</p>`:''}</aside>`:''}${Array.isArray(D.rules)&&D.rules.length?`<details class="play-rules"><summary>${t(i18n('游玩规则与备用材料','Play rules and backup materials'))}</summary><ol>${D.rules.map(r=>`<li>${textHTML(r)}</li>`).join('')}</ol></details>`:''}<div class="row"><label for="team">${t(i18n('小组名（可不填）','Team name (optional)'))}</label><input id="team" maxlength="40" value="${e(S.team)}"></div><div class="row"><label for="mode">${t(i18n('游玩方式','Play mode'))}</label><select id="mode"><option value="desktop" ${S.mode==='desktop'?'selected':''}>${t(i18n('桌面试玩 · 使用题包图示','Desktop · use the kit diagrams'))}</option><option value="field" ${S.mode==='field'?'selected':''}>${t(i18n('实地试玩 · 遵守现场开放边界','On site · respect access boundaries'))}</option></select></div><p class="quiet">${t(i18n('两种方式使用同一组题目和答案；桌面试玩不会自动记为现场观察。','Both modes use the same puzzles and answers. Desktop play never counts automatically as a site observation.'))}</p></section>`;}
 if(S.stage<5){
  const q=D.stages[S.stage];html+=`<section class="panel"><div class="site">${e(t(q.site))}</div><h2>${e(t(q.title))}</h2>${dialogue(q.before)}${q.beforeFigure?`<div class="story-figure">${figure(q.beforeFigure)}</div>`:''}<p>${textHTML(q.intro)}</p>${q.operation?`<div class="operation"><strong>${t(i18n('你们现在要做的事','YOUR ACTION'))}</strong>${textHTML(q.operation)}</div>`:''}${q.prompt?`<p><strong>${textHTML(q.prompt)}</strong></p>`:''}<div class="puzzle">`;
  if(q.cards){const order=input.order||[];html+=`<div class="cardgrid ${q.cards.length===4?'four':''}">${q.cards.map(c=>`<button class="card ${order.includes(c.id)?'selected':''}" data-card="${e(c.id)}" aria-pressed="${order.includes(c.id)}">${c.icon?F.icon(c.icon):''}<span>${e(t(c.label))}</span></button>`).join('')}</div><div class="slots">${order.map(id=>e(t(q.cards.find(c=>c.id===id)?.label||''))).join(' → ')||t(i18n('按顺序点选卡片，放进这里。','Select cards in order to place them here.'))}</div><button id="clearOrder">${t(i18n('清空排列','Clear order'))}</button>`;}
  if(q.type==='timeline')html+=`<div class="diagram memorial">${F.memorial()}</div><p class="quiet">${t(i18n('题图为自制识别示意，表现现代庭园中的坐像、台座和景观墙。它不是历史照片或馆藏复制。','An original recognition diagram of the monument, plinth and scenery wall in the modern garden. It is not a historical photograph or collection reproduction.'))}</p>`;
  if(['river','park'].includes(q.type)){
   html+=`<div class="diagram">${q.type==='river'?F.river(input):F.park(input)}</div><div class="controls"><button id="rotate">${t(i18n('顺时针转90°','Rotate 90° clockwise'))}</button><button id="flip">${t(i18n('翻面','Turn over'))}</button></div><p class="quiet">${t(i18n('这是不按比例的功能示意；图上的线不表示现实通路开放。','This functional diagram is not to scale. Its lines do not establish that a real path is open.'))}</p>`;
   if(q.type==='park')html+=`<div class="diagram">${F.facade()}</div><p class="quiet">${S.choice==='share'?t(i18n('已交换校准资料：大锚点方向已提供。相机侧、建筑和用途仍由你们判断。','Calibration was shared: the large anchors are oriented. The camera side, building and purpose are still yours to determine.')):t(i18n('独立核验：请翻正图卡，同时对照三个大锚点。','Independent verification: orient the card and compare all three large anchors.'))}</p>`;
  }
  html+=fields(q.fields,input)+`</div><label class="observed"><input id="observed" type="checkbox" ${S.observed[S.stage]?'checked':''}><span>${t(i18n('我们已在允许区域实际查看本关的现场物证。不要为勾选越界。','We examined this stage’s on-site evidence from permitted areas. Never trespass to tick this box.'))}</span></label><div class="controls no-print"><button id="submit" class="primary">${t(i18n('提交证据','Submit evidence'))}</button><button id="hint">${t(i18n('免费提示','Free hint'))} ${S.hints[S.stage]||0}/3</button><button id="assist">${t(i18n('辅助完成','Complete with assistance'))}</button></div>`;
  if(S.hints[S.stage])html+=`<div class="hint">${textHTML(q.hints[Math.min(2,S.hints[S.stage]-1)])}</div>`;
  if(feedback)html+=`<div class="feedback ${feedback.ok?'good':'bad'}" role="status">${e(feedback.message)}</div>`;
  if(S.passed[S.stage]){
   html+=`<section class="reveal" id="stageReveal"><div class="eyebrow">${t(i18n('行动之后','AFTER YOUR ACTION'))}</div><p>${textHTML(q.success)}</p>${q.afterFigure?`<div class="story-figure">${figure(q.afterFigure)}</div>`:(S.stage===0?`<div class="wide">${F.scene()}</div>`:'')}${dialogue(q.after)}`;
   if(S.stage===2){html+=`<div class="choice">${['challenge','share'].map(id=>`<button id="${id}" class="${S.choice===id?'primary':''}" aria-pressed="${S.choice===id}">${e(t(D.choiceLabels?.[id]||(id==='challenge'?i18n('公开驳回','Formal challenge'):i18n('交换来源','Exchange sources'))))}</button>`).join('')}</div>${D.choiceResponses?.[S.choice]?`<p class="ending-response">${textHTML(D.choiceResponses[S.choice])}</p>`:''}<p class="quiet">${t(i18n('这个选择只影响第一次打开公园图时的校准援助；不会减少真相或纪念物。公园图已经开始后，更改选择不重置已有操作。','This choice affects calibration help when the park diagram is first opened. It never withholds the truth or souvenir. Later changes do not reset work already begun on that diagram.'))}</p>`;}
   html+=`<p class="route">${textHTML(q.lead)}</p><button id="next" class="primary">${t(i18n('继续','Continue'))}</button></section>`;
  }
  html+=sources(q.sources)+'</section>';
 }else{
  html+=`<section class="panel"><div class="eyebrow">${t(i18n('最后的行动','THE FINAL ACTION'))}</div><h2>${e(t(D.finalTitle||i18n('把完整证据交到一起','Bring the evidence together')))}</h2><p>${textHTML(D.finalIntro||i18n('提交你们的完整判断。能够提前推理出全部事实时，可以直接结案。','Submit your complete account. If you have inferred every required fact early, you may close the case now.'))}</p>${fields(D.finalFields,input)}<div class="row"><label for="ending">${t(i18n('以什么方式完成？两种都有完整真相。','How will you complete it? Both choices receive the whole truth.'))}</label><select id="ending">${['solo','joint'].map(id=>`<option value="${id}" ${S.ending===id?'selected':''}>${e(t(D.endingLabels?.[id]||(id==='solo'?i18n('独立签收','Independent completion'):i18n('联合签收','Joint completion'))))}</option>`).join('')}</select></div><div class="controls"><button id="submit" class="primary">${t(i18n('确认最终行动','Confirm final action'))}</button><button id="assist">${t(i18n('辅助结案','Close with assistance'))}</button></div><p class="quiet">${t(i18n('正确提前推理同样有效，无需逐章盖章。辅助结案会记录，但不削减结局。','Correct early reasoning is accepted without chapter stamps. Assistance is recorded but never reduces the ending.'))}</p>${feedback?`<div class="feedback ${feedback.ok?'good':'bad'}" role="status">${e(feedback.message)}</div>`:''}`;
  if(S.completed){
   html+=renderFinale();
   const observed=Object.values(S.observed).filter(Boolean).length,assisted=Object.values(S.assisted).filter(Boolean).length;
   html+=`<section class="receipt" id="receipt"><div class="eyebrow">${t(i18n('案件回执 · 不是入场券','CASE RECEIPT · NOT AN ADMISSION TICKET'))}</div><h2>${e(S.team||t(i18n('东京探访小队','Tokyo investigation team')))}</h2><p>${textHTML(D.ending?.[S.ending])}</p>${D.choiceResponses?.[S.choice]?`<p class="quiet">${textHTML(D.choiceResponses[S.choice])}</p>`:''}<div class="wide">${F.scene()}</div><dl>${D.finalFields.map(f=>`<dt>${e(t(f.label))}</dt><dd>${e(t(f.options.find(([v])=>v===D.finalAnswer[f.id])[1]))}</dd>`).join('')}</dl><p class="quiet">${t(i18n(`方式：${S.mode==='field'?'实地试玩':'桌面试玩'}；现场自报 ${observed}/5；辅助 ${assisted} 项。策略：${S.choice==='share'?'交换来源':'公开驳回'}。此回执不证明实地验收或商业许可。`,`Mode: ${S.mode}; self-reported observations ${observed}/5; assisted actions ${assisted}. Strategy: ${S.choice==='share'?'source exchange':'formal challenge'}. This receipt is not evidence of field validation or commercial permission.`))}</p><button id="printReceipt">${t(i18n('打印回执','Print receipt'))}</button></section>`;
  }
  html+='</section>';
 }
 $('main').innerHTML=html;bind();window.R6_CAPER?.activate(document);
}
function submit(){
 const expected=S.stage<5?D.stages[S.stage].answer:D.finalAnswer,res=E.check(expected,initInput(S.stage));
 if(res.ok){if(S.stage<5)S.passed[S.stage]=true;else{S.completed=true;reelIndex=0;}feedback={ok:true,message:t(i18n('证据成立。你们的行动已经改变了局势。','The evidence holds. Your action has changed the situation.'))};}
 else{
  if(S.stage<5)delete S.passed[S.stage];else S.completed=false;
  const fs=S.stage<5?D.stages[S.stage].fields:D.finalFields;
  const names=res.wrong.map(k=>{const f=fs.find(x=>x.id===k);return f?t(f.label):t({order:i18n('卡片顺序','Card order'),rotation:i18n('图的朝向','Diagram orientation'),mirror:i18n('图卡正反面','Diagram face')}[k]||k);});
  feedback={ok:false,message:t(i18n('还需要核对：','Please check: '))+names.join(S.lang==='zh'?'、':', ')+t(i18n('。可以免费查看史料和提示，不扣分。','. History cards and hints are free; there is no penalty.'))};
 }
 persist();render();
}
function bind(){
 document.querySelectorAll('[data-field]').forEach(sel=>sel.onchange=()=>{const fs=S.stage<5?D.stages[S.stage].fields:D.finalFields,f=fs.find(x=>x.id===sel.dataset.field),pair=f.options.find(([v])=>String(v)===sel.value);initInput(S.stage)[f.id]=pair?pair[0]:'';invalidate();persist();render();});
 if($('team'))$('team').oninput=()=>{S.team=$('team').value.slice(0,40);persist();};
 if($('mode'))$('mode').onchange=()=>{S.mode=$('mode').value;persist();};
 if($('observed'))$('observed').onchange=()=>{S.observed[S.stage]=$('observed').checked;persist();};
 document.querySelectorAll('[data-card]').forEach(b=>b.onclick=()=>{const p=initInput(S.stage);p.order=p.order||[];if(p.order.includes(b.dataset.card))return;p.order.push(b.dataset.card);invalidate();persist();render();});
 if($('clearOrder'))$('clearOrder').onclick=()=>{initInput(S.stage).order=[];invalidate();persist();render();};
 if($('rotate'))$('rotate').onclick=()=>{Object.assign(initInput(S.stage),E.rotate(initInput(S.stage)));invalidate();persist();render();};
 if($('flip'))$('flip').onclick=()=>{Object.assign(initInput(S.stage),E.flip(initInput(S.stage)));invalidate();persist();render();};
 if($('hint'))$('hint').onclick=()=>{S.hints[S.stage]=Math.min((S.hints[S.stage]||0)+1,3);persist();render();};
 if($('submit'))$('submit').onclick=submit;
 if($('assist'))$('assist').onclick=()=>{if(!confirm(t(i18n('查看完整解答继续，并在回执中记录辅助？结局和纪念物不会减少。','Continue using the complete answer and record assistance? The ending and souvenir remain complete.'))))return;S.inputs[S.stage]=E.clone(S.stage<5?D.stages[S.stage].answer:D.finalAnswer);S.assisted[S.stage]=true;submit();};
 if($('next'))$('next').onclick=()=>{S.stage++;feedback=null;persist();render();window.scrollTo(0,0);};
 for(const id of ['challenge','share'])if($(id))$(id).onclick=()=>{S.choice=id;persist();render();};
 if($('ending'))$('ending').onchange=()=>{S.ending=$('ending').value;persist();if(S.completed)render();};
 if($('printReceipt'))$('printReceipt').onclick=()=>window.print();
 if($('previousScene'))$('previousScene').onclick=()=>{reelIndex--;render();$('finale').scrollIntoView({block:'start'});};
 if($('nextScene'))$('nextScene').onclick=()=>{reelIndex++;render();$('finale').scrollIntoView({block:'start'});};
 if($('replayScenes'))$('replayScenes').onclick=()=>{reelIndex=0;render();$('finale').scrollIntoView({block:'start'});};
}
$('language').onclick=()=>{S.lang=S.lang==='zh'?'en':'zh';feedback=null;persist();render();};
$('reset').onclick=()=>{if(confirm(t(i18n('清除这个版本在本机的试玩进度？已导出的文件不受影响。','Clear this version’s local progress? Exported files are unaffected.')))){S=E.initial();feedback=null;reelIndex=0;persist();render();window.scrollTo(0,0);}};
$('saveFile').onclick=()=>{const a=document.createElement('a'),url=URL.createObjectURL(new Blob([JSON.stringify({format:'tokyo-five-sites-progress',product:D.version,state:S},null,2)],{type:'application/json'}));a.href=url;a.download='tokyo-five-sites-r6-progress.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
$('loadFile').onclick=()=>$('fileInput').click();
$('fileInput').onchange=async()=>{
 const f=$('fileInput').files[0];if(!f)return;
 try{
  if(f.size>1000000)throw new Error('size');
  const parsed=JSON.parse(await f.text());
  if(!parsed||typeof parsed!=='object'||Array.isArray(parsed))throw new Error('format');
  if(parsed.format==='tokyo-five-sites-progress'&&parsed.product!==D.version)throw new Error('version');
  const raw=parsed.format==='tokyo-five-sites-progress'?parsed.state:parsed;
  if(raw?.version!==E.initial().version)throw new Error('version');
  S=clean(parsed);feedback=null;reelIndex=0;persist();render();$('importMessage').hidden=false;$('importMessage').textContent=t(i18n('进度已导入；无法识别或不一致的输入已清除。','Progress imported; unrecognised or inconsistent inputs were cleared.'));
 }catch(_){$('importMessage').hidden=false;$('importMessage').textContent=t(i18n('这个文件不能作为本版进度导入。请使用本版导出的JSON文件；现有进度已保留。','This file cannot be imported for this release. Use a JSON progress export from this game. Your current progress was kept.'));}
 $('fileInput').value='';
};
window.R6_TEST={getState:()=>E.clone(S),setState:x=>{S=clean(x);feedback=null;reelIndex=0;persist();render();},getScene:()=>reelIndex,submit};
render();
})();

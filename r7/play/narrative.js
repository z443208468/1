(function(root,factory){
  const api=factory(typeof module==='object'&&module.exports?require('./figures.js'):root.R3_FIG);
  if(typeof module==='object'&&module.exports)module.exports=api;else root.R7_NARRATIVE=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(F){
  'use strict';
  let source={};
  const esc=F.esc;
  const tr=(x,l)=>typeof x==='object'&&x?String(x[l]??x.zh??x.en??''):String(x??'');
  const base={scene:()=>F.scene(),river:()=>F.river({rotation:0,mirror:false}),park:()=>F.park({rotation:0,mirror:false}),memorial:()=>F.memorial(),facade:()=>F.facade()};
  function configure(data){source=data?.figures||{};return api;}
  function wrap(value,lang,max){
    const s=tr(value,lang),tokens=lang==='zh'?Array.from(s):s.split(/\s+/),out=[];let line='';
    for(const token of tokens){const next=line+(lang==='zh'||!line?'':' ')+token;if(next.length>max&&line){out.push(line);line=token;}else line=next;}if(line)out.push(line);return out;
  }
  function lines(value,lang,x,y,width,size=18,color='#1b3d46',limit=5){
    const max=Math.max(8,Math.floor(width/(lang==='zh'?size:size*.53)));
    return '<text x="'+x+'" y="'+y+'" font-size="'+size+'" fill="'+color+'">'+wrap(value,lang,max).slice(0,limit).map((s,i)=>'<tspan x="'+x+'" dy="'+(i?size*1.45:0)+'">'+esc(s)+'</tspan>').join('')+'</text>';
  }
  function embedded(scene,x,y,w,h){
    const raw=(base[scene]||base.scene)();
    return raw.replace('<svg','<svg x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" preserveAspectRatio="xMidYMid meet"');
  }
  const bi=(zh,en)=>({zh,en});
  function originalFrame(x,y,w,h){
    return '<g class="original-three-strip-frame"><rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="2" fill="#fcf9ec" stroke="#274c52" stroke-width="5"/>'+embedded('scene',x+5,y+5,w-10,h-10)+'<path d="M'+(x+w/3)+' '+(y+4)+'V'+(y+h-4)+'M'+(x+w*2/3)+' '+(y+4)+'V'+(y+h-4)+'" stroke="#b4aa8c" stroke-dasharray="3 3" stroke-width="1"/></g>';
  }
  function aya(x,y,scale=1){
    return '<g transform="translate('+x+' '+y+') scale('+scale+')"><path d="M-33 20Q-42-16-22-35Q0-54 24-33Q40-13 33 28L24 61H-29Z" fill="#253b40"/><ellipse cy="-9" rx="23" ry="28" fill="#dcb394"/><path d="M-24-10Q-3-15 15-37Q31-22 25 0L21-19Q0-4-24-2Z" fill="#253b40"/><path d="M-34 33Q0 18 35 34L49 98H-47Z" fill="#567c82"/><path d="M-8 8Q0 13 9 8" fill="none" stroke="#9f654f" stroke-width="2"/><circle cx="-8" cy="-6" r="1.7" fill="#263a3f"/><circle cx="9" cy="-6" r="1.7" fill="#263a3f"/></g>';
  }
  function table(x,y,w){return '<g><rect x="'+x+'" y="'+y+'" width="'+w+'" height="10" rx="2" fill="#b38d64"/><path d="M'+(x+13)+' '+(y+10)+'v16M'+(x+w-13)+' '+(y+10)+'v16" stroke="#907353" stroke-width="7"/></g>';}
  function packet(x,y,w=72){return '<g class="paper-packet"><rect x="'+x+'" y="'+y+'" width="'+w+'" height="44" rx="3" fill="#d8ba8e" stroke="#8f7355" stroke-width="2"/><path d="M'+x+' '+y+'l'+w/2+' 22L'+(x+w)+' '+y+'M'+(x+w/2)+' '+(y+20)+'v24" fill="none" stroke="#ae8b64" stroke-width="2"/></g>';}
  function captionCard(text,lang,x,y,w=150){return '<g><rect x="'+x+'" y="'+y+'" width="'+w+'" height="28" rx="2" fill="#faf6e8" stroke="#b6a382"/>'+lines(text,lang,x+8,y+19,w-16,13,'#494e42',1)+'</g>';}
  const motionStyle='<style>@keyframes r7-lift{0%,18%{transform:translateY(24px)}55%,100%{transform:translateY(0)}}@keyframes r7-lower{0%,20%{transform:translateY(-58px)}68%,100%{transform:translateY(0)}}@keyframes r7-receive{0%,25%{transform:translateX(-46px)}65%,100%{transform:translateX(0)}}@keyframes r7-retitle{0%,25%{transform:translateX(44px);opacity:.25}72%,100%{transform:translateX(0);opacity:1}}@keyframes r7-join-left{0%,20%{transform:translateX(-18px)}75%,100%{transform:translateX(0)}}@keyframes r7-join-right{0%,20%{transform:translateX(18px)}75%,100%{transform:translateX(0)}}.handoff-run .handoff-lift{animation:r7-lift 3.3s ease-in-out both}.handoff-run .handoff-lower{animation:r7-lower 4s ease-in-out both}.handoff-run .handoff-receive{animation:r7-receive 3.3s ease-in-out both}.handoff-run .handoff-retitle{animation:r7-retitle 4s ease-in-out both}.handoff-run .join-left{animation:r7-join-left 3.8s ease-in-out both}.handoff-run .join-right{animation:r7-join-right 3.8s ease-in-out both}@media(prefers-reduced-motion:reduce){.handoff-run .handoff-lift,.handoff-run .handoff-lower,.handoff-run .handoff-receive,.handoff-run .handoff-retitle,.handoff-run .join-left,.handoff-run .join-right{animation:none!important;transform:none!important}}</style>';
  function handoff(spec,lang){
    const mode=spec.mode||'cut';let art=motionStyle;
    if(mode==='cut'){
      art+='<rect x="28" y="90" width="338" height="304" rx="5" fill="#e8eeea"/><rect x="434" y="90" width="338" height="304" rx="5" fill="#eee6d8"/>'+lines(bi('片段一 · 举起纸框','SHOT A · LIFTING THE FRAME'),lang,45,120,304,16,'#36545b',1)+lines(bi('片段二 · 接住纸包','SHOT B · RECEIVING A PACKET'),lang,451,120,304,16,'#36545b',1);
      art+=aya(190,199,.83)+table(55,338,284)+'<g class="handoff-lift">'+originalFrame(98,222,190,80)+'<path d="M98 263q-18-4-22 8l22 5M288 263q18-4 22 8l-22 5" fill="#dcb394" stroke="#a6785f" stroke-width="1.5"/></g>';
      art+='<path d="M742 233l-68 20-24 28 34 16 67-25" fill="#455d65"/><path d="M675 257l-36 8q-18 4-15 17 9 13 25 7l36-14" fill="#dcb394" stroke="#a6785f" stroke-width="1.5"/><g class="handoff-receive">'+packet(563,237,88)+'</g>'+table(456,338,292);
      art+='<path d="M382 217l36 24-36 24Z" fill="#a3442e"/>'+lines(bi('剪切','CUT'),lang,379,292,43,15,'#a3442e',1)+lines(bi('两只手没有在同一个连续镜头中交接。','No uninterrupted shot shows a hand-to-hand transfer.'),lang,46,418,690,16,'#774835',1);
    }else if(mode==='uncut'){
      const xs=[28,284,540],width=232;
      xs.forEach((x,i)=>{art+='<rect x="'+x+'" y="92" width="'+width+'" height="310" rx="5" fill="'+(i===1?'#f6e5ca':'#e9eee8')+'" stroke="'+(i===1?'#bd7b35':'#bdcac0')+'" stroke-width="'+(i===1?3:1)+'"/>';});
      art+=lines(bi('1 · 举框拍摄','1 · FRAME SHOT'),lang,42,121,204,16,'#36545b',1)+lines(bi('2 · 放回桌面','2 · PUT IT BACK'),lang,298,121,204,16,'#8a4b24',1)+lines(bi('3 · 换签另拍','3 · RESET / NEW TAKE'),lang,554,121,204,16,'#36545b',1);
      art+=aya(144,204,.7)+table(42,338,204)+'<g class="handoff-lift">'+originalFrame(66,226,156,66)+'<path d="M66 258q-16-5-17 7l17 5M222 258q16-5 17 7l-17 5" fill="#dcb394"/></g>';
      art+=aya(400,204,.7)+table(298,338,204)+'<rect x="322" y="214" width="156" height="66" fill="none" stroke="#c9b58f" stroke-dasharray="5 4" stroke-width="2"/><path d="M491 265v50m-8-9 8 10 8-10" fill="none" stroke="#a75a28" stroke-width="4"/><g class="handoff-lower">'+originalFrame(322,272,156,66)+'<path d="M322 299q-16-5-17 7l17 5M478 299q16-5 17 7l-17 5" fill="#dcb394"/></g>';
      art+=table(554,338,204)+originalFrame(563,229,148,64)+captionCard(bi('上一张题签','PREVIOUS CAPTION'),lang,552,154,132)+'<path d="M612 193h48m-9-7 10 7-10 7" stroke="#a76535" stroke-width="3" fill="none"/><g class="handoff-retitle">'+captionCard(bi('另一张题签','ANOTHER CAPTION'),lang,617,198,143)+'<path d="M771 190l-30 13-2 18 30-6" fill="#dcb394"/></g><g class="handoff-receive">'+packet(593,296,68)+'</g><path d="M766 300l-66 9-17 10 15 14 68-13" fill="#dcb394"/><g fill="#405b64"><rect x="710" y="250" width="33" height="24" rx="4"/><circle cx="721" cy="262" r="7" fill="#dce7e1"/><path d="M744 256l13-6v26l-13-7Z"/></g>';
      art+=lines(bi('原框在此回到桌面','THE FRAME RETURNS HERE'),lang,300,389,200,13,'#8a4b24',1)+lines(bi('不同片段 · 不等于连续交付','SEPARATE TAKES ≠ ONE TRANSFER'),lang,556,389,200,12,'#36545b',2);
    }else if(mode==='rebuild'){
      art+='<rect x="28" y="92" width="336" height="308" rx="5" fill="#eee7da"/><rect x="430" y="92" width="342" height="308" rx="5" fill="#e6eee6"/>'+lines(bi('三条原景 · 同一个来源','THREE ORIGINAL STRIPS'),lang,43,123,307,17,'#36545b',1)+lines(bi('原景接回 · 制作记录保留','REJOINED WITH ITS RECORD'),lang,445,123,313,17,'#36545b',1);
      const inner=F.scene().split('>').slice(1).join('>').replace(/<\/svg>\s*$/,'');
      [0,1,2].forEach((i)=>{const x=56+i*96;art+='<g class="'+(i===0?'join-left':i===2?'join-right':'')+'"><rect x="'+x+'" y="192" width="88" height="90" fill="#fffaf0" stroke="#a7987c"/><svg x="'+(x+3)+'" y="198" width="82" height="80" viewBox="'+(i*200)+' 0 200 180" preserveAspectRatio="none">'+inner+'</svg></g>';});
      art+='<path d="M382 229l30 18-30 18Z" fill="#467163"/>'+originalFrame(453,182,294,105)+captionCard(bi('制作来源 · 保留','SOURCE RECORD · RETAINED'),lang,459,313,282)+lines(spec.record||bi('事实与复原过程一起留档。','Keep the facts and the reconstruction together.'),lang,51,325,293,17,'#425f68',3);
    }else throw new Error('Unsupported handoff mode: '+mode);
    return art;
  }
  function svg(name,lang='zh',options={}){
    const spec=source[name];if(!spec)return base[name]?base[name]():'';
    const title=tr(spec.title,lang),caption=tr(spec.caption,lang),labels=spec.labels||[];
    let art='<rect width="800" height="480" rx="8" fill="#fbf7ee"/><path d="M32 68H768" stroke="#b9c4bf"/>'+lines(spec.title,lang,32,43,735,23,'#193e45',1);
    if(spec.kind==='handoff'){
      art+=handoff(spec,lang);
    }else if(spec.kind==='timeline'){
      const items=spec.items||[];art+='<path d="M72 220H728" stroke="#b8894f" stroke-width="5"/>';
      items.slice(0,5).forEach((it,i)=>{const x=72+(items.length>1?656*i/(Math.min(5,items.length)-1):328);art+='<circle cx="'+x+'" cy="220" r="9" fill="#a3442e"/>'+lines(it.year||it.label,lang,x-54,192,108,23,'#193e45',2)+lines(it.text,lang,x-60,258,120,16,'#425f68',5);});
    }else if(spec.kind==='comparison'){
      const a=spec.left||{},b=spec.right||{};
      art+='<rect x="28" y="94" width="356" height="296" fill="#f2eadd" stroke="#c7b7a0"/><rect x="416" y="94" width="356" height="296" fill="#eaf1ea" stroke="#9fb4aa"/>'+embedded(a.scene||spec.scene,48,135,316,172)+embedded(b.scene||spec.scene,436,135,316,172)+lines(a.title,lang,48,121,316,17,'#8d432f',1)+lines(b.title,lang,436,121,316,17,'#25614f',1)+lines(a.text,lang,48,338,316,16,'#3e5860',2)+lines(b.text,lang,436,338,316,16,'#3e5860',2);
    }else{
      const side=labels.length>0;
      art+='<rect x="28" y="94" width="'+(side?492:744)+'" height="298" fill="#fffdf6" stroke="#b9c4bf"/>'+embedded(spec.scene||'scene',44,110,side?460:712,266);
      if(side)labels.slice(0,3).forEach((label,i)=>{const y=98+i*99;art+='<rect x="546" y="'+y+'" width="225" height="87" rx="4" fill="'+(i===labels.length-1?'#e5eee5':'#eee7db')+'"/>'+lines(label,lang,562,y+29,193,17,'#1b3d46',2);});
    }
    art+=lines(spec.footer||{zh:'原创叙事分镜 · 不是实况、原始录像或现场照片',en:'Original storyboard · not a live feed, source recording or site photograph'},lang,32,443,735,14,'#647875',2);
    const family=lang==='en'?'DejaVu Sans,Noto Sans CJK SC,sans-serif':'Noto Sans CJK SC,DejaVu Sans,sans-serif';
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 480" role="img" aria-label="'+esc(title+'. '+caption)+'" data-narrative="'+esc(name)+'"><title>'+esc(title)+'</title><desc>'+esc(caption)+'</desc><g font-family="'+family+'">'+art+'</g></svg>';
  }
  function render(name,lang='zh'){
    const spec=source[name]||{},image=svg(name,lang);if(!image)return '';
    return '<figure class="narrative-figure">'+image+(spec.caption?'<figcaption>'+esc(tr(spec.caption,lang))+'</figcaption>':'')+(spec.kind==='handoff'?'<div class="narrative-playback"><button type="button" data-story-replay>'+esc(tr(bi('重看这个动作','Replay this action'),lang))+'</button><span class="quiet">'+esc(tr(bi('所有分镜静态保留；重播不改变进度。','Every panel stays visible; replay never changes progress.'),lang))+'</span></div>':'')+'</figure>';
  }
  function activate(container){
    if(typeof window==='undefined')return;
    const start=s=>{s.classList.remove('handoff-run');void s.getBoundingClientRect();s.classList.add('handoff-run');};
    for(const b of container.querySelectorAll('[data-story-replay]'))b.onclick=()=>start(b.closest('figure').querySelector('svg'));
    const figures=[...container.querySelectorAll('svg[data-narrative]')].filter(s=>source[s.dataset.narrative]?.kind==='handoff');
    if(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)return;
    if(typeof IntersectionObserver!=='undefined'){
      const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){start(e.target);observer.unobserve(e.target);}},{threshold:.25});
      figures.forEach(s=>observer.observe(s));
    }else figures.forEach(start);
  }
  const api={configure,svg,render,activate,get supported(){return Object.keys(source);}};
  return api;
});

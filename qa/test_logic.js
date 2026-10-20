'use strict';
const fs=require('fs'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'..'),D=JSON.parse(fs.readFileSync(path.join(root,'play/data.json'),'utf8')),E=require('../play/engine.js');
let checks=[];const test=(name,fn)=>{fn();checks.push({name,result:'PASS'});};
function perms(a){if(!a.length)return [[]];return a.flatMap((x,i)=>perms(a.filter((_,j)=>j!==i)).map(p=>[x,...p]));}
function product(items){return items.reduce((a,b)=>a.flatMap(x=>b.map(v=>[...x,v])),[[]]);}
let enumeration=[];
for(const q of D.stages){const options={},k=Object.keys(q.answer);for(const key of k){if(key==='order')options[key]=perms(q.cards.map(x=>x.id));else if(key==='rotation')options[key]=[0,1,2,3];else if(key==='mirror')options[key]=[false,true];else options[key]=q.fields.find(x=>x.id===key).options.map(x=>x[0]);}const all=product(k.map(x=>options[x])).map(a=>Object.fromEntries(k.map((x,i)=>[x,a[i]]))),ok=all.filter(a=>E.check(q.answer,a).ok);test(q.id+' exactly one allowed discrete answer',()=>assert.equal(ok.length,1));enumeration.push({stage:q.id,cases:all.length,solutions:ok.length});test(q.id+' empty input rejected',()=>assert(!E.check(q.answer,{}).ok));test(q.id+' own answer accepted',()=>assert(E.check(q.answer,E.clone(q.answer)).ok));}
const keys=D.finalFields.map(x=>x.id),fa=product(D.finalFields.map(x=>x.options.map(x=>x[0]))).map(a=>Object.fromEntries(keys.map((k,i)=>[k,a[i]]))),fv=fa.filter(a=>E.check(D.finalAnswer,a).ok);test('final exact semantic solution',()=>assert.equal(fv.length,1));enumeration.push({stage:'final',cases:fa.length,solutions:fv.length});
test('clockwise four turns restores face',()=>{let p={rotation:1,mirror:true};for(let i=0;i<4;i++)p=E.rotate(p);assert.deepEqual(p,{rotation:1,mirror:true});});
test('two flips restore pose',()=>{for(let r=0;r<4;r++)for(const m of [false,true]){const p={rotation:r,mirror:m};assert.deepEqual(E.flip(E.flip(p)),p);}});
test('eight distinct asymmetric anchor configurations',()=>{const seen=new Set();for(let r=0;r<4;r++)for(const m of [false,true])seen.add(JSON.stringify([[61,150],[192,138],[261,156]].map(([x,y])=>E.point(x,y,{rotation:r,mirror:m}))));assert.equal(seen.size,8);});
test('1995 equality is not a valid inference',()=>{assert(!E.check(D.stages[2].answer,{...D.stages[2].answer,dateMeaning:'exact'}).ok);});
test('knowing Meijiza alone does not answer the case',()=>assert(!E.check(D.finalAnswer,{recipient:'meijiza'}).ok));
test('earliest correct full case does not require artificial stage stamps',()=>assert(E.check(D.finalAnswer,D.finalAnswer).ok));
test('admission claim rejected',()=>assert(!E.check(D.finalAnswer,{...D.finalAnswer,channel:'theatre_entry'}).ok));
test('discarding old scene label rejected',()=>assert(!E.check(D.finalAnswer,{...D.finalAnswer,stage:'sumida'}).ok));
test('date, place and purpose are distinct',()=>{for(const [k,v] of [['object','1930_original'],['park','deliver_sports'],['time','exact_1995']])assert(!E.check(D.finalAnswer,{...D.finalAnswer,[k]:v}).ok);});
test('corrupt progress safely resets',()=>assert.deepEqual(E.restore('not-json'),E.initial()));
test('unsupported version resets',()=>assert.deepEqual(E.restore({version:'R0'}),E.initial()));
test('team text capped and fields normalized',()=>{const r=E.restore({version:'R3.1',team:'a'.repeat(100),stage:99,lang:'xx'});assert.equal(r.team.length,40);assert.equal(r.stage,0);assert.equal(r.lang,'zh');});
test('every clue has a source and three hints',()=>{for(const q of D.stages){assert.equal(q.hints.length,3);assert(q.sources.length);assert(q.evidence);assert(q.success.zh&&q.success.en);for(const id of q.sources)assert(D.sources.find(s=>s.id===id));}});
test('no banned old code table or address fragments in game data',()=>{const raw=JSON.stringify(D);for(const forbidden of ['71-4141','LASYLA','TURN OVER THE FIRST BUTTON','213','CAB'])assert(!raw.includes(forbidden));});
const costs=[4,6,8].map(n=>({players:n,gross:n*4800,contribution:n*4800*.85-n*280-Math.ceil(n/4)*120-13500}));test('cost scenarios',()=>assert.deepEqual(costs.map(c=>c.contribution),[1580,9060,16660]));
const report={version:D.version,date:'2026-10-20',checks,enumeration,costs,scope:'Discrete authored logic and arithmetic only; no claim of field or enjoyment validation'};fs.writeFileSync(path.join(__dirname,'logic_results.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({checks:checks.length,passed:checks.length,cases:enumeration.reduce((s,x)=>s+x.cases,0)},null,2));

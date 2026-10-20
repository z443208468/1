(function(root){
'use strict';
const clone=x=>JSON.parse(JSON.stringify(x));
function same(a,b){if(Array.isArray(b))return Array.isArray(a)&&a.length===b.length&&b.every((v,i)=>same(a[i],v));return a===b;}
function check(expected,input){const wrong=[];for(const k of Object.keys(expected))if(!same(input&&input[k],expected[k]))wrong.push(k);return {ok:wrong.length===0,wrong};}
function rotate(p){return {rotation:((p.rotation||0)+1)%4,mirror:!!p.mirror};}
function flip(p){return {rotation:(4-(p.rotation||0))%4,mirror:!p.mirror};}
function point(x,y,p,c=150){let dx=x-c,dy=y-c;if(p.mirror)dx=-dx;for(let i=0;i<(p.rotation||0);i++){const t=dx;dx=-dy;dy=t;}return [dx+c,dy+c];}
function initial(){return {version:'R3.1',team:'',lang:'zh',mode:'desktop',stage:0,inputs:{},passed:{},hints:{},observed:{},assisted:{},choice:'challenge',ending:'solo',completed:false};}
function restore(raw){const s=initial();try{const a=typeof raw==='string'?JSON.parse(raw):raw;if(!a||a.version!==s.version)return s;for(const k of ['inputs','passed','hints','observed','assisted'])if(a[k]&&typeof a[k]==='object'&&!Array.isArray(a[k]))s[k]=a[k];s.team=String(a.team||'').slice(0,40);s.lang=a.lang==='en'?'en':'zh';s.mode=['desktop','field'].includes(a.mode)?a.mode:'desktop';s.stage=Number.isInteger(a.stage)&&a.stage>=0&&a.stage<=5?a.stage:0;s.choice=a.choice==='share'?'share':'challenge';s.ending=a.ending==='joint'?'joint':'solo';s.completed=!!a.completed;}catch(e){}return s;}
const api={clone,check,rotate,flip,point,initial,restore};if(typeof module!=='undefined'&&module.exports)module.exports=api;root.R3_ENGINE=api;
})(typeof window!=='undefined'?window:globalThis);

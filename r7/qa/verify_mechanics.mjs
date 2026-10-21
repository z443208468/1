import {createHash} from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyMechanics(root,data){
 const frozen=JSON.parse(fs.readFileSync(path.join(root,'qa/mechanics_contract.json'),'utf8'));
 assert.equal(hash(path.join(root,'play/engine.js')),frozen.engine_sha256,'Original engine bytes must remain unchanged');
 assert.equal(hash(path.join(root,'play/figures.js')),frozen.figures_sha256,'Original puzzle figures must remain unchanged');
 assert.equal(data.stages.length,5,'Exactly five stages');
 for(let i=0;i<5;i++){
  const q=data.stages[i],s=frozen.stages[i];
  assert.equal(q.id,s.id);assert.equal(q.type,s.type);
  assert.deepEqual(q.answer,s.answer,`${q.id}: answer changed`);
  assert.deepEqual((q.cards||[]).map(c=>({id:c.id,icon:c.icon??null})),s.cards,`${q.id}: cards changed`);
  assert.deepEqual(q.fields.map(f=>({id:f.id,options:f.options.map(x=>x[0])})),s.fields,`${q.id}: option IDs changed`);
  assert.equal(q.hints.length,3);assert.equal(q.evidence,s.evidence);
  for(const id of q.sources)assert(data.sources.some(x=>x.id===id),`${q.id}: missing source ${id}`);
 }
 assert.deepEqual(data.finalFields.map(f=>({id:f.id,options:f.options.map(x=>x[0])})),frozen.final_fields,'Final field values changed');
 assert.deepEqual(data.finalAnswer,frozen.finalAnswer,'Final answer changed');
 for(const key of ['title','subtitle','opening','safety'])assert(data[key]?.zh&&data[key]?.en,`Missing bilingual ${key}`);
 for(const q of data.stages){for(const key of ['title','site','intro','success','lead'])assert(q[key]?.zh&&q[key]?.en,`Missing bilingual ${q.id}.${key}`);for(const hint of q.hints)assert(hint.zh&&hint.en,`Missing bilingual ${q.id} hint`);}
 for(const key of ['solo','joint'])assert(data.ending?.[key]?.zh&&data.ending?.[key]?.en,`Missing bilingual ${key} ending`);
 return frozen;
}

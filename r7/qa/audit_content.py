"""Validate authored bilingual completeness, without rating story quality."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1];p=R/'content/game.json';D=json.loads(p.read_text());checks=[]
def check(name,c):
    checks.append({'name':name,'passed':bool(c)})
    if not c:raise AssertionError(name)
def bi(v):return isinstance(v,dict) and all(isinstance(v.get(l),str) and v[l].strip() for l in ['zh','en'])
def dialog(rows):return isinstance(rows,list) and all(bi(x['text']) and (not x.get('speaker') or bi(x['speaker'])) for x in rows)
check('five_complete_chapters',len(D['stages'])==5)
for n in ['title','subtitle','openingTitle','opening','fictionNotice','finalTitle','finalIntro','paperEnding','safety']:check('bilingual_'+n,bi(D.get(n)))
check('opening_dialogue_bilingual',dialog(D.get('openingDialogue')))
for i,q in enumerate(D['stages'],1):
    for n in ['title','site','intro','operation','prompt','success','lead']:check(f's{i}_bilingual_{n}',bi(q.get(n)))
    check(f's{i}_three_free_hints',len(q['hints'])==3 and all(bi(h) for h in q['hints']))
    check(f's{i}_bilingual_dialogue',dialog(q.get('before')) and dialog(q.get('after')))
check('complete_bilingual_finale',bool(D.get('finale')) and all(bi(x['title']) and bi(x['text']) and dialog(x.get('dialogue',[])) for x in D['finale']))
for n,keys in [('choiceLabels',{'challenge','share'}),('choiceResponses',{'challenge','share'}),('endingLabels',{'solo','joint'}),('ending',{'solo','joint'})]:check('complete_'+n,set(D.get(n,{}))==keys and all(bi(x) for x in D[n].values()))
check('source_ids_unique',len({x['id'] for x in D['sources']})==len(D['sources']))
check('bilingual_facts',all(bi(x['fact']) for x in D['sources']))
figures=D.get('figures',{});refs=[D.get('openingFigure')]+[q.get(k) for q in D['stages'] for k in ['beforeFigure','afterFigure']]+[x.get('figure') for x in D['finale']]
check('all_figure_references_resolve',all(not f or f in figures or f in ['river','scene','park','memorial','facade'] for f in refs))
check('rejected_R6_cast_not_in_player_source',not re.search(r'空舟|\bUtsuro\b|\bShio\b|借景怪盗|The River Thief',p.read_text(),re.I))
check('current_build_status_bilingual',bi(D.get('buildNotes')))
out={'product':D['version'],'scope':'Static bilingual completeness and asset references only; no assessment of enjoyment or historical truth.','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checks':checks,'passed':len(checks),'failed':0,'human_blind_test':'NOT_RUN','field_test':'NOT_RUN'}
(R/'qa/content_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':len(checks),'failed':0}))

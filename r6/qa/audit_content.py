"""Check release content completeness and the specific D2 production conditions.

This is a mechanical editorial audit, not a test of enjoyment or historical truth.
The historical judgements remain documented in research/ and the human-test protocol.
"""
from pathlib import Path
import json
import re
import hashlib

R=Path(__file__).resolve().parents[1]
path=R/'content/game.json'
D=json.loads(path.read_text(encoding='utf-8'))
checks=[]
def check(name,condition):
    checks.append({'name':name,'passed':bool(condition)})
    if not condition: raise AssertionError(name)
def bilingual(value):
    return isinstance(value,dict) and all(isinstance(value.get(k),str) and value[k].strip() for k in ('zh','en'))
check('five_complete_chapters',len(D['stages'])==5)
for name in ('title','subtitle','opening','fictionNotice','originalCaption','parkAnnotation','finalTitle','finalIntro','paperEnding'):
    check('bilingual_'+name,bilingual(D[name]))
check('opening_has_three_spoken_lines',len(D['openingDialogue'])>=3)
for i,q in enumerate(D['stages'],1):
    for name in ('title','site','intro','operation','prompt','success','lead'):
        check(f's{i}_bilingual_{name}',bilingual(q[name]))
    check(f's{i}_three_free_hints',len(q['hints'])==3 and all(bilingual(x) for x in q['hints']))
    check(f's{i}_before_and_after_actions',bool(q.get('beforeFigure')) and bool(q.get('afterFigure')) and q['beforeFigure']!=q['afterFigure'])
    check(f's{i}_dialogue_bilingual',all(bilingual(x['speaker']) and bilingual(x['text']) for name in ('before','after') for x in q[name]))
check('six_complete_finale_scenes',len(D['finale'])==6 and all(bilingual(x['title']) and bilingual(x['text']) and x.get('figure') for x in D['finale']))
check('two_independent_strategy_responses',set(D['choiceLabels'])==set(D['choiceResponses'])=={'challenge','share'})
check('two_complete_endings',set(D['endingLabels'])==set(D['ending'])=={'solo','joint'} and all(bilingual(x) for x in D['ending'].values()))
check('s4_has_theatre_year_sources_without_s5_gate',{'M03','M04','P01'}.issubset(set(D['stages'][3]['sources'])))
check('clearing_annotation_present_at_opening','千歳座' in D['originalCaption']['zh'] and '浜町公园' in D['parkAnnotation']['zh'])
check('source_ids_unique',len({x['id'] for x in D['sources']})==len(D['sources']))
check('sources_have_two_languages',all(bilingual(x['fact']) for x in D['sources']))
check('no_rejected_characters_or_contest_in_player_source',not re.search(r'澪|伊都|\bMio\b|\bRen\b|\bIto\b|\bcompetition\b|竞赛',path.read_text(),re.I))
check('no_live_feed_claim',D['buildNotes']['externalRequests'] is False and 'not a live feed' in D['fictionNotice']['en'])
check('no_new_required_site',D['buildNotes']['mustVisitNewSites'] is False)
out={'product':D['version'],'scope':'static completeness and D2 implementation conditions, not story-quality validation','source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checks':checks,'passed':len(checks),'failed':0,'human_blind_test':'NOT_RUN','field_test':'NOT_RUN'}
(R/'qa/content_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'failed':0,'scope':out['scope']},ensure_ascii=False))

"""Idempotently reconcile the earlier committed base with the checked R3.1 release.
No network access and no user data are used. Existing refinements are preserved.
"""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def change(path, old, new, marker=None):
 p=R/path;s=p.read_text(encoding='utf8')
 if marker and marker in s:return
 if new in s:return
 if old not in s:raise RuntimeError(f'{path}: expected base text is absent; reconcile before building')
 p.write_text(s.replace(old,new,1),encoding='utf8')
mem="""function memorial(){return svg('<rect width="300" height="180" fill="#faf9f3"/><path d="M14 110 H280 V145 H14Z" fill="#e2e5df" stroke="#687986"/><rect x="25" y="48" width="87" height="63" fill="#c4d7dc" stroke="#687986"/><path d="M28 65 H109 M68 49 V109" stroke="#faf9f3" stroke-width="2"/><path d="M18 149 Q68 120 123 147" stroke="#687986" fill="none"/><rect x="153" y="116" width="108" height="49" fill="#d1d6d3" stroke="#253746" stroke-width="2"/><rect x="180" y="134" width="43" height="18" fill="#687986"/><path d="M169 114 Q172 87 184 68 L199 59 Q190 54 191 39 Q193 27 204 28 Q217 26 220 40 Q221 54 211 59 L232 70 Q247 94 249 114Z" fill="#536c6c" stroke="#253746" stroke-width="2"/><path d="M193 78 Q206 92 233 86 M207 65 L198 100 M183 111 Q201 95 230 113" fill="none" stroke="#d1d6d3" stroke-width="2"/><text x="16" y="18" font-size="10">ROOF-GARDEN REFERENCE / NOT AN OLD PHOTOGRAPH</text><path d="M273 113 V69 M283 114 V69" stroke="#687986" stroke-width="2"/>',300,180);}
"""
change('play/figures.js','root.R3_FIG={icon,river,park,facade,scene,esc};',mem+'root.R3_FIG={icon,river,park,facade,memorial,scene,esc};','function memorial()')
change('play/app.js',"if(q.type==='river'||q.type==='park')","if(q.type==='timeline')html+=`<div class=\"diagram\" style=\"max-width:300px\">${F.memorial()}</div><p class=\"sub\">${S.lang==='zh'?'参照对象：屋顶庭园的大型坐像、台座与景观墙。自制识别图，不是1930照片或馆藏复制。':'Reference: the roof-garden monument, plinth and scenery wall. An original recognition sketch, not a 1930 photograph or museum reproduction.'}</p>`;\nif(q.type==='river'||q.type==='park')","F.memorial()")
change('tools/build_print.py',"facade:f.facade(),scene:f.scene()","facade:f.facade(),memorial:f.memorial(),scene:f.scene()")
change('tools/build_print.py','</p><div class="strip">REN: ORIGINAL PHOTOGRAPH — 1930</div>','</p><div class="diagram" style="width:52mm;margin:1mm auto">{F["memorial"]}</div><div class="strip">REN: ORIGINAL PHOTOGRAPH — 1930</div>','{F["memorial"]}')
change('tools/build_data.py','按照由左侧远塔、经过道路标志、向馆楼方向扫视的连续关系，把三张取景卡放回画框。','以馆楼那张为画框右端，观察另外两幅景物在连续扫视中的位置，把三张取景卡放回画框。')
change('tools/build_data.py','compare them with a continuous sweep of the same corner, from the distant tower toward the museum building.','compare them with a continuous sweep of the same corner. The building card belongs at the right end; locate the other two relative to it.')
print('R3.1 reference refinement present (idempotent).')

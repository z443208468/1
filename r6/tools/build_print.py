#!/usr/bin/env python3
"""Build bilingual, self-contained R6 paper kits from content/game.json.

The historical diagrams remain byte-identical in figures.js. This renderer
adds no required clue, place, answer, material category, or hidden story gate.
The paper appendix contains all hints, answers, scene changes and six ending
frames, so a phone is optional rather than an answer authority.
"""
from __future__ import annotations

import html
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "content/game.json"


def esc(value: object) -> str:
    return html.escape(str(value))


def txt(value: object, lang: str) -> str:
    if isinstance(value, dict):
        if lang not in value:
            raise ValueError(f"Missing {lang} translation in {value!r}")
        return str(value[lang])
    return str(value)


def paragraphs(value: object, lang: str, cls: str = "") -> str:
    return "".join(f"<p class='{cls}'>{esc(p)}</p>" for p in txt(value, lang).split("\n") if p)


CSS = r"""
@page { size:A4; margin:13mm 14mm; }
* { box-sizing:border-box; }
body { margin:0; color:#183541; font:10pt/1.48 "Noto Sans CJK SC","Noto Sans",Arial,sans-serif; }
body.en { font-family:"Nimbus Sans","DejaVu Sans",Arial,"Noto Sans CJK SC",sans-serif; font-size:10.1pt; line-height:1.47; }
.page { position:relative; height:270mm; width:182mm; break-after:page; }
.page:last-child { break-after:auto; }
.page-content { padding-bottom:2mm; }
.page-foot { position:absolute; bottom:0; width:100%; border-top:.3mm solid #c1cbcd; padding-top:2mm; font-size:7.1pt; display:flex; justify-content:space-between; gap:7mm; }
header { display:flex; justify-content:space-between; gap:6mm; border-bottom:.55mm solid #183541; padding-bottom:2.4mm; font-size:7.4pt; letter-spacing:.035em; }
h1 { font-size:22pt; line-height:1.2; margin:5mm 0 3mm; letter-spacing:-.025em; }
h2 { font-size:13.8pt; line-height:1.3; margin:4mm 0 2mm; }
h3 { font-size:10.4pt; line-height:1.3; margin:3mm 0 1.3mm; }
p { margin:2.3mm 0 3mm; }
ul,ol { padding-left:5.5mm; margin:2mm 0 3mm; }
li { margin:1.5mm 0; }
.sub { font-size:8pt; color:#4a616c; margin-bottom:4mm; }
.small { font-size:8.7pt; line-height:1.48; }
.quiet { font-size:7.9pt; line-height:1.45; color:#4d626b; }
.dialogue { border-left:.8mm solid #a9753c; padding-left:3.5mm; margin:3mm 0 4mm; }
.dialogue p { margin:1.8mm 0; }
.dialogue b { margin-right:2mm; }
.note { border:.35mm solid #9cafb7; background:#f5f7f4; padding:3mm; margin:3mm 0; }
.claim { border:.55mm double #173e49; padding:3mm 4mm; margin:3mm 0; background:#fbf7ee; }
.claim .quiet { margin:0 0 1mm; }
.action { border-left:1.4mm solid #173e49; padding:1mm 3.6mm; margin:3mm 0; }
.route { display:flex; flex-wrap:wrap; gap:1.6mm; }
.route span { border:.3mm solid #aebfc5; padding:1.5mm 2.5mm; font-size:8.4pt; }
.choice { border:.35mm solid #9aadb7; padding:3mm 4mm; margin:3mm 0; }
.write { border-bottom:.3mm solid #687d87; height:10mm; }
.write.short { height:7mm; }
.inline-blank { display:inline-block; min-width:24mm; border-bottom:.25mm solid #687d87; }
.cards { display:flex; gap:3mm; align-items:stretch; margin:3mm 0; }
.card { flex:1; min-width:0; border:.3mm dashed #627b86; padding:2mm; text-align:center; }
.card b { display:block; min-height:8mm; font-size:8.3pt; line-height:1.35; }
.card svg { display:block; width:100%; height:35mm; }
.cut-label { font-size:7.4pt; color:#4d626b; text-align:center; margin:1mm 0 2mm; }
.strip { border:.3mm dashed #627b86; padding:2.6mm 3mm; margin:2.5mm 0; }
.theatre-strip { height:13mm; display:flex; align-items:center; font-size:12pt; }
.half { display:flex; gap:5mm; align-items:flex-start; }
.half>div { width:calc(50% - 2.5mm); min-width:0; }
.diagram { width:81mm; margin:3mm auto; border:.3mm dashed #627b86; padding:1mm; }
.diagram svg { display:block; width:100%; height:auto; }
.half svg { display:block; width:100%; height:auto; }
.wide { width:100%; margin:3mm 0; }
.wide svg { display:block; width:100%; height:auto; }
.performance { width:118mm; margin:3mm auto; }
.performance svg { display:block; width:100%; height:auto; }
.performance.compact { width:102mm; }
.reference { width:143mm; margin:3mm auto; }
.reference svg { display:block; width:100%; height:auto; }
.source { font-size:8.5pt; line-height:1.5; border-top:.3mm solid #c1cdcf; padding-top:2.5mm; margin-top:3mm; overflow-wrap:anywhere; }
.source b { font-size:8.6pt; }
.source .url { font-size:7.3pt; color:#4a606c; margin-top:1mm; }
.source-summary { font-size:8.7pt; border-left:.7mm solid #9aadb6; padding-left:3mm; margin:3mm 0; }
.source-summary p { margin:1.5mm 0; }
table { width:100%; border-collapse:collapse; margin:3mm 0; font-size:9pt; line-height:1.4; }
th,td { border:.28mm solid #aebfc5; padding:2.3mm; vertical-align:top; text-align:left; }
th { width:31%; background:#eef2ef; font-weight:600; }
.field-option { margin-bottom:1.5mm; }
.field-option:last-child { margin-bottom:0; }
.field-check { display:inline-block; width:2.6mm; height:2.6mm; border:.25mm solid #46616f; margin-right:1.7mm; vertical-align:-.2mm; }
.fields.compact { font-size:8.8pt; }
.fields.compact th,.fields.compact td { padding:1.9mm 2.2mm; }
.track { border:.3mm solid #68808b; padding:3mm; height:16mm; margin:3mm 0; }
.material-scene-row { display:flex; gap:3mm; margin:5mm 0; }
.scene-piece { width:53.333mm; outline:.25mm dashed #627b86; box-sizing:border-box; }
.scene-piece svg { display:block; width:53.333mm; height:48mm; }
.scene-piece-label { min-height:10mm; padding:1.5mm; font-size:8pt; text-align:center; }
.assembly-frame { border:1mm solid #213f4c; padding:3mm; width:168mm; height:68mm; margin:5mm auto; }
.assembly-area { width:160mm; height:58mm; outline:.25mm dashed #aebfc5; display:flex; align-items:center; justify-content:center; text-align:center; font-size:10pt; color:#627982; }
.souvenir { display:flex; width:172.6mm; border:.3mm dashed #627b86; margin:4mm auto; }
.souvenir-face { flex:0 0 86mm; width:86mm; height:67mm; padding:2mm; text-align:center; }
.souvenir-face+div { border-left:.3mm dashed #627b86; }
.souvenir-face svg { width:81.7mm; height:49.02mm; display:block; }
.souvenir-face b { display:block; font-size:9pt; margin:2mm 0; }
.receipt { border:.6mm double #183541; padding:4mm; margin:4mm 0; }
.receipt h2 { margin-top:0; }
.receipt p { font-size:9pt; margin:2mm 0; }
.hint { border-top:.3mm solid #b9c8ce; margin:3mm 0; padding-top:2mm; }
.hint b { font-size:9pt; }
.answer { border:.5mm solid #183541; padding:3mm; margin:4mm 0; font-size:9pt; }
.spoiler-header { background:#183541; color:white; padding:1.5mm 2.8mm; font-size:8pt; }
.ending-panel { display:flex; gap:5mm; margin:4mm 0 6mm; align-items:flex-start; }
.ending-panel .art { flex:0 0 91mm; }
.ending-panel .art svg { display:block; width:91mm; height:54.6mm; }
.ending-panel .story { flex:1; font-size:9.3pt; }
.ending-panel h2 { margin-top:0; }
.ending-panel .dialogue { font-size:9.2pt; }
.no-print { padding:12px; margin:0 0 16px; background:#edf2ef; font:15px/1.4 sans-serif; }
a { color:inherit; text-decoration:none; }
.cover h1 { font-size:30pt; }
.cover .performance { width:112mm; }
.cover .dialogue { font-size:9.3pt; }
.cover .claim { font-size:9pt; }
.sources-page h1 { font-size:23pt; }
.hint-page { font-size:9.1pt; line-height:1.42; }
.hint-page h1 { font-size:20pt; }
.hint-page h2 { font-size:12pt; margin:3mm 0 1.5mm; }
.hint-page p { margin:1.5mm 0 2mm; }
.hint-page .hint { margin:2mm 0; padding-top:1.5mm; }
.hint-page .answer { margin:3mm 0; padding:2.5mm; }
.hint-page .performance { width:70mm; margin:2.5mm auto; }
.hint-page .dialogue { margin:2mm 0 3mm; }
.hint-page .note { margin:2mm 0; padding:2.5mm; }
@media screen { body { background:#e4e9e9; } .page { margin:16px auto; padding:0; background:white; box-shadow:0 1px 7px #b4c1c5; outline:13mm solid white; margin-bottom:40mm; } .no-print { text-align:center; } }
@media print { .no-print { display:none; } }
"""


class Kit:
    def __init__(self, data: dict, figures: dict, lang: str):
        self.d, self.f, self.l = data, figures, lang
        self.sources = {s["id"]: s for s in data["sources"]}
        self.pages: list[dict] = []

    def T(self, zh: str, en: str) -> str:
        return zh if self.l == "zh" else en

    def text(self, value: object) -> str:
        return txt(value, self.l)

    def p(self, value: object, cls: str = "") -> str:
        return paragraphs(value, self.l, cls)

    def art(self, name: str, cls: str = "performance") -> str:
        return f"<div class='{cls}'>{self.f[self.l][name]}</div>"

    def dialogue(self, rows: list) -> str:
        return "<div class='dialogue'>" + "".join(f"<p><b>{esc(self.text(r['speaker']))}</b>{esc(self.text(r['text']))}</p>" for r in rows) + "</div>"

    def add(self, key: str, title: str, body: str, sub: str = "", cls: str = "") -> None:
        if any(p["key"] == key for p in self.pages):
            raise ValueError(f"Duplicate page {key}")
        self.pages.append(dict(key=key,title=title,body=body,sub=sub,cls=cls))

    def ref(self, key: str) -> str:
        return self.T("第", "p. ") + "{{page:" + key + "}}" + self.T("页", "")

    def fields(self, fields: list, compact: bool = False) -> str:
        rows = []
        for field in fields:
            options = "".join(f"<div class='field-option'><span class='field-check'></span>{esc(self.text(label))}</div>" for _, label in field["options"])
            rows.append(f"<tr><th>{esc(self.text(field['label']))}</th><td>{options}</td></tr>")
        return "<table class='fields" + (" compact" if compact else "") + "'><tbody>" + "".join(rows) + "</tbody></table>"

    def facts(self, ids: list[str], full: bool = False) -> str:
        pieces = []
        for sid in ids:
            s = self.sources[sid]
            title = self.text(s["title"]) if isinstance(s["title"], dict) else s["title"]
            content = f"<b>{esc(sid)} · {esc(title)}</b>" + self.p(s["fact"])
            if full and s.get("url"):
                content += f"<div class='url'>{esc(s['url'])}</div>"
            elif full:
                content += f"<div class='url'>{self.T('既有现场研究记录；公开包不含原始照片。','Existing field-evidence review; original photographs are not included.')}</div>"
            pieces.append(f"<div class='{'source' if full else 'source-summary'}'>{content}</div>")
        return "".join(pieces)

    def check_link(self, index: int) -> str:
        return "<div class='note small'>" + self.T("想要提示或完成核对？翻到", "For hints or solution checking, turn to ") + self.ref(f"h{index}") + self.T("。先按需读提示1→2→3；作答后再读“画面改变”。全部免费。", ". Read hints 1 → 2 → 3 as needed. After answering, read the scene change. Everything is free.") + "</div>"

    def answered(self, q: dict) -> str:
        answer = q["answer"]
        lines = []
        if "order" in answer:
            labels={c["id"]:self.text(c["label"]) for c in q["cards"]}
            lines.append(" → ".join(labels[c] for c in answer["order"]))
        if "rotation" in answer:
            if q["id"] == "s2":
                lines.append(self.T("河图：北箭头朝上，支流从主河左上侧进入；采用另一面图的这一方向。", "River card: north arrow up, tributary entering from upper left; use the alternate face in this orientation."))
            else:
                lines.append(self.T("公园图：河侧在上，大场地在左，体育中心在右。将B面顺时针转四分之一圈。", "Park card: river edge above, field left, sports centre right. Rotate Face B a quarter-turn clockwise."))
        for field in q["fields"]:
            value = answer[field["id"]]
            label=next(label for option,label in field["options"] if option==value)
            lines.append(self.text(field["label"])+self.T("：", ": ")+self.text(label))
        return "<div class='answer'><b>"+self.T("完整核对", "Complete solution")+"</b>"+"".join(f"<p>{esc(line)}</p>" for line in lines)+"</div>"

    def build(self) -> None:
        d, l, T = self.d, self.l, self.T
        q=d["stages"]
        # Opening: antagonist claims are visible from the first page, not added
        # opportunistically at the park. This is player fiction, not a source.
        cover=(self.p(d["subtitle"],"sub")+self.art(d["openingFigure"])+self.p(d["opening"])
            +"<div class='claim'><p class='quiet'>"+T("开场题签 · 影戏中的角色约定", "OPENING CAPTION · A condition within the fictional show")+"</p>"+self.p(d["originalCaption"])+"</div>"
            +"<div class='claim'>"+self.p(d["parkAnnotation"])+"</div>"
            +self.p(d["fictionNotice"],"quiet")
            +"<div class='note small'>"+T("每组只打印一种语言。准备与预裁说明见", "Print only one language per team. Preparation and cutting: ")+self.ref("rules")+T("。<br>",".<br>")+T("任务与原道具", "Tasks & original pieces")+" "+self.ref("s1")+"—"+self.ref("souvenir")+" · "+T("史料", "Sources")+" "+self.ref("sources1")+"—"+self.ref("sources3")+"<br>"+T("提示与核对", "Hints & checking")+" "+self.ref("h1")+"—"+self.ref("finalcheck")+" · "+T("完整六幕", "All six ending scenes")+" "+self.ref("ending1")+"—"+self.ref("ending3")+"</div>")
        self.add("cover",self.text(d["title"]),cover,cls="cover")
        materials=T("三张街景识别卡、三条横向河景与原框；两面河图和两标签；双时间轨与下界条；公园A/B图、四相机片、两用途片、外墙参照；四剧院名条与1928迁址条；回执与可折叠双面纪念片。", "Three view cards, three horizontal river strips and frame; two-face river card and two labels; two timelines and lower-bound strip; park A/B, four camera markers, two purpose labels and facade reference; four theatre-name strips and 1928 move; receipt and foldable two-face souvenir.")
        rules="<ol>"+"".join("<li>"+esc(self.text(r))+"</li>" for r in d["rules"])+"</ol>"
        route="<div class='route'>"+"".join("<span>"+esc(s)+"</span>" for s in T(["01 纽扣馆外","02 两国桥","03 芭蕉免费庭园","04 浜町公园","05 明治座外"],["01 Button Museum exterior","02 Ryogoku Bridge","03 Free Basho garden","04 Hamacho Park","05 Meijiza exterior"]))+"</div>"
        how=(route+rules+"<h2>"+T("出发前准备", "Prepare before you leave")+"</h2><p>"+T("一组2—4人，只印一种语言的一套纸包，带笔、夹板和纸夹。A4单面、100%打印，不用‘适合页面’，不需要双面套印。提前沿虚线剪好可移动件，折好纪念片，不在街上剪纸。", "For a team of 2–4, print one language only. Bring a pen, clipboard and clips. Print A4, single-sided at 100%, without fit-to-page. No duplex registration is needed. Cut movable pieces and fold the souvenir before leaving.")+"</p><p class='small'>"+materials+"</p>"
            +"<p class='small'>"+T("任务页与剪好的原道具放在随手可取处；来源和揭示附录另夹一叠，仍一起携带，按提示页码取用。", "Keep task pages and cut pieces readily accessible. Clip source and reveal appendices separately, but carry them with you and use the printed page references.")+"</p>"
            +"<h2>"+T("全纸怎么玩", "Playing entirely on paper")+"</h2><p>"+T("轮流观察、持图和记录。每关完成后翻到该关提示附录核对，再读画面改变与下一站。终局核对七项后读取全部六格收场。可请同伴代读提示，但不必配备主持人或手机。", "Take turns observing, holding diagrams and recording. After each puzzle, check that stop’s appendix, then read its scene change and next stop. Check the seven finale entries and read all six ending frames. A teammate may read hints aloud; neither a host nor a phone is required.")+"</p>"
            +self.p(d["safety"],"small")+"<p class='small'>"+T("小组名／日期", "Team / date")+"：____________________　"+T("模式", "Mode")+"：□ "+T("桌面", "Desktop")+"　□ "+T("实地", "Field")+"</p>"
            +"<p class='quiet'>"+T("每关自行记录：现场观察／备用资料，以及用到的提示。它不会减少结尾或奖励。", "At each stop record site observation or backup materials and any hints used. Neither reduces the ending or reward.")+"</p>")
        self.add("rules",T("带着同一条河出发", "Carry the same river"),how)
        opening=self.dialogue(d["openingDialogue"])+"<h2>"+T("先把遮片放上去", "Place the screen")+"</h2><p>"+T("从纪念片页取出折好的卡，窄窗面朝上。S01拼好原景后，把它放在原框的一端，覆盖部分景条。把其余纸件放在旁边，随时可查。先不翻看六格收场。", "Take the folded souvenir card with its narrow-window face up. Once S01 is assembled, place it across one end of the original frame to cover part of the strips. Keep the other papers beside it, available whenever needed. Leave the six ending frames unread for now.")+"</p><p class='small'>"+T("纪念片见", "Souvenir: ")+self.ref("souvenir")+T("。先看这个街角，别急着替空舟寻找另一座城市。", ". Start with this street corner, before searching another city for Utsuro.")+"</p>"
        self.add("opening",self.text(d["openingTitle"]),opening+self.art("fragments"),T("阅读页 · 无需剪下", "Reading page · do not cut"))
        # S01: three recognition cards and the one categorical reading.
        s=q[0]
        cards="<div class='cards'>"+"".join(f"<div class='card'><b>{esc(self.text(c['label']))}</b>{self.f[c['icon']]}</div>" for c in s["cards"])+"</div>"
        s1=self.dialogue(s["before"])+self.p(s["intro"])+cards+"<div class='track'>"+T("连续视野顺序", "Continuous-view order")+"：________ → ________ → ________</div>"+self.fields(s["fields"])+self.p(s["prompt"],"small")+self.check_link(1)
        self.add("s1",self.text(s["title"]),s1,self.text(s["site"]))
        strips=[]
        scene_inner=self.f["scene"].split(">",1)[1].rsplit("</svg>",1)[0]
        for c in s["cards"]:
            x={"tower":0,"sign":200,"roof":400}[c["id"]]
            svg=f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{x} 0 200 180'>{scene_inner}</svg>"
            strips.append(f"<div class='scene-piece' data-material='scene-strip'><div class='scene-piece-label'>{esc(self.text(c['label']))}</div>{svg}</div>")
        assembly=self.p(s["operation"])+"<p class='cut-label'>"+T("沿各片虚线剪下 · 三条景横向接合", "Cut each dashed outline · join the three strips horizontally")+"</p><div class='material-scene-row'>"+"".join(strips)+"</div><div class='assembly-frame' data-material='frame'><div class='assembly-area'>"+T("原框：将三条景横向接好", "ORIGINAL FRAME: join the three strips horizontally")+"</div></div><div class='claim'>"+self.p(d["originalCaption"])+"</div>"+self.facts(["B02"])+"<p class='quiet'>"+T("图为原创示意，不是馆藏复制；街景卡与横景条不是可拆景深装置。不要再裁开图内的前景。", "Original diagrams, not museum reproductions. The view cards and horizontal strips are not detachable depth layers. Do not cut out their foreground objects.")+"</p>"
        self.add("s1pieces",T("01B · 原景条与画框", "01B · Original strips and frame"),assembly,T("物料页 · 100%原尺寸打印", "Materials · print at 100%"))
        # S02: the alternate paper face is supplied, not manufactured with a
        # precision duplex operation. Geographical alignment is still required.
        s=q[1]
        s2=self.dialogue(s["before"])+self.p(s["intro"])+self.art(s["beforeFigure"],"performance compact")+self.p(s["operation"],"action")+self.facts(["R02","M01"])
        self.add("s2",self.text(s["title"]),s2,self.text(s["site"]))
        river_a="<div class='diagram' data-material='river-A'>"+self.f["riverA"]+"</div>"+"<p class='small'>"+T("可旋转此卡。要查看另一面，使用下一页的同一河图替代面；不需要双面套准。两面都要与主河、支流和桥的关系对照。", "Rotate this card. To view the other side, use the alternate river face on the next page; no precise duplex registration is needed. Compare either face with the main river, tributary and bridges.")+"</p>"+self.fields(s["fields"])+self.p(s["prompt"],"small")+"<p class='quiet'>"+T("图例：N北；YANAGI柳桥；NOW现两国桥；OLD旧桥示意。", "Legend: N north; YANAGI Yanagi Bridge; NOW present Ryogoku Bridge; OLD symbolic old bridge.")+"</p>"+self.check_link(2)
        self.add("s2work",T("02A · 转正河图，再分开落签", "02A · Orient the river; place both labels"),river_a)
        river_b="<div class='diagram' data-material='river-B'>"+self.f["riverB"]+"</div><div class='half'><div class='strip' data-material='river-label'>稲瀬川 / INASE</div><div class='strip' data-material='river-label'>隅田川 / SUMIDA</div></div><div class='track'>"+T("舞台称呼", "STAGE NAME")+"：________________</div><div class='track'>"+T("真实借景地", "REAL SCENERY")+"：________________</div>"+self.facts(["R01"])+"<p class='quiet'>"+T("桥上只拿当前所需的一页；展开整套纸件时请移到不挡通行的允许停留处。", "On the bridge, hold only the page you need. Spread the kit only at a permitted stopping place clear of pedestrian traffic.")+"</p>"
        self.add("s2back",T("02B · 河图另一面与两张标签", "02B · Alternate face and two labels"),river_b,T("物料页 · 不是另一条河", "Materials · the other face of the same river"))
        # S03: the image is a modern functional reference, and the paper record
        # contains an actual detachable lower-bound strip, not only a prose label.
        s=q[2]
        s3=self.dialogue(s["before"])+self.p(s["intro"])+"<div class='reference' style='width:125mm'>"+self.f["memorial"]+"</div>"+self.facts(["H07","H01"])+self.p(s["prompt"],"small")
        self.add("s3",self.text(s["title"]),s3,self.text(s["site"]))
        choice="<div class='choice'><b>"+T("核对本关后，作出中段选择", "After checking this stop, choose how to continue")+"</b>"+"".join("<p>□ "+esc(self.text(d["choiceLabels"][c]))+"</p>" for c in ("challenge","share"))+"<p class='quiet'>"+T("只影响第一次公园图的校准帮助；相机侧与用途仍由你们判断。若已经开始公园关，之后更改此选择不重摆正在使用的图。", "This affects initial park-map calibration only. You still choose the camera side and purpose. If you have already started the park puzzle, changing this choice does not reset that work.")+"</p></div>"
        s3work=self.p(s["operation"],"action")+"<div class='track' data-material='life-track'>"+T("人物生活轨：芭蕉迁居深川", "PERSON: Basho moves to Fukagawa")+"　________</div><div class='track' data-material='facility-track'>"+T("纪念设施轨：这座庭园可以被拍到", "SETTING: this garden can be photographed")+"　________</div><div class='strip' data-material='lower-bound'>"+T("摄影下界：不早于 ________；不能据此知道确切拍摄年。", "LOWER BOUND: no earlier than ________; the exact year remains unknown.")+"</div>"+self.fields(s["fields"])+choice+self.check_link(3)
        self.add("s3work",T("03B · 两条时间线", "03B · Two timelines"),s3work,T("物料与作答 · 不把人物年代当作设施年代", "Materials and answers · distinguish person from setting"))
        # S04 supplies all historical dates on the current page. It does not
        # pretend 1929 derives a present camera orientation.
        s=q[3]
        s4=self.dialogue(s["before"])+self.p(s["intro"])+"<div class='claim'>"+self.p(d["parkAnnotation"])+"</div>"+self.facts(["M03","M04","P01"])+self.p(s["operation"],"action")
        self.add("s4",self.text(s["title"]),s4,self.text(s["site"]))
        facade="<div class='reference'>"+self.f["facade"]+"</div><p class='quiet'>"+T("原创功能参照：前景游乐设施，后景菱形外墙；不是照片，不证明大楼建造年份。", "Original functional reference: play equipment in front, diamond facade behind. This is not a photograph and does not date the building.")+"</p>"+self.fields(s["fields"])+self.p(s["prompt"],"small")+self.check_link(4)
        self.add("s4work",T("04A · 让前后两层同时留下", "04A · Keep foreground and background"),facade)
        markers=[("playground",T("游乐区侧", "PLAYGROUND SIDE")),("river",T("河岸侧", "RIVER SIDE")),("entrance",T("圆形入口侧", "CIRCULAR ENTRANCE")),("field",T("大场地侧", "FIELD SIDE"))]
        mapwork="<p class='small'>"+T("A、B沿边剪下，背靠背夹起即可模拟翻面；分别转动也可以。不用透明片或精密套印。先同时对准河边、大场地和体育中心。", "Cut A and B, then clip them back-to-back to simulate turning the map over; you may also rotate them separately. No transparency or exact registration is needed. Match river edge, large field and sports centre together.")+"</p><div class='half'><div><h3>"+T("A面", "FACE A")+"</h3><div data-material='park-A'>"+self.f["parkA"]+"</div></div><div><h3>"+T("B面", "FACE B")+"</h3><div data-material='park-B'>"+self.f["parkB"]+"</div></div></div><h2>"+T("相机位置片 · 选择一张", "Camera markers · choose one")+"</h2>"
        for j in range(0,4,2):
            mapwork+="<div class='half'>"+"".join("<div class='strip' data-material='camera-marker'>□ "+esc(label)+"</div>" for _,label in markers[j:j+2])+"</div>"
        mapwork+="<div class='half'><div class='strip' data-material='purpose-label'>CAPTURE AT<br>"+T("从这里取景", "VIEW FROM HERE")+"</div><div class='strip' data-material='purpose-label'>DELIVER TO<br>"+T("向这里交付", "DELIVER HERE")+"</div></div><div class='note small'><b>"+T("只在你选了“交换校准资料”时读", "Read only if you chose “Exchange calibration”")+"</b><p>"+T("把B面顺时针转四分之一圈：河边在上、大场地在左、体育中心在右。只帮你摆正大锚点；相机片放哪边、用途是什么，仍由你们决定。", "Turn Face B a quarter-turn clockwise: river edge above, field left, sports centre right. This aligns the large anchors only. You still place the camera and choose the purpose.")+"</p></div><p class='quiet'>"+T("图例：FIELD场地；CENTRE体育中心；PLAY游乐区；ENTRANCE入口；POOL水池；LAWN草地。布局图不证明当日通行。", "Legend: FIELD, CENTRE (sports centre), PLAY (playground), ENTRANCE, POOL, LAWN. The layout does not establish access on the day.")+"</p>"
        self.add("s4pieces",T("04B · 公园图与观察端", "04B · Park card and viewpoint"),mapwork,T("物料页 · 不沿示意线进入场地或围挡", "Materials · do not follow diagram lines into restricted areas"))
        # S05's records keep all four old names and the move as separate objects.
        s=q[4]
        s5=self.dialogue(s["before"])+self.p(s["intro"])+self.art(s["beforeFigure"],"performance compact")+self.facts(["M01","M07"])+self.p(s["prompt"],"small")
        self.add("s5",self.text(s["title"]),s5,self.text(s["site"]))
        names=self.p(s["operation"],"action")+"".join("<div class='strip theatre-strip' data-material='theatre-name'>"+esc(self.text(c["label"]))+"</div>" for c in s["cards"])+"<div class='strip theatre-strip' data-material='move-1928'>1928 · "+T("迁址与重新开场", "RELOCATION & REOPENING")+"</div><div class='track'>"+T("名字沿革", "NAME HISTORY")+"：________ → ________ → ________ → ________</div><div class='track'>"+T("位置变化", "LOCATION HISTORY")+"：________________________</div>"+self.fields(s["fields"])+self.check_link(5)
        self.add("s5work",T("05B · 名字与位置各归一行", "05B · Names and location on separate tracks"),names)
        # Finale entries preserve the frozen seven fields. No chapter stamps.
        ending_choice="<div class='choice'>"+"".join("<p>□ "+esc(self.text(d["endingLabels"][key]))+"</p>" for key in ("solo","joint"))+"</div>"
        final=self.p(d["finalIntro"],"small")+self.fields(d["finalFields"],compact=True)+ending_choice+"<p class='small'>"+T("完成后对照", "When ready, check ")+self.ref("finalcheck")+T("；全部成立即可读取六格结尾。无需集齐五关印章，正确早解也成立。", " and read all six ending frames. No five-stamp requirement: a correct early solution counts.")+"</p>"
        self.add("final",self.text(d["finalTitle"]),final)
        souvenir="<div class='receipt' data-material='receipt'><h2>"+T("原景回执", "ORIGINAL SCENE RECEIPT")+"</h2>"
        for zh,en in [("舞台称呼 / 真实借景地","Stage name / real scenery"),("现代参照的下界","Lower bound of the modern reference"),("观察端 / 用途","Viewpoint / purpose"),("旧名 → 当代对应","Old name → present counterpart"),("小组签名 / 汐（联合时）","Team signature / Shio (if joint)")]:
            souvenir+="<p>"+T(zh,en)+"：________________________________________________</p>"
        souvenir+="</div><h2>"+T("同一张纪念片，两面", "One souvenir, two faces")+"</h2><div class='souvenir' data-material='souvenir'><div class='souvenir-face'><b>"+T("正面 · 窄窗／遮片", "FRONT · NARROW WINDOW / SCREEN")+"</b>"+self.f[l]["caper_open"]+"</div><div class='souvenir-face'><b>"+T("背面 · 完整舞台／放下遮片", "BACK · WHOLE STAGE / SCREEN DOWN")+"</b>"+self.f[l]["caper4"]+"</div></div><p class='cut-label'>"+T("只剪外框，中间虚线折叠；图面朝外，背面对背面。折好后约86 × 67毫米。", "Cut the outer border only. Fold the centre dashed line with the illustrations facing out, blank backs together. Folded size approximately 86 × 67 mm.")+"</p>"+self.p(d["paperEnding"],"small")+"<p class='quiet'>"+T("纪念片属于本场原创影戏，不是门票、馆藏或现场授权。它只覆盖原景一端，不替换也不拆开三条横景。", "This original souvenir is not a ticket, museum object or venue authorization. It covers one end of the original scene; it neither replaces nor separates the three strips.")+"</p>"
        self.add("souvenir",T("回执与可折叠纪念片", "Receipt and foldable souvenir"),souvenir,T("物料页 · 单面打印即可完成两面", "Materials · both faces come from one printed side"))
        # Full sources include facts and bounds in both complete language packs.
        ids=list(self.sources)
        for start in range(0,len(ids),6):
            number=start//6+1
            self.add(f"sources{number}",T("史料随身读", "History to carry")+f" · {number}",
                "<p class='quiet'>"+T("真实史料与原创戏的角色主张分开阅读。网址供复核，纸包已印必要事实，无需联网。资料检索基准：2026-10-20。", "Separate historical sources from claims made by fictional characters. URLs allow verification; the needed facts are printed here, so internet access is optional. Research date: 20 October 2026.")+"</p>"+self.facts(ids[start:start+6],full=True),cls="sources-page")
        # The solution/scene-change appendix is deliberately not a gate. Each
        # stage has exactly three free hints and the full post-answer material.
        for index,s in enumerate(q,1):
            hints="<div class='spoiler-header'>"+T("提示／核对／画面改变 · 按需翻阅", "HINTS / SOLUTION / SCENE CHANGE · Read as needed")+"</div>"
            hints+="".join(f"<div class='hint'><b>{T('免费提示','Free hint')} {j}</b>{self.p(hint)}</div>" for j,hint in enumerate(s["hints"],1))
            hints+=self.answered(s)+self.art(s["afterFigure"],"performance compact")+"<h2>"+T("画面改变", "The scene changes")+"</h2>"+self.p(s["success"],"small")+self.dialogue(s["after"])+"<div class='note small'>"+self.p(s["lead"])+"</div>"
            if index==3:
                hints+="<p class='quiet'>"+T("中段选择的两种回应见", "Both midgame responses are printed on ")+self.ref("choices")+T("。</p>",".</p>")
            self.add(f"h{index}",T("核对", "Check")+f" {index:02d} · "+self.text(s["title"]).split(" · ",1)[-1],hints,cls="hint-page")
        finalrows=[]
        for field in d["finalFields"]:
            val=d["finalAnswer"][field["id"]]
            label=next(label for option,label in field["options"] if option==val)
            finalrows.append(f"<tr><th>{esc(self.text(field['label']))}</th><td>{esc(self.text(label))}</td></tr>")
        finalcheck="<div class='spoiler-header'>"+T("终局核对 · 七项一起成立", "FINALE CHECK · All seven entries agree")+"</div><table>"+"".join(finalrows)+"</table><p>"+T("有任何一项不符，回看对应的史料和操作；想跳过也可以把这份完整判断作为辅助完成，照样读取全部结尾。", "If an entry differs, revisit its source and operation. You may also use this complete account as assistance and still read the whole ending.")+"</p><h2>"+T("把舞台留住，再读终局", "Keep the stage, then read the ending")+"</h2>"+self.p(d["paperEnding"])+"<p>"+T("从", "Begin at ")+self.ref("ending1")+T("开始顺序读取六幕。独立／联合只改变最后落款与回应，没有缺页、隐藏真相或奖励差别。", ". Read all six scenes in order. Independent or joint signatures change only the final response and receipt; neither hides content or reduces the souvenir.")+"</p>"
        self.add("finalcheck",T("这条河，留在同一幅景里", "Keep the river in the same picture"),finalcheck)
        # Six complete frames: two per A4 page, with image and source-script text.
        for start in range(0,6,2):
            body="<div class='spoiler-header'>"+T("完整收场 · 依次读完六幕", "THE COMPLETE ENDING · Read all six scenes in order")+"</div>"
            for scene in d["finale"][start:start+2]:
                body+="<h2>"+esc(self.text(scene["title"]))+"</h2><div class='ending-panel'><div class='art'>"+self.f[l][scene["figure"]]+"</div><div class='story'>"+self.p(scene["text"])+self.dialogue(scene["dialogue"])+"</div></div>"
                if "byEnding" in scene:
                    body+="<div class='half'>"+"".join("<div class='note small'><b>"+esc(self.text(d["endingLabels"][key]))+"</b>"+self.p(scene["byEnding"][key])+"</div>" for key in ("solo","joint"))+"</div>"
            self.add(f"ending{start//2+1}",T("最后一幕归你们", "The last scene is yours")+f" · {start+1}—{start+2}",body)
        responses="<div class='spoiler-header'>"+T("选择附录 · 四种组合，完整收场", "CHOICE APPENDIX · Four combinations, one complete ending")+"</div>"
        for key in ("challenge","share"):
            responses+="<h2>"+esc(self.text(d["choiceLabels"][key]))+"</h2>"+self.p(d["choiceResponses"][key],"small")
        responses+="<table><thead><tr><th>"+T("中段", "Midgame")+"</th><th>"+T("落款", "Signature")+"</th><th>"+T("得到的内容", "What you receive")+"</th></tr></thead><tbody>"
        for a in ("challenge","share"):
            for b in ("solo","joint"):
                responses+="<tr><td>"+esc(self.text(d["choiceLabels"][a]))+"</td><td>"+esc(self.text(d["endingLabels"][b]))+"</td><td>"+T("同一真相、完整六幕、同一原景与纪念片", "The same truth, all six scenes, original view and souvenir")+"</td></tr>"
        responses+="</tbody></table>"
        for key in ("solo","joint"):
            responses+="<h2>"+esc(self.text(d["endingLabels"][key]))+"</h2>"+self.p(d["ending"][key],"small")
        self.add("choices",T("把名字写在留下来的景旁", "Sign beside the scene that stayed"),responses)

    def html(self) -> str:
        count=len(self.pages)
        lookup={p["key"]:i+1 for i,p in enumerate(self.pages)}
        pieces=[]
        for i,p in enumerate(self.pages,1):
            sub=f"<p class='sub'>{esc(p['sub'])}</p>" if p["sub"] else ""
            body=f"<section class='page {p['cls']}' id='{p['key']}'><div class='page-content'><header><span>THE RIVER THIEF · R6</span><span>{self.T('玩家纸包 · 中文', 'PLAYER KIT · ENGLISH')}</span></header><h1>{esc(p['title'])}</h1>{sub}{p['body']}</div><footer class='page-foot'><span>{self.T('A4 · 单面 · 100% · 原创游戏材料', 'A4 · SINGLE-SIDED · 100% · ORIGINAL GAME MATERIAL')}</span><span>{i} / {count}</span></footer></section>"
            body=re.sub(r"\{\{page:([^}]+)\}\}",lambda m:str(lookup[m.group(1)]),body)
            pieces.append(body)
        title=self.text(self.d["title"])
        return f"<!doctype html><html lang='{self.l}'><head><meta charset='utf-8'><title>{esc(title)} · {self.l.upper()} Player Kit</title><style>{CSS}</style></head><body class='{self.l}'><div class='no-print'><button onclick='window.print()'>{self.T('打印题包','Print kit')}</button> · A4 · 100% · {count} {self.T('页','pages')} · <a href='print.html'>{self.T('选择语言','Choose language')}</a></div>"+"".join(pieces)+"</body></html>"


def main() -> None:
    if not DATA.exists():
        raise SystemExit("Missing r6/content/game.json; earlier story data will not be substituted.")
    data=json.loads(DATA.read_text(encoding="utf-8"))
    required=("openingDialogue","fictionNotice","originalCaption","parkAnnotation","finale","paperEnding","choiceLabels","choiceResponses","endingLabels")
    for key in required:
        if key not in data:
            raise SystemExit(f"Missing current R6 content: {key}")
    if len(data["stages"])!=5 or any(len(s["hints"])!=3 for s in data["stages"]) or len(data["finale"])!=6:
        raise SystemExit("Expected exactly five stages, three free hints each, and six ending scenes.")
    js=r"""const F=require('./play/figures.js'),C=require('./play/caper.js');
    const r={tower:F.icon('tower'),sign:F.icon('sign'),roof:F.icon('roof'),
    riverA:F.river({rotation:1,mirror:true}),riverB:F.river({rotation:0,mirror:false}),
    parkA:F.park({rotation:3,mirror:true}),parkB:F.park({rotation:3,mirror:false}),
    facade:F.facade(),memorial:F.memorial(),scene:F.scene()};
    const names=['caper_open','caper0','caper1','caper2','caper3','caper4','caper5','fragments','joined','riverWrong','riverBoth','oldClaim','modernReference','parkCrop','parkFull','oldExit','lineageJoined'];
    for(const l of ['zh','en'])r[l]=Object.fromEntries(names.map(n=>[n,C.svg(n,l,{static:true})]));
    process.stdout.write(JSON.stringify(r));"""
    node=os.environ.get("CODEX_PRIMARY_RUNTIME_NODE") or shutil.which("node")
    if not node:
        raise SystemExit("Node is required to render the unchanged SVG drawing functions.")
    figures=json.loads(subprocess.check_output([node,"-e",js],cwd=ROOT,text=True))
    out=ROOT/"play"
    out.mkdir(parents=True,exist_ok=True)
    metadata={"content_source":"content/game.json","content_sha256":hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "figures_sha256":hashlib.sha256((ROOT/"play/figures.js").read_bytes()).hexdigest(),
        "caper_sha256":hashlib.sha256((ROOT/"play/caper.js").read_bytes()).hexdigest(),
        "required_material_categories_unchanged":True,
        "print_instruction":"One language per team; A4 single-sided at 100%; prepare cuts and folds before the walk.",
        "sections":{"opening_and_preparation":[1,3],"tasks_and_original_materials":[4,17],"sources":[18,20],"hints_and_checks":[21,26],"complete_ending":[27,29],"four_choice_combinations":[30,30]},
        "material_pages":[4,5,7,8,10,12,13,15,17],
        "materials":{"view_cards":3,"horizontal_scene_strips":3,"frame":1,"river_map_faces":2,"river_labels":2,"timeline_tracks":2,"lower_bound_strip":1,"park_map_faces":2,"camera_markers":4,"purpose_labels":2,"facade_reference":1,"theatre_name_strips":4,"move_1928":1,"receipt":1,"folded_souvenir":1},
        "languages":{}}
    for lang in ("zh","en"):
        kit=Kit(data,figures,lang)
        kit.build()
        target=out/f"print_{lang}.html"
        target.write_text(kit.html(),encoding="utf-8")
        metadata["languages"][lang]={"pages":len(kit.pages),"page_index":[{"page":i+1,"key":p["key"],"title":p["title"]}for i,p in enumerate(kit.pages)]}
        print(f"{target}: {len(kit.pages)} fixed A4 pages")
    (out/"print.html").write_text("<!doctype html><html lang='zh'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>The River Thief · Print kits</title><style>body{font:18px/1.6 sans-serif;max-width:760px;margin:50px auto;padding:0 24px;color:#173b46}a{display:block;padding:16px;margin:16px 0;background:#eef3ef;color:#173b46;border:1px solid #9ab0b8;text-decoration:none}</style><h1>借景怪盗：消失的隅田川<br><small>The River Thief</small></h1><p>完整玩家纸包 · Complete paper player kits</p><a href='print_zh.html'>中文题包</a><a href='print_en.html'>English player kit</a><a href='guide.html'>设计审阅指南 / Designer guide</a><p>A4 · 100% · 单面 / single-sided</p><p>提示、答案和完整结尾均在纸包中。No phone is required for hints, checking or the complete ending.</p></html>",encoding="utf-8")
    (ROOT/"qa/print_manifest.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()

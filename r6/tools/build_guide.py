#!/usr/bin/env python3
"""Build the R6 designer review HTML from the current authored sources.

This renderer never imports or falls back to an earlier story. PDF creation is
handled by render_pdfs.py so the same local HTML can be inspected in a browser.
"""
from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCAL_PACKAGES = ROOT.parents[0] / "runtime-python"
# The optional local dependency directory is a convenience, never downloaded.
for candidate in (ROOT.parents[1] / "runtime-python", LOCAL_PACKAGES):
    if candidate.is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
from markdown_it import MarkdownIt


def e(value: object) -> str:
    return html.escape(str(value))


CSS = """
@page { size:A4; margin:17mm 16mm 19mm; }
* { box-sizing:border-box; }
html { color:#172e3c; background:white; }
body { margin:0; width:178mm; font:9.6pt/1.62 "Nimbus Sans","DejaVu Sans","Noto Sans CJK SC",Arial,sans-serif; }
h1 { font-size:24pt; line-height:1.25; margin:7mm 0 5mm; }
h2 { font-size:17pt; line-height:1.3; margin:8mm 0 3mm; }
h3 { font-size:12pt; margin:5mm 0 2mm; }
h4 { font-size:10.5pt; margin:4mm 0 1mm; }
h1,h2,h3,h4 { break-after:avoid; }
p { margin:2.6mm 0; orphans:3; widows:3; }
ul,ol { margin:2.5mm 0; padding-left:6mm; }
li { margin:1.2mm 0; }
table { border-collapse:collapse; width:100%; margin:4mm 0; font-size:8pt; line-height:1.5; }
thead { display:table-header-group; }
tr { break-inside:avoid; }
th,td { border:0.3mm solid #bec9cd; padding:2mm; text-align:left; vertical-align:top; overflow-wrap:anywhere; }
th { background:#eef2f0; font-weight:700; }
a { color:#24516c; overflow-wrap:anywhere; text-decoration:none; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; border:0.3mm solid #c8d1d4; background:#f4f6f5; padding:4mm; font:7.6pt/1.5 monospace; }
code { font-size:.9em; overflow-wrap:anywhere; }
blockquote { border-left:1mm solid #b3884b; padding:1mm 4mm; margin:4mm 0; background:#f6f3ec; }
hr { border:0; border-top:0.4mm solid #b8c6cb; margin:7mm 0; }
img { max-width:100%; }
.chapter { break-before:page; }
.chapter:first-child { break-before:auto; }
.chapter-label { font-size:8pt; letter-spacing:.07em; border-bottom:.5mm solid #173445; padding-bottom:3mm; }
.cover { min-height:250mm; display:flex; flex-direction:column; justify-content:space-between; }
.cover h1 { font-size:34pt; max-width:150mm; }
.subtitle { font-size:17pt; }
.status { border:0.5mm solid #173445; padding:5mm; margin:6mm 0; }
.small { font-size:8.4pt; color:#465d69; }
.source-item { break-inside:avoid; padding:3mm 0; border-bottom:0.3mm solid #d2dadd; }
.toc li { margin:2.8mm 0; }
.no-print { margin:16px; padding:12px; background:#edf3f3; }
@media print { .no-print { display:none; } }
"""

RESEARCH_INDEX = [
    ("00_NARRATIVE_RESEARCH.md", "创作原理、研究证据与对标产品。研究给出可检验设计假设，不能保证作品好看。"),
    ("01_HISTORY_AND_CAUSALITY.md", "史实、地点关系、已读官方来源及推断边界。"),
    ("02_EVENT_CANDIDATES.md", "第一轮事件候选；不得作为有效玩家剧情读取。"),
    ("03_REJECTED_NARRATIVE_REVIEW.md", "第一轮叙事否决记录。"),
    ("04_REJECTED_HISTORY_REVIEW.md", "第一轮史实与因果否决记录。"),
    ("05_BASELINE_RECOVERY.md", "R3.1 机制、图形与已知缺陷的回收基线。"),
    ("06_EVENT_D_ACTION_CONTRACT.md", "D 第一版行动合同；已经修订，非最终玩家文本。"),
    ("06b_D_INDEPENDENT_REVISE.md", "D 第一版独立复核与退修问题。"),
    ("07_D_REVISION_STORYBOARD.md", "D 修订分镜、场景变化、物料限制与六格结尾。"),
    ("08_D2_PROTOTYPE_REVIEW.md", "仅允许进入完整原型的独立判断；不等于游客质量通过。"),
]


def build(allow_incomplete: bool = False) -> Path:
    data_path = ROOT / "content/game.json"
    if not data_path.exists():
        raise SystemExit("Missing r6/content/game.json; earlier story data will not be substituted.")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    for key in ("title", "sources", "stages", "finalAnswer"):
        if key not in data:
            raise SystemExit(f"R6 content is missing {key}.")
    files = sorted((ROOT / "design").glob("*.md"))
    missing = [str(i).zfill(2) for i in range(1, 5)
               if not any(p.name.startswith(str(i).zfill(2)) for p in files)]
    if missing and not allow_incomplete:
        raise SystemExit("Designer source chapters not complete: " + ", ".join(missing))
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    title = data["title"]
    title_zh = title["zh"] if isinstance(title, dict) else str(title)
    title_en = title["en"] if isinstance(title, dict) else "The River Thief"
    cover = f"""<section class="chapter cover">
      <div><div class="chapter-label">R6 · DESIGNER REVIEW / 设计审阅</div>
      <h1>{e(title_zh)}</h1><p class="subtitle">{e(title_en)}</p>
      <p>五个真实地点 · 一场原创影戏 · 中英文完整原型</p></div>
      <div><div class="status"><b>交付性质：可运行、可打印、可供测试的原型</b>
      <p>本包呈现当前设计、史实边界、操作流程与实际测试记录。故事吸引力、游客情感反应、实地时长与商业运营仍须由相应测试确认。完成构建或代码检查不等于质量认可。</p></div>
      <p class="small">历史与开放信息检索基准：2026-10-20。人物、对抗和舞台演出为原创虚构。真实场馆没有被设定为合作方，工作人员不承担游戏角色。</p>
      <p class="small">来源：r6/design、r6/research、r6/qa 与 r6/content/game.json。生成器只排版本轮资料，不改写游戏数据。</p></div>
    </section>"""
    toc = ["<section class='chapter'><div class='chapter-label'>READING MAP / 阅读导航</div><h1>如何审阅这套产品</h1>"]
    toc.append("<p>先读事件与五站因果，再对照机制和纸件；用离线页或纸包完整体验一次，最后查看技术检查与尚未完成的游客验证。旧方案的否决记录保留在研究目录，避免把被淘汰剧情重新当作生产依据。</p>")
    toc.append("<ol class='toc'>")
    for p in files:
        first = next((line.lstrip("# ") for line in p.read_text(encoding="utf-8").splitlines() if line.startswith("# ")), p.stem)
        toc.append(f"<li>{e(first)} <span class='small'>（{e(p.name)}）</span></li>")
    toc.append("<li>史料目录与来源摘要</li><li>测试记录与实地验证方案</li></ol>")
    if missing:
        toc.append("<div class='status'>内部构建提示：设计章节尚缺 " + e(", ".join(missing)) + "。此文件不得当作完整指南交付。</div>")
    toc.append("<h2>配套文件</h2><p>玩家题包：R6_Player_Kit_ZH.pdf / R6_Player_Kit_EN.pdf。单文件离线试玩与源文件在同一 R6 交付目录中。玩家纸包包含全部提示、核对答案、分支说明与完整六格结尾，不依赖联网或手机解锁。</p></section>")
    chunks = [cover, "".join(toc)]
    for p in files:
        chunks.append(f"<section class='chapter'><div class='chapter-label'>DESIGN SOURCE · {e(p.name)}</div>{md.render(p.read_text(encoding='utf-8'))}</section>")
    research = ["<section class='chapter'><div class='chapter-label'>RESEARCH INDEX / 研究索引</div><h1>来源、候选与独立审查</h1><p>下表只索引完整研究文件。被否决方案和较早行动合同保留为过程证据，不是玩家正篇。</p><table><thead><tr><th>文件</th><th>用途与状态</th></tr></thead><tbody>"]
    for name, purpose in RESEARCH_INDEX:
        if (ROOT / "research" / name).exists():
            research.append(f"<tr><td>{e(name)}</td><td>{e(purpose)}</td></tr>")
    research.append("</tbody></table></section>")
    chunks.append("".join(research))
    sources = ["<section class='chapter'><div class='chapter-label'>FACTS & REFERENCES / 事实与来源</div><h1>玩家资料使用的来源</h1><p>以下为已选资料的摘要；原创游戏动作和人物台词不据此变为真实历史。没有来源网址的条目属于既有实拍研究记录，公开包不含私人原始照片。</p>"]
    for source in data["sources"]:
        fact = source.get("fact", {})
        zh = fact.get("zh", "") if isinstance(fact, dict) else fact
        en = fact.get("en", "") if isinstance(fact, dict) else ""
        stitle = source.get("title", "")
        if isinstance(stitle, dict):
            stitle = stitle.get("zh", "")
        url = source.get("url", "")
        sources.append(f"<div class='source-item'><b>{e(source.get('id',''))} · {e(stitle)}</b><p>{e(zh)}</p><p class='small'>{e(en)}</p>" + (f"<p class='small'><a href='{e(url)}'>{e(url)}</a></p>" if url else "<p class='small'>既有现场研究记录；未将私人照片公开到产品中。</p>") + "</div>")
    sources.append("</section>")
    chunks.append("".join(sources))
    qa_files = sorted((ROOT / "qa").glob("*.md"))
    for p in qa_files:
        chunks.append(f"<section class='chapter'><div class='chapter-label'>QA SOURCE · {e(p.name)}</div>{md.render(p.read_text(encoding='utf-8'))}</section>")
    # Stable small machine reports complement prose. Exclude PDF results because
    # embedding the current PDF's own page count would create a build cycle.
    report_names = ["baseline_recovery.json", "content_audit.json", "mechanics_results.json", "logic_results.json", "browser_results.json", "caper_results.json", "runtime_results.json"]
    reports = [(name, ROOT / "qa" / name) for name in report_names if (ROOT / "qa" / name).exists()]
    if reports:
        chunks.append("<section class='chapter'><div class='chapter-label'>MACHINE REPORTS / 机器检查</div><h1>可复核测试摘要</h1><p>这些检查验证指定功能和约束，不证明实地通行、纸件手感或故事受欢迎。完整记录保存在对应 JSON 文件中。</p>")
        for name, path in reports:
            raw = json.loads(path.read_text(encoding="utf-8"))
            checks = raw.get("checks", [])
            passed = sum(c.get("result") == "PASS" or c.get("passed") is True for c in checks)
            failed = len(checks) - passed
            chunks.append(f"<h2>{e(name)}</h2>")
            if name == "baseline_recovery.json":
                chunks.append("<p>原版恢复与既有行为基线，仅供比较；它不是 R6 最终内容验收，也不是新故事质量证明。</p>")
                summary = {k: raw[k] for k in ("status", "archive_verified", "archive_files", "manifest_matches", "field_tested", "commercial_ready") if k in raw}
                chunks.append("<pre>" + e(json.dumps(summary, ensure_ascii=False, indent=2)) + "</pre>")
            else:
                chunks.append(f"<p>逐项检查 {len(checks)} 项：通过 {passed} 项，未通过 {failed} 项。完整逐项记录见 r6/qa/{e(name)}。</p>")
                if raw.get("scope"):
                    chunks.append(f"<p class='small'>{e(raw['scope'])}</p>")
                if raw.get("enumeration"):
                    enums = raw["enumeration"]
                    chunks.append("<table><tr><th>解题空间</th><th>枚举组合</th><th>成立组合</th></tr>" + "".join(f"<tr><td>{e(x['stage'])}</td><td>{e(x['cases'])}</td><td>{e(x['solutions'])}</td></tr>" for x in enums) + "</table>")
                if "javascript_errors" in raw:
                    chunks.append(f"<p>JavaScript 错误：{len(raw['javascript_errors'])}；自动外部请求：{len(raw.get('automatic_network_requests', []))}。</p>")
                if name == "content_audit.json":
                    chunks.append(f"<p>真人盲测：{e(raw.get('human_blind_test', 'NOT_RUN'))}；实地测试：{e(raw.get('field_test', 'NOT_RUN'))}。静态完整性检查不得作为故事质量通过的理由。</p>")
        chunks.append("</section>")
    doc = "<!doctype html><html lang='zh'><head><meta charset='utf-8'><title>R6 Designer Guide</title><style>" + CSS + "</style></head><body><div class='no-print'><button onclick='window.print()'>打印指南 / Print guide</button> A4 · 100%</div>" + "".join(chunks) + "</body></html>"
    output = ROOT / "play/guide.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(doc, encoding="utf-8")
    print(json.dumps({"output": str(output), "design_chapters": len(files), "qa_chapters": len(qa_files), "sources": len(data["sources"]), "incomplete": missing}, ensure_ascii=False))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-incomplete", action="store_true", help="Internal layout preview only; mark missing design chapters.")
    args = parser.parse_args()
    build(args.allow_incomplete)

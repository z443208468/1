#!/usr/bin/env python3
"""Render all three R6 PDFs, check page layout, and create full-page proof images.

Usage (after installing the documented local Playwright/fonts dependencies):
  PYTHONPATH=/path/to/runtime-python CHROMIUM_PATH=/path/to/chromium \
    FONTCONFIG_FILE=/path/to/fonts.conf python r6/tools/render_pdfs.py

Python dependencies: playwright, PyMuPDF (imported as fitz), Pillow, and
markdown-it-py for the guide builder. Install Chromium with Playwright in advance
or supply CHROMIUM_PATH. When no explicit/local/system browser is found,
Playwright uses its normally installed browser cache. No software is downloaded
by this renderer.

No network is needed. This script must not be confused with a human physical or
field playtest. It reports only the checks actually performed below.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT.parents[1]
if (SCRATCH / "runtime-python").is_dir():
    sys.path.insert(0, str(SCRATCH / "runtime-python"))
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import fitz

DEFAULT_CHROMIUM = SCRATCH / "runtime-browsers/chromium_headless_shell-1161/chrome-linux/headless_shell"
DEFAULT_FONTS = SCRATCH / "runtime-fonts/fonts.conf"

OVERFLOW_JS = r"""() => {
  const pages=[...document.querySelectorAll('.page')];
  return pages.map((p,i)=>{
    const b=p.getBoundingClientRect();
    const c=p.querySelector('.page-content');
    const f=p.querySelector('.page-foot');
    const cb=c.getBoundingClientRect(), fb=f.getBoundingClientRect();
    const wide=[...c.querySelectorAll('*')].filter(n=>!n.closest('svg')).map(n=>({
      tag:n.tagName, cls:n.className, text:(n.innerText||'').slice(0,70), r:n.getBoundingClientRect()
    })).filter(n=>n.r.width && (n.r.left < b.left-1 || n.r.right > b.right+1));
    return {page:i+1, title:p.querySelector('h1')?.innerText,
      height_px:Math.round(b.height*100)/100,
      content_bottom_px:Math.round((cb.bottom-b.top)*100)/100,
      footer_top_px:Math.round((fb.top-b.top)*100)/100,
      overflow_y_px:Math.max(0,Math.round((cb.bottom-fb.top+5)*100)/100),
      overflow_x:wide.map(n=>({tag:n.tag,cls:n.cls,text:n.text}))};
  });
}"""

MATERIAL_JS = r"""() => {
  const mm=n=>Math.round(n*25.4/96*100)/100;
  const sizes=sel=>[...document.querySelectorAll(sel)].map(e=>{
    const r=e.getBoundingClientRect();return {width_mm:mm(r.width),height_mm:mm(r.height)};
  });
  const strips=sizes('.scene-piece'), frame=sizes('.assembly-area')[0];
  return {scene_strips:strips,frame_assembly_area:frame,
    souvenir_faces:sizes('.souvenir-face'),
    three_strips_fit_frame:Math.abs(strips.reduce((a,b)=>a+b.width_mm,0)-frame.width_mm)<0.15
      && strips.every(s=>s.height_mm<=frame.height_mm+0.15),
    scale:'CSS physical dimensions at 100%; no physical printer tolerance or cut test performed'};
}"""


def proof_images(pdf: Path, directory: Path, dpi: int) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    # Delete only screenshots owned by this named PDF, never unrelated files.
    for old in directory.glob("page-*.png"):
        old.unlink()
    for old in directory.parent.glob(f"{pdf.stem}_contact_*.png"):
        old.unlink()
    document = fitz.open(pdf)
    records = []
    for i, page in enumerate(document):
        out = directory / f"page-{i+1:03d}.png"
        page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False).save(out)
        words = page.get_text("words")
        outside = [w[4] for w in words if w[0] < -0.5 or w[1] < -0.5 or w[2] > page.rect.width+0.5 or w[3] > page.rect.height+0.5]
        records.append({"page": i+1, "size_pt": [round(page.rect.width,2),round(page.rect.height,2)],
                        "text_characters": len(page.get_text().strip()), "outside_media_box": outside,
                        "image": str(out.relative_to(ROOT)) if out.is_relative_to(ROOT) else str(out)})
    # Separate contact sheets avoid shrinking a long guide into one unreadable image.
    contacts = []
    tile_w, tile_h = 255, 381
    cols, rows = 3, 4
    for start in range(0, len(records), cols*rows):
        group = records[start:start+cols*rows]
        used_rows = (len(group)+cols-1)//cols
        sheet = Image.new("RGB", (cols*tile_w, used_rows*tile_h+38), "#dfe6e8")
        draw = ImageDraw.Draw(sheet)
        draw.text((12, 12), f"{pdf.stem} | pages {start+1}-{start+len(group)}", fill="#173445")
        for j, rec in enumerate(group):
            p = directory / f"page-{rec['page']:03d}.png"
            im = Image.open(p).convert("RGB")
            im.thumbnail((tile_w-18, tile_h-36))
            x = (j%cols)*tile_w+(tile_w-im.width)//2
            y = (j//cols)*tile_h+40
            sheet.paste(im, (x,y))
            draw.text(((j%cols)*tile_w+12, y+im.height+5), f"p. {rec['page']}", fill="#173445")
        contact = directory.parent / f"{pdf.stem}_contact_{start//(cols*rows)+1:02d}.png"
        sheet.save(contact)
        contacts.append(str(contact.relative_to(ROOT)) if contact.is_relative_to(ROOT) else str(contact))
    return {"pages": records, "contacts": contacts, "dpi": dpi}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--layout-only", action="store_true", help="Check current player-page geometry without replacing the PDF report or images.")
    parser.add_argument("--allow-incomplete-guide", action="store_true")
    parser.add_argument("--dpi", type=int, default=110)
    parser.add_argument("--review-dir", type=Path, default=ROOT/"output/qa/pdf_pages")
    args=parser.parse_args()
    if not args.skip_build:
        subprocess.run([sys.executable, str(ROOT/"tools/build_print.py")], check=True)
        guide_args=[sys.executable, str(ROOT/"tools/build_guide.py")]
        if args.allow_incomplete_guide:
            guide_args.append("--allow-incomplete")
        subprocess.run(guide_args, check=True)
    if "FONTCONFIG_FILE" not in os.environ and DEFAULT_FONTS.exists():
        os.environ["FONTCONFIG_FILE"] = str(DEFAULT_FONTS)
    chromium=os.environ.get("CHROMIUM_PATH") or (str(DEFAULT_CHROMIUM) if DEFAULT_CHROMIUM.exists() else shutil.which("chromium"))
    out=ROOT/"output/pdf"
    out.mkdir(parents=True,exist_ok=True)
    jobs=[("ZH", ROOT/"play/print_zh.html", out/"R6_Player_Kit_ZH.pdf"),
          ("EN", ROOT/"play/print_en.html", out/"R6_Player_Kit_EN.pdf"),
          ("Guide", ROOT/"play/guide.html", out/"R6_Designer_Guide.pdf")]
    if args.layout_only:
        jobs=jobs[:2]
    report={"generated_at_utc":datetime.now(timezone.utc).isoformat(),
            "content_sha256":hashlib.sha256((ROOT/"content/game.json").read_bytes()).hexdigest(),
            "figures_sha256":hashlib.sha256((ROOT/"play/figures.js").read_bytes()).hexdigest(),
            "caper_sha256":hashlib.sha256((ROOT/"play/caper.js").read_bytes()).hexdigest(),
            "scope":"Automated local HTML/PDF rendering and geometry; not physical, blind-user, or field validation.",
            "physical_print_test":False,"tourist_blind_test":False,"field_test":False,
            "documents":[],"errors":[]}
    with sync_playwright() as playwright:
        launch_options={"headless":True,"args":["--no-sandbox"]}
        if chromium:
            launch_options["executable_path"]=chromium
        browser=playwright.chromium.launch(**launch_options)
        for name, source, pdf in jobs:
            if not source.exists():
                raise SystemExit(f"Missing current source: {source}")
            page=browser.new_page(viewport={"width":1000,"height":1300}, device_scale_factor=1)
            external=[]
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(("file:","data:","about:")) else (external.append(route.request.url),route.abort()))
            page.goto(source.as_uri(), wait_until="load")
            page.emulate_media(media="print")
            page.evaluate("document.fonts.ready")
            layout=page.evaluate(OVERFLOW_JS) if name != "Guide" else []
            geometry=page.evaluate(MATERIAL_JS) if name != "Guide" else None
            font_status=page.evaluate("({cjk:document.fonts.check('12px \"Noto Sans CJK SC\"'), sans:document.fonts.check('12px \"Noto Sans\"')})")
            # Check the actual platform font selected for visible text; checking
            # only the CSS family declaration can hide an unintended CJK fallback.
            probe_selector="#h4 .small" if name!="Guide" else "[data-font-probe]"
            if name=="Guide":
                page.evaluate("""() => {
                    const p=[...document.querySelectorAll('p')].find(p=>p.textContent.includes('Utsuro'))
                        || document.querySelector('p');
                    p.setAttribute('data-font-probe','');
                }""")
            client=page.context.new_cdp_session(page)
            client.send("DOM.enable"); client.send("CSS.enable")
            root_node=client.send("DOM.getDocument")["root"]["nodeId"]
            node=client.send("DOM.querySelector",{"nodeId":root_node,"selector":probe_selector})["nodeId"]
            font_status["actual_platform_fonts"]=client.send("CSS.getPlatformFontsForNode",{"nodeId":node})["fonts"]
            client.detach()
            bad=[p for p in layout if p["overflow_y_px"]>0 or p["overflow_x"]]
            if bad:
                report["errors"].append({"document":name,"type":"html_page_overflow","pages":bad})
            if external:
                report["errors"].append({"document":name,"type":"external_requests","urls":external})
            if geometry and not geometry["three_strips_fit_frame"]:
                report["errors"].append({"document":name,"type":"scene_strips_do_not_fit_frame","geometry":geometry})
            if args.layout_only:
                report["documents"].append({"name":name,"html_layout":layout,"material_geometry":geometry})
                page.close()
                continue
            options={"path":str(pdf),"print_background":True,"prefer_css_page_size":True,
                     "display_header_footer":name=="Guide"}
            if name=="Guide":
                options["header_template"]="<span></span>"
                options["footer_template"]="<div style='width:100%;padding:0 16mm;font-size:8px;color:#516773;display:flex;justify-content:space-between'><span>THE RIVER THIEF · R6 · DESIGNER REVIEW</span><span><span class='pageNumber'></span> / <span class='totalPages'></span></span></div>"
            page.pdf(**options)
            page.close()
            proofs=proof_images(pdf, args.review_dir/pdf.stem, args.dpi)
            if layout and len(layout)!=len(proofs["pages"]):
                report["errors"].append({"document":name,"type":"unexpected_pdf_page_count","html_pages":len(layout),"pdf_pages":len(proofs["pages"])})
            blank=[p["page"] for p in proofs["pages"] if p["text_characters"]<20]
            outside=[p for p in proofs["pages"] if p["outside_media_box"]]
            if blank:
                report["errors"].append({"document":name,"type":"near_blank_pdf_pages","pages":blank})
            if outside:
                report["errors"].append({"document":name,"type":"text_outside_media_box","pages":outside})
            report["documents"].append({"name":name,"html":str(source.relative_to(ROOT)),"pdf":str(pdf.relative_to(ROOT)),
                "page_count":len(proofs["pages"]),"file_bytes":pdf.stat().st_size,"font_check":font_status,
                "html_layout":layout,"material_geometry":geometry,"proofs":proofs,"external_requests":external})
            print(f"{name}: {len(proofs['pages'])} pages → {pdf}")
        browser.close()
    report["automated_layout_pass"] = not report["errors"]
    report["visual_review"]="Full-page PNGs and contact sheets generated; human visual review must be recorded separately."
    report_path=ROOT/"qa"/("print_layout_preview.json" if args.layout_only else "pdf_results.json")
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"report":str(report_path),"automated_layout_pass":report["automated_layout_pass"],"error_count":len(report["errors"])},ensure_ascii=False))
    if report["errors"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()

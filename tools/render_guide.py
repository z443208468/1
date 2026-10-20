from pathlib import Path
import os
from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
paths=['design/01_R3_STORY.md','design/02_R3_MECHANICS.md','commercial/01_PRODUCT_AND_COSTS.md','qa/02_R3_BENCHMARK_AND_LIMITS.md','research/05_R3_SOURCE_LINKS.md']
md=MarkdownIt('commonmark').enable('table')
body=''.join('<section class="chapter">'+md.render((R/p).read_text().replace('\\n','\n'))+'</section>' for p in paths)
css='''@page{size:A4;margin:18mm 17mm 20mm}body{font:10.5pt/1.7 "Noto Sans CJK SC",sans-serif;color:#203441}h1{font-size:24pt;line-height:1.3;border-bottom:2px solid #203441;padding-bottom:6mm}h2{font-size:16pt;line-height:1.4;margin-top:7mm;break-after:avoid}h3{font-size:12pt;break-after:avoid}p{margin:3mm 0}table{border-collapse:collapse;width:100%;font-size:8.5pt;line-height:1.5;margin:4mm 0}th,td{border:1px solid #b9c7cc;padding:2.5mm;text-align:left;vertical-align:top}th{background:#edf1ed}tr{break-inside:avoid}blockquote{border-left:3px solid #20736b;padding-left:5mm;color:#334e58}a{overflow-wrap:anywhere;color:#20655e}.chapter{break-before:page}.chapter:first-child{break-before:auto}pre,code{font:9pt monospace;white-space:pre-wrap;overflow-wrap:anywhere}ul,ol{padding-left:7mm}li{margin:1.5mm 0}'''
doc='<html><meta charset="utf-8"><style>'+css+'</style><body>'+body+'</body></html>'
(R/'R3_Designer_Guide.html').write_text(doc)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox']);pg=b.new_page();pg.set_content(doc,wait_until='load');pg.pdf(path=str(R/'R3_Designer_Guide.pdf'),format='A4',print_background=True,display_header_footer=True,header_template='<div></div>',footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#566875">SCENE EXPRESS / R3.1 — <span class="pageNumber"></span> / <span class="totalPages"></span></div>',prefer_css_page_size=True);b.close()

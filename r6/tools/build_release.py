"""Rebuild the R6 review product from its editable content and source.

No R2-R5 story generator is run. `content/game.json` is the authoring source.
"""
from pathlib import Path
import argparse
import subprocess
import sys

R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--pdf',action='store_true',help='Render the two player PDFs and designer guide; requires Playwright/Chromium and CJK fonts')
p.add_argument('--browser-test',action='store_true',help='Run real file:// browser tests; requires the same browser dependencies')
a=p.parse_args()
def run(*args):subprocess.run(args,cwd=R,check=True)
run('node',str(R/'tools/build_runtime.mjs'))
run(sys.executable,str(R/'tools/build_print.py'))
run(sys.executable,str(R/'qa/audit_content.py'))
run('node',str(R/'qa/test_logic.mjs'))
if a.browser_test:run(sys.executable,str(R/'qa/test_runtime.py'))
run(sys.executable,str(R/'tools/build_guide.py'))
if a.pdf:run(sys.executable,str(R/'tools/render_pdfs.py'))
print('R6 files rebuilt. Software success does not establish audience, field or commercial acceptance.')

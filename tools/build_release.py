"""Build the offline/print release; --pdf also renders and browser-tests it."""
from pathlib import Path
import argparse,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--pdf',action='store_true');args=a.parse_args()
if not shutil.which('node'):raise SystemExit('Node.js is required for diagram generation and logic checks.')
for script in ['apply_release_refinements.py','build_data.py','build_print.py']:
 subprocess.run([sys.executable,str(R/'tools'/script)],cwd=R,check=True)
subprocess.run(['node',str(R/'qa/test_logic.js')],cwd=R,check=True)
if args.pdf:
 subprocess.run([sys.executable,str(R/'qa/test_browser.py')],cwd=R,check=True)
 subprocess.run([sys.executable,str(R/'tools/render_guide.py')],cwd=R,check=True)
print('Ready: R3_Offline.html and play/print.html. Generated files are local build outputs.')

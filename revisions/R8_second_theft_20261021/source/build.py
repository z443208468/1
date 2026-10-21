"""Build the self-contained R8 game. Python 3 standard library only.

Run from any directory: python source/build.py
No network requests, fonts or original field photographs are bundled.
"""
from pathlib import Path
import hashlib
import json

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parent


def build():
    content = json.loads((SOURCE / "content.json").read_text(encoding="utf-8"))
    required = ["title", "opening", "stages", "characters", "endings", "fullTruth"]
    missing = [key for key in required if key not in content]
    if missing:
        raise ValueError(f"Missing content fields: {missing}")
    if [stage["id"] for stage in content["stages"]] != [f"S0{i}" for i in range(1, 6)]:
        raise ValueError("Expected five ordered stages S01 to S05")
    if {c["id"] for c in content["characters"]} != {"maker", "broker", "handler"}:
        raise ValueError("Expected independent maker, broker and handler characters")
    for stage in content["stages"]:
        if len(stage.get("hints", [])) != 3:
            raise ValueError(f"Three hints required for {stage['id']}")
    css = (SOURCE / "style.css").read_text(encoding="utf-8")
    scripts = [(SOURCE / name).read_text(encoding="utf-8") for name in ["engine.js", "figures.js", "app.js"]]
    encoded = json.dumps(content, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    title = content["title"].get("zh", "第二次失窃") if isinstance(content["title"], dict) else content["title"]
    from html import escape
    doc = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{escape(title)} · R8</title><style>{css}</style></head>
<body><div id="storage-warning" class="notice" role="status" hidden></div><header class="top"><div><div class="brand">TOKYO · CNW · R8</div><div id="game-title" class="title-small">{escape(title)}</div></div><button id="language" aria-label="切换语言 / Change language">EN / English</button></header>
<div class="layout"><aside class="sidebar" id="sidebar"></aside><div><div id="import-note" class="notice" role="status" hidden></div><div id="feedback" class="" role="status" aria-live="polite" style="white-space:pre-line"></div><main id="main"></main></div></div>
<input id="import-file" type="file" accept="application/json,.json" hidden>
<script>{scripts[0]}</script><script>{scripts[1]}</script><script>window.R8Content={encoded};</script><script>{scripts[2]}</script>
</body></html>'''
    (ROOT / "play").mkdir(exist_ok=True)
    for path in [ROOT / "R8_Offline.html", ROOT / "play/index.html"]:
        path.write_text(doc, encoding="utf-8")
    (ROOT / "play/content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "qa").mkdir(exist_ok=True)
    build_info = {
        "version": "R8.1",
        "artifact": "R8_Offline.html",
        "sha256": hashlib.sha256(doc.encode()).hexdigest(),
        "bytes": len(doc.encode()),
        "offline_self_contained": True,
        "network_requests_required": False,
        "source_files": ["content.json", "engine.js", "figures.js", "app.js", "style.css", "build.py"],
        "build_status": "BUILT_NOT_A_FIELD_OR_HUMAN_TEST",
    }
    (ROOT / "qa/software_build.json").write_text(json.dumps(build_info, indent=2), encoding="utf-8")
    print(json.dumps(build_info))


if __name__ == "__main__":
    build()

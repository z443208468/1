"""Overlay each registered semantic pass on a candidate or compare states of the same camera."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_pair(run_dir, picture):
    run, picture = Path(run_dir), Path(picture)
    report = json.loads((run / 'visibility.json').read_text(encoding='utf-8-sig'))
    if sha(run / 'scene-snapshot.json') != report['scene_sha256']:
        raise ValueError('scene-snapshot.json differs from the recorded render')
    semantic_hash = sha(run / 'semantic.png')
    if report.get('pass_sha256', {}).get('semantic') != semantic_hash:
        raise ValueError('semantic.png differs from its render receipt; regenerate the reference pass')
    with Image.open(run / 'semantic.png') as file:
        semantic = file.convert('RGB')
    with Image.open(picture) as file:
        final = file.convert('RGB')
    w, h = semantic.size
    fw, fh = final.size
    if [w,h] != report['camera']['resolution'] or fw*h != fh*w:
        raise ValueError(f'{picture}: camera and image aspect ratios differ. Use a reviewed same-framing export; no implicit crop.')
    rgb = np.asarray(semantic.resize(final.size, Image.Resampling.NEAREST))
    edge = np.zeros(rgb.shape[:2], dtype=bool)
    edge[1:] |= np.any(rgb[1:] != rgb[:-1], axis=2)
    edge[:,1:] |= np.any(rgb[:,1:] != rgb[:,:-1], axis=2)
    overlay = final.copy()
    overlay.paste((255,32,126),(0,0,fw,fh),Image.fromarray(edge))
    record = dict(state_id=report['state_id'], input=str(picture), input_sha256=sha(picture),
                  semantic_sha256=semantic_hash, visibility_sha256=sha(run/'visibility.json'),
                  scene_sha256=report['scene_sha256'], place_entity_id=report['place_entity_id'],
                  blockout_version=report['blockout_version'], camera=report['camera'])
    return record, final, overlay

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pair',nargs=2,action='append',required=True,metavar=('RENDER_DIR','IMAGE'))
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.out.exists():
        ap.error('use a new output directory')
    records=[]
    sheet=Image.new('RGB',(960,300*len(args.pair)),(28,28,28))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(dir=args.out.parent))
    try:
        for i,pair in enumerate(args.pair):
            record,final,overlay=read_pair(*pair)
            for key in ('place_entity_id','blockout_version','scene_sha256','camera'):
                if records and record[key]!=records[0][key]:
                    raise ValueError('Different place, blockout version, source hash or camera; re-render with one version.')
            records.append(record)
            filename = f'overlay-{i+1:02}.png'
            overlay.save(temp / filename)
            record['overlay_file'] = filename
            record['overlay_sha256'] = sha(temp / filename)
            for x,img in ((0,final),(480,overlay)):
                img.thumbnail((478,270),Image.Resampling.LANCZOS)
                sheet.paste(img,(x,300*i+25))
            ImageDraw.Draw(sheet).text((8,300*i+5),f'{i+1:02}  original / projected contours',fill='white')
        sheet.save(temp/'comparison.png')
        comparison_hash = sha(temp/'comparison.png')
        for record in records:
            record['comparison_file'] = 'comparison.png'
            record['comparison_sha256'] = comparison_hash
        (temp/'inputs.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
        temp.rename(args.out)
    finally:
        if temp.exists():
            shutil.rmtree(temp)

if __name__=='__main__':
    main()

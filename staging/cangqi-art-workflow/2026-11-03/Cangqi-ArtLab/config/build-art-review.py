#!/usr/bin/env python3
"""Build an offline review of one scene or character checkpoint from production readbacks."""
import argparse
from collections import defaultdict
import hashlib
from html import escape
import json
from pathlib import Path
import shutil
import tempfile

from PIL import Image, ImageDraw

PORTRAITS = {"base", "expression", "gaze"}
KINDS = PORTRAITS | {"identity", "costume", "design", "background", "cg", "prop"}
SPACE_FILES = {"plan":"登记平面图", "top":"白模俯视图", "frustum":"机位视锥",
               "legend":"实体／版本图例", "camera_history":"同机位全部状态的查询记录", "clay":"灰模", "stage1":"本地结构图",
               "camera_comparison":"同机位已有状态对照", "overhead_comparison":"平面与俯视对照",
               "structure_comparison":"灰模与结构图对照"}
PHASES = {"checkpoint": "角色早期定版", "scene": "整场审核"}
DECISIONS = {"通过", "退回", "接受较轻版"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def h(value):
    return escape(str(value), quote=True)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def version_id(value):
    if type(value) is int:
        return str(value) if value>0 else ""
    return value.strip() if isinstance(value, str) else ""


def receipt_history(data, directory):
    """Only exact version receipts tied to retrievable, literal user replies count."""
    result, seen, problems = [], set(), []
    entries = data.get("receipts", [])
    if isinstance(entries, str):
        entries = read_json(directory / entries)
    for r in entries:
        if r["project"] != data["project"]:
            continue
        if r["id"] in seen:
            raise ValueError(f"重复回执 ID {r['id']}，请按实际时间去重排序")
        seen.add(r["id"])
        if r["decision"] not in DECISIONS or r.get("actor") != "user" or r.get("phase") not in PHASES:
            raise ValueError(f"回执 {r['id']} 缺少用户决定或阶段")
        evidence = directory / r["evidence"]
        if not evidence.is_file() or not r.get("quote") or r["quote"] not in evidence.read_text(encoding="utf-8-sig"):
            problems.append(f"回执 {r['id']} 缺原始用户回复或找不到原话，未计入决定")
            continue
        if not version_id(r.get("version")) or not all(r.get(k) for k in ("key", "scene", "clause")) or len(r["sha256"]) != 64:
            raise ValueError(f"回执 {r['id']} 缺少版本、场次、条款或指纹")
        result.append(r)
    return result, problems


class Bundle:
    def __init__(self, directory, target):
        self.directory = directory
        self.target = target
        self.assets = target / "files"
        self.assets.mkdir()
        self.copied = {}

    def copy(self, value):
        if not value:
            return ""
        path = (self.directory / value).resolve()
        if not path.is_file():
            return ""
        if path not in self.copied:
            name = f"{len(self.copied)+1:04d}{path.suffix.lower()}"
            shutil.copyfile(path, self.assets / name)
            self.copied[path] = "files/" + name
        return self.copied[path]

    def contact(self, name, entries):
        if not entries:
            return ""
        width, height = 168, 158
        columns = min(len(entries), 6)
        sheet = Image.new("RGB", (width*columns, height*((len(entries)+columns-1)//columns)), "#e4e4e4")
        draw = ImageDraw.Draw(sheet)
        for n, row in enumerate(entries):
            x, y = width*(n % columns), height*(n//columns)
            with Image.open(self.target / row["files"]["image"]) as img:
                tile = img.convert("RGBA")
                tile.thumbnail((width-8, height-22))
                sheet.paste(tile, (x+(width-tile.width)//2, y+3), tile)
            draw.text((x+5, y+height-16), row["ref"], fill="black")
        name += ".jpg"
        sheet.save(self.target/name, quality=88)
        return name


def space_record(item, files, pack, sha, issues):
    """Bind S7 products to the actual registered frame and camera, including archived states."""
    needed=("compare_inputs","visibility","overlay","camera_comparison","top","clay")
    if any(not files.get(f) for f in needed):
        issues.append("缺 S7 inputs.json、visibility.json、叠图、同机位对照或原生白模通道")
        return []
    try:
        records=read_json(pack.target/files["compare_inputs"])
        visibility=read_json(pack.target/files["visibility"])
        def camera_matches(r):
            return (r["place_entity_id"],r["blockout_version"],r["camera"]["id"])==(item["place"],item["blockout"],item["camera"])
        choices=[r for r in records if camera_matches(r) and r["state_id"]==item["state_id"] and r["input_sha256"]==sha]
        if len(choices)!=1:
            raise ValueError("成品指纹／场所／机位／白模版本／状态没有唯一匹配")
        selected=choices[0]
        for key,original,field in (("overlay",item["overlay"],"overlay"),("comparison",item["evidence_files"]["camera_comparison"],"camera_comparison")):
            name=selected[key+"_file"]
            if any(c in name for c in "/\\:") or name!=Path(original).name or selected[key+"_sha256"]!=digest(pack.target/files[field]):
                raise ValueError(key+" 文件名或指纹与 inputs.json 不符")
        if not camera_matches(visibility) or visibility["state_id"]!=item["state_id"] or visibility["scene_sha256"]!=selected["scene_sha256"] or selected["visibility_sha256"]!=digest(pack.target/files["visibility"]):
            raise ValueError("visibility 回读与该行不符")
        for field in ("top","clay"):
            if digest(pack.target/files[field])!=visibility["pass_sha256"][field]:
                raise ValueError(field+" 指纹与实际渲染不符")
        if any(not camera_matches(r) or r["comparison_sha256"]!=selected["comparison_sha256"] for r in records):
            raise ValueError("同机位对照混入不同机位或不同对照图")
        return records
    except (OSError, ValueError, TypeError, KeyError) as error:
        issues.append("S7 证据未对应本图："+str(error))
        return []


def process(item, number, pack, history, phase, scene):
    key, kind = item["key"], item["kind"]
    if not key or kind not in KINDS or item["status"] not in {"ready", "failed", "waiting"}:
        raise ValueError(f"无效工单类型、对象或生产状态，行 {number}")
    issues = []
    files = {}
    for field in ("image", "evidence", "brief", "face", "eyes", "locality", "stitch", "overlay", "scale", "source_image"):
        if item.get(field):
            files[field] = pack.copy(item[field])
            if not files[field]:
                issues.append(f"找不到 {field}：{item[field]}")
    for field, value in item.get("evidence_files", {}).items():
        files[field] = pack.copy(value)
        if not files[field]:
            issues.append(f"找不到证据 {field}：{value}")
    ready = item["status"] == "ready"
    sha, size = "", []
    if files.get("image"):
        image = pack.target / files["image"]
        try:
            with Image.open(image) as actual:
                actual.load()
                size = list(actual.size)
                if actual.format != "PNG":
                    issues.append("成品非 PNG")
            sha = digest(image)
        except OSError:
            issues.append("成品不可打开")
            files["image"] = ""
    version = version_id(item.get("version"))
    canonical = version
    if item.get("source_version") or item.get("source") == "同图复用":
        source = files.get("source_image")
        if not sha or not source or digest(pack.target / source) != sha or not version_id(item.get("source_version")):
            issues.append("同图来源版本或文件指纹未核实")
        else:
            canonical = version_id(item["source_version"])
    if not files.get("evidence"):
        issues.append("缺本项实际生产或回读记录")
    if ready:
        if not sha or sha != str(item.get("sha256", "")).lower() or not version:
            issues.append("缺采纳／设计版本或登记指纹与实图不符")
        if size != item.get("size") or item.get("technical") != "pass" or item.get("glance") != "pass":
            issues.append("实际尺寸与规格不合或技术检查／一瞥未过")
        if not files.get("brief") and not item.get("checklist"):
            issues.append("缺本单正文或可见要求清单")
    for field in ("draws", "failures"):
        if type(item.get(field)) is not int or item[field] < 0:
            issues.append(f"缺有效计数 {field}")
    warnings = list(item.get("warnings", []))
    if ready and kind in {"expression", "gaze"} and item.get("source") != "同图复用":
        for field in ("face", "eyes", "stitch", "locality"):
            if not files.get(field):
                issues.append(f"缺差分证据 {field}")
    if files.get("stitch") and read_json(pack.target / files["stitch"]).get("status") != "pass":
        issues.append("stitch-check 未通过")
    if files.get("locality"):
        qa = read_json(pack.target / files["locality"])
        def statuses(value):
            if isinstance(value, dict):
                if "status" in value:
                    yield value["status"]
                for sub in value.values():
                    yield from statuses(sub)
            elif isinstance(value, list):
                for sub in value:
                    yield from statuses(sub)
        levels = set(statuses(qa))
        if "fail" in levels:
            issues.append("locality-qa 有失败项")
        warnings.extend(str(w) for w in qa.get("warnings", []))
        warnings.extend(sorted(levels & {"warn", "needs-visual-review"}))
    if ready and not item.get("source"):
        issues.append("缺生产来源")
    if ready and kind=="cg" and type(item.get("spatial")) is not bool:
        issues.append("CG 未注明是否依赖固定场所")
    owner=item.get("first_scene") or scene
    common=item.get("unreferenced_common") is True
    if common:
        owner=item.get("production_scene")
        if not owner or not files.get("common_evidence"):
            issues.append("常见心境缺首次制作场或4c／5f证据")
    owners={owner} if owner else set()
    if item.get("review_scene"):
        if files.get("review_scope_evidence"):
            owners.add(item["review_scene"])
        elif item["review_scene"]!=owner:
            issues.append("跨场纠错缺本版审核归属依据")
    if ready and kind in PORTRAITS:
        if not common and not item.get("first_scene"):
            issues.append("缺首次引用场")
        if not item.get("group") or not item.get("character") or len(item.get("anchor", [])) != 2:
            issues.append("缺人物兼容组、角色或同画布锚点")
    spatial=item.get("camera") or item.get("spatial") or kind=="background" and item.get("spatial") is not False
    if ready and spatial:
        if not item.get("camera") or not item.get("blockout") or not files.get("overlay"):
            issues.append("缺机位、白模版本或本图轮廓叠图")
        for field in ("plan","top","frustum","legend","clay","stage1","camera_history"):
            if not files.get(field):
                issues.append("缺空间证据："+SPACE_FILES[field])
        if not item.get("place") or not isinstance(item.get("camera_peers"), list):
            issues.append("缺场所实体或已有同机位状态清单（无其他状态时显式填空数组）")
    comparisons=space_record(item,files,pack,sha,issues) if ready and spatial else []
    peer_views=[]
    for peer in item.get("camera_peers",[]):
        if not all(peer.get(k) for k in ("key","state_id","scene","version","place","blockout","camera","sha256")) or any(peer[k]!=item.get(k) for k in ("place","blockout","camera")):
            issues.append("同机位对照的场所、白模、机位或状态版本未核实")
            continue
        if not any(row["state_id"]==peer["state_id"] and row["input_sha256"]==peer["sha256"] for row in comparisons):
            issues.append(f"同机位对照 inputs.json 缺实际状态行：{peer['key']}")
        picture=pack.copy(peer.get("image"))
        if picture and digest(pack.target/picture)==peer.get("sha256"):
            try:
                with Image.open(pack.target/picture) as other:
                    other.verify()
                peer_views.append(dict(peer,bundled=picture))
            except OSError:
                issues.append(f"同机位历史状态图片不可读：{peer['key']}")
        elif not files.get("camera_comparison"):
            issues.append(f"缺同机位历史状态的实图或已生成的对照：{peer['key']}")
        else:
            peer_views.append(dict(peer,bundled=""))
    def eligible(r):
        if r["phase"]=="checkpoint":
            return (kind in {"identity","costume","base"} and r.get("kind")==kind and r.get("character") and
                    r["character"]==item.get("character") and (kind!="base" or phase=="checkpoint" or item.get("checkpoint_base") is True))
        if r["scene"] not in owners:
            return False
        if phase == "checkpoint" and r["decision"] != "退回":
            return (r.get("confirms_checkpoint") is True and r.get("kind") == kind
                    and r.get("character") == item.get("character") and bool(r.get("character")))
        return True
    decisions = [r for r in history if r["key"] == key and eligible(r)]
    exact = [r for r in decisions if version_id(r["version"]) == canonical and r["sha256"].lower() == sha]
    receipt = exact[-1] if exact else None
    if receipt:
        files["receipt"] = pack.copy(receipt["evidence"])
    state = {"failed":"技术失败", "waiting":"待前置", "ready":"待用户审"}[item["status"]]
    if ready and issues:
        state = "材料待补"
    elif ready and receipt:
        state = "用户退回" if receipt["decision"] == "退回" else "用户已审"
    if state == "待用户审" and phase == "scene" and kind in PORTRAITS and scene not in owners:
        state = "待归属场用户审"
    return dict(item, ref=f"R{number:03d}", files=files, peer_views=peer_views, canonical=canonical, actual_sha=sha,
                actual_size=size, review=state, issues=issues, warnings=list(dict.fromkeys(warnings)),
                returns=sum(r["decision"] == "退回" for r in decisions), receipt=receipt)


def link(path, label):
    return f'<a href="{h(path)}">{h(label)}</a>' if path else ""


def build(data, manifest_dir, target, rules):
    phase, scene = data["phase"], data["scene"]
    if phase not in PHASES or not scene or not data["project"] or not isinstance(data.get("items"),list):
        raise ValueError("需要项目、单场、审核阶段和实际清单")
    pack = Bundle(manifest_dir, target)
    history, receipt_problems = receipt_history(data, manifest_dir)
    items = [read_json(manifest_dir/x) if isinstance(x, str) else x for x in data["items"]]
    if phase == "checkpoint" and any(x["kind"] not in {"identity","costume","base"} for x in items):
        raise ValueError("定版包只收身份、衣装及首张样板")
    checkpoint=data.get("checkpoint", {})
    checkpoint_proof=pack.copy(checkpoint.get("evidence"))
    checkpoint_character=checkpoint.get("character")
    if phase=="checkpoint" and any(x.get("character")!=checkpoint_character or not checkpoint_character for x in items):
        raise ValueError("一个早期定版包只收一个实际角色，请指明 checkpoint.character 并按角色拆包")
    required={"identity","costume"} if checkpoint.get("cg_only") is True and checkpoint_proof else {"identity","costume","base"}
    rows = [process(x, n, pack, history, phase, scene) for n, x in enumerate(items, 1)]
    groups, cameras = defaultdict(list), defaultdict(list)
    for r in rows:
        if r["kind"] in PORTRAITS and r.get("group"):
            groups[(r.get("character", ""), r["group"])].append(r)
        if r.get("camera"):
            cameras[(r.get("place",""),r.get("blockout",""), r["camera"])].append(r)
    parts = [f'<h1>{h(scene)} · {PHASES[phase]}</h1><p>项目 {h(data["project"])}　每项按编号、版本及指纹追踪。点击缩略图或文件名看原尺寸。</p>']
    if receipt_problems:
        parts.append("<p class='flag'>"+h("；".join(receipt_problems))+"</p>")
    for n,(group, members) in enumerate(groups.items(),1):
        members.sort(key=lambda r:r["kind"] != "base")
        shown = [r for r in members if r["files"].get("image")]
        if not any(r["kind"] == "base" for r in shown):
            for r in shown:
                r["issues"].append("兼容组缺实际基准图")
                if r["status"]=="ready":
                    r["review"]="材料待补"
        sheet = pack.contact(f"character-{n}", shown)
        parts.append(f'<h2>人物套装 · {h(" / ".join(group))}</h2>')
        if sheet:
            parts.append(f'<a href="{sheet}"><img class="sheet" src="{sheet}" alt="兼容组总览"></a>')
        coordinates = {(tuple(r["actual_size"]), tuple(r.get("anchor",[]))) for r in shown}
        if len(shown)>1 and (len(coordinates) != 1 or any(len(r.get("anchor",[]))!=2 for r in shown)):
            for r in shown:
                r["issues"].append("组内画布或锚点不一致，暂不能作同画布切换")
                if r["status"] == "ready":
                    r["review"] = "材料待补"
        elif len(shown)>1:
            buttons = " ".join(f'<button data-image="{r["files"]["image"]}">{r["ref"]}</button>' for r in shown)
            parts.append(f'<div class="switch"><p>同画布切换　{buttons}</p><img src="{shown[0]["files"]["image"]}" alt="切换预览"></div>')
    for n,(camera,members) in enumerate(cameras.items(),1):
        previews=[r for r in members if r["files"].get("image")]
        seen={(r["key"],str(r.get("version")),r["actual_sha"]) for r in previews}
        captions=[]
        for member in members:
            for peer in member["peer_views"]:
                key=(peer["key"],str(peer["version"]),peer.get("sha256"))
                if key in seen:
                    continue
                seen.add(key)
                label=f"P{len(captions)+1}"
                captions.append(f'{label} · {h(peer["scene"])} / {h(peer["key"])} / {h(peer["version"])}　'+
                                link(peer["bundled"],"原图")+"　"+h(peer.get("image","见该项对照及查询记录")))
                if peer["bundled"]:
                    previews.append({"ref":label,"files":{"image":peer["bundled"]}})
        group_image=pack.contact(f"camera-{n}",previews)
        if group_image:
            parts.append(f'<h2>同机位状态 · {h(" / ".join(camera))}</h2><a href="{group_image}"><img class="sheet" src="{group_image}" alt="同机位对照"></a>')
            parts.extend("<p>"+caption+"</p>" for caption in captions)
            if len(members)==1 and not captions and members[0].get("camera_peers")==[] and members[0]["files"].get("camera_history"):
                parts.append("<p>按随包查询记录，本机位无其他已登记状态。</p>")
    other = pack.contact("scene-overview",[r for r in rows if r["kind"] in {"background","cg","prop","design"} and r["files"].get("image")])
    if other:
        parts.append(f'<h2>非人物与事件 CG · {h(scene)}</h2><a href="{other}"><img class="sheet" src="{other}" alt="逐单缩略总览"></a>')
    parts.append('<h2>逐单清单与回执</h2>')
    references, reply = {}, []
    for r in rows:
        files = r["files"]
        unique = (r["key"],r["canonical"],r["actual_sha"])
        same = references.get(unique) if r["actual_sha"] else None
        if not same and r["review"] == "待用户审":
            references[unique] = r["ref"]
            reply.append(f'{r["ref"]} | {r["key"]} | {r["canonical"]} | {r["actual_sha"]} | ')
        status = f'与 {same} 同状态同版本，同次答复' if same and r["review"]=="待用户审" else r["review"]
        flags = r["warnings"] + r["issues"]
        if isinstance(r.get("failures"),int) and r["failures"] > 1:
            flags.append("反复技术失败")
        parts.append(f'<article><h3>{r["ref"]}　{h(r["key"])}　{h(status)}</h3>')
        if files.get("image"):
            parts.append(f'<a href="{files["image"]}"><img class="thumb" src="{files["image"]}" alt="登记图"></a>')
        details = [("工单", r.get("job") or "无本场制作单"), ("类型",r["kind"]),
                   ("首次引用场",r.get("first_scene") or ("无实际引用，首次制作于 "+str(r.get("production_scene","待核")) if r.get("unreferenced_common") else "未提供")), ("本场版本",r.get("version","—")),
                   ("原文件",r.get("image","无图")), ("指纹",r["actual_sha"] or "—"),
                   ("出图 / 技术失败 / 用户退回",f'{r.get("draws","—")} / {r.get("failures","—")} / {r["returns"]}'),
                   ("技术 / 一瞥",f'{r.get("technical","未完成")} / {r.get("glance","未完成")}'),
                   ("来源",r.get("source","未提供")), ("说明／下一动作",r.get("next","—"))]
        if r.get("camera"):
            details.append(("白模 / 机位",f'{r.get("blockout","—")} / {r["camera"]}'))
        if r.get("receipt"):
            rec = r["receipt"]
            details.append(("最近用户回执",f'{rec["id"]} · {rec["scene"]} · {PHASES[rec["phase"]]} · {rec["decision"]} · {rec["quote"]} · {rec["clause"]}'))
            if rec["decision"] == "退回":
                details.append(("返工单",rec.get("rework_job") or "待登记并回读真实 ID"))
        parts.append("<dl>"+"".join(f"<dt>{h(k)}</dt><dd>{h(v)}</dd>" for k,v in details)+"</dl>")
        if flags:
            parts.append("<p class='flag'>优先查看　"+" · ".join(h(v) for v in flags)+"</p>")
        if r.get("checklist"):
            parts.append("<p>工单要求　"+h(r["checklist"])+"</p>")
        labels = {"face":"三格脸部对照","eyes":"逐眼对照","overlay":"轮廓叠图","scale":"同画布总览",
                  "brief":"工单正文","evidence":"生产与版本回读","stitch":"拼接检查","locality":"局部检查","source_image":"来源同图","receipt":"原始用户回执"}
        labels.update({k:SPACE_FILES.get(k,k) for k in r.get("evidence_files",{})})
        parts.append("　".join(link(files.get(k),v) for k,v in labels.items() if files.get(k)))
        for field1,field2 in (("plan","top"),("clay","stage1")):
            if files.get(field1) and files.get(field2):
                parts.append("<div>"+" ".join(f'<a href="{files[f]}"><img class="thumb" src="{files[f]}" alt="{h(SPACE_FILES[f])}"></a>' for f in (field1,field2))+"</div>")
        parts.append("</article>")
    parts.append('<h2>用户核对标准</h2><p>设计按 A2；背景、CG、道具按 A4；基准、人物身份与衣装按 A5；差分和整套切换按 A6；技术底线及交付按 A7。空间场景同时看叠图和同机位对照。</p>')
    rules_text = rules.read_text(encoding="utf-8")
    (target/"美术验收标准.md").write_text(rules_text,encoding="utf-8")
    parts.append('<details><summary>展开本包对应的规则全文（含逐项退回条款）</summary><pre>'+h(rules_text)+'</pre></details>')
    scope=data.get("scope", [])
    scope_file=pack.copy(data.get("scope_evidence"))
    present={r.get("job") or r["key"] for r in rows}
    missing=sorted(set(scope)-present)
    extra=sorted(present-set(scope))
    complete=bool(scope and scope_file and data.get("scope_complete") is True) and not (missing or extra) and all(r["status"]=="ready" and not r["issues"] for r in rows)
    if phase=="checkpoint":
        actual_kinds={r["kind"] for r in rows}
        absent=sorted(required-actual_kinds)
        if not checkpoint_proof or not checkpoint_character or absent or actual_kinds!=required:
            complete=False
        parts.append(f'<p>角色 {h(checkpoint_character or "未指定")}　'+link(checkpoint_proof,"已审出镜方式与定版范围")+
                     ("　仅 CG 出现，本轮确认身份与衣装。" if required=={"identity","costume"} else "　本轮确认身份、衣装与首张样板。")+
                     ("　缺少："+h(", ".join(absent)) if absent else "")+
                     ("　缺已审出镜依据" if not checkpoint_proof else "")+"</p>")
        parts.append("<p>"+("本角色适用定版项均有用户回执。" if complete and all(r["review"]=="用户已审" for r in rows)
                              else "保留本角色的后续派工；其他独立角色和背景可继续。")+"</p>")
    parts.insert(1,"<p><strong>"+("本次提交范围的材料齐备" if complete else "进度包 · 材料尚未齐备")+"</strong>　"+link(scope_file,"本次范围回读")+"</p>")
    if missing or extra or not (scope and scope_file) or data.get("scope_complete") is not True:
        parts.insert(2,"<p class='flag'>范围核对　"+h("缺少清单条目："+", ".join(missing) if missing else "")+"　"+h("范围外条目："+", ".join(extra) if extra else "")+("　缺实际范围清单或其回读证据" if not(scope and scope_file) else "")+("　仅有本批范围，未证明整场／该角色定版范围齐全" if data.get("scope_complete") is not True else "")+"</p>")
    if not complete:
        reply=["进度记录，本轮不提交逐项验收。补齐缺项后生成新轮次。"]
    (target/"回复清单.txt").write_text(("逐项填写 通过 / 退回 / 接受较轻版，以及一句原因、对应条款。\n" if complete else "")+"\n".join(reply),encoding="utf-8")
    write_json(target/"清单.json",dict(project=data["project"],scene=scene,phase=phase,materials_complete=complete,
                                      missing=missing,extra=extra,scope_evidence=scope_file,checkpoint_evidence=checkpoint_proof,items=rows))
    rework=[dict(key=r["key"],job=r.get("job"),version=r["version"],receipt=r["receipt"]["id"],
                 clause=r["receipt"]["clause"],reason=r["receipt"]["quote"],rework_job=r["receipt"].get("rework_job"))
            for r in rows if r["review"]=="用户退回"]
    write_json(target/"返工待办.json",rework)
    parts.append('<p><a href="回复清单.txt">逐项回复清单</a> · <a href="清单.json">版本与证据索引</a> · <a href="返工待办.json">本版本返工待办</a></p>')
    page = """<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>美术审核包</title>
<style>body{max-width:980px;margin:2rem auto;padding:0 1rem;color:#1e293b;font:16px/1.55 system-ui}article,details,.switch{border:1px solid #cbd5e1;padding:1rem;margin:1rem 0}h2{margin-top:2rem}.thumb{max-width:260px;max-height:240px}.sheet{max-width:100%}.switch img{height:360px;max-width:100%;object-fit:contain;background:#d3d3d3}dl{display:grid;grid-template-columns:max-content 1fr;gap:.25rem 1rem}dd{overflow-wrap:anywhere;margin:0}pre{white-space:pre-wrap}.flag{color:#92400e}button{cursor:pointer;margin:.15rem;padding:.35rem}</style><body>"""
    page += "\n".join(parts) + """<script>document.addEventListener('click',e=>{if(e.target.dataset.image)e.target.closest('.switch').querySelector('img').src=e.target.dataset.image})</script></body></html>"""
    (target/"index.html").write_text(page,encoding="utf-8")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest",type=Path)
    parser.add_argument("output",type=Path,help="new directory for this immutable review round")
    args=parser.parse_args()
    output=args.output.resolve()
    if output.exists():
        parser.error("输出目录已存在，使用新的审核轮次目录")
    output.parent.mkdir(parents=True,exist_ok=True)
    rules=Path(__file__).resolve().parent.parent/"docs"/"苍岐美术生产规则.md"
    try:
        with tempfile.TemporaryDirectory(prefix=".review-",dir=output.parent) as tmp:
            staging=Path(tmp)/"result"
            staging.mkdir()
            build(read_json(args.manifest),args.manifest.resolve().parent,staging,rules)
            staging.rename(output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1,f"未生成审核包：{error}\n")
    print(output/"index.html")


if __name__=="__main__":
    main()

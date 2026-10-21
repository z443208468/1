"""Package existing, reviewed R8 outputs. Does not run or certify any tests.

Run after all source, PDF and QA files have been frozen:
  python source/build_package.py --output /absolute/path/Tokyo_Second_Theft_R8.zip
The retained test reports describe their own tested versions and limits.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent
VERSION = "R8-20261021"
EXCLUDED_PARTS = {"qa_work", "screenshots", "__pycache__", ".git", "node_modules"}
EXCLUDED_FILES = {"PROJECT_MANIFEST.json", "qa/delivery_validation.json"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files():
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if not p.is_file() or set(rel.parts) & EXCLUDED_PARTS:
            continue
        if rel.as_posix() in EXCLUDED_FILES or p.suffix in {".pyc", ".zip"}:
            continue
        if p.suffix.lower() in {".heic", ".jpg", ".jpeg", ".png", ".mov", ".mp4", ".otf", ".ttf"}:
            raise ValueError("Private/original/binary image material must not enter this release: " + str(rel))
        yield p


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    artifacts = []
    for i, p in enumerate(files(), 1):
        artifacts.append({"id": f"A{i:03}", "path": p.relative_to(ROOT).as_posix(),
                          "required": True, "status": "PRESENT", "version": VERSION, "sha256": sha(p)})
    declarations = [
        ("C01", "logic", "PASS", ["qa/logic_results.json"], "42 retained engine checks; test scope and date are in the report, not a quality certificate."),
        ("C02", "browser", "PASS", ["qa/browser_results.json"], "49 retained actual browser checks; subsequent label defect is separately documented."),
        ("C03", "independent_review", "PASS", ["qa/04_FINAL_INDEPENDENT_REVIEW.md", "qa/final_independent_results.json", "qa/final_s03_delta_results.json"], "35 checks on the stated baseline plus 9 final delta checks; not 44 final-version independent tests."),
        ("C04", "limited_model_walkthrough", "PARTIAL", ["qa/04a_LIMITED_MODEL_WALKTHROUGH.md", "qa/04_FINAL_INDEPENDENT_REVIEW.md"], "Visible-UI model walkthrough found the earlier S03 leak; final fix separately checked. No human blind test."),
        ("C05", "print", "PASS", ["qa/05_PRINT_QA.md", "qa/print_results.json", "print/print_geometry.json"], "52 pages rendered and visually reviewed; DOM geometry only, no physical assembly."),
        ("C06", "fresh_extraction", "PASS", ["qa/cold_start_results.json"], "17 actual UI checks after fresh ZIP extraction; final functional-component hashes must match."),
        ("C07", "site_dependency_G2", "FAIL", ["qa/04_FINAL_INDEPENDENT_REVIEW.md"], "Known deletion/replacement counterexamples for S01/S04/S05 remain REJECTED; required contract unchanged."),
        ("C08", "human_blind_playtest", "NOT_RUN", [], "No real human session occurred."),
        ("C09", "field_playtest", "NOT_RUN", [], "Original material review is not current on-site playtesting."),
        ("C10", "physical_assembly", "NOT_RUN", [], "No real printing, cutting, holding or outdoor assembly trial."),
        ("C11", "commercial_permission", "NOT_RUN", [], "No venue commercial-use permission is claimed."),
        ("C12", "traceability_structure", "PASS", ["qa/traceability_results.json"], "Structural references only; no narrative, historical or field certification."),
    ]
    checks = [{"id": i, "kind": k, "status": s, "version": VERSION, "evidence_paths": e, "notes": n}
              for i, k, s, e, n in declarations]
    cold = json.loads((ROOT / "qa/cold_start_results.json").read_text())
    for rel, expected in cold["component_sha256"].items():
        if sha(ROOT / rel) != expected:
            raise ValueError("Cold-tested functional bytes changed: " + rel)
    manifest = {"schema_version": 1, "template": False, "project_id": "tokyo-second-theft",
                "version": VERSION, "workflow_version": "3.0-merged-2026-10-21",
                "distribution": "complete_experimental_prototype", "artifacts": artifacts, "checks": checks,
                "limits": "Complete files do not remove the rejected required site-dependency gate. Validator output and this manifest are excluded from their own hash list to avoid circular hashes."}
    mp = ROOT / "PROJECT_MANIFEST.json"
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    spec = importlib.util.spec_from_file_location("delivery_validator", ROOT / "source/validate_delivery.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.audit(mp, ROOT)
    (ROOT / "qa/delivery_validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["errors"]:
        raise ValueError(result)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    entries = list(files()) + [mp, ROOT / "qa/delivery_validation.json"]
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for p in sorted(entries):
            name = "Tokyo_CNW_R8/" + p.relative_to(ROOT).as_posix()
            info = ZipInfo(name, date_time=(2026, 10, 21, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, p.read_bytes(), compresslevel=9)
    with ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC mismatch")
    output.with_suffix(output.suffix + ".sha256").write_text(sha(output) + "  " + output.name + "\n")
    print(json.dumps({"status": result["status"], "files": len(entries), "hashed_artifacts": len(artifacts),
                      "zip": str(output), "bytes": output.stat().st_size, "sha256": sha(output),
                      "non_pass_declarations": result["warnings"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

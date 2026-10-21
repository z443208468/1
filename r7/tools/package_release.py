#!/usr/bin/env python3
"""Package the frozen R7 review product and verify an actual extracted copy.

Run only after final PDFs, PDF_VISUAL_REVIEW.json and the current PDF contact
sheets have been frozen. This script never rebuilds or edits product content.
It generates MANIFEST.sha256 and release artifacts using Python's standard
library. Identical input bytes produce identical ZIP bytes in the same Python /
zlib environment: member order, timestamps, permissions and compression are fixed.

Usage, from any directory:
    python3 /path/to/r7/tools/package_release.py

This is a package-integrity check. It neither conducts nor certifies human
playtesting, physical printing, field testing, story quality or commercial readiness.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tempfile
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_PREFIX = "Tokyo_Five_Sites_R7"
ARCHIVE_NAME = "Tokyo_Five_Sites_R7_Review_20261021.zip"
FIXED_ZIP_TIME = (2026, 10, 21, 0, 0, 0)
MANIFEST_NAME = "MANIFEST.sha256"
CONTACT_DIRECTORY = "qa/pdf_contacts"
ARCHIVE_PUBLISHED_THIS_RUN = False

# Required finished deliverables and the sources needed to rebuild them.
REQUIRED_FILES = (
    "README.md",
    "requirements-build.txt",
    "R7_Offline.html",
    "content/game.json",
    "content/mechanics_contract.json",
    "output/pdf/R7_Player_Kit_ZH.pdf",
    "output/pdf/R7_Player_Kit_EN.pdf",
    "output/pdf/R7_Designer_Guide.pdf",
    "play/index.html",
    "play/app.js",
    "play/narrative.js",
    "play/engine.js",
    "play/figures.js",
    "play/style.css",
    "play/data.js",
    "play/data.json",
    "play/print.html",
    "play/print_zh.html",
    "play/print_en.html",
    "play/guide.html",
    "tools/build_release.py",
    "tools/build_runtime.mjs",
    "tools/build_print.py",
    "tools/print_style.css",
    "tools/build_guide.py",
    "tools/render_pdfs.py",
    "tools/package_release.py",
    "qa/mechanics_contract.json",
    "qa/verify_mechanics.mjs",
    "qa/audit_content.py",
    "qa/test_logic.mjs",
    "qa/test_runtime.py",
    "qa/test_narrative.py",
    "qa/logic_results.json",
    "qa/browser_results.json",
    "qa/narrative_results.json",
    "qa/content_audit.json",
    "qa/pdf_results.json",
    "qa/PDF_VISUAL_REVIEW.json",
    "qa/RELEASE_REVIEW.md",
)


class PackageError(RuntimeError):
    """The input or extracted package failed a concrete integrity requirement."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exclusion_reason(relative: PurePosixPath) -> str | None:
    parts = relative.parts
    if parts and parts[0] == "release":
        return "release artifacts are external to the packaged payload"
    if parts[:2] == ("output", "qa"):
        return "rebuildable PDF page renders; retained contact sheets are in qa/pdf_contacts"
    if "__pycache__" in parts or relative.suffix in (".pyc", ".pyo"):
        return "Python bytecode cache"
    if relative.as_posix() == MANIFEST_NAME:
        return "manifest is generated separately and must not hash itself"
    return None


def collect_files() -> tuple[list[Path], dict[str, int]]:
    payload: list[Path] = []
    excluded: dict[str, int] = {}
    for path in sorted(ROOT.rglob("*"), key=lambda p: p.relative_to(ROOT).as_posix()):
        relative = PurePosixPath(path.relative_to(ROOT).as_posix())
        reason = exclusion_reason(relative)
        if reason:
            if path.is_file():
                excluded[reason] = excluded.get(reason, 0) + 1
            continue
        if path.is_symlink():
            raise PackageError(f"Symlinks are not packaged; use a regular source file: {relative}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(path.stat().st_mode):
            raise PackageError(f"Not a regular file: {relative}")
        name = relative.as_posix()
        if any(character in name for character in ("\n", "\r", "\\")):
            raise PackageError(f"Filename cannot be represented safely in the SHA-256 manifest: {name!r}")
        payload.append(path)
    return payload, excluded


def check_inputs(files: list[Path]) -> list[str]:
    available = {path.relative_to(ROOT).as_posix() for path in files}
    missing = [name for name in REQUIRED_FILES if name not in available]
    if missing:
        raise PackageError("Required deliverables or rebuild sources are missing: " + ", ".join(missing))
    empty = [name for name in REQUIRED_FILES if (ROOT / name).stat().st_size == 0]
    if empty:
        raise PackageError("Required files are empty: " + ", ".join(empty))
    for name in REQUIRED_FILES:
        if name.endswith(".json"):
            try:
                json.loads((ROOT / name).read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise PackageError(f"Required JSON cannot be read: {name}: {error}") from error
        if name.endswith(".pdf"):
            with (ROOT / name).open("rb") as stream:
                if stream.read(5) != b"%PDF-":
                    raise PackageError(f"Required PDF has no PDF header: {name}")

    # A passing old record must not authorize packaging different current bytes.
    visual = json.loads((ROOT / "qa/PDF_VISUAL_REVIEW.json").read_text(encoding="utf-8"))
    if not isinstance(visual, dict) or not isinstance(visual.get("final_documents"), list):
        raise PackageError("qa/PDF_VISUAL_REVIEW.json must identify its final_documents.")
    if visual.get("status") != "COMPLETE_FOR_RENDERED_LAYOUT" or visual.get("unresolved_visual_issues"):
        raise PackageError("Rendered-page visual review is incomplete or has unresolved issues.")
    required_pdfs = {name for name in REQUIRED_FILES if name.endswith(".pdf")}
    reviewed_pdfs: set[str] = set()
    for document in visual["final_documents"]:
        if not isinstance(document, dict) or not isinstance(document.get("path"), str) or document["path"] not in required_pdfs:
            raise PackageError("Visual-review final_documents must identify the three required PDF paths.")
        relative = document["path"]
        if relative in reviewed_pdfs:
            raise PackageError(f"Visual-review record repeats a PDF: {relative}")
        reviewed_pdfs.add(relative)
        actual = sha256_file(ROOT / relative)
        if document.get("sha256") != actual:
            raise PackageError(f"Visual-review SHA-256 is stale or missing for current PDF: {relative}")
        if "bytes" in document and document["bytes"] != (ROOT / relative).stat().st_size:
            raise PackageError(f"Visual-review byte count is stale for current PDF: {relative}")
        count = document.get("page_count")
        if not isinstance(count, int) or count < 1 or document.get("reviewed_pages") != list(range(1, count + 1)):
            raise PackageError(f"Visual-review record must identify every actually reviewed page: {relative}")
    if reviewed_pdfs != required_pdfs:
        raise PackageError("Visual-review final_documents does not cover all three required PDFs.")

    bound_files = {
        "data_sha256": "play/data.json",
        "bundle_sha256": "R7_Offline.html",
        "app_sha256": "play/app.js",
    }
    current_hashes = {field: sha256_file(ROOT / relative) for field, relative in bound_files.items()}
    source_hash = sha256_file(ROOT / "content/game.json")
    if current_hashes["data_sha256"] != source_hash:
        raise PackageError("play/data.json differs from the frozen content/game.json; rebuild and revalidate before packaging.")
    for relative in ("qa/logic_results.json", "qa/browser_results.json", "qa/narrative_results.json"):
        record = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            raise PackageError(f"Runtime verification record must be a JSON object: {relative}")
        if not record.get("checks") or any(not (c.get("result") == "PASS" or c.get("passed") is True) for c in record["checks"]):
            raise PackageError(f"Runtime verification contains an unresolved failure or no checks: {relative}")
        for field, actual in current_hashes.items():
            if record.get(field) != actual:
                raise PackageError(f"{relative} has a stale or missing {field} for current {bound_files[field]}.")
    audit = json.loads((ROOT / "qa/content_audit.json").read_text(encoding="utf-8"))
    if not isinstance(audit, dict) or audit.get("source_sha256") != source_hash:
        raise PackageError("qa/content_audit.json has a stale or missing source_sha256 for current content/game.json.")

    contacts = sorted(name for name in available if name.startswith(CONTACT_DIRECTORY + "/") and name.lower().endswith(".png"))
    reviewed_contacts = visual.get("contact_sheets", [])
    if not contacts or not isinstance(reviewed_contacts, list):
        raise PackageError("Reviewed PDF contact sheets are required.")
    bound_contacts = {entry.get("path"): entry.get("sha256") for entry in reviewed_contacts if isinstance(entry, dict)}
    if set(bound_contacts) != set(contacts):
        raise PackageError("Visual review must bind every retained contact sheet by its exact path.")
    for relative, digest in bound_contacts.items():
        if sha256_file(ROOT / relative) != digest:
            raise PackageError("Reviewed contact-sheet hash is stale: " + relative)
    pdf_record = json.loads((ROOT / "qa/pdf_results.json").read_text())
    if pdf_record.get("content_sha256") != source_hash or pdf_record.get("errors"):
        raise PackageError("PDF rendering record has stale content or unresolved rendering errors.")
    if pdf_record.get("narrative_sha256") != sha256_file(ROOT / "play/narrative.js"):
        raise PackageError("PDF rendering record has stale narrative figures.")
    authored = [ROOT / "content/game.json"] + sorted((ROOT / "design").glob("*.md")) + sorted((ROOT / "research").glob("*.md")) + sorted((ROOT / "qa").glob("*.md"))
    authored_hashes = {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in authored}
    if pdf_record.get("authored_source_sha256") != authored_hashes:
        raise PackageError("PDF authored source records are stale; rebuild the affected documents.")
    if {d.get("pdf") for d in pdf_record.get("documents", [])} != required_pdfs:
        raise PackageError("PDF rendering record must cover exactly the three final PDFs.")
    for document in pdf_record.get("documents", []):
        if document.get("pdf") in required_pdfs and document.get("sha256") != sha256_file(ROOT / document["pdf"]):
            raise PackageError("PDF proof record does not bind current final bytes.")
        if document.get("html_sha256") != sha256_file(ROOT / document["html"]):
            raise PackageError("PDF proof record has stale HTML: " + document["html"])
    for directory in ("design", "research"):
        if not any(name.startswith(directory + "/") and name.endswith(".md") for name in available):
            raise PackageError(f"The complete source package needs the {directory}/ Markdown documents.")
    return contacts


def fixed_member(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIME)
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def validate_archive(archive_path: Path, scratch: Path, expected: dict[str, dict[str, object]], manifest: bytes) -> list[dict[str, object]]:
    extraction = scratch / "extracted"
    extraction.mkdir()
    expected_names = set(expected) | {MANIFEST_NAME}
    expected_members = {ARCHIVE_PREFIX + "/" + name for name in expected_names}
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise PackageError("ZIP contains duplicate member names.")
        if set(names) != expected_members:
            raise PackageError("ZIP member set does not match the complete payload and manifest.")
        for member in archive.infolist():
            relative = PurePosixPath(member.filename)
            if relative.is_absolute() or ".." in relative.parts or relative.parts[0] != ARCHIVE_PREFIX:
                raise PackageError(f"Unsafe ZIP member name: {member.filename}")
            if stat.S_ISLNK(member.external_attr >> 16):
                raise PackageError(f"ZIP member is unexpectedly a symlink: {member.filename}")
        damaged = archive.testzip()
        if damaged is not None:
            raise PackageError(f"ZIP CRC check failed: {damaged}")
        # This is an actual extraction, followed by hashes of files on disk.
        archive.extractall(extraction)

    extracted_root = extraction / ARCHIVE_PREFIX
    extracted_names = {path.relative_to(extracted_root).as_posix() for path in extracted_root.rglob("*") if path.is_file()}
    if extracted_names != expected_names:
        raise PackageError("Extracted file set does not match the payload plus manifest.")
    manifest_path = extracted_root / MANIFEST_NAME
    if manifest_path.read_bytes() != manifest:
        raise PackageError("Extracted manifest differs from the manifest placed in the ZIP.")

    parsed: dict[str, str] = {}
    for line in manifest.decode("utf-8").splitlines():
        digest, separator, relative = line.partition("  ")
        if separator != "  " or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise PackageError("Extracted manifest contains an invalid SHA-256 line.")
        if relative == MANIFEST_NAME or relative in parsed:
            raise PackageError("Manifest contains itself or a duplicate path.")
        parsed[relative] = digest
    if set(parsed) != set(expected):
        raise PackageError("Manifest entries do not match the payload files.")

    verified = []
    for relative in sorted(expected):
        path = extracted_root / relative
        actual = sha256_file(path)
        if actual != parsed[relative] or actual != expected[relative]["sha256"]:
            raise PackageError(f"Extracted SHA-256 mismatch: {relative}")
        if path.stat().st_size != expected[relative]["bytes"]:
            raise PackageError(f"Extracted size mismatch: {relative}")
        verified.append({"path": relative, "bytes": path.stat().st_size, "sha256": actual, "extracted_check": "PASS"})
    verified.append({"path": MANIFEST_NAME, "bytes": len(manifest), "sha256": hashlib.sha256(manifest).hexdigest(), "extracted_check": "PASS; verified against generated bytes, excluded from its own entries"})
    return verified


def atomic_write(path: Path, data: bytes, scratch: Path) -> None:
    temporary = scratch / (path.name + ".pending")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def package() -> dict[str, object]:
    global ARCHIVE_PUBLISHED_THIS_RUN
    ARCHIVE_PUBLISHED_THIS_RUN = False
    files, excluded = collect_files()
    contacts = check_inputs(files)
    records = {
        path.relative_to(ROOT).as_posix(): {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in files
    }
    manifest = "".join(f"{records[name]['sha256']}  {name}\n" for name in sorted(records)).encode("utf-8")
    release = ROOT / "release"
    release.mkdir(exist_ok=True)
    archive_path = release / ARCHIVE_NAME

    with tempfile.TemporaryDirectory(prefix="r7-package-", dir=release) as working:
        scratch = Path(working)
        pending_archive = scratch / ARCHIVE_NAME
        with zipfile.ZipFile(pending_archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as archive:
            for relative in sorted(set(records) | {MANIFEST_NAME}):
                content = manifest if relative == MANIFEST_NAME else (ROOT / relative).read_bytes()
                archive.writestr(fixed_member(ARCHIVE_PREFIX + "/" + relative), content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        verified = validate_archive(pending_archive, scratch, records, manifest)

        # Refuse to publish a package if a producer edited or added source files
        # while packaging was under way. All release/ work is excluded here.
        current_files, _ = collect_files()
        current_names = {path.relative_to(ROOT).as_posix() for path in current_files}
        if current_names != set(records):
            raise PackageError("Payload file set changed while packaging; freeze producers and rerun.")
        changed = [name for name in sorted(records) if sha256_file(ROOT / name) != records[name]["sha256"]]
        if changed:
            raise PackageError("Input files changed while packaging: " + ", ".join(changed))

        archive_sha = sha256_file(pending_archive)
        archive_size = pending_archive.stat().st_size
        report: dict[str, object] = {
            "schema": "tokyo-five-sites-package-validation/v1",
            "result": "PASS",
            "validated_at_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "Complete release-package inventory and actual extraction SHA-256 verification only.",
            "not_tested_or_certified_by_this_script": ["human playtesting", "physical printing", "on-site field testing", "story quality", "commercial readiness"],
            "archive": {
                "path": "release/" + ARCHIVE_NAME,
                "top_level_directory": ARCHIVE_PREFIX + "/",
                "bytes": archive_size,
                "sha256": archive_sha,
                "file_count_including_manifest": len(verified),
                "fixed_member_timestamp": "2026-10-21 00:00:00",
                "sorted_member_order": True,
                "unix_file_mode": "0644",
                "compression": "DEFLATE level 9",
                "python": sys.version.split()[0],
                "zlib": zlib.ZLIB_RUNTIME_VERSION,
            },
            "manifest": {
                "path": MANIFEST_NAME,
                "sha256": hashlib.sha256(manifest).hexdigest(),
                "entries": len(records),
                "self_reference": False,
                "present_in_zip": True,
            },
            "validation": {
                "required_files_present_and_nonempty": True,
                "required_json_parseable": True,
                "three_required_pdfs_have_pdf_headers": True,
                "visual_review_hashes_match_current_pdfs": True,
                "runtime_record_hashes_match_current_data_bundle_app": True,
                "content_audit_hash_matches_current_source": True,
                "zip_crc": "PASS",
                "actual_temporary_directory_extraction": True,
                "exact_extracted_file_set": True,
                "all_extracted_sha256": "PASS",
                "source_files_unchanged_during_packaging": True,
            },
            "required_files": list(REQUIRED_FILES),
            "retained_pdf_contact_sheets": contacts,
            "excluded_file_counts_by_reason": excluded,
            "files": verified,
        }
        # Publish the ZIP only after full extraction verification has succeeded.
        atomic_write(ROOT / MANIFEST_NAME, manifest, scratch)
        os.replace(pending_archive, archive_path)
        ARCHIVE_PUBLISHED_THIS_RUN = True
        atomic_write(release / "SHA256SUMS", f"{archive_sha}  {ARCHIVE_NAME}\n".encode("ascii"), scratch)
        atomic_write(release / "package_validation.json", (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"), scratch)
    return report


def main() -> int:
    try:
        report = package()
    except (PackageError, OSError, zipfile.BadZipFile) as error:
        # Before extraction verification, failures leave an earlier ZIP untouched.
        # If publication succeeded but metadata writing failed, report that truthfully.
        failure = {
            "schema": "tokyo-five-sites-package-validation/v1",
            "result": "FAIL",
            "validated_at_utc": datetime.now(timezone.utc).isoformat(),
            "error": str(error),
            "new_archive_published": ARCHIVE_PUBLISHED_THIS_RUN,
            "scope": "Packaging integrity only; no human, physical, field or story-quality certification.",
        }
        release = ROOT / "release"
        try:
            release.mkdir(exist_ok=True)
            (release / "package_validation.json").write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass
        print("Packaging failed: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps({"result": report["result"], "archive": report["archive"], "manifest_entries": report["manifest"]["entries"], "retained_contact_sheets": len(report["retained_pdf_contact_sheets"])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate a delivery manifest against local files; never judge creative quality.
Requires Python 3.9+ and standard library only. Does not modify any file.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ARTIFACT_STATUSES = {"PRESENT", "MISSING", "NOT_APPLICABLE"}
CHECK_STATUSES = {"PASS", "FAIL", "PARTIAL", "NOT_RUN", "BLOCKED", "NOT_APPLICABLE"}

def audit(manifest_path, root):
    root = Path(root).resolve()
    errors, warnings = [], []
    checked = 0
    try:
        data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"status": "INVALID", "errors": [str(exc)], "warnings": [], "checked_files": 0}
    if not isinstance(data, dict):
        return {"status": "INVALID", "errors": ["Manifest must be an object."], "warnings": [], "checked_files": 0}

    def issue(message):
        errors.append(message)

    def local_path(value, label):
        if not isinstance(value, str) or not value.strip():
            issue(label + ": nonempty relative path required")
            return None
        if "\\" in value or Path(value).is_absolute() or ".." in Path(value).parts:
            issue(label + ": unsafe or non-portable path")
            return None
        p = (root / value).resolve()
        try:
            p.relative_to(root)
        except ValueError:
            issue(label + ": path escapes product root")
            return None
        return p

    if data.get("schema_version") != 1:
        issue("schema_version must be 1")
    if data.get("template") is not False:
        issue("Set template=false only after completing the actual project manifest.")
    for key in ("project_id", "version"):
        if not isinstance(data.get(key), str) or not data[key].strip() or data[key].startswith("SET_"):
            issue(key + ": actual project value required")
    version = data.get("version")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        issue("artifacts must be a nonempty array")
        artifacts = []
    ids, paths = set(), set()
    for index, item in enumerate(artifacts):
        label = "artifacts[" + str(index) + "]"
        if not isinstance(item, dict):
            issue(label + ": object required")
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in ids:
            issue(label + ": nonempty unique id required")
        elif identifier:
            ids.add(identifier)
        required = item.get("required")
        if not isinstance(required, bool):
            issue(label + ": required must be boolean")
        status = item.get("status")
        if not isinstance(status, str) or status not in ARTIFACT_STATUSES:
            issue(label + ": invalid artifact status")
            continue
        if item.get("version") != version:
            issue(label + ": artifact release version does not match manifest")
        if status != "PRESENT":
            if required:
                issue(label + ": required artifact is not PRESENT")
            if not isinstance(item.get("reason"), str) or not item["reason"].strip():
                issue(label + ": omitted artifact needs a reason")
            continue
        p = local_path(item.get("path"), label)
        if p is None:
            continue
        if p in paths:
            issue(label + ": duplicate resolved artifact path")
        paths.add(p)
        if not p.is_file():
            issue(label + ": artifact file missing")
            continue
        try:
            if p.stat().st_size == 0:
                issue(label + ": artifact file empty")
                continue
            digest = hashlib.sha256()
            with p.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        except OSError as exc:
            issue(label + ": " + str(exc))
            continue
        claimed = item.get("sha256")
        if not isinstance(claimed, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", claimed):
            issue(label + ": SHA-256 required for PRESENT artifact")
        elif digest.hexdigest() != claimed.lower():
            issue(label + ": SHA-256 mismatch")
        checked += 1

    checks = data.get("checks")
    if not isinstance(checks, list):
        issue("checks must be an array; [] means no checks recorded")
        checks = []
    if not checks:
        warnings.append("No design, player, field or operational checks recorded.")
    check_ids = set()
    for index, check in enumerate(checks):
        label = "checks[" + str(index) + "]"
        if not isinstance(check, dict):
            issue(label + ": object required")
            continue
        identifier = check.get("id")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in check_ids:
            issue(label + ": nonempty unique id required")
        else:
            check_ids.add(identifier)
        if not isinstance(check.get("kind"), str) or not check["kind"].strip():
            issue(label + ": kind required")
        status = check.get("status")
        if not isinstance(status, str) or status not in CHECK_STATUSES:
            issue(label + ": invalid check status")
        if check.get("version") != version:
            issue(label + ": check version does not match manifest")
        evidence = check.get("evidence_paths")
        if not isinstance(evidence, list):
            issue(label + ": evidence_paths must be an array")
            evidence = []
        if isinstance(status, str) and status in {"PASS", "FAIL", "PARTIAL"} and not evidence:
            issue(label + ": completed check claim requires an evidence file")
        if not isinstance(check.get("notes"), str) or not check["notes"].strip():
            issue(label + ": notes must describe scope or reason")
        for value in evidence:
            p = local_path(value, label + ".evidence")
            if p is None:
                continue
            try:
                if not p.is_file() or p.stat().st_size == 0:
                    issue(label + ": evidence file missing or empty")
                elif p not in paths:
                    issue(label + ": evidence must be a versioned, hashed PRESENT artifact")
            except OSError as exc:
                issue(label + ": " + str(exc))
        if status != "PASS":
            warnings.append(label + ": " + str(status))
    return {
        "status": "INVALID" if errors else "FILES_CONSISTENT",
        "project_id": data.get("project_id"),
        "version": version,
        "checked_files": checked,
        "errors": errors,
        "warnings": warnings,
        "limits": "Only file integrity and declaration consistency. No proof of quality, playability, authenticity of test reports, or user acceptance."
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--root", required=True, help="Directory containing the product artifacts")
    args = parser.parse_args()
    report = audit(args.manifest, args.root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0

if __name__ == "__main__":
    sys.exit(main())

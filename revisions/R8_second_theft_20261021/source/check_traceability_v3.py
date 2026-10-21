#!/usr/bin/env python3
"""Verify structural linkage and truthful labels for an OPTIONAL project traceability file.

It does NOT verify facts, narrative creativity, puzzle fairness, player enjoyment,
or that a claimed human/field session was actually performed.

Usage: python scripts/check_traceability.py TRACK.json --level story_design
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ENUMS = {
    "world_basis": {"documented", "invented", "mixed"},
    "play_surface": {"physical", "digital", "tabletop", "hybrid"},
    "site_binding": {"required", "preferred", "none"},
    "mechanics_policy": {"greenfield", "preserve", "locked"},
}
LEVELS = ("concept", "story_design", "playable_spec", "prototype", "field_ready")
VALIDATION_LEVELS = {"DESIGN_REVIEWED", "LOGIC_DRYRUN", "BLIND_PLAYTESTED", "FIELD_PLAYTESTED", "RELEASE_REVIEWED"}
REAL_TESTS = {"BLIND_PLAYTESTED", "FIELD_PLAYTESTED"}
GATE_STATUSES = {"PASS_WITH_EVIDENCE", "REJECTED", "BLOCKED", "NOT_TESTED", "NOT_APPLICABLE"}


def check(data: dict, level: str = "concept") -> dict:
    errors, warnings = [], []
    if not isinstance(data, dict):
        return {"status": "INVALID", "errors": ["root must be an object"], "warnings": []}
    proj = data.get("project")
    if not isinstance(proj, dict):
        errors.append("project must be an object")
        proj = {}
    for key in ("id", "version"):
        if not isinstance(proj.get(key), str) or not proj[key].strip():
            errors.append(f"project.{key} required")
    for key, choices in ENUMS.items():
        if proj.get(key) not in choices:
            errors.append(f"project.{key} invalid: {proj.get(key)!r}")
    if level not in LEVELS:
        errors.append(f"unrecognized level {level!r}")
    declared_level = proj.get("delivery_level")
    if declared_level is not None and declared_level not in LEVELS:
        errors.append(f"project.delivery_level invalid: {declared_level!r}")
    if declared_level is not None and declared_level != level:
        errors.append(f"project.delivery_level={declared_level!r} differs from checked --level={level!r}")

    entities, all_ids = {}, set()
    for name in ("sites", "evidence", "events", "player_actions", "puzzles"):
        items = data.get(name)
        if not isinstance(items, list):
            errors.append(f"{name} must be array")
            items = []
        entities[name] = {}
        for i, entry in enumerate(items):
            if not isinstance(entry, dict):
                errors.append(f"{name}[{i}] must be object")
                continue
            ident = entry.get("id")
            if not isinstance(ident, str) or not ident.strip():
                errors.append(f"{name}[{i}].id missing")
                continue
            if ident in entities[name] or ident in all_ids:
                errors.append(f"duplicate ID {ident} (global uniqueness required)")
            entities[name][ident] = entry
            all_ids.add(ident)

    if not entities["events"]:
        errors.append("no event candidates: not a valid content traceability claim even at concept level")
    if level in LEVELS[1:]:
        for key in ("player_actions", "puzzles"):
            if not entities[key]:
                errors.append(f"no {key} for {level}")
    if level in LEVELS[2:] and not entities["sites"]:
        warnings.append("No site/screen/prop inventory; check whether project scope genuinely omits scenes")

    def refs(entry, key, collection, ident):
        ls = entry.get(key, [])
        if not isinstance(ls, list):
            errors.append(f"{ident}.{key} must be array")
            return
        for ref in ls:
            if not isinstance(ref, str) or ref not in entities[collection]:
                errors.append(f"{ident}.{key} missing or malformed reference {ref!r} in {collection}")

    for ident, entry in entities["events"].items():
        refs(entry, "evidence_ids", "evidence", ident)
        for key in ("why_now", "player_stakes"):
            if not entry.get(key):
                (errors if level in LEVELS[1:] else warnings).append(f"event {ident}: {key} missing")
    for ident, entry in entities["player_actions"].items():
        event_id = entry.get("event_id")
        if not isinstance(event_id, str) or event_id not in entities["events"]:
            errors.append(f"action {ident}: unknown event_id {event_id!r}")
        if entry.get("before") == entry.get("after") and entry.get("before") is not None:
            warnings.append(f"action {ident}: state unchanged; explain cognitive impact")
        for key in ("action", "feedback", "before", "after"):
            if not entry.get(key):
                (errors if level in LEVELS[1:] else warnings).append(f"action {ident}: {key} missing")
    for ident, entry in entities["puzzles"].items():
        sid = entry.get("site_id")
        if sid is not None and (not isinstance(sid, str) or sid not in entities["sites"]):
            errors.append(f"puzzle {ident}: unknown site_id {sid!r}")
        refs(entry, "evidence_ids", "evidence", ident)
        refs(entry, "action_ids", "player_actions", ident)
        if level in LEVELS[1:] and not entry.get("action_ids"):
            errors.append(f"puzzle {ident}: no linked player action")
        for key in ("answer", "operation", "fallback"):
            if not entry.get(key):
                (errors if level in LEVELS[1:] else warnings).append(f"puzzle {ident}: {key} missing")
        if level in LEVELS[2:]:
            for key in ("visible_inputs", "solution_steps", "feedback"):
                if not entry.get(key):
                    errors.append(f"puzzle {ident}: playable_spec requires {key}")

    claims = data.get("validation", [])
    if not isinstance(claims, list):
        errors.append("validation must be array")
        claims = []
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"validation[{i}] not object")
            continue
        label = claim.get("level")
        if label not in VALIDATION_LEVELS:
            errors.append(f"validation[{i}]: unknown level {label!r}")
        if not isinstance(claim.get("evidence_ref"), str) or not claim.get("evidence_ref", "").strip():
            errors.append(f"validation[{i}]: claim without evidence_ref")
        if label in REAL_TESTS:
            sessions = claim.get("actual_sessions")
            if not isinstance(sessions, list) or not sessions:
                errors.append(f"validation[{i}]: real test requires nonempty actual_sessions")
            else:
                for j, session in enumerate(sessions):
                    if not isinstance(session, dict):
                        errors.append(f"validation[{i}].actual_sessions[{j}]: object required")
                        continue
                    for field in ("session_id", "date", "record_ref"):
                        if not isinstance(session.get(field), str) or not session[field].strip():
                            errors.append(f"validation[{i}].actual_sessions[{j}]: missing {field}")
                    if not isinstance(session.get("participant_count"), int) or session.get("participant_count", 0) <= 0:
                        errors.append(f"validation[{i}].actual_sessions[{j}]: positive participant_count required")
                    if label == "FIELD_PLAYTESTED" and not session.get("site_or_environment"):
                        errors.append(f"validation[{i}].actual_sessions[{j}]: actual field site required")
            if claim.get("tester_type") in ("AI", "AUTHOR_SIMULATION"):
                errors.append(f"validation[{i}]: AI/author simulation cannot be human test")

    if level == "field_ready":
        witnessed_levels = {v.get("level") for v in claims if isinstance(v, dict)}
        if "RELEASE_REVIEWED" not in witnessed_levels:
            errors.append("field_ready declaration requires RELEASE_REVIEWED evidence entry")
        if proj.get("play_surface") in ("physical", "hybrid") and proj.get("site_binding") == "required" and "FIELD_PLAYTESTED" not in witnessed_levels:
            errors.append("physical/hybrid field_ready declaration with required sites needs FIELD_PLAYTESTED evidence")

    gates = data.get("gate_reviews", [])
    if not isinstance(gates, list):
        errors.append("gate_reviews must be array")
        gates = []
    for i, gate in enumerate(gates):
        if not isinstance(gate, dict):
            errors.append(f"gate_reviews[{i}] not object")
            continue
        if gate.get("status") not in GATE_STATUSES:
            errors.append(f"gate_reviews[{i}] invalid status")
        if gate.get("status") == "PASS_WITH_EVIDENCE" and (not isinstance(gate.get("evidence_refs"), list) or not any(isinstance(v, str) and v.strip() for v in gate.get("evidence_refs", []))):
            errors.append(f"gate_reviews[{i}] passed without meaningful evidence_refs")
        if gate.get("status") in ("REJECTED", "BLOCKED") and not gate.get("counterexample"):
            warnings.append(f"gate_reviews[{i}]: no counterexample")
    diffs = data.get("mechanics_lock_diffs", [])
    if not isinstance(diffs, list):
        errors.append("mechanics_lock_diffs must be array")
        diffs = []
    for i, diff in enumerate(diffs):
        if not isinstance(diff, dict):
            errors.append(f"mechanics_lock_diffs[{i}] not object")
            continue
        if diff.get("status") == "APPLIED" and (not isinstance(diff.get("approval_ref"), str) or not diff["approval_ref"].strip()):
            errors.append(f"mechanics_lock_diffs[{i}]: applied locked change without approval_ref")

    return {"status": "INVALID" if errors else "REFERENCES_STRUCTURALLY_VALID", "level": level,
            "errors": errors, "warnings": warnings,
            "counts": {k: len(v) for k, v in entities.items()},
            "limits": "No factual, literary, human-experience, independent-review or field certification."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project_traceability")
    ap.add_argument("--level", choices=LEVELS, default="concept")
    args = ap.parse_args()
    try:
        obj = json.loads(Path(args.project_traceability).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as ex:
        print(json.dumps({"status": "INVALID", "errors": [str(ex)]}, ensure_ascii=False, indent=2))
        return 1
    report = check(obj, args.level)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(bool(report["errors"]))


if __name__ == "__main__":
    sys.exit(main())

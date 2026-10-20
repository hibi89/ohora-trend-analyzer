#!/usr/bin/env python3
"""Offline taxonomy integrity and P0 tagging-output contract checks.

No external API, database, network or actual image classification performed.
Usage:
    python scripts/validate_taxonomy.py
    python scripts/validate_taxonomy.py --result fixtures/sample_valid_tag_result.json
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "taxonomy" / "tag_schema_v1_1.json"
DRAFT = ROOT / "taxonomy" / "tag_schema_v1_0_draft.json"
RULES = ROOT / "taxonomy" / "tag_rules_v1_1.json"
P0 = {"F01", "F03", "F05", "F06", "F08", "F09", "F10"}
ALL = {f"F{i:02}" for i in range(1, 15)}
STATUSES = {"observed", "unknown", "not_applicable", "not_evaluated"}
EVIDENCE = {"image", "caption", "both", "human"}
SOURCE_VALUES = {"synthetic", "synthetic_fixture", "approved_sample", "approved_readonly_export"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_dictionary() -> list[str]:
    errors: list[str] = []
    old, new, rules = load(DRAFT), load(TAXONOMY), load(RULES)
    categories = new.get("categories", [])
    old_categories = old.get("categories", [])
    ids = [c.get("id") for c in categories]
    if ids != [f"F{i:02}" for i in range(1, 15)]:
        errors.append("category IDs must be F01..F14 in order")
    tags = [t for c in categories for t in c["tags"]]
    old_tags = [t for c in old_categories for t in c["tags"]]
    if len(tags) != 159 or len(old_tags) != 159:
        errors.append("expected 159 original and current tags")
    if len({t.get("tag_id") for t in tags}) != len(tags):
        errors.append("duplicate tag IDs")
    preserved = ("tag_id", "slug", "label_ko", "label_en", "label_ja", "aliases", "status")
    if len(tags) == len(old_tags):
        for o, n in zip(old_tags, tags):
            for field in preserved:
                if o.get(field) != n.get(field):
                    errors.append(f"original {field} changed: {o.get('tag_id')}")
    observed_ids: set[str] = set()
    for cat in categories:
        group, aliases = cat["id"], defaultdict(set)
        for tag in cat["tags"]:
            tag_id = tag["tag_id"]
            observed_ids.add(tag_id)
            if not tag_id.startswith(group + "."):
                errors.append(f"tag prefix mismatch: {tag_id}")
            for term in [tag.get("label_ko"), tag.get("label_en"), *(tag.get("aliases") or [])]:
                if term:
                    aliases[term.casefold().strip()].add(tag_id)
        for term, associated_ids in aliases.items():
            if len(associated_ids) > 1:
                errors.append(f"ambiguous alias {group}: {term}")
    actual_p0 = {c["id"] for c in categories if c.get("phase") == "P0"}
    if actual_p0 != P0:
        errors.append(f"P0 facet mismatch: {actual_p0}")
    if {c["id"] for c in categories if c.get("phase") == "P1"} != ALL - P0:
        errors.append("P1 facet mismatch")
    rule_ids = set(rules.get("criteria_by_tag", {}))
    p0_tag_ids = {t["tag_id"] for c in categories if c["id"] in P0 for t in c["tags"]}
    if len(p0_tag_ids) != 84 or rule_ids != p0_tag_ids:
        errors.append("expected exactly 84 P0 tag rules with matching IDs")
    if any(not (entry.get("criterion_ko") or "").strip() for entry in rules.get("criteria_by_tag", {}).values()):
        errors.append("missing P0 criterion")
    if len(rules.get("pairwise_rules", [])) != 10:
        errors.append("expected 10 ambiguity rules")
    if new.get("version") != rules.get("version") or new.get("version") != "1.1.0":
        errors.append("schema/rules version mismatch")
    if set(new.get("tag_result_contract", {}).get("status_values", [])) != STATUSES:
        errors.append("four-state contract mismatch")
    if "not_observed" in new.get("tag_result_contract", {}).get("status_values", []):
        errors.append("ambiguous legacy status not allowed")
    return errors


def check_result(data: dict) -> list[str]:
    """Validate structure, not visual-semantic truth or model accuracy."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ['tagging result must be a JSON object']
    try:
        dictionary = load(TAXONOMY)
        allowed_by_facet = {
            cat["id"]: {tag["tag_id"] for tag in cat["tags"]}
            for cat in dictionary["categories"]
        }
    except (OSError, ValueError, KeyError) as exc:
        return [f"cannot load dictionary: {exc}"]

    for key in ("post_id", "media_id", "taxonomy_version", "model_id", "prompt_version"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"missing/invalid {key}")
    if data.get("taxonomy_version") != "1.1.0":
        errors.append("wrong taxonomy_version")
    if data.get("schema_version") not in (None, "analyzer_tag_result_v0_1"):
        errors.append("unsupported schema_version")
    if data.get("is_nail_design") is not True:
        errors.append("non-nail/unavailable input must use job-level result instead")
    if data.get("review_status") not in ("unreviewed", "approved", "corrected", "rejected"):
        errors.append("invalid review_status")
    if not isinstance(data.get("source_provenance"), dict) or not data["source_provenance"]:
        errors.append("source_provenance required")
    fingerprint = data.get("analysis_input_hash")
    if not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", fingerprint):
        errors.append("analysis_input_hash must be a SHA-256 hex digest")
    try:
        analyzed_at = data.get("analyzed_at", "")
        parsed = datetime.fromisoformat(analyzed_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("naive time")
    except (ValueError, TypeError, AttributeError):
        errors.append("analyzed_at must have a timezone")
    rows = data.get("facet_results")
    if not isinstance(rows, list) or len(rows) != 14:
        return errors + ["successful P0 output requires exactly 14 facet_results"]
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"facet row {index} is not an object")
            continue
        facet = row.get("facet_id")
        if not isinstance(facet, str) or facet not in ALL:
            errors.append(f"unknown facet {facet}")
            continue
        if facet in seen:
            errors.append(f"duplicate facet row {facet}")
        seen.add(facet)
        status = row.get("status")
        tag_ids = row.get("tag_ids")
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(f"invalid status {facet}: {status}")
            continue
        if not isinstance(tag_ids, list) or any(not isinstance(x, str) for x in tag_ids):
            errors.append(f"invalid tag_ids {facet}")
            continue
        if len(tag_ids) != len(set(tag_ids)):
            errors.append(f"duplicate tags {facet}")
        if any(tag not in allowed_by_facet[facet] for tag in tag_ids):
            errors.append(f"unknown/mismatched tag IDs {facet}")
        if status == "observed" and not tag_ids:
            errors.append(f"observed requires tags {facet}")
        if status != "observed" and tag_ids:
            errors.append(f"{status} requires no tags {facet}")
        if facet in P0 and status == "not_evaluated":
            errors.append(f"P0 facet cannot be skipped {facet}")
        if facet not in P0 and status != "not_evaluated":
            errors.append(f"P1 facet cannot be assessed in P0 run {facet}")
        confidence = row.get("confidence")
        if confidence is not None and (
            isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not 0 <= confidence <= 1
        ):
            errors.append(f"confidence out of range {facet}")
        source = row.get("evidence_source")
        note = row.get("evidence_note")
        if status == "observed" and (
            source not in EVIDENCE or not isinstance(note, str) or not note.strip()
        ):
            errors.append(f"observed requires evidence source and explanation {facet}")
        if status == "unknown" and (not isinstance(note, str) or not note.strip()):
            errors.append(f"unknown requires abstention reason {facet}")
        if status == "not_applicable" and (not isinstance(note, str) or not note.strip()):
            errors.append(f"not_applicable requires a visible-scope reason {facet}")
        if status == "not_evaluated" and (source is not None or confidence is not None or note not in (None, "")):
            errors.append(f"not_evaluated cannot assert evidence/confidence {facet}")
    if seen != ALL:
        errors.append(f"facet coverage mismatch: missing {sorted(ALL - seen)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, help="Path to one synthetic or authorized analyzed result JSON")
    args = parser.parse_args()
    problems = check_dictionary()
    if args.result:
        try:
            problems.extend(check_result(load(args.result)))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"cannot load result: {exc}")
    if problems:
        for issue in problems:
            print("FAIL:", issue, file=sys.stderr)
        return 1
    print("PASS: 14 facets, 159 immutable tags, 84 P0 rules, 10 ambiguity rules, 4 statuses")
    if args.result:
        print("PASS: P0 tagging-result contract; this does not test AI visual accuracy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

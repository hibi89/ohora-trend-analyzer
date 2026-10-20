#!/usr/bin/env python3
"""Strict offline validator for compact 7-facet VLM output, NOT DERIVED DB records.

Run from repository root:
    python -m scripts.validate_model_output --input fixtures/sample_p0_model_output.json
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from scripts.validate_taxonomy import TAXONOMY, P0, load

FACET_STATUSES = {"observed", "unknown", "not_applicable"}
VISUAL_SOURCES = {"image", "both"}
KNOWN_SOURCES = VISUAL_SOURCES | {"caption"}
FACET_KEYS = {"facet_id", "status", "tag_ids", "evidence_source", "evidence_note", "scope"}
ROOT_KEYS = {"is_nail_design", "facets", "reason"}


def validate_model_output(result: object) -> list[str]:
    """Reject malformed/unsupported model suggestions before normalization.

    This validates shape and vocabulary, not whether pixels justify a visual claim.
    """
    errors: list[str] = []
    if not isinstance(result, dict):
        return ["model output must be a JSON object"]
    if set(result) - ROOT_KEYS:
        errors.append(f"unexpected model fields: {sorted(set(result) - ROOT_KEYS)}")
    if type(result.get("is_nail_design")) is not bool:
        return errors + ["is_nail_design must be a JSON boolean"]
    facets = result.get("facets")
    if result["is_nail_design"] is False:
        if facets != []:
            errors.append("non-nail result must have empty facets")
        reason = result.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append("non-nail result requires a reason")
        return errors
    if not isinstance(facets, list) or len(facets) != 7:
        return errors + ["nail result must have exactly seven P0 facets"]

    dictionary = load(TAXONOMY)
    allowed = {
        cat["id"]: {tag["tag_id"] for tag in cat["tags"]}
        for cat in dictionary["categories"] if cat["id"] in P0
    }
    seen: set[str] = set()
    for i, facet in enumerate(facets):
        if not isinstance(facet, dict):
            errors.append(f"facet[{i}] must be a JSON object")
            continue
        unexpected = set(facet) - FACET_KEYS
        if unexpected:
            errors.append(f"facet[{i}] unexpected keys: {sorted(unexpected)}")
        facet_id = facet.get("facet_id")
        if not isinstance(facet_id, str) or facet_id not in P0:
            errors.append(f"facet[{i}] unknown or P1 facet: {facet_id}")
            continue
        if facet_id in seen:
            errors.append(f"duplicate facet_id {facet_id}")
        seen.add(facet_id)
        status = facet.get("status")
        if not isinstance(status, str) or status not in FACET_STATUSES:
            errors.append(f"{facet_id}: invalid or unevaluated status")
            continue
        tag_ids = facet.get("tag_ids")
        if not isinstance(tag_ids, list) or any(not isinstance(x, str) for x in tag_ids):
            errors.append(f"{facet_id}: tag_ids must be string list")
            continue
        if len(set(tag_ids)) != len(tag_ids):
            errors.append(f"{facet_id}: duplicate tag IDs")
        if any(tag not in allowed[facet_id] for tag in tag_ids):
            errors.append(f"{facet_id}: unknown or wrong-facet tag")
        if status == "observed" and not tag_ids:
            errors.append(f"{facet_id}: observed requires tags")
        if status != "observed" and tag_ids:
            errors.append(f"{facet_id}: non-observed status cannot have tags")
        source = facet.get("evidence_source")
        if source is not None and (not isinstance(source, str) or source not in KNOWN_SOURCES):
            errors.append(f"{facet_id}: bad evidence source")
        if status == "observed" and (not isinstance(source, str) or source not in VISUAL_SOURCES):
            errors.append(f"{facet_id}: visual tag requires image evidence")
        note = facet.get("evidence_note")
        if not isinstance(note, str) or not note.strip() or len(note) > 300:
            errors.append(f"{facet_id}: evidence_note required (max 300 chars)")
        scope = facet.get("scope")
        if scope is not None and (not isinstance(scope, str) or len(scope) > 120):
            errors.append(f"{facet_id}: invalid scope")
        if status == "not_applicable" and (not isinstance(scope, str) or not scope.strip()):
            errors.append(f"{facet_id}: not_applicable requires visible scope")
        if status == "not_applicable" and (not isinstance(source, str) or source not in VISUAL_SOURCES):
            errors.append(f"{facet_id}: not_applicable requires image evidence")
    if seen != P0:
        errors.append(f"missing P0 facets: {sorted(P0 - seen)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        data = load(args.input)
        problems = validate_model_output(data)
    except (OSError, ValueError) as exc:
        problems = [f"cannot read strict JSON: {exc}"]
    for problem in problems:
        print("FAIL:", problem, file=sys.stderr)
    if problems:
        return 1
    print("PASS: seven P0 facet model-output contract (synthetic structure only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

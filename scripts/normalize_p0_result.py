#!/usr/bin/env python3
"""Pure offline conversion: validated seven-facet VLM proposal -> DERIVED 14-facet result.

No network, Meta API, P6 RAW DB or derived DB writes.
Source IDs, model/prompt version and timestamps must come from trusted runner input.
"""
from __future__ import annotations

from scripts.validate_model_output import validate_model_output
from scripts.validate_taxonomy import ALL, P0, check_result

TRUSTED_REQUIRED = (
    "post_id", "media_id", "model_id", "prompt_version",
    "analyzed_at", "analysis_input_hash", "source_provenance",
)
P1 = ALL - P0


def normalize_p0_output(model_output: dict, trusted: dict) -> dict:
    """Transform a verified VLM suggestion; raise ValueError on any invalid input.

    A non-nail result is a job-level decision and MUST NOT create 14 fake tags.
    """
    violations = validate_model_output(model_output)
    if violations:
        raise ValueError("untrusted model output: " + "; ".join(violations))
    if not isinstance(trusted, dict):
        raise ValueError("trusted execution metadata must be a dict")
    missing = [field for field in TRUSTED_REQUIRED if field not in trusted]
    if missing:
        raise ValueError("missing trusted fields: " + ", ".join(missing))
    observation_id = trusted.get("source_observation_id")
    if observation_id is not None and (not isinstance(observation_id, str) or not observation_id.strip()):
        raise ValueError("source_observation_id must be a non-empty string or null")
    if model_output["is_nail_design"] is False:
        return {
            "job_status": "non_nail",
            "source_post_id": trusted["post_id"],
            "source_media_id": trusted["media_id"],
            "reason": model_output["reason"],
        }

    results = []
    from_model = {row["facet_id"]: row for row in model_output["facets"]}
    for facet in sorted(ALL):
        if facet in P1:
            results.append({
                "facet_id": facet, "status": "not_evaluated", "tag_ids": [],
                "confidence": None, "evidence_source": None, "evidence_note": None,
                "scope": None,
            })
            continue
        suggestion = from_model[facet]
        results.append({
            "facet_id": facet,
            "status": suggestion["status"],
            "tag_ids": list(suggestion["tag_ids"]),
            "confidence": None,  # never fabricate confidence from text
            "evidence_source": suggestion.get("evidence_source"),
            "evidence_note": suggestion["evidence_note"],
            "scope": suggestion.get("scope"),
        })

    output = {
        "schema_version": "analyzer_tag_result_v0_1",
        "post_id": trusted["post_id"],
        "media_id": trusted["media_id"],
        "taxonomy_version": "1.1.0",
        "model_id": trusted["model_id"],
        "prompt_version": trusted["prompt_version"],
        "analyzed_at": trusted["analyzed_at"],
        "analysis_input_hash": trusted["analysis_input_hash"],
        "is_nail_design": True,
        "review_status": "unreviewed",
        "source_provenance": trusted["source_provenance"],
        "facet_results": results,
        "structure": {"S01": None, "S02": None, "S03": None, "S04": None},
    }
    if trusted.get("source_observation_id") is not None:
        output["source_observation_id"] = trusted["source_observation_id"]
    errors = check_result(output)
    if errors:
        raise ValueError("normalized tagging result is invalid: " + "; ".join(errors))
    return output

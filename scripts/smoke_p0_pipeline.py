#!/usr/bin/env python3
"""Run a complete offline P0 model-output -> 14-facet normalized result smoke check.

Synthetic inputs only by default. No Meta requests, n8n calls, AI charges,
database writes or image processing. Use this before connecting n8n.

Examples:
  python -m scripts.smoke_p0_pipeline
  python -m scripts.smoke_p0_pipeline --print-result
  python -m scripts.smoke_p0_pipeline --model-output fixtures/sample_p0_model_output.json --trusted-context fixtures/sample_trusted_execution_context.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

from scripts.normalize_p0_result import normalize_p0_output
from scripts.validate_taxonomy import ROOT, check_dictionary, check_result, load

DEFAULT_MODEL = ROOT / "fixtures" / "sample_p0_model_output.json"
DEFAULT_TRUSTED = ROOT / "fixtures" / "sample_trusted_execution_context.json"
NORMALIZED_SCHEMA = ROOT / "taxonomy" / "p0_tag_result.schema.json"


def smoke(model_path: Path, trusted_path: Path) -> dict:
    """Execute pure contracts and return normalized synthetic result or raise ValueError."""
    try:
        integrity_errors = check_dictionary()
        if integrity_errors:
            raise ValueError("taxonomy integrity failed: " + "; ".join(integrity_errors))

        schema = load(NORMALIZED_SCHEMA)
        Draft202012Validator.check_schema(schema)
        proposed = load(model_path)
        trusted = load(trusted_path)
        normalized = normalize_p0_output(proposed, trusted)
        if normalized.get("job_status") == "non_nail":
            raise ValueError("non-nail is a job-level outcome, not a successful tagging sample")
        errors = check_result(normalized)
        if errors:
            raise ValueError("Python P0 validator rejected result: " + "; ".join(errors))
        schema_errors = list(Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(normalized))
        if schema_errors:
            raise ValueError("JSON Schema rejected normalized result: " +
                             "; ".join(err.message for err in schema_errors))
        return normalized
    except (OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"smoke input or normalization failure: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-output", type=Path, default=DEFAULT_MODEL,
                        help="Strict JSON model-like 7-facet result. Default synthetic.")
    parser.add_argument("--trusted-context", type=Path, default=DEFAULT_TRUSTED,
                        help="Trusted execution metadata. Default synthetic.")
    parser.add_argument("--print-result", action="store_true",
                        help="Emit normalized JSON from trusted/synthetic input (no file writes).")
    args = parser.parse_args()
    try:
        result = smoke(args.model_output, args.trusted_context)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.print_result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS: synthetic P0 seven-facet proposal -> trusted normalization -> "
              "14-facet Python and JSON Schema validation; no AI, n8n or DB activity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

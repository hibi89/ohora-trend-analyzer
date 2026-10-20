"""Pure synthetic trusted-normalization test suite. No live API, no database."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.normalize_p0_result import normalize_p0_output
from scripts.validate_taxonomy import check_result

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "taxonomy" / "p0_tag_result.schema.json").read_text(encoding="utf-8"))
SCHEMA_CHECK = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def model_sample():
    return {
        "is_nail_design": True,
        "facets": [
            {"facet_id": fid, "status": "unknown", "tag_ids": [],
             "evidence_source": None, "evidence_note": "Synthetic: visual evidence uncertain",
             "scope": "visible nails"}
            for fid in ("F01", "F03", "F05", "F06", "F08", "F09", "F10")
        ],
    }


def trusted():
    return {
        "post_id": "SYNTHETIC_POST",
        "media_id": "SYNTHETIC_MEDIA",
        "model_id": "synthetic-model",
        "prompt_version": "prompt-v1.1",
        "analyzed_at": "2026-10-20T17:00:00+09:00",
        "analysis_input_hash": "a" * 64,
        "source_provenance": {"origin": "synthetic_fixture"},
        "source_observation_id": "SYNTHETIC_OBS",
    }


class TestNormalizeP0(unittest.TestCase):
    def test_normalized_passes_both_contracts(self):
        normalized = normalize_p0_output(model_sample(), trusted())
        self.assertEqual(check_result(normalized), [])
        self.assertEqual(list(SCHEMA_CHECK.iter_errors(normalized)), [])

    def test_14_facets_exactly_once(self):
        output = normalize_p0_output(model_sample(), trusted())
        self.assertEqual({x["facet_id"] for x in output["facet_results"]},
                         {f"F{i:02d}" for i in range(1, 15)})
        self.assertEqual(len(output["facet_results"]), 14)

    def test_seven_p1_explicitly_unevaluated(self):
        output = normalize_p0_output(model_sample(), trusted())
        p1 = {"F02", "F04", "F07", "F11", "F12", "F13", "F14"}
        for facet in output["facet_results"]:
            if facet["facet_id"] in p1:
                self.assertEqual(facet["status"], "not_evaluated")
                self.assertEqual(facet["tag_ids"], [])
                self.assertIsNone(facet["evidence_source"])
                self.assertIsNone(facet["scope"])

    def test_observed_visual_tag_kept(self):
        input_model = model_sample()
        input_model["facets"][0].update(
            status="observed", tag_ids=["F01.pink"],
            evidence_source="image", evidence_note="Fictional pink nail")
        output = normalize_p0_output(input_model, trusted())
        self.assertEqual(output["facet_results"][0]["tag_ids"], ["F01.pink"])
        self.assertEqual(list(SCHEMA_CHECK.iter_errors(output)), [])

    def test_model_cannot_spoof_trusted_post_id(self):
        data = model_sample()
        data["post_id"] = "UNTRUSTED_META_ID"
        with self.assertRaisesRegex(ValueError, "untrusted model output"):
            normalize_p0_output(data, trusted())

    def test_trusted_source_ids_preserved(self):
        output = normalize_p0_output(model_sample(), trusted())
        self.assertEqual(output["post_id"], "SYNTHETIC_POST")
        self.assertEqual(output["media_id"], "SYNTHETIC_MEDIA")
        self.assertEqual(output["source_observation_id"], "SYNTHETIC_OBS")

    def test_non_nail_is_job_state_without_facet_result(self):
        data = {"is_nail_design": False, "facets": [], "reason": "no nails in image"}
        output = normalize_p0_output(data, trusted())
        self.assertEqual(output["job_status"], "non_nail")
        self.assertNotIn("facet_results", output)

    def test_reject_unknown_tag(self):
        data = model_sample()
        data["facets"][0].update(
            status="observed", tag_ids=["F01.magic"],
            evidence_source="image", evidence_note="Fictional")
        with self.assertRaisesRegex(ValueError, "untrusted model output"):
            normalize_p0_output(data, trusted())

    def test_reject_missing_trusted_field(self):
        metadata = trusted()
        metadata.pop("model_id")
        with self.assertRaisesRegex(ValueError, "missing trusted fields"):
            normalize_p0_output(model_sample(), metadata)

    def test_reject_bad_trusted_input_hash(self):
        metadata = trusted()
        metadata["analysis_input_hash"] = "not-a-sha"
        with self.assertRaisesRegex(ValueError, "normalized tagging result is invalid"):
            normalize_p0_output(model_sample(), metadata)

    def test_default_confidence_is_null(self):
        result = normalize_p0_output(model_sample(), trusted())
        self.assertTrue(all(row["confidence"] is None for row in result["facet_results"]))

    def test_deterministic_synthetic_result(self):
        self.assertEqual(normalize_p0_output(model_sample(), trusted()),
                         normalize_p0_output(model_sample(), trusted()))


if __name__ == "__main__":
    unittest.main()

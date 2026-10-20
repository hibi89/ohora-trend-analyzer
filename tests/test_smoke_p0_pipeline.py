"""Run the actual offline smoke function on synthetic GitHub-tracked fixtures."""
import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.smoke_p0_pipeline import DEFAULT_MODEL, DEFAULT_TRUSTED, smoke
from scripts.validate_taxonomy import load
import json


class TestSyntheticP0Smoke(unittest.TestCase):
    def test_default_synthetic_pipeline(self):
        output = smoke(DEFAULT_MODEL, DEFAULT_TRUSTED)
        self.assertEqual(len(output["facet_results"]), 14)
        self.assertEqual(output["taxonomy_version"], "1.1.0")
        self.assertEqual(output["source_provenance"]["origin"], "synthetic_fixture")

    def test_source_ids_from_trusted_input(self):
        output = smoke(DEFAULT_MODEL, DEFAULT_TRUSTED)
        trusted = load(DEFAULT_TRUSTED)
        self.assertEqual(output["post_id"], trusted["post_id"])
        self.assertEqual(output["media_id"], trusted["media_id"])

    def test_reject_fabricated_model_tag(self):
        with TemporaryDirectory() as tmp:
            model = copy.deepcopy(load(DEFAULT_MODEL))
            model["facets"][0].update(status="observed", tag_ids=["F01.future_unknown_tag"],
                                      evidence_source="image", evidence_note="synthetic image")
            path = Path(tmp) / "model.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "untrusted model output"):
                smoke(path, DEFAULT_TRUSTED)

    def test_reject_bad_trusted_metadata(self):
        with TemporaryDirectory() as tmp:
            context = copy.deepcopy(load(DEFAULT_TRUSTED))
            context["analyzed_at"] = "2026-10-20"  # timezone missing
            path = Path(tmp) / "trusted.json"
            path.write_text(json.dumps(context), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "normalized tagging result is invalid"):
                smoke(DEFAULT_MODEL, path)

    def test_reject_non_nail_fake_success(self):
        with TemporaryDirectory() as tmp:
            model = {"is_nail_design": False, "facets": [], "reason": "No nail visible"}
            path = Path(tmp) / "model.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "job-level outcome"):
                smoke(path, DEFAULT_TRUSTED)


if __name__ == "__main__":
    unittest.main()

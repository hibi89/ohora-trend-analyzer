"""JSON Schema contract tests for normalized DERIVED tagging result; no live I/O."""
from copy import deepcopy
from pathlib import Path
import json
import unittest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "taxonomy" / "p0_tag_result.schema.json").read_text(encoding="utf-8"))
SAMPLE = json.loads((ROOT / "fixtures" / "sample_valid_tag_result.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


class TestJsonSchemaContract(unittest.TestCase):
    def assert_invalid(self, update):
        data = deepcopy(SAMPLE)
        update(data)
        self.assertTrue(list(VALIDATOR.iter_errors(data)))

    def test_schema_itself_is_valid(self):
        Draft202012Validator.check_schema(SCHEMA)

    def test_valid_synthetic_sample(self):
        self.assertEqual(list(VALIDATOR.iter_errors(SAMPLE)), [])

    def test_reject_duplicate_facet(self):
        self.assert_invalid(lambda d: d["facet_results"][1].update(facet_id="F01"))

    def test_reject_wrong_facet_tag(self):
        self.assert_invalid(lambda d: d["facet_results"][0].update(
            status="observed", tag_ids=["F09.ribbon"], evidence_source="image", evidence_note="synthetic"))

    def test_reject_skipped_p0(self):
        self.assert_invalid(lambda d: d["facet_results"][0].update(status="not_evaluated"))

    def test_reject_fake_p1_result(self):
        self.assert_invalid(lambda d: d["facet_results"][1].update(
            status="observed", tag_ids=["F02.pastel"], evidence_source="image", evidence_note="synthetic"))

    def test_reject_observed_without_evidence(self):
        self.assert_invalid(lambda d: d["facet_results"][0].update(
            status="observed", tag_ids=["F01.pink"]))

    def test_reject_not_applicable_without_reason(self):
        self.assert_invalid(lambda d: d["facet_results"][0].update(
            status="not_applicable", evidence_note=None))

    def test_accept_not_applicable_with_reason(self):
        data = deepcopy(SAMPLE)
        data["facet_results"][0].update(
            status="not_applicable", evidence_source="image", scope="whole nail visible", evidence_note="Synthetic full visible nail area is colorless")
        self.assertEqual(list(VALIDATOR.iter_errors(data)), [])

    def test_reject_no_visual_input_as_success(self):
        self.assert_invalid(lambda d: d.update(is_nail_design=False))

    def test_reject_invalid_sha(self):
        self.assert_invalid(lambda d: d.update(analysis_input_hash="foo"))

    def test_reject_unzoned_date(self):
        self.assert_invalid(lambda d: d.update(analyzed_at="2026-10-20T17:00:00"))

    def test_reject_extra_undeclared_property(self):
        self.assert_invalid(lambda d: d.update(unrecognized_field=123))

    def test_reject_facets_missing(self):
        self.assert_invalid(lambda d: d["facet_results"].pop())


    def test_reject_missing_required_schema_version(self):
        self.assert_invalid(lambda d: d.pop("schema_version"))

    def test_reject_undeclared_facet_property(self):
        self.assert_invalid(lambda d: d["facet_results"][0].update(undeclared="value"))

    def test_reject_not_evaluated_scope_claim(self):
        self.assert_invalid(lambda d: d["facet_results"][1].update(scope="visible_nails"))

    def test_reject_not_evaluated_blank_note(self):
        self.assert_invalid(lambda d: d["facet_results"][1].update(evidence_note=""))

    def test_reject_observed_untrusted_evidence_source(self):
        self.assert_invalid(lambda d: d["facet_results"][0].update(
            status="observed", tag_ids=["F01.pink"], evidence_source={"image": True},
            evidence_note="synthetic"))

    def test_reject_unknown_bad_scope_type(self):
        self.assert_invalid(lambda d: d["facet_results"][0].update(scope=["nails"]))



    def test_reject_caption_only_observed_tag(self):
        self.assert_invalid(lambda d: d["facet_results"][0].update(
            status="observed", tag_ids=["F01.pink"], evidence_source="caption",
            evidence_note="caption claims color"))

    def test_reject_missing_visible_scope_for_absence(self):
        self.assert_invalid(lambda d: d["facet_results"][9].update(
            status="not_applicable", evidence_source="image",
            evidence_note="Entire visible nail area has no ornament", scope=None))

    def test_reject_caption_only_absence(self):
        self.assert_invalid(lambda d: d["facet_results"][9].update(
            status="not_applicable", evidence_source="caption",
            evidence_note="caption claims no ornament", scope="whole nail visible"))


if __name__ == "__main__":
    unittest.main()

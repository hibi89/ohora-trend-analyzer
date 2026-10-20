"""Synthetic unit tests only: no Meta, no VLM, no database."""
import copy
import unittest

from scripts.validate_taxonomy import ALL, P0, check_dictionary, check_result


def sample():
    return {
        "schema_version": "analyzer_tag_result_v0_1",
        "post_id": "SYNTHETIC_POST",
        "media_id": "SYNTHETIC_CHILD_IMAGE",
        "taxonomy_version": "1.1.0",
        "model_id": "synthetic-test",
        "prompt_version": "p0-contract-1",
        "analyzed_at": "2026-10-20T16:00:00+09:00",
        "analysis_input_hash": "a" * 64,
        "is_nail_design": True,
        "review_status": "unreviewed",
        "source_provenance": {"origin": "synthetic_fixture"},
        "facet_results": [
            {
                "facet_id": facet,
                "status": "unknown" if facet in P0 else "not_evaluated",
                "tag_ids": [],
                "confidence": None,
                "evidence_source": None,
                "evidence_note": "Synthetic sample: no visual assertion" if facet in P0 else None,
            }
            for facet in sorted(ALL)
        ],
    }


def row(data, facet):
    return next(x for x in data["facet_results"] if x["facet_id"] == facet)


class TestTaggingContract(unittest.TestCase):
    def test_dictionary_unmodified_159(self):
        self.assertEqual(check_dictionary(), [])

    def test_valid_synthetic_sample(self):
        self.assertEqual(check_result(sample()), [])

    def test_valid_observed(self):
        x = sample()
        f = row(x, "F01")
        f.update(status="observed", tag_ids=["F01.pink"], confidence=0.75,
                 evidence_source="image", evidence_note="Synthetic example pink area")
        self.assertEqual(check_result(x), [])

    def test_reject_wrong_facet_tag(self):
        x = sample()
        row(x, "F01").update(status="observed", tag_ids=["F05.cat_eye"],
                              evidence_source="image", evidence_note="Synthetic example")
        self.assertTrue(any("mismatched" in e for e in check_result(x)))

    def test_reject_hallucinated_tag(self):
        x = sample()
        row(x, "F05").update(status="observed", tag_ids=["F05.unknown_magic"],
                              evidence_source="image", evidence_note="Synthetic example")
        self.assertTrue(check_result(x))

    def test_reject_unknown_with_tags(self):
        x = sample()
        row(x, "F01")["tag_ids"] = ["F01.pink"]
        self.assertTrue(check_result(x))

    def test_reject_observed_without_evidence(self):
        x = sample()
        row(x, "F01").update(status="observed", tag_ids=["F01.pink"])
        self.assertTrue(any("evidence" in e for e in check_result(x)))

    def test_reject_skipped_p0(self):
        x = sample()
        row(x, "F01").update(status="not_evaluated", evidence_note=None)
        self.assertTrue(any("P0 facet" in e for e in check_result(x)))

    def test_reject_evaluated_p1(self):
        x = sample()
        row(x, "F13").update(status="unknown", evidence_note="unsupported mood")
        self.assertTrue(any("P1 facet" in e for e in check_result(x)))

    def test_reject_duplicate_facet(self):
        x = sample()
        x["facet_results"][1] = copy.deepcopy(x["facet_results"][0])
        self.assertTrue(any("duplicate facet" in e for e in check_result(x)))

    def test_reject_partial_facet_response(self):
        x = sample()
        x["facet_results"].pop()
        self.assertTrue(any("exactly 14" in e for e in check_result(x)))

    def test_reject_boolean_confidence(self):
        x = sample()
        row(x, "F01")["confidence"] = True
        self.assertTrue(any("confidence" in e for e in check_result(x)))

    def test_reject_unzoned_datetime(self):
        x = sample()
        x["analyzed_at"] = "2026-10-20T16:00:00"
        self.assertTrue(any("timezone" in e for e in check_result(x)))

    def test_reject_bad_fingerprint(self):
        x = sample()
        x["analysis_input_hash"] = "not-a-sha"
        self.assertTrue(any("SHA-256" in e for e in check_result(x)))

    def test_reject_non_nail_job_as_success(self):
        x = sample()
        x["is_nail_design"] = False
        self.assertTrue(any("job-level" in e for e in check_result(x)))

    def test_reject_legacy_not_observed(self):
        x = sample()
        row(x, "F01")["status"] = "not_observed"
        self.assertTrue(any("invalid status" in e for e in check_result(x)))


    def test_reject_non_object_result(self):
        self.assertTrue(any("JSON object" in e for e in check_result(["not", "a", "dict"])))

    def test_reject_array_facet_id_gracefully(self):
        x = sample()
        x["facet_results"][0]["facet_id"] = ["F01"]
        self.assertTrue(any("unknown facet" in e for e in check_result(x)))

    def test_reject_dict_status_gracefully(self):
        x = sample()
        row(x, "F01")["status"] = {"observed": True}
        self.assertTrue(any("invalid status" in e for e in check_result(x)))

    def test_reject_not_applicable_without_reason(self):
        x = sample()
        row(x, "F10").update(status="not_applicable", evidence_note=None)
        self.assertTrue(any("visible-scope reason" in e for e in check_result(x)))

    def test_accept_not_applicable_with_reason(self):
        x = sample()
        row(x, "F10").update(status="not_applicable", evidence_note="Entire synthetic nail area visible; no raised decoration")
        self.assertEqual(check_result(x), [])

    def test_reject_not_evaluated_with_claim(self):
        x = sample()
        row(x, "F13")["evidence_note"] = "glamorous despite being unevaluated"
        self.assertTrue(any("cannot assert" in e for e in check_result(x)))


if __name__ == "__main__":
    unittest.main()

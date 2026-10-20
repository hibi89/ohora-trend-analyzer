"""Synthetic 7-facet model-output validation cases; no model/API/database calls."""
import copy
import unittest

from scripts.validate_model_output import validate_model_output


FACETS = ["F01", "F03", "F05", "F06", "F08", "F09", "F10"]


def sample():
    return {
        "is_nail_design": True,
        "facets": [
            {
                "facet_id": code,
                "status": "unknown",
                "tag_ids": [],
                "evidence_source": None,
                "evidence_note": "Synthetic test: not enough visible evidence",
                "scope": "synthetic visible nail area",
            }
            for code in FACETS
        ],
    }


def row(x, facet):
    return next(a for a in x["facets"] if a["facet_id"] == facet)


class TestModelOutputContract(unittest.TestCase):
    def test_valid_unknown_p0_facets(self):
        self.assertEqual(validate_model_output(sample()), [])

    def test_valid_visual_tag(self):
        x = sample()
        row(x, "F01").update(
            status="observed", tag_ids=["F01.pink"], evidence_source="image",
            evidence_note="Fictional pink image region",
        )
        self.assertEqual(validate_model_output(x), [])

    def test_valid_non_nail(self):
        self.assertEqual(validate_model_output({
            "is_nail_design": False, "facets": [], "reason": "no nail visible",
        }), [])

    def test_reject_untyped_result(self):
        self.assertTrue(validate_model_output(["not", "json", "object"]))

    def test_reject_wrong_boolean_type(self):
        x = sample()
        x["is_nail_design"] = "true"
        self.assertTrue(validate_model_output(x))

    def test_reject_legacy_missing_facet(self):
        x = sample()
        x["facets"].pop()
        self.assertTrue(validate_model_output(x))

    def test_reject_duplicate_facet(self):
        x = sample()
        x["facets"][1]["facet_id"] = "F01"
        self.assertTrue(any("duplicate facet_id" in e for e in validate_model_output(x)))

    def test_reject_unexpected_metadata(self):
        x = sample()
        x["post_id"] = "hallucinated-by-model"
        self.assertTrue(any("unexpected model fields" in e for e in validate_model_output(x)))

    def test_reject_p1_facet(self):
        x = sample()
        x["facets"][0]["facet_id"] = "F13"
        self.assertTrue(validate_model_output(x))

    def test_reject_unknown_tag(self):
        x = sample()
        row(x, "F01").update(
            status="observed", tag_ids=["F01.magic_nails"], evidence_source="image",
            evidence_note="fictional",
        )
        self.assertTrue(any("unknown or wrong-facet tag" in e for e in validate_model_output(x)))

    def test_reject_other_facet_tag(self):
        x = sample()
        row(x, "F01").update(
            status="observed", tag_ids=["F05.cat_eye"], evidence_source="image",
            evidence_note="fictional",
        )
        self.assertTrue(validate_model_output(x))

    def test_reject_unknown_with_tags(self):
        x = sample()
        row(x, "F01")["tag_ids"] = ["F01.pink"]
        self.assertTrue(validate_model_output(x))

    def test_reject_caption_only_visual_tag(self):
        x = sample()
        row(x, "F01").update(
            status="observed", tag_ids=["F01.pink"], evidence_source="caption",
            evidence_note="caption claims pink; image not visible",
        )
        self.assertTrue(any("requires image evidence" in e for e in validate_model_output(x)))

    def test_reject_not_applicable_without_scope(self):
        x = sample()
        row(x, "F10").update(status="not_applicable", scope=None)
        self.assertTrue(any("requires visible scope" in e for e in validate_model_output(x)))

    def test_accept_not_applicable_with_scope(self):
        x = sample()
        row(x, "F10").update(
            status="not_applicable", scope="all visible nails in image",
            evidence_note="All visible nails show no raised element",
        )
        self.assertEqual(validate_model_output(x), [])

    def test_reject_dict_evidence_without_crash(self):
        x = sample()
        row(x, "F01").update(
            status="observed", tag_ids=["F01.pink"], evidence_source={"image": True},
            evidence_note="synthetic",
        )
        self.assertTrue(any("bad evidence source" in e for e in validate_model_output(x)))

    def test_reject_non_nail_with_fake_facets(self):
        x = sample()
        x["is_nail_design"] = False
        x["reason"] = "not a nail"
        self.assertTrue(any("empty facets" in e for e in validate_model_output(x)))

    def test_reject_non_nail_without_reason(self):
        self.assertTrue(validate_model_output({"is_nail_design": False, "facets": []}))

    def test_reject_not_evaluated_in_p0(self):
        x = sample()
        row(x, "F01")["status"] = "not_evaluated"
        self.assertTrue(validate_model_output(x))

    def test_reject_extra_facet_field(self):
        x = sample()
        row(x, "F01")["product_sku"] = "fake"
        self.assertTrue(any("unexpected keys" in e for e in validate_model_output(x)))


if __name__ == "__main__":
    unittest.main()

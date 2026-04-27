import unittest

from pydantic import ValidationError

from reporter.models import (
    FundingMechanism,
    IncludeField,
    NIHAgency,
    SearchParams,
    StateCode,
    parse_include_fields,
)
from reporter.models.spending_categories import (
    SPENDING_CATEGORY_MAP_FY2024,
    is_valid_spending_category_id,
    get_spending_category_name,
)


class SpendingCategoriesTests(unittest.TestCase):
    def test_mapping_contains_known_ids(self):
        self.assertIn(27, SPENDING_CATEGORY_MAP_FY2024)
        self.assertEqual(
            SPENDING_CATEGORY_MAP_FY2024[27],
            "Adolescent Sexual Activity",
        )

    def test_validation_accepts_valid_ids(self):
        params = SearchParams(
            spending_categories={"values": [27, 31, 27], "match_all": False}
        )
        self.assertEqual(params.spending_categories.values, [27, 31])
        self.assertFalse(params.spending_categories.match_all)

    def test_validation_accepts_spending_category_names(self):
        params = SearchParams(
            spending_categories={"values": ["Aging", "31", 31], "match_all": False}
        )
        self.assertEqual(params.spending_categories.values, [31])

    def test_validation_rejects_invalid_ids(self):
        with self.assertRaises(ValidationError):
            SearchParams(spending_categories={"values": [27, 999999], "match_all": False})

    def test_to_api_criteria_serializes_spending_categories(self):
        params = SearchParams(
            years=[2024],
            spending_categories={"values": [27, 31], "match_all": True},
        )
        criteria = params.to_api_criteria()
        self.assertEqual(criteria["fiscal_years"], [2024])
        self.assertEqual(
            criteria["spending_categories"],
            {"values": [27, 31], "match_all": True},
        )

    def test_mapping_helpers(self):
        self.assertTrue(is_valid_spending_category_id(27))
        self.assertFalse(is_valid_spending_category_id(999999))
        self.assertEqual(get_spending_category_name(27), "Adolescent Sexual Activity")

    def test_enum_metadata_properties(self):
        self.assertEqual(NIHAgency.NCI.full_name, "National Cancer Institute")
        self.assertEqual(StateCode.PR.full_name, "Puerto Rico")
        self.assertEqual(
            FundingMechanism.SBIR_STTR_RESEARCH.description,
            "SBIR/STTR research grants",
        )
        self.assertEqual(IncludeField.AWARD_AMOUNT.description, "Award amount for the record.")

    def test_to_api_criteria_uses_singular_funding_mechanism_key(self):
        params = SearchParams(funding_mechanisms=["SB"])
        criteria = params.to_api_criteria()
        self.assertIn("funding_mechanism", criteria)
        self.assertEqual(criteria["funding_mechanism"], ["SB"])
        self.assertNotIn("funding_mechanisms", criteria)

    def test_single_agency_string_coerces_to_list(self):
        params = SearchParams(agencies="NIMHD")
        criteria = params.to_api_criteria()
        self.assertEqual(criteria["agencies"], ["NIMHD"])

    def test_parse_include_fields_accepts_names_and_values(self):
        parsed = parse_include_fields(["AWARD_AMOUNT", "ProjectNum"])
        self.assertEqual(parsed, [IncludeField.AWARD_AMOUNT, IncludeField.PROJECT_NUM])

    def test_parse_include_fields_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            parse_include_fields(["NOT_A_REAL_FIELD"])


if __name__ == "__main__":
    unittest.main()


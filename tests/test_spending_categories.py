import unittest

from pydantic import ValidationError

from reporter.models import SearchParams
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


if __name__ == "__main__":
    unittest.main()


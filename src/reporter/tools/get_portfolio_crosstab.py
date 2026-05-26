from reporter.utils import get_all_responses, build_crosstab, DIMENSION_FIELDS
from reporter.models import SearchParams, IncludeField
from fastmcp import Context


def register(mcp):
    @mcp.tool()
    async def get_portfolio_crosstab(
        ctx: Context,
        search_params: SearchParams,
        row_field: str,
        col_field: str,
    ):
        """
        Return a cross-tabulation of grant counts and total funding by any two project fields.

        Use this to generate stacked bar charts, heatmaps, or tables comparing any two
        dimensions of the portfolio (e.g. fiscal year x activity code, org state x funding mechanism).

        Args:
            search_params (SearchParams): Search parameters to scope the portfolio.
            row_field (str): Field to use as rows. Valid options:
                fiscal_year, activity_code, funding_mechanism, agency_ic_admin,
                org_name, org_state, organization_type, award_type
            col_field (str): Field to use as columns. Same valid options as row_field.

        Returns:
            dict: Nested dict of {row: {col: {"count": N, "total_funding": X}}}, sorted by row.
        """

        valid = list(DIMENSION_FIELDS.keys())
        if row_field not in DIMENSION_FIELDS:
            raise ValueError(f"Invalid row_field '{row_field}'. Valid options: {valid}")
        if col_field not in DIMENSION_FIELDS:
            raise ValueError(f"Invalid col_field '{col_field}'. Valid options: {valid}")

        # Deduplicate include fields (org_name and org_state both map to Organization)
        include_fields = list({
            DIMENSION_FIELDS[row_field].value,
            DIMENSION_FIELDS[col_field].value,
            IncludeField.AWARD_AMOUNT.value,
        })

        all_results = await get_all_responses(search_params, include_fields)
        return build_crosstab(all_results, row_field, col_field)

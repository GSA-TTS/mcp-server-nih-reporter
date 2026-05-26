from reporter.utils import get_initial_response, get_project_distributions
from reporter.models import SearchParams, IncludeField
from fastmcp import Context


def register(mcp):
    @mcp.tool()
    async def get_search_preview(
        ctx: Context,
        search_params: SearchParams,
    ):
        """
        Return key statistics about a search portfolio by sampling up to 500 projects.

        Use this tool first to quickly characterize a search — checking scope, funding levels,
        and portfolio composition — before committing to a full analysis with get_search_summary.
        Because it samples rather than pages through all results, it is fast but approximate for
        large portfolios.

        Args:
            search_params (SearchParams): Search parameters including search term, years, agencies, organizations, pi_name, po_names, award_types, and spending_categories.

        Returns:
            dict: Key statistics sampled from up to 500 matching projects:
            - total_projects: Total number of matching projects in the database (exact)
            - year_distribution: Breakdown of projects by fiscal year
            - institute_distribution: Top NIH institutes/centers by project count
            - activity_code_distribution: Top activity codes (R01, U01, etc.) by project count
            - organization_distribution: Top institutions by project count
            - funding_mechanism_distribution: Breakdown by funding mechanism
            - active_status_distribution: Active vs inactive project counts
            - award_amount_stats: Funding statistics (total, average, min, max) for the sample
            - pi_distribution: Top PIs by number of projects in the sample
            - pi_funding: Top PIs by total award dollars in the sample
        """

        # Get data with fields needed for distributions
        include_fields = [
            IncludeField.PROJECT_NUM.value,
            IncludeField.FISCAL_YEAR.value,
            IncludeField.AGENCY_IC_ADMIN.value,
            IncludeField.ACTIVITY_CODE.value,
            IncludeField.ORGANIZATION.value,
            IncludeField.FUNDING_MECHANISM.value,
            IncludeField.IS_ACTIVE.value,
            IncludeField.AWARD_AMOUNT.value,
            IncludeField.PRINCIPAL_INVESTIGATORS.value,
        ]

        # Get initial response (limit 500 for distribution sampling)
        limit = 500
        total_projects, all_results = await get_initial_response(
            search_params,
            include_fields,
            limit
        )

        distributions = get_project_distributions(all_results)

        return {
            "total_projects": total_projects,
            "year_distribution": dict(sorted(distributions["year_distribution"].items(), reverse=True)),
            "institute_distribution": dict(distributions["institute_distribution"].most_common(15)),
            "activity_code_distribution": dict(distributions["activity_code_distribution"].most_common(15)),
            "organization_distribution": dict(distributions["organization_distribution"].most_common(15)),
            "funding_mechanism_distribution": dict(distributions["funding_mechanism_distribution"].most_common()),
            "active_status_distribution": dict(distributions["active_status_distribution"]),
            "award_amount_stats": distributions["award_amount_stats"],
            "pi_distribution": dict(distributions["pi_distribution"].most_common(15)),
            "pi_funding": dict(distributions["pi_funding"].most_common(15)),
        }

from reporter.utils import get_all_responses, get_project_distributions
from reporter.models import SearchParams, IncludeField
from fastmcp import Context


def register(mcp):
    @mcp.tool()
    async def get_search_summary(
        ctx: Context,
        search_params: SearchParams,
    ):
        """
        Tool to get a comprehensive summary of ALL projects matching search criteria.

        Unlike get_search_preview (which samples the first 500 results for a quick preview),
        this tool fetches all matching projects to provide accurate, complete statistics.
        Use this when you need exact totals (e.g., "total funding for cancer research").

        When searching for terms, default to searching spending categories before using a 
        text search. Spending category labels are the official NIH designation for grants. 

        Note: This may be slower for large result sets as it pages through all results.

        Args:
            search_params (SearchParams): Search parameters including search term, years, agencies, organizations, pi_name, po_names, award_types, and spending_categories.

        Returns:
            dict: API response containing complete statistics:
            - total_projects: Total number of matching projects
            - year_distribution: Complete breakdown of projects by fiscal year
            - institute_distribution: Complete breakdown by NIH institute/center
            - activity_code_distribution: Complete breakdown by activity code (grant type)
            - organization_distribution: Complete breakdown by institution/organization
            - funding_mechanism_distribution: Complete breakdown by funding mechanism
            - active_status_distribution: Complete breakdown of active vs inactive projects
            - award_amount_stats: Complete funding statistics (total, average, min, max)
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

        # Fetch ALL results (pages through entire result set)
        all_results = await get_all_responses(
            search_params,
            include_fields,
        )

        distributions = get_project_distributions(all_results)
        total_projects = len(distributions["project_ids"])

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

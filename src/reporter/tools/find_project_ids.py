from reporter.utils import paged_query, get_project_distributions
from reporter.models import SearchParams, IncludeField
from fastmcp import Context


def register(mcp):
    @mcp.tool()
    async def find_project_ids(
        ctx: Context,
        search_params: SearchParams,
        offset: int = 0,
        limit: int = 500,
    ):
        """
        Tool to perform a search of the NIH RePORTER API and return project IDs based on search criteria.
        
        This is the primary search tool - use it to find grants matching your criteria.
        Returns project IDs for a single page of results so callers can paginate through
        large result sets.
        
        Args:
            search_params (SearchParams): Search parameters including search term, years, agencies, organizations, pi_name, po_names, award_types, and spending_categories.
            offset (int): Zero-based result offset for pagination.
            limit (int): Number of project IDs to return for this page (max 500).

        Returns:
            dict: API response containing:
            - total_projects: Total number of matching projects in database
            - returned_projects: Number of project IDs returned in this page
            - project_ids: List of project ID numbers
            - offset: Offset used for this page
            - limit: Limit used for this page
            - next_offset: Offset for the next page, or null if there are no more results
            - year_distribution: Breakdown of projects by fiscal year
            - institute_distribution: Breakdown by NIH institute/center
            - activity_code_distribution: Breakdown by activity code (grant type)
            - has_more_results: Whether additional projects exist beyond this page
        """

        if offset < 0:
            raise ValueError("offset must be >= 0")
        if limit < 1 or limit > 500:
            raise ValueError("limit must be between 1 and 500")
        
        # Get data with fields needed for distributions
        include_fields = [
            IncludeField.PROJECT_NUM.value,
            IncludeField.FISCAL_YEAR.value,
            IncludeField.AGENCY_IC_ADMIN.value,
            IncludeField.ACTIVITY_CODE.value,
        ]
        
        # Get the requested page of results
        total_projects, all_results = await paged_query(
            search_params,
            include_fields,
            limit=limit,
            offset=offset,
        )

        distributions = get_project_distributions(all_results)
        project_ids = distributions["project_ids"]
        next_offset = offset + len(project_ids) if total_projects > offset + len(project_ids) else None

        return {
            "total_projects": total_projects,
            "returned_projects": len(project_ids),
            "project_ids": project_ids,
            "offset": offset,
            "limit": limit,
            "next_offset": next_offset,
            "year_distribution": dict(sorted(distributions["year_distribution"].items(), reverse=True)),
            "institute_distribution": dict(distributions["institute_distribution"].most_common(15)),
            "activity_code_distribution": dict(distributions["activity_code_distribution"].most_common(15)),
            "has_more_results": next_offset is not None,
        }

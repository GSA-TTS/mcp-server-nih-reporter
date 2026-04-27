from typing import List
from reporter.utils import get_all_responses, get_initial_response, get_project_distributions, build_crosstab, DIMENSION_FIELDS, paged_query
from reporter.models import SearchParams, ProjectNum, IncludeField, parse_include_fields
from fastmcp import Context

def register_tools(mcp):
    @mcp.tool()
    async def search_projects(
        ctx: Context,
        search_params: SearchParams,
    ):
        """
        Tool to perform an initial search of the NIH RePORTER API and return the count of matching projects.

        Use this tool first to see how many projects match your search criteria before
        retrieving detailed results.

        Args:
            search_params (SearchParams): Search parameters including search term, years, agencies, organizations, pi_name, po_names, award_types, and spending_categories.

        Returns:
            dict: API response containing:
            - total_projects: Total number of matching projects in database
            - year_distribution: Breakdown of projects by fiscal year
            - institute_distribution: Breakdown by NIH institute/center
            - activity_code_distribution: Breakdown by activity code (grant type)
            - organization_distribution: Breakdown by institution/organization
            - funding_mechanism_distribution: Breakdown by funding mechanism
            - active_status_distribution: Breakdown of active vs inactive projects
            - award_amount_stats: Funding statistics (total, average, min, max)
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
        }

    @mcp.tool()
    async def get_search_summary(
        ctx: Context,
        search_params: SearchParams,
    ):
        """
        Tool to get a comprehensive summary of ALL projects matching search criteria.

        Unlike search_projects (which samples the first 500 results for a quick preview),
        this tool fetches all matching projects to provide accurate, complete statistics.
        Use this when you need exact totals (e.g., "total funding for cancer research").

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
        }

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
        
    @mcp.tool()
    async def get_project_information(
        project_ids: list[str],
        include_fields: List[str],
    ):
        """
        Tool to get specified metadata for a project based on project number.
        Use this to answer questions about award amounts, organizations, PIs, etc.

        Args:
            project_ids (list[str]): project ID numbers
            include_fields (List[str]): List of fields to return from the API.
                Choose fields relevant to the query (e.g., AWARD_AMOUNT for funding questions,
                PRINCIPAL_INVESTIGATORS for PI questions, ORGANIZATION for institution questions).

        Returns:
            dict: API response with specified project metadata
        """

        # add project_ids to a search_params object
        search_params = SearchParams(
            project_nums=[ProjectNum(project_num=p) for p in project_ids]
        )

        # Validate and convert include_fields strings to IncludeField enum values
        fields = parse_include_fields(include_fields)

        # Call the API
        return await get_all_responses(search_params, [f.value for f in fields])

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


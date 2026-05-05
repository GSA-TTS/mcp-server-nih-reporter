from typing import List
from reporter.utils import get_all_responses, get_initial_response, get_project_distributions, build_crosstab, DIMENSION_FIELDS, paged_query
from reporter.models import SearchParams, ProjectNum, IncludeField, parse_include_fields
from reporter.models.spending_categories import (
    SPENDING_CATEGORY_MAP_FY2024,
    _normalize_spending_category_name,
)
from fastmcp import Context
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Heading, DataTable, DataTableColumn

def register_tools(mcp):
    @mcp.tool()
    async def search_spending_categories(
        query: str,
        limit: int = 10,
    ):
        """
        Search NIH spending categories by name and return matching (id, name) pairs.

        Use this tool BEFORE filtering by `spending_categories` when you only know a
        plain-English topic (e.g., "aging", "breast cancer", "opioid") and need
        valid numeric IDs.

        Args:
            query (str): Plain-English category search text. Partial matches are supported.
            limit (int): Maximum number of matches to return (default 10, max 50).

        Returns:
            list[dict]: Matching categories as [{"id": int, "name": str}] ordered by match quality.
        """
        if not query or not query.strip():
            return []

        limit = max(1, min(limit, 50))
        normalized_query = _normalize_spending_category_name(query)
        query_tokens = set(normalized_query.split())

        scored: list[tuple[int, int, str]] = []  # (-score, id, name)
        for category_id, category_name in SPENDING_CATEGORY_MAP_FY2024.items():
            normalized_name = _normalize_spending_category_name(category_name)

            if normalized_query == normalized_name:
                score = 3  # exact match
            elif normalized_name.startswith(normalized_query):
                score = 2  # prefix match
            elif query_tokens and query_tokens.issubset(set(normalized_name.split())):
                score = 1  # all tokens present
            elif any(token in normalized_name for token in query_tokens):
                score = 0  # partial token match
            else:
                continue

            scored.append((-score, category_id, category_name))

        scored.sort(key=lambda item: (item[0], item[2]))
        return [{"id": category_id, "name": name} for _, category_id, name in scored[:limit]]

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

    @mcp.tool()
    async def get_top_awarded(
        ctx: Context,
        search_params: SearchParams,
        group_by: str,
        limit: int = 15,
    ):
        """
        Rank PIs or institutions by total funding and project count for a search portfolio.

        Use this to answer questions like "who are the top-funded PIs in cancer research?"
        or "which organizations receive the most NIH funding for diabetes grants?".
        Fetches all matching projects, so results are complete and accurate.

        Args:
            search_params (SearchParams): Search parameters to scope the portfolio.
            group_by (str): Dimension to rank by. Valid options:
                - "pi": Principal investigators (each PI on a grant is credited individually)
                - "org_name": Grantee institution name
                - "agency_ic_admin": NIH institute/center abbreviation
                - "activity_code": Grant activity code (R01, U01, etc.)
                - "org_state": Grantee institution state
                - "funding_mechanism": Funding mechanism
            limit (int): Number of top results to return (default 15).

        Returns:
            list[dict]: Entities ranked by total funding (descending), each with:
                - name: Entity identifier
                - total_funding: Sum of award amounts across all grants
                - project_count: Number of grants attributed to this entity
        """
        from collections import Counter

        valid = ["pi"] + [k for k in DIMENSION_FIELDS if k != "fiscal_year"]
        if group_by not in valid:
            raise ValueError(f"Invalid group_by '{group_by}'. Valid options: {valid}")

        if group_by == "pi":
            include_fields = [
                IncludeField.AWARD_AMOUNT.value,
                IncludeField.PRINCIPAL_INVESTIGATORS.value,
            ]
        else:
            include_fields = list({
                IncludeField.AWARD_AMOUNT.value,
                DIMENSION_FIELDS[group_by].value,
            })

        all_results = await get_all_responses(search_params, include_fields)

        funding_totals = Counter()
        project_counts = Counter()

        for r in all_results.get("results", []):
            if not isinstance(r, dict):
                continue
            award = r.get("award_amount") or 0
            if group_by == "pi":
                for pi in (r.get("principal_investigators") or []):
                    funding_totals[pi] += award
                    project_counts[pi] += 1
            else:
                key = r.get(group_by)
                if key:
                    funding_totals[key] += award
                    project_counts[key] += 1

        return [
            {"name": name, "total_funding": total, "project_count": project_counts[name]}
            for name, total in funding_totals.most_common(limit)
        ]

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

    @mcp.tool(app=True)
    async def get_project_table(
        search_params: SearchParams,
    ) -> PrefabApp:
        """
        Search NIH RePORTER and display matching projects as an interactive table.

        Use this instead of get_project_information when you want results rendered as a
        sortable, searchable, paginated table rather than raw text. Performs the search
        internally — no need to call find_project_ids first.

        Args:
            search_params (SearchParams): Search parameters including search term, years,
                agencies, organizations, pi_name, po_names, award_types, and spending_categories.
                Use search_spending_categories first if you need to resolve a category name to an ID.

        Returns:
            PrefabApp: Interactive table with project number, title, PI, fiscal year,
            award amount, activity code, NIH institute, and organization.
        """

        include_fields = [
            IncludeField.PROJECT_NUM.value,
            IncludeField.PROJECT_TITLE.value,
            IncludeField.CONTACT_PI_NAME.value,
            IncludeField.FISCAL_YEAR.value,
            IncludeField.AWARD_AMOUNT.value,
            IncludeField.ACTIVITY_CODE.value,
            IncludeField.AGENCY_IC_ADMIN.value,
            IncludeField.ORGANIZATION.value,
        ]

        results_data = await get_all_responses(search_params, include_fields)
        rows = results_data.get("results", [])

        with PrefabApp() as app:
            with Column(gap=4, css_class="p-6"):
                Heading(f"NIH Reporter Projects ({len(rows)} results)")
                DataTable(
                    columns=[
                        DataTableColumn(key="project_num", header="Project #", sortable=True),
                        DataTableColumn(key="project_title", header="Title", sortable=True),
                        DataTableColumn(key="contact_pi_name", header="PI", sortable=True),
                        DataTableColumn(key="fiscal_year", header="FY", sortable=True),
                        DataTableColumn(key="award_amount", header="Award Amount", sortable=True),
                        DataTableColumn(key="activity_code", header="Activity Code", sortable=True),
                        DataTableColumn(key="agency_ic_admin", header="Institute", sortable=True),
                        DataTableColumn(key="org_name", header="Organization", sortable=True),
                    ],
                    rows=rows,
                    search=True,
                    paginated=True,
                    page_size=20,
                )

        return app


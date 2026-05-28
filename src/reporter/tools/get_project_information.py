from typing import Annotated, Literal 
from reporter.utils import get_all_responses
from reporter.models import SearchParams, ProjectNum, IncludeField 


def register(mcp):
    @mcp.tool()
    async def get_project_information(
        project_ids: list[str],
        include_fields: list[IncludeField],
):
        """
        Tool to get specified metadata for a project based on project number.
        Use this to answer questions about award amounts, organizations, PIs, etc.

        Args:
            project_ids (list[str]): project ID numbers (e.g. ['P50DA056408-01', '1F32AG052995-01A1']).
            include_fields (list[str]): List of fields to return from the API.
                Choose fields relevant to the query (e.g., AwardAmount for funding questions,
                PrincipalInvestigators for PI questions, Organization for institution questions).

        Returns:
            dict: API response with specified project metadata
        """

        # add project_ids to a search_params object
        search_params = SearchParams(
            project_nums=project_ids
        )

        # Validate and convert include_fields strings to IncludeField enum values
        # fields = parse_include_fields(include_fields)

        # Call the API
        return await get_all_responses(search_params, include_fields)

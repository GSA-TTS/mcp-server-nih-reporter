from collections import Counter
from reporter.utils import get_all_responses, DIMENSION_FIELDS
from reporter.models import SearchParams, IncludeField
from fastmcp import Context


def register(mcp):
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
        
        **IMPORTANT:** This tool fetches ALL matching projects. If your search returns
        more than 15,000 results, the API pagination limit will be exceeded and an error
        will be raised. Refine your search criteria (narrower year range, specific 
        agencies, etc.) to return fewer results.

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
                
        Raises:
            ValueError: If search returns more than 15,000 results (API pagination limit)
        """

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

"""
NIH Reporter MCP Tools

This module provides tools for interacting with the NIH RePORTER API,
allowing searches, summaries, and analysis of NIH research grants.
"""

from . import (
    create_search_dashboard,
    search_spending_categories,
    get_search_preview,
    get_search_summary,
    get_top_awarded,
    find_project_ids,
    get_project_information,
    get_portfolio_crosstab,
    get_project_table,
)


def register_tools(mcp):
    """Register all NIH Reporter tools with the MCP server."""
    create_search_dashboard.register(mcp)
    search_spending_categories.register(mcp)
    get_search_preview.register(mcp)
    get_search_summary.register(mcp)
    get_top_awarded.register(mcp)
    find_project_ids.register(mcp)
    get_project_information.register(mcp)
    get_portfolio_crosstab.register(mcp)
    get_project_table.register(mcp)

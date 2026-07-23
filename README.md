# NIH RePORTER MCP Server

⚠️ DISCLAIMER: This is a proof of concept and is not intended for production use.

## 📖 Overview

This project is a pilot study for the creation of an MCP server for the NIH's grant database: RePORTER. The server provides the following tools:

**Search & discovery**

- **find_project_ids**: The primary search tool. Returns a paginated page of project IDs matching search criteria, plus overview statistics (year, institute, and activity code distributions) for that page. Use `offset` and `limit` to page through large result sets.
- **search_spending_categories**: Searches NIH spending categories by plain-English name and returns matching `(id, name)` pairs. Use this to resolve a topic (e.g., "aging", "breast cancer") into the numeric IDs required by the `spending_categories` filter.
- **get_project_information**: Retrieves specified metadata for projects by their project number (award amounts, principal investigators, abstracts, organizations, and other project details).

**Analysis & summaries**

- **get_search_preview**: Returns key portfolio statistics by sampling up to 500 matching projects. Fast but approximate for large portfolios — use it first to characterize a search before committing to a full analysis.
- **get_search_summary**: Fetches ALL matching projects to provide complete, accurate statistics. Use this when you need exact totals (e.g., "total funding for cancer research"). Automatically splits queries over 15,000 results into sub-queries; slower for large result sets.
- **get_top_awarded**: Ranks entities by total funding and project count for a search portfolio. Supports grouping by PI, organization name, NIH institute, activity code, organization state, or funding mechanism.
- **get_portfolio_crosstab**: Returns a cross-tabulation of grant counts and total funding across any two project dimensions (e.g., fiscal year × activity code), suitable for stacked bar charts, heatmaps, or tables.

**Interactive UI**

- **create_search_dashboard**: Builds a comprehensive dashboard for a search, with key metrics and visualizations (award amount distribution, institute and activity-code breakdowns).
- **get_project_table**: Displays matching projects as an interactive, sortable, searchable, paginated table (project number, title, PI, fiscal year, award amount, activity code, institute, organization). Performs the search internally.

Each tool is registered with the MCP server and can be called by an LLM or other MCP client. 

## Search Parameters

`SearchParams` now supports NIH spending category filtering via `spending_categories`:

```json
{
  "spending_categories": {
    "values": [27, 31],
    "match_all": false
  }
}
```

- `values`: List of NIH spending category numeric IDs (Appendix I, FY2024).
- `match_all`: `true` requires projects to match all listed categories; `false` matches at least one.

## 🚀 Quick Start 

The code as written is intended for cloud deployment. Contact the admins if you are interested in testing the cloud deployment. Otherwise, the repository may be forked and modified for local implementation. 

## 📐 Project Structure 

- `src/reporter/` - Main MCP server package
  - `app.py` - FastMCP server setup (registers tools, prompts, routes, and skills)
  - `main.py` - Entry point
  - `tools/` - MCP tool implementations (search, summaries, dashboards, tables)
  - `models/` - Pydantic models for search parameters and API fields (e.g., `SearchParams`, `IncludeField`, spending categories)
  - `prompts.py` - Custom MCP prompts
  - `routes.py` - Custom HTTP routes
  - `instructions/` - Server instructions loaded at startup
  - `skills/` - Reference skills exposed as MCP resources (spending-categories, award-type-lookup)
  - `utils.py` - Shared helpers for querying the RePORTER API and building distributions
- `scripts/` - Scripts for querying the API outside of the MCP server
- `tests/` - Unit tests
- `eval/` - Evaluation harnesses (`phoenix/`, `databricks_eval/`, `mcp-data-check/`)
- `agent/` - Example agents that connect to the MCP server

## 📚 Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/docs/getting-started/intro)
- [FastMCP Documentation](https://gofastmcp.com/getting-started/welcome)
- [NIH RePORTER API Documentation](https://api.reporter.nih.gov/)

## 💬 Contact

For any questions please contact [Mark Aronson](mailto:mark.aronson@gsa.gov)


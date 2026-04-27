# NIH RePORTER MCP Server

[![mcp-data-check](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/GSA-TTS/nih-reporter-mcp-server/main/eval/badge.json)](https://github.com/GSA-TTS/mcp-data-check)

⚠️ DISCLAIMER: This is a proof of concept and is not intended for production use.

## 📖 Overview

This project is a pilot study for the creation of an MCP server for the NIH's grant database: RePORTER. The server provides four tools:

- **search_projects**: Performs an initial search and returns the count of matching projects along with distribution statistics (institutes, activity codes, organizations, funding). Samples the first 500 results for quick previews.
- **get_search_summary**: Fetches ALL matching projects to provide complete, accurate statistics. Use this when you need exact totals (e.g., "total funding for cancer research"). Slower for large result sets.
- **find_project_ids**: Returns a paginated page of project IDs matching search criteria, plus overview statistics for that page. Use `offset` and `limit` to retrieve all matching grants for further detail retrieval.
- **get_project_information**: Retrieves detailed metadata for specific projects by their project number. Use this to get award amounts, principal investigators, abstracts, organizations, and other project details.

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

- src/reporter/ - Main package code 
- scripts/ - Scripts used for querying the API outside of the MCP server 

## 📚 Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/docs/getting-started/intro)
- [FastMCP Documentation](https://gofastmcp.com/getting-started/welcome)
- [NIH RePORTER API Documentation](https://api.reporter.nih.gov/)

## 💬 Contact

For any questions please contact [Mark Aronson](mailto:mark.aronson@gsa.gov)


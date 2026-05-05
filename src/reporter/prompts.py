def register_prompts(mcp):

    @mcp.prompt()
    def project_information_search() -> str:
        """Use this prompt to answer questions about the information of NIH-funded research projects."""

        return f"""Please help me do a summary analysis of NIH research grants. Follow these steps:

            1. Start with get_search_preview to get a quick preview of matching projects (samples first 500)
               - Returns total count and key statistics (year, institute, activity code, organization, funding mechanism, active status, award stats, top PIs)
               - Review distributions to understand the data landscape
               - To refine results, call get_search_preview again with filters added to search_params (years, agencies, activity_codes, states)
               - Repeat until the scope is appropriate for the query

            2. Use get_search_summary when you need accurate, complete statistics (e.g., "total funding for X")
               - Fetches ALL matching projects (not just a 500-result sample)
               - Use this for precise totals, not for exploration
               - May be slower for large result sets

            3. Use find_project_ids to get the list of project IDs for detailed queries
               - Returns one page of project IDs matching the search criteria
               - Use offset and limit to page through result sets larger than 500

            4. Use get_project_information with only the include_fields needed to answer the query:
               - For funding questions: AWARD_AMOUNT, FISCAL_YEAR, DIRECT_COST_AMT, INDIRECT_COST_AMT
               - For PI questions: PRINCIPAL_INVESTIGATORS, CONTACT_PI_NAME
               - For organization questions: ORGANIZATION, CONG_DIST, ORGANIZATION_TYPE
               - For grant type questions: ACTIVITY_CODE, FUNDING_MECHANISM, AGENCY_IC_ADMIN
               - Always include PROJECT_NUM for reference

            5. Use the returned information to answer the user's question."""

#     @mcp.prompt()
#     def rcdc_term_frequency(
#         rcdc_terms: str,
#         fiscal_years: str,
#         institutes: str = "",
#     ) -> str:
#         """Plot the number of NIH grants matching one or more RCDC terms across fiscal years.

#         Args:
#             rcdc_terms: Comma-separated RCDC terms to search for (e.g., "breast cancer,ovarian cancer").
#             fiscal_years: Comma-separated fiscal years (e.g., "2020,2021,2022,2023,2024").
#             institutes: Comma-separated NIH institute codes to filter by (e.g., "NCI,NIMHD").
#                 Leave empty to search across all institutes.
#         """

#         terms_list = [t.strip() for t in rcdc_terms.split(",") if t.strip()]
#         years_list = [y.strip() for y in fiscal_years.split(",") if y.strip()]

#         if institutes:
#             institute_list = [i.strip() for i in institutes.split(",") if i.strip()]
#             institutes_label = institutes
#             agencies_instruction = f"- `agencies`: {institute_list}"
#         else:
#             institutes_label = "all institutes"
#             agencies_instruction = "- (omit `agencies` to search all institutes)"

#         terms_bullet_list = "\n".join(f'  - "{t}"' for t in terms_list)

#         return f"""Plot the number of NIH grants for each RCDC term by fiscal year.

#             **RCDC Terms**: {rcdc_terms}
#             **Fiscal Years**: {fiscal_years}
#             **Institutes**: {institutes_label}

#             ---

#             ## Step 1: Fetch grant counts per term

#             For **each term** listed below, call `get_search_summary` with:
#             {agencies_instruction}
#             - `years`: [{", ".join(years_list)}]
#             - `advanced_text_search`:
#             - `search_text`: <the term>
#             - `search_field`: ["terms"]
#             - `operator`: "and"

#             Terms to search:
#             {terms_bullet_list}

#             Each response includes a `year_distribution` with the grant count per fiscal year for that term.

#             ---

#             ## Step 2: Plot the results

#             Use Python (matplotlib or similar) to produce a line chart with one line per term:
#             - X-axis: fiscal year
#             - Y-axis: number of grants
#             - One labeled line per term
#             - Title: 'NIH Grant Counts by RCDC Term and Fiscal Year ({institutes_label})'

#             Also display the raw counts in a table:

#             | Fiscal Year | {" | ".join(terms_list)} |
#             |-------------|{"---|" * len(terms_list)}
#             | YYYY        | {"N | " * len(terms_list)}"""

#     @mcp.prompt()
#     def activity_code_stacked_bar(
#         fiscal_years: str,
#         filters: str = "",
#     ) -> str:
#         """Plot a stacked bar chart of NIH grant counts by activity code over fiscal years.

#         Args:
#             fiscal_years: Comma-separated fiscal years (e.g., "2020,2021,2022,2023,2024").
#             filters: Natural language description of any additional filters to apply, such as
#                 institutes, organizations, PIs, search terms, or activity codes.
#                 Examples: "NCI only", "R01 grants on breast cancer", "Johns Hopkins, PI Jane Smith".
#                 Leave empty to include all grants.
#         """

#         years_list = [y.strip() for y in fiscal_years.split(",") if y.strip()]
#         filters_section = f"**Filters**: {filters}" if filters else "**Filters**: none"

#         return f"""Plot a stacked bar chart of NIH grant counts by activity code for each fiscal year.

# **Fiscal Years**: {fiscal_years}
# {filters_section}

# ---

# ## Step 1: Fetch the cross-tabulation

# Construct `search_params` from the filters described above, mapping them to the appropriate
# `SearchParams` fields (e.g. `agencies`, `organizations`, `pi_name`, `activity_codes`, `spending_categories`,
# `advanced_text_search`, etc.), then call `get_portfolio_crosstab` with:
# - `row_field`: "fiscal_year"
# - `col_field`: "activity_code"
# - `years`: [{", ".join(years_list)}]
# - Any additional fields derived from the filters

# The response is a nested dict of `{{fiscal_year: {{activity_code: {{"count": N, "total_funding": X}}}}}}` covering all requested years.

# ---

# ## Step 2: Plot the results

# Use Python (matplotlib or similar) to produce a stacked bar chart:
# - X-axis: fiscal year
# - Y-axis: number of grants (`count`) or total funding (`total_funding`) — choose based on context
# - Each bar stacked by activity code
# - Legend identifying each activity code
# - Title: 'NIH Grant Counts by Activity Code' or 'NIH Total Funding by Activity Code'

# Also display the raw counts in a table with one column per activity code:

# | Fiscal Year | R01 | R21 | ... |
# |-------------|-----|-----|-----|
# | YYYY        | N   | N   | ... |"""


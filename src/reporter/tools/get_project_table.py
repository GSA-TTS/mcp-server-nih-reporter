from reporter.utils import get_all_responses
from reporter.models import SearchParams, IncludeField
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Row, Heading, DataTable, DataTableColumn, EVENT, Button 
from prefab_ui.actions.mcp import CallTool, RequestDisplayMode

def register(mcp):
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
                with Row(gap=4, align="center", justify="between"):
                    Heading(f"NIH Reporter Projects ({len(rows)} results)")
                    Button("Go Fullscreen", on_click=RequestDisplayMode("fullscreen"))
                DataTable(
                    columns=[
                        DataTableColumn(key="project_num", header="Project #", sortable=True),
                        DataTableColumn(key="project_title", header="Title", sortable=True, max_width="400px", cell_class="truncate"),
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
                    on_row_click=CallTool(
                        "get_project_information",
                        arguments={
                            "project_ids": [
                                {
                                    "project_num": EVENT.row_data["project_num"]
                                }
                            ],
                        },
                    ),
                )

        return app

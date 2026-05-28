from reporter.utils import get_all_responses
from reporter.models import SearchParams, IncludeField
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Row, Heading, DataTable, DataTableColumn, EVENT, Button, Dialog, Text, Badge, Separator, RESULT
from prefab_ui.components.control_flow import If, Elif, Else
from prefab_ui.actions.mcp import CallTool, RequestDisplayMode
from prefab_ui.actions import SetState, CloseOverlay, OpenLink

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
                    on_row_click=[
                        SetState("loading_project", True),
                        SetState("project_error", None),
                        SetState("project_dialog_open", True),
                        CallTool(
                            "get_project_information",
                            arguments={
                                "project_ids": [
                                    {
                                        "project_num": EVENT.row_data["project_num"]
                                    }
                                ],
                                "include_fields": [
                                    IncludeField.PROJECT_NUM.value,
                                    IncludeField.PROJECT_TITLE.value,
                                    IncludeField.CONTACT_PI_NAME.value,
                                    IncludeField.PRINCIPAL_INVESTIGATORS.value,
                                    IncludeField.ORGANIZATION.value,
                                    IncludeField.FISCAL_YEAR.value,
                                    IncludeField.AWARD_AMOUNT.value,
                                    IncludeField.DIRECT_COST_AMT.value,
                                    IncludeField.INDIRECT_COST_AMT.value,
                                    IncludeField.ACTIVITY_CODE.value,
                                    IncludeField.AGENCY_IC_ADMIN.value,
                                    IncludeField.PROJECT_START_DATE.value,
                                    IncludeField.PROJECT_END_DATE.value,
                                    IncludeField.ABSTRACT_TEXT.value,
                                    IncludeField.PHR_TEXT.value,
                                    IncludeField.PROJECT_DETAIL_URL.value,
                                ],
                            },
                            on_success=[
                                SetState("selected_project", RESULT["results"][0]),
                                SetState("loading_project", False)
                            ],
                            on_error=[
                                SetState("project_error", RESULT),
                                SetState("loading_project", False)
                            ]
                        ),
                    ],
                )
                
                # Project Detail Dialog
                with If("{{ project_dialog_open }}"):
                    with Dialog(
                        title="Project Details",
                        description="{{ selected_project.project_num if selected_project else '' }}",
                        name="project_dialog_open",
                        dismissible=True
                    ):
                        Button("View Details", css_class="hidden")  # Hidden trigger
                        
                        # Error State
                        with If("{{ project_error }}"):
                            with Column(gap=4, css_class="p-4"):
                                Text("**Error loading project details**", css_class="text-red-600")
                                Text("{{ project_error }}", css_class="text-sm text-muted-foreground")
                                Button("Close", on_click=CloseOverlay(), variant="secondary")
                        
                        # Project Details Content
                        with Elif("{{ selected_project }}"):
                            with Column(gap=4, css_class="max-h-[600px] overflow-y-auto p-4"):
                                # Title
                                Heading("{{ selected_project.project_title }}", level=3)
                                
                                Separator()
                                
                                # Basic Information Section
                                Heading("Basic Information", level=4)
                                with Row(gap=4, align="start"):
                                    with Column(gap=2, css_class="flex-1"):
                                        Text("**Project Number:**")
                                        Text("{{ selected_project.project_num }}")
                                        
                                        Text("**Principal Investigators:**")
                                        with If("{{ selected_project.principal_investigators }}"):
                                            with Column(gap=1):
                                                # Display all PIs
                                                Text("{{ selected_project.contact_pi_name }}", css_class="text-sm")
                                        with Else():
                                            Text("{{ selected_project.contact_pi_name }}", css_class="text-sm")
                                        
                                        Text("**Organization:**")
                                        with If("{{ selected_project.organization and selected_project.organization.org_name }}"):
                                            Text("{{ selected_project.organization.org_name }}", css_class="text-sm")
                                        with Else():
                                            Text("N/A", css_class="text-sm text-muted-foreground")
                                    
                                    with Column(gap=2, css_class="flex-1"):
                                        Text("**Fiscal Year:**")
                                        Text("{{ selected_project.fiscal_year }}")
                                        
                                        Text("**Activity Code:**")
                                        Text("{{ selected_project.activity_code }}")
                                        
                                        Text("**Institute:**")
                                        Text("{{ selected_project.agency_ic_admin }}")
                                
                                Separator()
                                
                                # Funding Information Section
                                Heading("Funding Information", level=4)
                                with Row(gap=4, css_class="flex-wrap"):
                                    with Column(gap=1):
                                        Text("**Award Amount:**")
                                        with If("{{ selected_project.award_amount }}"):
                                            Badge("${{ selected_project.award_amount }}", variant="default")
                                        with Else():
                                            Badge("N/A", variant="outline")
                                    
                                    with Column(gap=1):
                                        Text("**Direct Costs:**")
                                        with If("{{ selected_project.direct_cost_amt }}"):
                                            Badge("${{ selected_project.direct_cost_amt }}", variant="secondary")
                                        with Else():
                                            Badge("N/A", variant="outline")
                                    
                                    with Column(gap=1):
                                        Text("**Indirect Costs:**")
                                        with If("{{ selected_project.indirect_cost_amt }}"):
                                            Badge("${{ selected_project.indirect_cost_amt }}", variant="secondary")
                                        with Else():
                                            Badge("N/A", variant="outline")
                                
                                Separator()
                                
                                # Project Timeline
                                Heading("Project Timeline", level=4)
                                with Row(gap=4):
                                    with Column(gap=1):
                                        Text("**Start Date:**")
                                        with If("{{ selected_project.project_start_date }}"):
                                            Text("{{ selected_project.project_start_date }}", css_class="text-sm")
                                        with Else():
                                            Text("N/A", css_class="text-sm text-muted-foreground")
                                    
                                    with Column(gap=1):
                                        Text("**End Date:**")
                                        with If("{{ selected_project.project_end_date }}"):
                                            Text("{{ selected_project.project_end_date }}", css_class="text-sm")
                                        with Else():
                                            Text("N/A", css_class="text-sm text-muted-foreground")
                                
                                # Abstract (if available)
                                with If("{{ selected_project.abstract_text }}"):
                                    Separator()
                                    Heading("Abstract", level=4)
                                    Text("{{ selected_project.abstract_text }}", css_class="text-sm text-muted-foreground whitespace-pre-wrap")
                                
                                # Public Health Relevance (if available)
                                with If("{{ selected_project.phr_text }}"):
                                    Separator()
                                    Heading("Public Health Relevance", level=4)
                                    Text("{{ selected_project.phr_text }}", css_class="text-sm text-muted-foreground whitespace-pre-wrap")
                                
                                Separator()
                                
                                # Actions
                                with Row(gap=2, justify="end"):
                                    with If("{{ selected_project.project_detail_url }}"):
                                        Button(
                                            "View on NIH RePORTER",
                                            on_click=OpenLink("{{ selected_project.project_detail_url }}"),
                                            variant="outline"
                                        )
                                    Button("Close", on_click=CloseOverlay(), variant="secondary")

        return app

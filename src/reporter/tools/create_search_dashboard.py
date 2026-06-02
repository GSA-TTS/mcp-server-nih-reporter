from reporter.utils import get_all_responses, get_project_distributions, get_project_distributions_df
from reporter.models import SearchParams, IncludeField
import pandas as pd 
from prefab_ui.app import PrefabApp
from prefab_ui.components import Dashboard, DashboardItem, Metric, Histogram, Card, CardContent, CardDescription, CardHeader, CardTitle
from prefab_ui.components.charts import PieChart

def register(mcp):
    @mcp.tool(app=True)
    async def create_search_dashboard(
        search_params: SearchParams,
    ) -> PrefabApp:
        """
        Tool to create a comprehensive search dashboard for NIH RePORTER data based on 
        user-defined search parameters.

        Args:
            search_params (SearchParams): The parameters defining the search criteria for NIH RePORTER data
        
        Returns:
            PrefabApp: A PrefabApp instance containing the search dashboard with key metrics and visualizations.
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

        # convert responses to a dataframe 
        df = get_project_distributions_df(all_results)

        # convert to dictionary for pie chart 
        data_ic = df.groupby('agency_ic_admin').agg(
            count=('project_num', 'count'),
            total_amount=('award_amount', 'sum')
        ).reset_index()

        # Rename columns to match your desired format
        data_ic = data_ic.rename(columns={'agency_ic_admin': 'ic_name'})

        # Convert to list of dictionaries
        data_ic = data_ic.to_dict('records')

        # convert responses to dictionary for activity code distribution 
        data_activity = df.groupby('activity_code').agg(
            count=('project_num', 'count'),
            total_amount=('award_amount', 'sum')
        ).reset_index()

        data_activity = data_activity.to_dict('records')

        with PrefabApp() as app:
            with Card():
                with CardContent():
                    Metric(
                        label="Total Projects",
                        value=len(df),
                    )
            with Dashboard(columns=2, row_height=300, gap=30):   
                with DashboardItem(col=1,row=1):
                    with Card():
                        with CardHeader():
                            CardTitle("Award Amount Distribution")
                            CardDescription("Distribution of award amounts for the search results")
                        with CardContent():
                            Histogram(
                                label="Award Amount Distribution",
                                values=df["award_amount"],
                                bin_edges=[0,100000,200000,300000,400000,500000,750000,1000000,1500000,2000000,5000000,10000000]
                            )
                with DashboardItem(col=2,row=1):
                    with Card():
                        with CardHeader():
                            CardTitle("Fiscal Year Distribution")
                            CardDescription("Distribution of projects by fiscal year")
                        with CardContent():
                            Histogram(
                                label="Fiscal Year Distribution",
                                values=df["fiscal_year"],
                                bin_edges=list(range(df["fiscal_year"].min(), df["fiscal_year"].max() + 2, 1))
                            )
                with DashboardItem(col=1,row=2):
                    with Card():
                        with CardHeader():
                            CardTitle("Projects by Institute")
                            CardDescription("Distribution of projects by NIH institute/center")
                        with CardContent():
                            PieChart(
                                data=data_ic,
                                data_key="count",
                                name_key="ic_name",
                                show_legend=True,
                            )
                with DashboardItem(col=2,row=2):
                    with Card():
                        with CardHeader():
                            CardTitle("Projects by Activity Code")
                            CardDescription("Distribution of projects by activity code")
                        with CardContent():
                            PieChart(
                                data=data_activity,
                                data_key="count",
                                name_key="activity_code",
                                show_legend=True,
                            )

        return app


        

        # distributions = get_project_distributions(all_results)

        # # convert 

        # total_projects = len(distributions["project_ids"])

        # return {
        #     "total_projects": total_projects,
        #     "year_distribution": dict(sorted(distributions["year_distribution"].items(), reverse=True)),
        #     "institute_distribution": dict(distributions["institute_distribution"].most_common(15)),
        #     "activity_code_distribution": dict(distributions["activity_code_distribution"].most_common(15)),
        #     "organization_distribution": dict(distributions["organization_distribution"].most_common(15)),
        #     "funding_mechanism_distribution": dict(distributions["funding_mechanism_distribution"].most_common()),
        #     "active_status_distribution": dict(distributions["active_status_distribution"]),
        #     "award_amount_stats": distributions["award_amount_stats"],
        #     "pi_distribution": dict(distributions["pi_distribution"].most_common(15)),
        #     "pi_funding": dict(distributions["pi_funding"].most_common(15)),
        # }

from typing import Annotated, Literal 
from reporter.utils import get_all_responses
from reporter.models import SearchParams, ProjectNum


def register(mcp):
    @mcp.tool()
    async def get_project_information(
        project_ids: list[str],
        include_fields: Annotated[
        list[
            Literal[
                "ApplId",
                "SubprojectId",
                "ProjectNum",
                "ProjectSerialNum",
                "CoreProjectNum",
                "ProjectNumSplit",
                "FiscalYear",
                "ProjectStartDate",
                "ProjectEndDate",
                "AwardNoticeDate",
                "BudgetStart",
                "BudgetEnd",
                "DateAdded",
                "AwardAmount",
                "DirectCostAmt",
                "IndirectCostAmt",
                "AwardType",
                "ActivityCode",
                "FundingMechanism",
                "MechanismCodeDc",
                "CfdaCode",
                "Organization",
                "OrganizationType",
                "CongDist",
                "GeoLatLon",
                "PrincipalInvestigators",
                "ContactPiName",
                "ProgramOfficers",
                "AgencyCode",
                "AgencyIcAdmin",
                "AgencyIcFundings",
                "ProjectTitle",
                "AbstractText",
                "PhrText",
                "Terms",
                "PrefTerms",
                "SpendingCategories",
                "SpendingCategoriesDesc",
                "FullStudySection",
                "OpportunityNumber",
                "IsActive",
                "IsNew",
                "ArraFunded",
                "CovidResponse",
                "ProjectDetailUrl",
            ]
        ],
        """List of fields to include in the response. Available options:
        - ApplId: Application ID.
        - SubprojectId: Subproject ID.
        - ProjectNum: Full NIH project number.
        - ProjectSerialNum: Project serial number.
        - CoreProjectNum: Core project number.
        - ProjectNumSplit: Structured project number components.
        - FiscalYear: Fiscal year of the project record.
        - ProjectStartDate: Project period start date.
        - ProjectEndDate: Project period end date.
        - AwardNoticeDate: Award notice date.
        - BudgetStart: Budget period start date.
        - BudgetEnd: Budget period end date.
        - DateAdded: Date added to the NIH RePORTER data feed.
        - AwardAmount: Award amount for the record.
        - DirectCostAmt: Direct costs amount.
        - IndirectCostAmt: Indirect costs amount.
        - AwardType: Award/application type code.
        - ActivityCode: Activity code (e.g., R01, F32).
        - FundingMechanism: Funding mechanism code.
        - MechanismCodeDc: Mechanism code (data center field).
        - CfdaCode: CFDA assistance listing code.
        - Organization: Awardee organization object.
        - OrganizationType: Organization type.
        - CongDist: Congressional district.
        - GeoLatLon: Latitude and longitude coordinates.
        - PrincipalInvestigators: Principal investigators list.
        - ContactPiName: Contact PI full name.
        - ProgramOfficers: Program officers list.
        - AgencyCode: Agency code.
        - AgencyIcAdmin: Administering NIH institute/center.
        - AgencyIcFundings: Funding NIH institute/center list.
        - ProjectTitle: Project title.
        - AbstractText: Project abstract text.
        - PhrText: Public health relevance text.
        - Terms: NIH indexed terms.
        - PrefTerms: Preferred terms.
        - SpendingCategories: Spending categories IDs.
        - SpendingCategoriesDesc: Spending categories descriptions.
        - FullStudySection: Full study section.
        - OpportunityNumber: Funding opportunity number.
        - IsActive: Active flag.
        - IsNew: New project flag.
        - ArraFunded: ARRA-funded flag.
        - CovidResponse: COVID-response flag.
        - ProjectDetailUrl: NIH RePORTER project detail URL.
        """
    ],
):
        """
        Tool to get specified metadata for a project based on project number.
        Use this to answer questions about award amounts, organizations, PIs, etc.

        Args:
            project_ids (list[str]): project ID numbers
            include_fields (list[str]): List of fields to return from the API.
                Choose fields relevant to the query (e.g., AwardAmount for funding questions,
                PrincipalInvestigators for PI questions, Organization for institution questions).

        Returns:
            dict: API response with specified project metadata
        """

        # add project_ids to a search_params object
        search_params = SearchParams(
            project_nums=[ProjectNum(project_num=p) for p in project_ids]
        )

        # Validate and convert include_fields strings to IncludeField enum values
        # fields = parse_include_fields(include_fields)

        # Call the API
        return await get_all_responses(search_params, include_fields)

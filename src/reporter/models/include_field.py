from __future__ import annotations

"""Metadata and parsing for NIH RePORTER include fields."""

from enum import Enum
from typing import List

INCLUDE_FIELD_DESCRIPTIONS: dict[str, str] = {
    "APPL_ID": "Application ID.",
    "SUBPROJECT_ID": "Subproject ID.",
    "PROJECT_NUM": "Full NIH project number.",
    "PROJECT_SERIAL_NUM": "Project serial number.",
    "CORE_PROJECT_NUM": "Core project number.",
    "PROJECT_NUM_SPLIT": "Structured project number components.",
    "FISCAL_YEAR": "Fiscal year of the project record.",
    "PROJECT_START_DATE": "Project period start date.",
    "PROJECT_END_DATE": "Project period end date.",
    "AWARD_NOTICE_DATE": "Award notice date.",
    "BUDGET_START": "Budget period start date.",
    "BUDGET_END": "Budget period end date.",
    "DATE_ADDED": "Date added to the NIH RePORTER data feed.",
    "AWARD_AMOUNT": "Award amount for the record.",
    "DIRECT_COST_AMT": "Direct costs amount.",
    "INDIRECT_COST_AMT": "Indirect costs amount.",
    "AWARD_TYPE": "Award/application type code.",
    "ACTIVITY_CODE": "Activity code (e.g., R01, F32).",
    "FUNDING_MECHANISM": "Funding mechanism code.",
    "MECHANISM_CODE_DC": "Mechanism code (data center field).",
    "CFDA_CODE": "CFDA assistance listing code.",
    "ORGANIZATION": "Awardee organization object.",
    "ORGANIZATION_TYPE": "Organization type.",
    "CONG_DIST": "Congressional district.",
    "GEO_LAT_LON": "Latitude and longitude coordinates.",
    "PRINCIPAL_INVESTIGATORS": "Principal investigators list.",
    "CONTACT_PI_NAME": "Contact PI full name.",
    "PROGRAM_OFFICERS": "Program officers list.",
    "AGENCY_CODE": "Agency code.",
    "AGENCY_IC_ADMIN": "Administering NIH institute/center.",
    "AGENCY_IC_FUNDINGS": "Funding NIH institute/center list.",
    "PROJECT_TITLE": "Project title.",
    "ABSTRACT_TEXT": "Project abstract text.",
    "PHR_TEXT": "Public health relevance text.",
    "TERMS": "NIH indexed terms.",
    "PREF_TERMS": "Preferred terms.",
    "SPENDING_CATEGORIES": "Spending categories IDs.",
    "SPENDING_CATEGORIES_DESC": "Spending categories descriptions.",
    "FULL_STUDY_SECTION": "Full study section.",
    "OPPORTUNITY_NUMBER": "Funding opportunity number.",
    "IS_ACTIVE": "Active flag.",
    "IS_NEW": "New project flag.",
    "ARRA_FUNDED": "ARRA-funded flag.",
    "COVID_RESPONSE": "COVID-response flag.",
    "PROJECT_DETAIL_URL": "NIH RePORTER project detail URL.",
}


class IncludeField(str, Enum):
    """Valid field names for the include_fields parameter in NIH RePORTER API queries."""
    APPL_ID = "ApplId"
    SUBPROJECT_ID = "SubprojectId"
    PROJECT_NUM = "ProjectNum"
    PROJECT_SERIAL_NUM = "ProjectSerialNum"
    CORE_PROJECT_NUM = "CoreProjectNum"
    PROJECT_NUM_SPLIT = "ProjectNumSplit"

    FISCAL_YEAR = "FiscalYear"
    PROJECT_START_DATE = "ProjectStartDate"
    PROJECT_END_DATE = "ProjectEndDate"
    AWARD_NOTICE_DATE = "AwardNoticeDate"
    BUDGET_START = "BudgetStart"
    BUDGET_END = "BudgetEnd"
    DATE_ADDED = "DateAdded"

    AWARD_AMOUNT = "AwardAmount"
    DIRECT_COST_AMT = "DirectCostAmt"
    INDIRECT_COST_AMT = "IndirectCostAmt"
    AWARD_TYPE = "AwardType"
    ACTIVITY_CODE = "ActivityCode"
    FUNDING_MECHANISM = "FundingMechanism"
    MECHANISM_CODE_DC = "MechanismCodeDc"
    CFDA_CODE = "CfdaCode"

    ORGANIZATION = "Organization"
    ORGANIZATION_TYPE = "OrganizationType"
    CONG_DIST = "CongDist"
    GEO_LAT_LON = "GeoLatLon"

    PRINCIPAL_INVESTIGATORS = "PrincipalInvestigators"
    CONTACT_PI_NAME = "ContactPiName"
    PROGRAM_OFFICERS = "ProgramOfficers"

    AGENCY_CODE = "AgencyCode"
    AGENCY_IC_ADMIN = "AgencyIcAdmin"
    AGENCY_IC_FUNDINGS = "AgencyIcFundings"

    PROJECT_TITLE = "ProjectTitle"
    ABSTRACT_TEXT = "AbstractText"
    PHR_TEXT = "PhrText"
    TERMS = "Terms"
    PREF_TERMS = "PrefTerms"

    SPENDING_CATEGORIES = "SpendingCategories"
    SPENDING_CATEGORIES_DESC = "SpendingCategoriesDesc"
    FULL_STUDY_SECTION = "FullStudySection"
    OPPORTUNITY_NUMBER = "OpportunityNumber"

    IS_ACTIVE = "IsActive"
    IS_NEW = "IsNew"
    ARRA_FUNDED = "ArraFunded"
    COVID_RESPONSE = "CovidResponse"

    PROJECT_DETAIL_URL = "ProjectDetailUrl"

    @property
    def description(self) -> str:
        return INCLUDE_FIELD_DESCRIPTIONS.get(self.name, self.value)

    @classmethod
    def from_input(cls, value: str | IncludeField) -> IncludeField:
        """Parse either enum name (e.g., AWARD_AMOUNT) or API value (e.g., AwardAmount)."""
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise TypeError(f"Include field must be a string or IncludeField, got {type(value).__name__}")
        for field in cls:
            if value.upper() == field.name or value == field.value:
                return field
        raise ValueError(f"Invalid include field: {value}")


def _validate_include_field_info() -> None:
    enum_names = {field.name for field in IncludeField}
    info_names = set(INCLUDE_FIELD_DESCRIPTIONS.keys())
    missing = sorted(enum_names - info_names)
    extra = sorted(info_names - enum_names)
    if missing or extra:
        raise RuntimeError(
            "IncludeField metadata mismatch. "
            f"Missing metadata for: {missing}; Extra metadata keys: {extra}"
        )


_validate_include_field_info()


def parse_include_fields(values: List[str | IncludeField] | str | IncludeField) -> List[IncludeField]:
    """Normalize include_fields input to a validated list of IncludeField members."""
    if isinstance(values, (str, IncludeField)):
        values = [values]
    if not isinstance(values, list):
        raise TypeError("include_fields must be a list, string, or IncludeField")
    return [IncludeField.from_input(v) for v in values]

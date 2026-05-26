from enum import Enum


class IncludeField(str, Enum):
    """Fields available for NIH RePORTER project data retrieval."""
    
    APPL_ID = "ApplId"
    """Application ID"""
    
    SUBPROJECT_ID = "SubprojectId"
    """Subproject ID"""
    
    PROJECT_NUM = "ProjectNum"
    """Full NIH project number"""
    
    PROJECT_SERIAL_NUM = "ProjectSerialNum"
    """Project serial number"""
    
    CORE_PROJECT_NUM = "CoreProjectNum"
    """Core project number"""
    
    PROJECT_NUM_SPLIT = "ProjectNumSplit"
    """Structured project number components"""
    
    FISCAL_YEAR = "FiscalYear"
    """Fiscal year of the project record"""
    
    PROJECT_START_DATE = "ProjectStartDate"
    """Project period start date"""
    
    PROJECT_END_DATE = "ProjectEndDate"
    """Project period end date"""
    
    AWARD_NOTICE_DATE = "AwardNoticeDate"
    """Award notice date"""
    
    BUDGET_START = "BudgetStart"
    """Budget period start date"""
    
    BUDGET_END = "BudgetEnd"
    """Budget period end date"""
    
    DATE_ADDED = "DateAdded"
    """Date added to the NIH RePORTER data feed"""
    
    AWARD_AMOUNT = "AwardAmount"
    """Award amount for the record"""
    
    DIRECT_COST_AMT = "DirectCostAmt"
    """Direct costs amount"""
    
    INDIRECT_COST_AMT = "IndirectCostAmt"
    """Indirect costs amount"""
    
    AWARD_TYPE = "AwardType"
    """Award/application type code"""
    
    ACTIVITY_CODE = "ActivityCode"
    """Activity code (e.g., R01, F32)"""
    
    FUNDING_MECHANISM = "FundingMechanism"
    """Funding mechanism code"""
    
    MECHANISM_CODE_DC = "MechanismCodeDc"
    """Mechanism code (data center field)"""
    
    CFDA_CODE = "CfdaCode"
    """CFDA assistance listing code"""
    
    ORGANIZATION = "Organization"
    """Awardee organization object"""
    
    ORGANIZATION_TYPE = "OrganizationType"
    """Organization type"""
    
    CONG_DIST = "CongDist"
    """Congressional district"""
    
    GEO_LAT_LON = "GeoLatLon"
    """Latitude and longitude coordinates"""
    
    PRINCIPAL_INVESTIGATORS = "PrincipalInvestigators"
    """Principal investigators list"""
    
    CONTACT_PI_NAME = "ContactPiName"
    """Contact PI full name"""
    
    PROGRAM_OFFICERS = "ProgramOfficers"
    """Program officers list"""
    
    AGENCY_CODE = "AgencyCode"
    """Agency code"""
    
    AGENCY_IC_ADMIN = "AgencyIcAdmin"
    """Administering NIH institute/center"""
    
    AGENCY_IC_FUNDINGS = "AgencyIcFundings"
    """Funding NIH institute/center list"""
    
    PROJECT_TITLE = "ProjectTitle"
    """Project title"""
    
    ABSTRACT_TEXT = "AbstractText"
    """Project abstract text"""
    
    PHR_TEXT = "PhrText"
    """Public health relevance text"""
    
    TERMS = "Terms"
    """NIH indexed terms"""
    
    PREF_TERMS = "PrefTerms"
    """Preferred terms"""
    
    SPENDING_CATEGORIES = "SpendingCategories"
    """Spending categories IDs"""
    
    SPENDING_CATEGORIES_DESC = "SpendingCategoriesDesc"
    """Spending categories descriptions"""
    
    FULL_STUDY_SECTION = "FullStudySection"
    """Full study section"""
    
    OPPORTUNITY_NUMBER = "OpportunityNumber"
    """Funding opportunity number"""
    
    IS_ACTIVE = "IsActive"
    """Active flag"""
    
    IS_NEW = "IsNew"
    """New project flag"""
    
    ARRA_FUNDED = "ArraFunded"
    """ARRA-funded flag"""
    
    COVID_RESPONSE = "CovidResponse"
    """COVID-response flag"""
    
    PROJECT_DETAIL_URL = "ProjectDetailUrl"
    """NIH RePORTER project detail URL"""
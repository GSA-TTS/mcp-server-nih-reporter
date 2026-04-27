from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from enum import Enum 
from typing import Optional, List
from reporter.models.funding_mechanism_metadata import FUNDING_MECHANISM_DESCRIPTIONS
from reporter.models.include_field import IncludeField
from reporter.models.nih_agency import NIHAgency
from reporter.models.spending_categories import SPENDING_CATEGORY_IDS_FY2024
from reporter.models.state_code import StateCode

class SearchOperator(str, Enum):
    """How to combine multiple search terms."""
    ALL = "all"
    OR = "or"
    AND = "and"
    ADVANCED = "advanced"

    @property
    def description(self) -> str:
        return {
            "all": "for searching text in all search fields (title, abstract, scientific terms)",
            "or": "projects that contain at least one of the terms entered will be retrieved. Use quotes(\") around the entered text to search for exact phrases",
            "and": "projects in which all of the search terms are found within the title, abstract, or scientific terms will be retrieved",
            "advanced": "provides additional capability to narrow selection criteria more precisely and evaluate complex entries such as chemical references",
        }[self.value]

class SearchField(str, Enum):
    """Fields to search in."""
    PROJECT_TITLE = "projecttitle"
    TERMS = "terms"
    ABSTRACT = "abstract"

    @property
    def description(self) -> str:
        return {
            "projecttitle": "Search within project titles.",
            "terms": "Search indexed NIH RePORTER terms.",
            "abstract": "Search within project abstracts.",
        }[self.value]

class AdvancedTextSearch(BaseModel):
    operator: SearchOperator = Field(
        default=SearchOperator.AND,
        description="How to combine multiple search terms (defaults to AND)"
    )
    search_field: List[SearchField] = Field(
        default=[SearchField.PROJECT_TITLE, SearchField.ABSTRACT, SearchField.TERMS],
        description=(
            "One or more fields to search within. Choose any combination of: "
            "'projecttitle' (project title), 'abstract' (project abstract), "
            "'terms' (indexed NIH scientific terms). Defaults to all three."
        )
    )
    search_text: str = Field(
        ..., 
        description="Text to search for"
    )

    @field_validator("search_field", mode="before")
    def coerce_fields(cls, v):
        """Allow lists of strings or enums; convert everything to list of SearchField if possible."""
        if isinstance(v, str):
            v = [v]  # single string -> list
        if isinstance(v, list):
            out = []
            for f in v:
                if isinstance(f, SearchField):
                    out.append(f)
                elif isinstance(f, str):
                    f_lower = f.lower()
                    # match string to enum value
                    for field in SearchField:
                        if f_lower == field.value:
                            out.append(field)
                            break
                    else:
                        # leave as plain string if not matched
                        out.append(f)
                else:
                    out.append(f)
            return out
        return v

class ProjectNum(BaseModel):
    project_num: str = Field(
        ..., 
        description="Unique project identifier assigned by NIH RePORTER",
        min_length=1,
        examples=["1F32AG052995-01A1", "7R01DA034777-04", "1F32DK109635-01A1"]
    )

    @field_validator('project_num')
    @classmethod
    def validate_project_num(cls, v: str) -> str:
        # Remove any whitespace
        v = v.strip()
        
        # This is a loose check since formats can vary
        if not v:
            raise ValueError("Project number cannot be empty")
        
        return v.upper()  # Normalize to uppercase

class FundingMechanism(str, Enum):
    """NIH funding mechanism categories for budget tables."""
    NON_SBIR_STTR_RESEARCH = "RP"
    SBIR_STTR_RESEARCH = "SB"
    RESEARCH_CENTERS = "RC"
    OTHER_RESEARCH = "OR"
    TRAINING_INDIVIDUAL = "TR"
    TRAINING_INSTITUTIONAL = "TI"
    CONSTRUCTION = "CO"
    NON_SBIR_STTR_CONTRACTS = "NSRDC"
    SBIR_STTR_CONTRACTS = "SRDC"
    INTERAGENCY = "IAA"
    INTRAMURAL = "IM"
    OTHER = "Other"

    @property
    def description(self) -> str:
        return FUNDING_MECHANISM_DESCRIPTIONS.get(self.value, self.value)


class ApplicationType(str, Enum):
    """Single-digit code identifying the type of NIH grant application."""
    NEW = "1"
    COMPETING_CONTINUATION = "2"
    SUPPLEMENTAL = "3"
    COMPETING_EXTENSION = "4C"
    NONCOMPETING_EXTENSION = "4N"
    NONCOMPETING_CONTINUATION = "5"
    CHANGE_OF_INSTITUTION = "7"
    CHANGE_OF_DIVISION = "9"


class POName(BaseModel):
    """Program Officer name search criteria. All fields are wildcard-enabled partial match."""
    any_name: Optional[str] = Field(None, description="Search across all name fields (first, last, full name)")
    first_name: Optional[str] = Field(None, description="Program Officer first name")
    last_name: Optional[str] = Field(None, description="Program Officer last name")

class SpendingCategoriesFilter(BaseModel):
    """Filter grants by NIH spending category IDs from Appendix I (FY2024)."""
    values: List[int] = Field(
        ...,
        description="One or more NIH spending category numeric IDs (e.g. [27, 31])"
    )
    match_all: bool = Field(
        default=False,
        description="If true, project must match all provided categories. If false, match at least one."
    )

    @field_validator("values")
    @classmethod
    def validate_values(cls, values: List[int]) -> List[int]:
        if not values:
            raise ValueError("spending_categories.values must include at least one category ID")
        invalid = sorted({v for v in values if v not in SPENDING_CATEGORY_IDS_FY2024})
        if invalid:
            raise ValueError(f"Invalid spending category ID(s): {invalid}")

        # Remove duplicates while preserving user-provided order.
        seen = set()
        deduped = []
        for v in values:
            if v not in seen:
                seen.add(v)
                deduped.append(v)
        return deduped


class SearchParams(BaseModel):
    # optional filters
    advanced_text_search: Optional[AdvancedTextSearch] = Field(None, description="text search string and search parameters")
    years: Optional[List[int]] = Field(None, description="List of fiscal years where projects are active (e.g. [2023, 2024])")
    agencies: Optional[List[NIHAgency]] = Field([NIHAgency.NIH], description="the agency providing funding for the grant")
    organizations: Optional[List[str]] = Field(None, description="List of organization names who received funding (e.g. ['Johns Hopkins University'])")
    pi_name: Optional[str] = Field(None, description="Name of the grant's principal investigator (e.g. 'Allyson Sgro')")
    po_names: Optional[List[POName]] = Field(None, description="List of program officer name criteria to filter by (e.g. [{'any_name': 'Smith'}])")
    project_nums: Optional[List[ProjectNum]] = Field(None, description="Unique project identifier(s) assigned by NIH RePORTER (e.g. '1F32AG052995-01A1')")
    org_states: Optional[List[StateCode]] = Field(None, description="Organization state")
    opportunity_numbers: Optional[List[str]] = Field(None, description="Funding opportunity number(s) associated with the grant (e.g. 'PAR-21-293')")
    activity_codes: Optional[List[str]] = Field(None, description="Activity codes associated with the grant (e.g. 'R01', 'F32')")
    funding_mechanisms: Optional[List[FundingMechanism]] = Field(None, description="Funding mechanism categories (e.g. ['RP', 'RC'])")
    award_types: Optional[List[ApplicationType]] = Field(None, description="Application type codes to filter by (e.g. ['1', '2'] for new and competing continuation)")
    spending_categories: Optional[SpendingCategoriesFilter] = Field(
        None,
        description="NIH spending category IDs with match behavior (e.g. {'values': [27, 31], 'match_all': false})"
    )

    def to_api_criteria(self):
        """Convert to API criteria format"""
        criteria = {}
        
        # Add advanced text search if provided
        if self.advanced_text_search:
            ats = self.advanced_text_search
            sf = ats.search_field

            # Normalize to the comma-separated string the API expects
            if isinstance(sf, list):
                search_field_str = ", ".join(
                    s.value if isinstance(s, SearchField) else str(s) for s in sf
                )
            elif isinstance(sf, SearchField):
                search_field_str = sf.value
            else:
                # Already a string (or something else) — use as-is
                search_field_str = str(sf)

            criteria["advanced_text_search"] = {
                "search_text": ats.search_text,
                "search_field": search_field_str,
                "operator": ats.operator.value
            }

        # Add other filters
        if self.years:
            criteria["fiscal_years"] = self.years
        if self.agencies:
            criteria["agencies"] = [a.value if hasattr(a, 'value') else a for a in self.agencies]
        if self.organizations:
            criteria["org_names"] = self.organizations
        if self.pi_name:
            criteria["pi_names"] = [{"any_name": self.pi_name}]
        if self.po_names:
            criteria["po_names"] = [
                {k: v for k, v in po.model_dump().items() if v is not None}
                for po in self.po_names
            ]
        if self.project_nums:
            criteria["project_nums"] = [a.project_num for a in self.project_nums]
        if self.org_states:
            criteria["org_states"] = [a.value if hasattr(a, 'value') else a for a in self.org_states]
        if self.opportunity_numbers:
            criteria["opportunity_numbers"] = self.opportunity_numbers
        if self.activity_codes:
            criteria["activity_codes"] = self.activity_codes
        if self.funding_mechanisms:
            criteria["funding_mechanism"] = [a.value if hasattr(a, 'value') else a for a in self.funding_mechanisms]
        if self.award_types:
            criteria["award_types"] = [a.value if hasattr(a, 'value') else a for a in self.award_types]
        if self.spending_categories:
            criteria["spending_categories"] = {
                "values": self.spending_categories.values,
                "match_all": self.spending_categories.match_all,
            }

        return criteria
    




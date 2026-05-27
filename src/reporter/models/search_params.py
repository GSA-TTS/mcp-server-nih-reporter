from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from reporter.models.funding_mechanism import FundingMechanism
from reporter.models.nih_agency import NIHAgency
from reporter.models.state_code import StateCode
from reporter.models.application_type import ApplicationType 
from reporter.models.advanced_text_search import AdvancedTextSearch, SearchField
from reporter.models.spending_categories import SpendingCategoriesFilter 
from reporter.models.po_name import POName

class SearchParams(BaseModel):
    # optional filters
    advanced_text_search: Optional[AdvancedTextSearch] = Field(None, description="text search string and search parameters")
    years: Optional[List[int]] = Field(None, description="List of fiscal years where projects are active (e.g. [2023, 2024])")
    agencies: Optional[List[NIHAgency]] = Field([NIHAgency.NIH], description="the agency providing funding for the grant")
    organizations: Optional[List[str]] = Field(None, description="List of organization names who received funding (e.g. ['Johns Hopkins University'])")
    pi_name: Optional[str] = Field(None, description="Name of the grant's principal investigator (e.g. 'Allyson Sgro')")
    po_names: Optional[List[POName]] = Field(None, description="List of program officer name criteria to filter by (e.g. [{'any_name': 'Smith'}])")
    project_nums: Optional[List[str]] = Field(None, description="Unique project identifier(s) assigned by NIH RePORTER (e.g. '1F32AG052995-01A1')")
    org_states: Optional[List[StateCode]] = Field(None, description="Organization state")
    opportunity_numbers: Optional[List[str]] = Field(None, description="Funding opportunity number(s) associated with the grant (e.g. 'PAR-21-293')")
    activity_codes: Optional[List[str]] = Field(None, description="Activity codes associated with the grant (e.g. 'R01', 'F32')")
    funding_mechanisms: Optional[List[FundingMechanism]] = Field(None, description="Funding mechanism categories (e.g. ['RP', 'RC'])")
    award_types: Optional[List[ApplicationType]] = Field(None, description="Application type codes to filter by (e.g. ['1', '2'] for new and competing continuation)")
    spending_categories: Optional[SpendingCategoriesFilter] = Field(None, description="Filter projects by NIH Appendix I spending category. Use `search_spending_categories` to look up category IDs before populating this field.")

    @field_validator("agencies", mode="before")
    @classmethod
    def coerce_agencies(cls, value):
        """Allow callers to pass a single agency code instead of a list."""
        if value is None:
            return value
        if isinstance(value, (str, NIHAgency)):
            return [value]
        return value

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
            criteria["project_nums"] = self.project_nums
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
    




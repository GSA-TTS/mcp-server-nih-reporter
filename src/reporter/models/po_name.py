from pydantic import BaseModel, Field
from typing import Optional

class POName(BaseModel):
    """Program Officer name search criteria. All fields are wildcard-enabled partial match."""
    any_name: Optional[str] = Field(None, description="Search across all name fields (first, last, full name)")
    first_name: Optional[str] = Field(None, description="Program Officer first name")
    last_name: Optional[str] = Field(None, description="Program Officer last name")

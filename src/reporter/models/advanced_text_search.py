from enum import Enum 
from typing import List
from pydantic import BaseModel, Field, field_validator

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
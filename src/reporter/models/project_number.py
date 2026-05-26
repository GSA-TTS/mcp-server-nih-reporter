from pydantic import BaseModel, Field, field_validator

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
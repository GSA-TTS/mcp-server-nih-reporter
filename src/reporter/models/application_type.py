from enum import Enum 

class ApplicationType(str, Enum):
    """Single-digit code identifying the type of NIH grant application.
    
    Application types indicate the stage and nature of the funding request,
    from initial submissions to renewals, revisions, and institutional changes.

    Reference the nih-application-types skill for full details of each code.
    """
    
    NEW = "1"
    COMPETING_CONTINUATION = "2"
    SUPPLEMENTAL = "3"
    COMPETING_EXTENSION = "4C"
    NONCOMPETING_EXTENSION = "4N"
    NONCOMPETING_CONTINUATION = "5"
    CHANGE_OF_ORG_STATUS = "6"
    CHANGE_OF_INSTITUTION = "7"
    CHANGE_OF_IC_NONCOMPETING = "8"
    CHANGE_OF_DIVISION = "9"

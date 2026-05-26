from enum import Enum 

class ApplicationType(str, Enum):
    """Single-digit code identifying the type of NIH grant application.
    
    Application types indicate the stage and nature of the funding request,
    from initial submissions to renewals, revisions, and institutional changes.
    """
    
    NEW = "1"
    """Type 1 - New: Initial request for support of a project that has not yet 
    been funded."""
    
    COMPETING_CONTINUATION = "2"
    """Type 2 - Renewal: Initial request for additional funding for a period 
    subsequent to that provided by a current award. Renewal applications compete 
    for funding with all other peer reviewed applications and must be developed 
    as fully as though the applicant is applying for the first time. (Previously 
    referred to as "competing continuation.") If your renewal and subsequent 
    resubmission of renewal application are not funded, you must use the "new" 
    application type to compete for additional funding and continuity with your 
    previous award will not be retained."""
    
    SUPPLEMENTAL = "3"
    """Type 3 - Competing Revision: Initial request for (or the award of) 
    additional funds during a current project period to support new or additional 
    activities that are not identified in the current award. This request reflects 
    an expansion of the scope of the grant-approved activities. Competitive 
    revisions require peer review. (Competing revision replaces the previous NIH 
    term, "competing supplement.")"""
    
    COMPETING_EXTENSION = "4C"
    """Type 4 - Extension: Request for additional years of support beyond the 
    years previously awarded. (Used only for select programs.)"""
    
    NONCOMPETING_EXTENSION = "4N"
    """Type 4 - Extension: Request for additional years of support beyond the 
    years previously awarded. (Used only for select programs.)"""
    
    NONCOMPETING_CONTINUATION = "5"
    """Type 5 - Noncompeting Continuation: Request or award for a subsequent 
    budget period within a previously approved project for which a recipient 
    does not have to compete with other applications."""
    
    CHANGE_OF_ORG_STATUS = "6"
    """Type 6 - Change of Organization Status (Successor-in-Interest): Process 
    whereby the rights to and obligations under an NIH grant(s) are acquired 
    incidental to the transfer of all of the assets of the recipient or the 
    transfer of that part of the assets involved in the performance of the grant(s)."""
    
    CHANGE_OF_INSTITUTION = "7"
    """Type 7 - Change of Recipient or Training Institution: Transfer of the 
    legal and administrative responsibility for a grant-supported project or 
    activity from one legal entity to another before the completion date of 
    the approved project period (competitive segment)."""

    CHANGE_OF_IC_NONCOMPETING = "8"
    """Type 8 - Change of Institute or Center: Change of awarding NIH institute 
    or center for the noncompeting continuation (Type 5)."""
    
    CHANGE_OF_DIVISION = "9"
    """Type 9 - Change of Institute or Center: Change of awarding NIH institute 
    or center for the renewal (Type 2)."""
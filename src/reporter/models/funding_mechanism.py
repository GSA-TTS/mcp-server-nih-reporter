from enum import Enum

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


from enum import Enum

class NIHAgency(str, Enum):
    """NIH institutes and centers that fund research grants."""
    
    CLC = "CLC"
    """Clinical Center"""
    
    CSR = "CSR"
    """Center for Scientific Review"""
    
    CIT = "CIT"
    """Center for Information Technology"""
    
    FIC = "FIC"
    """John E. Fogarty International Center"""
    
    NCATS = "NCATS"
    """National Center for Advancing Translational Sciences"""
    
    NCCIH = "NCCIH"
    """National Center for Complementary and Integrative Health"""
    
    NCI = "NCI"
    """National Cancer Institute"""
    
    NCRR = "NCRR"
    """National Center for Research Resources"""
    
    NEI = "NEI"
    """National Eye Institute"""
    
    NHGRI = "NHGRI"
    """National Human Genome Research Institute"""
    
    NHLBI = "NHLBI"
    """National Heart, Lung, and Blood Institute"""
    
    NIA = "NIA"
    """National Institute on Aging"""
    
    NIAAA = "NIAAA"
    """National Institute on Alcohol Abuse and Alcoholism"""
    
    NIAID = "NIAID"
    """National Institute of Allergy and Infectious Diseases"""
    
    NIAMS = "NIAMS"
    """National Institute of Arthritis and Musculoskeletal and Skin Diseases"""
    
    NIBIB = "NIBIB"
    """National Institute of Biomedical Imaging and Bioengineering"""
    
    NICHD = "NICHD"
    """Eunice Kennedy Shriver National Institute of Child Health and Human Development"""
    
    NIDA = "NIDA"
    """National Institute on Drug Abuse"""
    
    NIDCD = "NIDCD"
    """National Institute on Deafness and Other Communication Disorders"""
    
    NIDCR = "NIDCR"
    """National Institute of Dental and Craniofacial Research"""
    
    NIDDK = "NIDDK"
    """National Institute of Diabetes and Digestive and Kidney Diseases"""
    
    NIEHS = "NIEHS"
    """National Institute of Environmental Health Sciences"""
    
    NIGMS = "NIGMS"
    """National Institute of General Medical Sciences"""
    
    NIH = "NIH"
    """National Institutes of Health"""
    
    NIMH = "NIMH"
    """National Institute of Mental Health"""
    
    NIMHD = "NIMHD"
    """National Institute on Minority Health and Health Disparities"""
    
    NINDS = "NINDS"
    """National Institute of Neurological Disorders and Stroke"""
    
    NINR = "NINR"
    """National Institute of Nursing Research"""
    
    NLM = "NLM"
    """National Library of Medicine"""
    
    OD = "OD"
    """Office of the Director"""
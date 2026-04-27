from enum import Enum

NIH_AGENCY_FULL_NAMES: dict[str, str] = {
    "CLC": "Clinical Center",
    "CSR": "Center for Scientific Review",
    "CIT": "Center for Information Technology",
    "FIC": "John E. Fogarty International Center",
    "NCATS": "National Center for Advancing Translational Sciences",
    "NCCIH": "National Center for Complementary and Integrative Health",
    "NCI": "National Cancer Institute",
    "NCRR": "National Center for Research Resources",
    "NEI": "National Eye Institute",
    "NHGRI": "National Human Genome Research Institute",
    "NHLBI": "National Heart, Lung, and Blood Institute",
    "NIA": "National Institute on Aging",
    "NIAAA": "National Institute on Alcohol Abuse and Alcoholism",
    "NIAID": "National Institute of Allergy and Infectious Diseases",
    "NIAMS": "National Institute of Arthritis and Musculoskeletal and Skin Diseases",
    "NIBIB": "National Institute of Biomedical Imaging and Bioengineering",
    "NICHD": "Eunice Kennedy Shriver National Institute of Child Health and Human Development",
    "NIDA": "National Institute on Drug Abuse",
    "NIDCD": "National Institute on Deafness and Other Communication Disorders",
    "NIDCR": "National Institute of Dental and Craniofacial Research",
    "NIDDK": "National Institute of Diabetes and Digestive and Kidney Diseases",
    "NIEHS": "National Institute of Environmental Health Sciences",
    "NIGMS": "National Institute of General Medical Sciences",
    "NIH": "National Institutes of Health",
    "NIMH": "National Institute of Mental Health",
    "NIMHD": "National Institute on Minority Health and Health Disparities",
    "NINDS": "National Institute of Neurological Disorders and Stroke",
    "NINR": "National Institute of Nursing Research",
    "NLM": "National Library of Medicine",
    "OD": "Office of the Director",
}


class NIHAgency(Enum):
    CLC = "CLC"
    CSR = "CSR"
    CIT = "CIT"
    FIC = "FIC"
    NCATS = "NCATS"
    NCCIH = "NCCIH"
    NCI = "NCI"
    NCRR = "NCRR"
    NEI = "NEI"
    NHGRI = "NHGRI"
    NHLBI = "NHLBI"
    NIA = "NIA"
    NIAAA = "NIAAA"
    NIAID = "NIAID"
    NIAMS = "NIAMS"
    NIBIB = "NIBIB"
    NICHD = "NICHD"
    NIDA = "NIDA"
    NIDCD = "NIDCD"
    NIDCR = "NIDCR"
    NIDDK = "NIDDK"
    NIEHS = "NIEHS"
    NIGMS = "NIGMS"
    NIH = "NIH"
    NIMH = "NIMH"
    NIMHD = "NIMHD"
    NINDS = "NINDS"
    NINR = "NINR"
    NLM = "NLM"
    OD = "OD"

    @classmethod
    def get_full_name(cls, code: str) -> str:
        """Get the full name of an agency from its code."""
        return NIH_AGENCY_FULL_NAMES.get(code, code)

    @property
    def full_name(self) -> str:
        """Get the full name of this agency."""
        return self.get_full_name(self.value)

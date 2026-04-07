from __future__ import annotations

from typing import Any


PROJECTS_SEARCH_URL = "https://api.reporter.nih.gov/v2/projects/search"
PUBLICATIONS_SEARCH_URL = "https://api.reporter.nih.gov/v2/publications/search"


QUERY_SPECS: list[dict[str, Any]] = [
    {
        "question": "What is the total number of active R01 grants funded by the National Cancer Institute (NCI) in fiscal year 2024?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "count_results",
        "params": {
            "criteria": {"fiscal_years": [2024], "agencies": ["NCI"], "activity_codes": ["R01"]},
            "include_fields": ["ProjectNum"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "Which principal investigator received the highest total funding from NIH in fiscal year 2023 and what was the award amount?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "top_pi_by_total_funding",
        "params": {
            "criteria": {"fiscal_years": [2023], "agencies": ["NIH"]},
            "include_fields": ["ProjectNum", "PrincipalInvestigators", "AwardAmount"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "List all grants funded under the BRAIN Initiative in fiscal year 2024 along with their project titles and administering institutes.",
        "url": PROJECTS_SEARCH_URL,
        "processor": "list_projects_with_fields",
        "processor_kwargs": {"fields": ["project_num", "project_title", "agency_ic_admin.abbreviation"]},
        "params": {
            "criteria": {
                "fiscal_years": [2024],
                "advanced_text_search": {
                    "search_text": "\"BRAIN Initiative\"",
                    "search_field": "projecttitle, abstract, terms",
                    "operator": "or",
                },
            },
            "include_fields": ["ProjectNum", "ProjectTitle", "AgencyIcAdmin"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "How many awards did the National Institute on Aging (NIA) make to institutions in the state of Florida in fiscal year 2023?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "count_results",
        "params": {
            "criteria": {"fiscal_years": [2023], "agencies": ["NIA"], "org_states": ["FL"]},
            "include_fields": ["ProjectNum", "Organization", "AgencyIcAdmin"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "What is the abstract for NIH project number 1R01CA123456-01?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "extract_first_fields",
        "processor_kwargs": {"fields": ["project_num", "abstract_text"]},
        "params": {
            "criteria": {"project_nums": ["1R01CA123456-01"]},
            "include_fields": ["ProjectNum", "ProjectTitle", "AbstractText"],
            "offset": 0,
            "limit": 10,
        },
    },
    {
        "question": "Which universities received the most NIH funding in fiscal year 2023? Provide the top 5 institutions and their total award amounts.",
        "url": PROJECTS_SEARCH_URL,
        "processor": "top_groups_by_sum",
        "processor_kwargs": {"group_field": "organization.org_name", "value_field": "award_amount", "top_n": 5},
        "params": {
            "criteria": {"fiscal_years": [2023], "agencies": ["NIH"]},
            "include_fields": ["ProjectNum", "Organization", "AwardAmount"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "How many R21 exploratory research grants were awarded by NIMH in fiscal year 2022 and 2023 combined?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "count_results",
        "params": {
            "criteria": {"fiscal_years": [2022, 2023], "agencies": ["NIMH"], "activity_codes": ["R21"]},
            "include_fields": ["ProjectNum", "FiscalYear", "ActivityCode", "AgencyIcAdmin"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "Find all clinical trial grants (activity code ending in clinical trial designation) funded by NHLBI in fiscal year 2024.",
        "url": PROJECTS_SEARCH_URL,
        "processor": "list_projects_with_fields",
        "processor_kwargs": {
            "fields": ["project_num", "project_title", "activity_code", "agency_ic_admin.abbreviation"]
        },
        "params": {
            "criteria": {
                "fiscal_years": [2024],
                "agencies": ["NHLBI"],
                "advanced_text_search": {
                    "search_text": "\"clinical trial\"",
                    "search_field": "projecttitle, abstract, terms",
                    "operator": "or",
                },
            },
            "include_fields": ["ProjectNum", "ProjectTitle", "ActivityCode", "AgencyIcAdmin"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "What are the contact PI name, project title, and total award amount for grant number 5R01DK110234-05?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "extract_first_fields",
        "processor_kwargs": {"fields": ["project_num", "contact_pi_name", "project_title", "award_amount"]},
        "params": {
            "criteria": {"project_nums": ["5R01DK110234-05"]},
            "include_fields": ["ProjectNum", "ProjectTitle", "ContactPiName", "AwardAmount"],
            "offset": 0,
            "limit": 10,
        },
    },
    {
        "question": "Which NIH institutes awarded the most grants to minority-serving institutions (MSIs) in fiscal year 2023?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "top_groups_by_count",
        "processor_kwargs": {"group_field": "agency_ic_admin.abbreviation", "top_n": 10},
        "params": {
            "criteria": {
                "fiscal_years": [2023],
                "agencies": ["NIH"],
                "advanced_text_search": {
                    "search_text": "\"minority-serving institution\" OR MSI OR HBCU OR Hispanic-serving",
                    "search_field": "projecttitle, abstract, terms",
                    "operator": "advanced",
                },
            },
            "include_fields": ["ProjectNum", "AgencyIcAdmin", "Organization"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "How much total funding did Harvard University receive from NIH across all institutes in fiscal year 2024?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "sum_field",
        "processor_kwargs": {"field": "award_amount"},
        "params": {
            "criteria": {"fiscal_years": [2024], "agencies": ["NIH"], "org_names": ["Harvard University"]},
            "include_fields": ["ProjectNum", "Organization", "AwardAmount"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "What is the budget period end date and project period end date for grant 5U01AI150810-03?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "extract_first_fields",
        "processor_kwargs": {"fields": ["project_num", "budget_end", "project_end_date"]},
        "params": {
            "criteria": {"project_nums": ["5U01AI150810-03"]},
            "include_fields": ["ProjectNum", "BudgetEnd", "ProjectEndDate"],
            "offset": 0,
            "limit": 10,
        },
    },
    {
        "question": "List all grants related to Alzheimer's disease funded by NIA in fiscal year 2024 with award amounts over $500,000.",
        "url": PROJECTS_SEARCH_URL,
        "processor": "list_projects_with_fields",
        "processor_kwargs": {
            "fields": ["project_num", "project_title", "award_amount", "agency_ic_admin.abbreviation"],
            "min_value_field": "award_amount",
            "min_value": 500000,
        },
        "params": {
            "criteria": {
                "fiscal_years": [2024],
                "agencies": ["NIA"],
                "advanced_text_search": {
                    "search_text": "\"Alzheimer's disease\" OR Alzheimer",
                    "search_field": "projecttitle, abstract, terms",
                    "operator": "advanced",
                },
            },
            "include_fields": ["ProjectNum", "ProjectTitle", "AwardAmount", "AgencyIcAdmin"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "How many new (Type 1) R01 awards were made by NIAID in fiscal year 2023?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "count_results",
        "params": {
            "criteria": {
                "fiscal_years": [2023],
                "agencies": ["NIAID"],
                "activity_codes": ["R01"],
                "award_types": ["1"],
            },
            "include_fields": ["ProjectNum", "AwardType", "ActivityCode", "AgencyIcAdmin"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "What is the geographic distribution of NIH R01 grants in fiscal year 2024 - how many were awarded to each U.S. state?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "group_counts",
        "processor_kwargs": {"group_field": "organization.org_state"},
        "params": {
            "criteria": {"fiscal_years": [2024], "agencies": ["NIH"], "activity_codes": ["R01"]},
            "include_fields": ["ProjectNum", "Organization"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "Find all grants where the project title contains the term 'CRISPR' funded in fiscal year 2023 or 2024. What institutes funded them?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "list_projects_with_fields",
        "processor_kwargs": {"fields": ["project_num", "project_title", "agency_ic_admin.abbreviation"]},
        "params": {
            "criteria": {
                "fiscal_years": [2023, 2024],
                "advanced_text_search": {
                    "search_text": "CRISPR",
                    "search_field": "projecttitle",
                    "operator": "and",
                },
            },
            "include_fields": ["ProjectNum", "ProjectTitle", "AgencyIcAdmin"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "What is the average award amount for NIDA-funded R01 grants in fiscal year 2024?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "average_field",
        "processor_kwargs": {"field": "award_amount"},
        "params": {
            "criteria": {"fiscal_years": [2024], "agencies": ["NIDA"], "activity_codes": ["R01"]},
            "include_fields": ["ProjectNum", "AwardAmount"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "Which foreign institutions received NIH funding in fiscal year 2023 and what were the top 5 countries by total award amount?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "top_foreign_countries_by_funding",
        "processor_kwargs": {"top_n": 5},
        "params": {
            "criteria": {"fiscal_years": [2023], "agencies": ["NIH"]},
            "include_fields": ["ProjectNum", "Organization", "AwardAmount"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "How many grants funded under the NIH Common Fund were active in fiscal year 2024 and what programs did they belong to?",
        "url": PROJECTS_SEARCH_URL,
        "processor": "count_active_and_collect_terms",
        "processor_kwargs": {"term_field": "terms"},
        "params": {
            "criteria": {
                "fiscal_years": [2024],
                "advanced_text_search": {
                    "search_text": "\"Common Fund\"",
                    "search_field": "projecttitle, abstract, terms",
                    "operator": "or",
                },
            },
            "include_fields": ["ProjectNum", "ProjectTitle", "IsActive", "Terms"],
            "offset": 0,
            "limit": 500,
        },
    },
    {
        "question": "What is the publication count and list of associated publications linked to NIH project number 5R01GM130386-04?",
        "url": PUBLICATIONS_SEARCH_URL,
        "processor": "publication_count_and_titles",
        "params": {
            "criteria": {"core_project_nums": ["R01GM130386"]},
            "offset": 0,
            "limit": 100,
        },
    },
]

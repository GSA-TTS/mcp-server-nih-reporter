import requests
import asyncio
from reporter.models import SearchParams, IncludeField
from fastmcp import Context
import pandas as pd

# NIH Reporter API pagination limit
# The API cannot reliably paginate beyond offset ~15,000
# Queries returning more results will fail silently after this threshold
API_PAGINATION_LIMIT = 15000

# Maps response field keys (after clean_json) to the IncludeField needed to fetch them.
# org_name and org_state both come from the Organization include field.
DIMENSION_FIELDS = {
    "fiscal_year":       IncludeField.FISCAL_YEAR,
    "activity_code":     IncludeField.ACTIVITY_CODE,
    "funding_mechanism": IncludeField.FUNDING_MECHANISM,
    "agency_ic_admin":   IncludeField.AGENCY_IC_ADMIN,
    "org_name":          IncludeField.ORGANIZATION,
    "org_state":         IncludeField.ORGANIZATION,
    "organization_type": IncludeField.ORGANIZATION_TYPE,
    "award_type":        IncludeField.AWARD_TYPE,
}

def clean_json(response):
    """
    Cleans JSON response by simplyfing fields with subfields. 

    Args: 
        response (dict): JSON response from the NIH RePORTER API

    Returns: 
        dict: Cleaned JSON response
    """

    # simply JSON response 
    for project in response.get('results', []):
        
        # keep only the organization name and the state
        if project.get('organization'):
            project['org_name'] = project['organization']['org_name']
            project['org_state'] = project['organization']['org_state']
            del project['organization']
        
        # keep only the first part of the agency name
        if project.get('agency_ic_admin'):
            project['agency_ic_admin'] = project['agency_ic_admin']['abbreviation']

        # create list of principal investigators full names
        if project.get('principal_investigators'):
            project['principal_investigators'] = [pi['full_name'] for pi in project['principal_investigators']]

    return response 

def get_total_amount(response):
    """
    Calculates the total award amount from the API response.

    Args:
        response (dict): JSON response from the NIH RePORTER API

    Returns:
        float: Total award amount
    """
    
    if not response or 'results' not in response:
        return 0.0
    
    total_amount = sum(project.get('award_amount', 0) for project in response['results'])
    
    return str(total_amount)

async def search_nih_reporter(payload):
    """
    Search NIH Reporter API for grant information
    
    Args:
        payload (dict): Search criteria
    
    Returns:
        dict: API response containing grant data
    """
    
    # NIH Reporter API endpoint
    url = "https://api.reporter.nih.gov/v2/projects/search"
    
    try:
        # Run the synchronous requests call in a thread pool
        response = await asyncio.to_thread(
            requests.post, 
            url, 
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"NIH RePORTER API request failed: {e}")
    
async def paged_query(search_params:SearchParams, include_fields: list[str], limit=100, offset=0, all_results=None):
    """
    Perform the initial query to get the total number of projects matching the criteria.
    
    Args:
        search_params (SearchParams): Search parameters including years, agencies, organizations, and pi_name.
        limit (int): Number of results to return per request (max 500).
        offset (int): Offset for pagination.
        
    Returns:
        dict: API response containing grant data
    """
    
    payload = {
        "criteria": search_params.to_api_criteria(),
        "offset": offset,
        "limit": limit,
        "include_fields": include_fields,
        "sort_field": "project_start_date",
        "sort_order": "desc"
    }

    response = await search_nih_reporter(payload)

    if response is None:
        raise Exception("NIH RePORTER API request failed - no response received")

    response = clean_json(response)

    total_responses = response['meta']['total']
    
    # if initial call, create empty list to collect results
    if all_results is None:
        all_results = {
            'meta': response['meta'],
            'results': []
        }

    # Collect results from first request
    all_results['results'].extend(response.get('results', []))

    return total_responses, all_results

async def get_initial_response(search_params:SearchParams, include_fields: list[str], limit=100):
    
    offset = 0 
    total_responses, all_results = await paged_query(search_params, include_fields, limit, offset)

    return total_responses, all_results

async def get_result_count(search_params: SearchParams) -> int:
    """
    Get the total number of results for a query without fetching data.
    Makes a lightweight API call with limit=1 to retrieve just the count.
    
    Args:
        search_params: Search parameters
        
    Returns:
        int: Total number of matching results
    """
    payload = {
        "criteria": search_params.to_api_criteria(),
        "offset": 0,
        "limit": 1,
        "include_fields": [IncludeField.PROJECT_NUM.value],
        "sort_field": "project_start_date",
        "sort_order": "desc"
    }
    
    response = await search_nih_reporter(payload)
    
    if response is None:
        raise Exception("NIH RePORTER API request failed - no response received")
    
    return response['meta']['total']

def slice_query_by_years(search_params: SearchParams):
    """
    Split a SearchParams into separate queries, one per fiscal year.
    
    Args:
        search_params: Original search parameters
        
    Returns:
        List of SearchParams, each with a single fiscal year
        
    Example:
        Input: SearchParams(years=[2020, 2021, 2022], agencies=["NCI"])
        Output: [
            SearchParams(years=[2020], agencies=["NCI"]),
            SearchParams(years=[2021], agencies=["NCI"]),
            SearchParams(years=[2022], agencies=["NCI"])
        ]
    """
    if not search_params.years or len(search_params.years) <= 1:
        return [search_params]
    
    sliced_params = []
    for year in search_params.years:
        # Create a copy with single year
        params_dict = search_params.model_dump()
        params_dict['years'] = [year]
        sliced_params.append(SearchParams(**params_dict))
    
    return sliced_params

def slice_query_by_ics(search_params: SearchParams):
    """
    Split a SearchParams into separate queries, one per NIH IC.
    
    Args:
        search_params: Original search parameters
        
    Returns:
        List of SearchParams, each with a single IC
        
    Notes:
        - If agencies is None or [NIHAgency.NIH], splits across all 30 ICs
        - If specific agencies specified, splits across those ICs only
    """
    from reporter.models.nih_agency import NIHAgency
    
    # Get list of all ICs from the enum
    all_ics = list(NIHAgency)
    
    # Determine which ICs to iterate over
    if not search_params.agencies or NIHAgency.NIH in search_params.agencies:
        # Query all ICs
        ics_to_query = all_ics
    else:
        # Use the specified ICs
        ics_to_query = search_params.agencies
    
    if len(ics_to_query) <= 1:
        return [search_params]
    
    sliced_params = []
    for ic in ics_to_query:
        # Create a copy with single IC
        params_dict = search_params.model_dump()
        params_dict['agencies'] = [ic]
        sliced_params.append(SearchParams(**params_dict))
    
    return sliced_params

def slice_query_by_year_and_ic(search_params: SearchParams):
    """
    Split a SearchParams into separate queries for each (year, IC) combination.
    
    Args:
        search_params: Original search parameters
        
    Returns:
        List of SearchParams, each with a single year and single IC
        
    Example:
        Input: SearchParams(years=[2023, 2024], agencies=["NCI", "NHLBI"])
        Output: [
            SearchParams(years=[2023], agencies=["NCI"]),
            SearchParams(years=[2023], agencies=["NHLBI"]),
            SearchParams(years=[2024], agencies=["NCI"]),
            SearchParams(years=[2024], agencies=["NHLBI"])
        ]
    """
    # Get year slices
    year_slices = slice_query_by_years(search_params)
    
    # For each year slice, further slice by IC
    combined_slices = []
    for year_slice in year_slices:
        ic_slices = slice_query_by_ics(year_slice)
        combined_slices.extend(ic_slices)
    
    return combined_slices

async def get_max_slice_count(sliced_params) -> int:
    """
    Find the maximum result count among a list of sliced queries.
    
    Args:
        sliced_params: List of SearchParams to check
        
    Returns:
        int: Maximum result count across all slices
        
    Notes:
        Makes lightweight count queries for each slice to validate
        that slicing will successfully bring queries under the limit.
    """
    max_count = 0
    
    for i, params in enumerate(sliced_params, 1):
        count = await get_result_count(params)
        print(f"  Checking slice {i}/{len(sliced_params)}: {count:,} results", end="")
        
        if count > max_count:
            max_count = count
        
        # Show status indicator
        if count > API_PAGINATION_LIMIT:
            print(" ✗ (exceeds limit)")
        else:
            print(" ✓")
    
    return max_count

async def fetch_sliced_query(
    search_params: SearchParams,
    include_fields: list[str],
    limit: int = 500
) -> list:
    """
    Fetch all results for a single query (assumed to be under API limit).
    This is the core pagination logic extracted from get_all_responses.
    
    Args:
        search_params: Search parameters (should return < 15K results)
        include_fields: Fields to include
        limit: Page size (default 500)
        
    Returns:
        list: All results for this query
    """
    offset = 0
    total_responses, all_results = await paged_query(
        search_params, include_fields, limit, offset
    )
    
    # Loop through remaining pages
    while offset + limit < total_responses:
        offset += limit
        print(f"    Fetching page {(offset // limit) + 1}/{(total_responses // limit) + 1}...")
        total_responses, all_results = await paged_query(
            search_params, include_fields, limit, offset, all_results
        )
    
    return all_results['results']

async def fetch_and_merge_sliced_queries(
    sliced_params,
    include_fields: list[str],
    limit: int = 500
) -> dict:
    """
    Fetch results for multiple SearchParams queries and merge them.
    
    Args:
        sliced_params: List of SearchParams to query separately
        include_fields: Fields to include in each query
        limit: Page size for each query
        
    Returns:
        dict: Merged results with 'meta' and 'results' keys
        
    Notes:
        Executes queries sequentially to avoid rate limits.
        Logs detailed progress for each sub-query.
    """
    all_results = []
    total_fetched = 0
    
    print(f"\nFetching {len(sliced_params)} slices sequentially...")
    
    for i, params in enumerate(sliced_params, 1):
        print(f"\n📊 Fetching slice {i}/{len(sliced_params)}...")
        
        # Fetch this slice
        slice_results = await fetch_sliced_query(params, include_fields, limit)
        
        all_results.extend(slice_results)
        total_fetched += len(slice_results)
        
        print(f"  ✓ Fetched slice {i}/{len(sliced_params)}: {len(slice_results):,} results (total so far: {total_fetched:,})")
    
    print(f"\n✓ Successfully retrieved {total_fetched:,} total results from {len(sliced_params)} slices")
    
    return {
        'meta': {
            'total': total_fetched,
            'sliced': True,
            'slice_count': len(sliced_params)
        },
        'results': all_results
    }

async def get_all_responses(
    search_params: SearchParams, 
    include_fields: list[str], 
    limit: int = 500,
    auto_slice: bool = True
) -> dict:
    """
    Fetch all results for a search query via pagination.
    
    Automatically slices queries exceeding the API pagination limit into smaller
    sub-queries based on fiscal years and/or NIH institutes/centers (ICs).
    
    Args:
        search_params: Search parameters to query
        include_fields: Fields to include in response
        limit: Number of results per page (default 500, max 500)
        auto_slice: If True, automatically slice queries exceeding 15K results (default True)
        
    Returns:
        dict: All results with 'meta' and 'results' keys
        
    Raises:
        ValueError: If total results exceed API_PAGINATION_LIMIT and:
            - auto_slice is False, OR
            - Even after slicing, individual slices still exceed limit
        
    Notes:
        The NIH Reporter API has a pagination limit of ~15,000 results.
        
        When auto_slice is enabled (default), queries exceeding this limit are
        automatically split using the following strategies (in order):
        
        1. Fiscal Year Slicing: Split by individual years if multiple years specified
        2. IC Slicing: Split by NIH institute/center (all 30 ICs)
        3. Combined Slicing: Split by (year × IC) combinations
        
        Sliced queries are executed sequentially and results are merged transparently.
        This ensures complete data retrieval for broad queries, though it may take
        longer for queries spanning many years and institutes.
    """
    
    # Step 1: Get initial count
    print("Checking total result count...")
    total_count = await get_result_count(search_params)
    print(f"Total results: {total_count:,}")
    
    # Step 2: If under limit, use original pagination logic
    if total_count <= API_PAGINATION_LIMIT:
        print(f"✓ Result count {total_count:,} is within API pagination limit")
        
        offset = 0 
        total_responses, all_results = await paged_query(search_params, include_fields, limit, offset)
        
        # Loop through remaining pages
        while offset + limit < total_responses:
            offset += limit
            print(f"Fetching results {offset} to {offset + limit}...")
            total_responses, all_results = await paged_query(search_params, include_fields, limit, offset, all_results)
        
        print(f"Retrieved {len(all_results['results'])} total results")
        return all_results
    
    # Step 3: Query exceeds limit - check if slicing is enabled
    print(f"⚠️  Query exceeds API pagination limit of {API_PAGINATION_LIMIT:,}")
    
    if not auto_slice:
        raise ValueError(
            f"Query returned {total_count:,} results, which exceeds the API "
            f"pagination limit of {API_PAGINATION_LIMIT:,}. The API cannot retrieve "
            f"results beyond this threshold. Please refine your search criteria:\n"
            f"  • Narrow the fiscal year range (e.g., 2020-2023 instead of 2000-2024)\n"
            f"  • Specify agencies/institutes (e.g., agencies=['NCI'])\n"
            f"  • Add organization filters (e.g., org_names=['Harvard'])\n"
            f"  • Add PI name filters (e.g., pi_names=['Smith'])\n"
            f"  • Use spending category filters for topical searches\n"
            f"  • Add award type filters (e.g., award_types=['R01'])\n\n"
            f"Alternatively, enable auto_slice=True to automatically split the query."
        )
    
    # Step 4: Attempt Strategy 1 - Slice by Year
    if search_params.years and len(search_params.years) > 1:
        print(f"\n🔄 Strategy 1: Attempting year-based slicing...")
        sliced_params = slice_query_by_years(search_params)
        print(f"   Split into {len(sliced_params)} year-based slices")
        
        max_slice_count = await get_max_slice_count(sliced_params)
        
        if max_slice_count <= API_PAGINATION_LIMIT:
            print(f"✓ Year-based slicing successful (largest slice: {max_slice_count:,})")
            return await fetch_and_merge_sliced_queries(sliced_params, include_fields, limit)
        else:
            print(f"✗ Year-based slicing insufficient (largest slice: {max_slice_count:,} > {API_PAGINATION_LIMIT:,})")
    
    # Step 5: Attempt Strategy 2 - Slice by IC
    print(f"\n🔄 Strategy 2: Attempting IC-based slicing...")
    sliced_params = slice_query_by_ics(search_params)
    print(f"   Split into {len(sliced_params)} IC-based slices")
    
    max_slice_count = await get_max_slice_count(sliced_params)
    
    if max_slice_count <= API_PAGINATION_LIMIT:
        print(f"✓ IC-based slicing successful (largest slice: {max_slice_count:,})")
        return await fetch_and_merge_sliced_queries(sliced_params, include_fields, limit)
    else:
        print(f"✗ IC-based slicing insufficient (largest slice: {max_slice_count:,} > {API_PAGINATION_LIMIT:,})")
    
    # Step 6: Attempt Strategy 3 - Slice by Year × IC
    print(f"\n🔄 Strategy 3: Attempting combined year+IC slicing...")
    sliced_params = slice_query_by_year_and_ic(search_params)
    print(f"   Split into {len(sliced_params)} combined (year×IC) slices")
    
    max_slice_count = await get_max_slice_count(sliced_params)
    
    if max_slice_count <= API_PAGINATION_LIMIT:
        print(f"✓ Combined slicing successful (largest slice: {max_slice_count:,})")
        return await fetch_and_merge_sliced_queries(sliced_params, include_fields, limit)
    else:
        print(f"✗ Combined slicing insufficient (largest slice: {max_slice_count:,} > {API_PAGINATION_LIMIT:,})")
    
    # Step 7: All strategies failed - raise detailed error
    raise ValueError(
        f"Query returned {total_count:,} results, exceeding the API "
        f"pagination limit of {API_PAGINATION_LIMIT:,}. Even after attempting "
        f"automatic slicing by year and IC, individual slices still exceed the limit.\n\n"
        f"Largest slice had {max_slice_count:,} results (limit: {API_PAGINATION_LIMIT:,}).\n\n"
        f"This indicates an extremely broad query. Please add additional filters:\n"
        f"  • Add organization filters (e.g., org_names=['Harvard University'])\n"
        f"  • Add PI name filters (e.g., pi_names=['Smith'])\n"
        f"  • Use spending category filters for topical searches\n"
        f"  • Add activity code filters (e.g., activity_codes=['R01'])\n"
        f"  • Add award type filters (e.g., award_types=['1'])\n"
        f"  • Narrow the fiscal year range further\n"
        f"  • Specify fewer institutes/centers"
    )

    return all_results

def build_crosstab(all_results, row_field, col_field):
    """
    Build a cross-tabulation of grant counts and total funding by any two project fields.

    Args:
        all_results (dict): API response containing grant data.
        row_field (str): Response field key to use as rows (e.g. "fiscal_year", "org_state").
        col_field (str): Response field key to use as columns (e.g. "activity_code", "funding_mechanism").

    Returns:
        dict: Nested dict of {row: {col: {"count": N, "total_funding": X}}}, sorted by row.
    """
    from collections import defaultdict

    crosstab = defaultdict(lambda: defaultdict(lambda: {"count": 0, "total_funding": 0}))

    for r in all_results.get("results", []):
        if not isinstance(r, dict):
            continue
        row = r.get(row_field)
        col = r.get(col_field)
        if row and col:
            crosstab[row][col]["count"] += 1
            crosstab[row][col]["total_funding"] += r.get("award_amount") or 0

    return {row: dict(cols) for row, cols in sorted(crosstab.items(), key=lambda x: str(x[0]))}


def get_project_distributions(all_results):
    """
    Calculate distributions of project years, institutes, activity codes,
    organizations, funding mechanisms, active status, and award amounts.

    Args:
        all_results (dict): API response containing grant data
    Returns:
        dict: Dictionary containing:
            - project_ids: List of project ID strings
            - year_distribution: Counter of fiscal years
            - institute_distribution: Counter of NIH institutes/centers
            - activity_code_distribution: Counter of activity codes
            - organization_distribution: Counter of organization names
            - funding_mechanism_distribution: Counter of funding mechanisms
            - active_status_distribution: Counter of active/inactive status
            - award_amount_stats: Dict with total, average, min, max award amounts
    """

    results = all_results.get("results", [])

    # Extract project IDs
    project_ids = []
    for r in results:
        if isinstance(r, dict) and r.get("project_num"):
            project_ids.append(r.get("project_num"))

    # Calculate distributions
    from collections import Counter

    # Year distribution - only process dict results
    year_dist = Counter(
        r.get("fiscal_year")
        for r in results
        if isinstance(r, dict) and r.get("fiscal_year")
    )

    # Institute/Center distribution
    ic_dist = Counter(
        r.get("agency_ic_admin")
        for r in results
        if isinstance(r, dict) and r.get("agency_ic_admin")
    )

    # Activity code distribution
    activity_dist = Counter(
        r.get("activity_code")
        for r in results
        if isinstance(r, dict) and r.get("activity_code")
    )

    # Organization distribution (uses org_name from clean_json)
    org_dist = Counter(
        r.get("org_name")
        for r in results
        if isinstance(r, dict) and r.get("org_name")
    )

    # Funding mechanism distribution
    funding_mech_dist = Counter(
        r.get("funding_mechanism")
        for r in results
        if isinstance(r, dict) and r.get("funding_mechanism")
    )

    # Active status distribution
    active_dist = Counter(
        "Active" if r.get("is_active") else "Inactive"
        for r in results
        if isinstance(r, dict) and r.get("is_active") is not None
    )

    # Award amount statistics
    award_amounts = [
        r.get("award_amount")
        for r in results
        if isinstance(r, dict) and r.get("award_amount") is not None
    ]

    if award_amounts:
        award_stats = {
            "total": sum(award_amounts),
            "average": sum(award_amounts) / len(award_amounts),
            "min": min(award_amounts),
            "max": max(award_amounts),
            "count": len(award_amounts)
        }
    else:
        award_stats = {
            "total": 0,
            "average": 0,
            "min": 0,
            "max": 0,
            "count": 0
        }

    # PI distribution — count projects and sum funding per PI
    pi_project_count = Counter()
    pi_total_funding = Counter()

    for r in results:
        if not isinstance(r, dict):
            continue
        award = r.get("award_amount") or 0
        pis = r.get("principal_investigators")
        if pis:
            for pi in pis:
                pi_project_count[pi] += 1
                pi_total_funding[pi] += award
        elif r.get("contact_pi_name"):
            pi = r["contact_pi_name"]
            pi_project_count[pi] += 1
            pi_total_funding[pi] += award

    return {
        "project_ids": project_ids,
        "year_distribution": year_dist,
        "institute_distribution": ic_dist,
        "activity_code_distribution": activity_dist,
        "organization_distribution": org_dist,
        "funding_mechanism_distribution": funding_mech_dist,
        "active_status_distribution": active_dist,
        "award_amount_stats": award_stats,
        "pi_distribution": pi_project_count,
        "pi_funding": pi_total_funding,
    }



def get_project_distributions_df(all_results):
    """
    Parse API response containing grant data and return a pandas DataFrame.

    Args:
        all_results (dict): API response containing grant data with a "results" key
    
    Returns:
        pd.DataFrame: DataFrame with one row per grant containing:
            - project_num: Project ID string
            - fiscal_year: Fiscal year of the grant
            - agency_ic_admin: NIH institute/center
            - activity_code: Activity code
            - org_name: Organization name
            - funding_mechanism: Funding mechanism
            - is_active: Boolean for active status
            - active_status: String ("Active" or "Inactive")
            - award_amount: Award amount (numeric)
            - principal_investigators: Semicolon-separated string of PIs
            - contact_pi_name: Primary contact PI name
            - pi_count: Number of principal investigators
    """
    
    results = all_results.get("results", [])
    
    # Filter to only dict results
    valid_results = [r for r in results if isinstance(r, dict)]
    
    # Build list of records for DataFrame
    records = []
    for r in valid_results:
        # Handle principal investigators
        pis = r.get("principal_investigators")
        if pis and isinstance(pis, list):
            pi_string = "; ".join(str(pi) for pi in pis)
            pi_count = len(pis)
        else:
            pi_string = None
            pi_count = 0
        
        # Get contact PI
        contact_pi = r.get("contact_pi_name")
        
        # Determine active status string
        is_active = r.get("is_active")
        active_status = None
        if is_active is not None:
            active_status = "Active" if is_active else "Inactive"
        
        record = {
            "project_num": r.get("project_num"),
            "fiscal_year": r.get("fiscal_year"),
            "agency_ic_admin": r.get("agency_ic_admin"),
            "activity_code": r.get("activity_code"),
            "org_name": r.get("org_name"),
            "funding_mechanism": r.get("funding_mechanism"),
            "is_active": is_active,
            "active_status": active_status,
            "award_amount": r.get("award_amount"),
            "principal_investigators": pi_string,
            "contact_pi_name": contact_pi,
            "pi_count": pi_count if pi_count > 0 else (1 if contact_pi else 0)
        }
        
        records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    return df
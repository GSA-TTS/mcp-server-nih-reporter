from reporter.models import SearchParams
import pandas as pd 

from question_utils import get_all_responses

def get_q11_answer():

    search_params = SearchParams(
        activity_codes=[
            "R01"
        ],
        agencies=[
            "NIMHD",
            "NICHD"
        ],
        years=[
            2023,
            2024,
            2025
        ]
    )

    limit = 500
    include_fields = ["ProjectNum","FiscalYear","AwardAmount","Organization","AgencyIcAdmin","ActivityCode"]

    # get all responses
    response = get_all_responses(search_params, include_fields, limit)

    results = pd.DataFrame(response['results'])

    data = results.groupby('agency_ic_admin').agg(
        count=('project_num', 'count'),
        total_amount=('award_amount', 'sum')
    ).reset_index()

    # Rename columns to match your desired format
    data = data.rename(columns={'agency_ic_admin': 'ic_name'})

    # Convert to list of dictionaries
    data = data.to_dict('records')

    print(data)

if __name__ == "__main__":
    get_q11_answer()
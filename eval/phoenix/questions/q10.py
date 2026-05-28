
from reporter.models import SearchParams
import pandas as pd 

from question_utils import get_all_responses

def get_q10_answer():

    search_params = SearchParams(
        years=[2026],
        opportunity_numbers=["PA-25-301"],
    )

    limit = 500
    include_fields = ["ProjectNum","FiscalYear","AwardAmount","Organization"]

    # get all responses
    response = get_all_responses(search_params, include_fields, limit)

    results = pd.DataFrame(response['results'])

    # group by org name and sum award amounts
    org_funding = results.groupby('org_name')['award_amount'].sum()

    # compute Herfindahl index
    total_funding = org_funding.sum()
    org_funding_share = org_funding / total_funding
    herfindahl_index = (org_funding_share ** 2).sum()

    print(f"Herfindahl Index: {herfindahl_index}")

if __name__ == "__main__":
    get_q10_answer()
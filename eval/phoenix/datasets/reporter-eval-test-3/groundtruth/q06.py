#  "Which PI has received the most funding for grants that are tagged with BOTH 'Alzheimer's Disease' and 'Artificial Intelligence' spending categories from 2018 to 2024?"

from reporter.models import SearchParams
import pandas as pd 

from question_utils import get_all_responses

def get_q06_answer():

    # set query parameters
    search_params = SearchParams(
        years=[2018,2019,2020,2021,2022,2023,2024],
        spending_categories={
            "values": [
            40,
            4372
            ],
            "match_all": "true"
        }
    )
    limit = 500
    include_fields = ["ProjectNum","AwardAmount","PrincipalInvestigators"]

    # get all responses
    response = get_all_responses(search_params, include_fields, limit)

    # convert responses to a dataframe
    results = pd.DataFrame(response['results'])

    # break out PIs into separate rows
    results = results.explode('principal_investigators')

    # group by PI and sum award amounts
    pi_funding = results.groupby('principal_investigators')['award_amount'].sum()
    top_pi = pi_funding.idxmax()
    top_pi_funding = pi_funding.max()
    print(results.head())
    print("Top PI:", top_pi)
    print("Total funding for top PI:", top_pi_funding)

if __name__ == "__main__":
    get_q06_answer()
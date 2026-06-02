# What percentage of R01 grants funded by NHLBI in fiscal years 2020-2023 went to institutions in the top 3 states by total grant count?

from reporter.models import SearchParams
import pandas as pd 

from question_utils import get_all_responses

def get_q05_answer():

    # set query parameters
    search_params = SearchParams(
        years=[2020],
        agencies=["NHLBI"],
        activit_codes=["R01"],
    )
    limit = 500
    include_fields = ["ProjectNum","Organization"]

    # get all responses
    response = get_all_responses(search_params, include_fields, limit)

    # convert responses to a dataframe
    results = pd.DataFrame(response['results'])

    # group by state and count grants
    state_counts = results['org_state'].value_counts()
    top_states = state_counts.head(3).index

    # count total grants and grants in top states
    total_grants = len(results)
    top_state_grants = results[results['org_state'].isin(top_states)]
    top_state_grant_count = len(top_state_grants)
    percentage_top_states = (top_state_grant_count / total_grants) * 100
    
    print(results.head())
    print("Top states by grant count:", top_states.tolist())
    print("Percentage of grants in top states:", percentage_top_states)
    # print("Median award amount:", results['award_amount'].median())

if __name__ == "__main__":
    get_q05_answer()

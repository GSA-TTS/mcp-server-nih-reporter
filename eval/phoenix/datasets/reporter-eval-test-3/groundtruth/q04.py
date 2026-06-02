from reporter.models import SearchParams
import pandas as pd 

from question_utils import get_all_responses

def get_q04_answer():

    # set query parameters
    search_params = SearchParams(
        years=[2019],
        agencies=["NCI"],
        organizations=["Boston University"],
    )
    limit = 500
    include_fields = ["ProjectNum","AwardAmount"]

    # get all responses
    response = get_all_responses(search_params, include_fields, limit)

    # convert responses to a dataframe
    results = pd.DataFrame(response['results'])

    print(results.head())
    print("Median award amount:", results['award_amount'].median())

if __name__ == "__main__":
    get_q04_answer()

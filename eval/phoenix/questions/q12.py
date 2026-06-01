from reporter.models import SearchParams
import pandas as pd 

from question_utils import get_all_responses

def get_q11_answer():

    search_params = SearchParams(
        activity_codes=[
            "R01"
        ],
        organizations=[
            "Harvard Medical School",
        ],
        years=[
            2022,
        ]
    )

    limit = 500
    include_fields = ["ProjectNum","FiscalYear","AwardAmount","Organization","AgencyIcAdmin","ActivityCode"]

    # get all responses
    response = get_all_responses(search_params, include_fields, limit)

    results = pd.DataFrame(response['results'])
    print(results.head(10))

    print("The average award amount is ${:,.2f}".format(results['award_amount'].mean()))

if __name__ == "__main__":
    get_q11_answer()
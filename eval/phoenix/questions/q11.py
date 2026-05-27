from reporter.models import SearchParams
import pandas as pd 

from question_utils import get_all_responses

def get_q11_answer():

    search_params = SearchParams(
        project_nums=["P50DA056408"]
    )

    limit = 500
    include_fields = ["ProjectNum","FiscalYear","AwardAmount","Organization"]

    # get all responses
    response = get_all_responses(search_params, include_fields, limit)

    results = pd.DataFrame(response['results'])

    print(results.head(20))

if __name__ == "__main__":
    get_q11_answer()
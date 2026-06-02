#  Compare the portfolios of program officers whose last name is 'Johnson' versus those with last name 'Smith' between the years of 2018 and 2023 in terms of average project duration. Which PO group manages longer projects on average?"

from reporter.models import SearchParams
import pandas as pd 

from question_utils import get_all_responses

def get_q07_answer():

    # set query parameters
    search_params = SearchParams(
        years=[2018,2019,2020,2021,2022,2023],
        po_names = [
            {
                "last_name": "Smith"
            },
            {
                "last_name": "Johnson"
            }  
        ]
    )
    limit = 500
    include_fields = ["ProjectNum","ProgramOfficers","ProjectStartDate","ProjectEndDate"]

    # get all responses
    response = get_all_responses(search_params, include_fields, limit)

    # convert responses to a dataframe
    results = pd.DataFrame(response['results'])

    # isolate PO last name
    results['po_last_name'] = results['program_officers'].apply(lambda pos: [po['last_name'] for po in pos] if isinstance(pos, list) else [])

    # calculate project duration in days
    results['project_duration'] = (pd.to_datetime(results['project_end_date']) - pd.to_datetime(results['project_start_date'])).dt.days

    # group by last name and calculate average duration
    po_duration = results.explode('po_last_name').groupby('po_last_name')['project_duration'].mean()
    print(po_duration)

if __name__ == "__main__":
    get_q07_answer()
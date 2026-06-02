spending_categories = [2597, 24, 27, 30, 31, 36, 39, 40, 3246, 3254, 44, 19, 47, 48, 50, 2610, 51, 54, 55, 58, 59, 64, 65, 66, 67, 69, 3454, 81, 84, 89, 98, 101, 229, 108, 2595, 117, 118, 120, 3932, 5654, 123, 3461, 132, 1393, 2609, 2601, 140, 3491, 4975, 144, 3466, 146, 157, 162, 373, 163, 4268, 170, 171, 172, 616, 296, 176, 180, 5224, 183, 187, 191, 196, 3533, 2037, 2382, 197, 200, 4835, 5009, 5011, 5005, 5014, 201, 204, 206, 4531, 2067, 216, 219, 224, 3527, 231, 232, 233, 234, 5745, 4998, 238, 240, 241, 242, 243, 2600, 4721, 2375, 246, 248, 3460, 3529, 250, 255, 4714, 257, 259, 262, 5724, 263, 264, 265, 4465, 1389, 267, 268, 269, 272, 273, 275, 276, 5552, 292, 5599, 5546, 3180, 2376, 298, 4511, 299, 300, 306, 307, 308, 309, 310, 284, 312, 313, 314, 289, 318, 320, 325, 1791, 326, 327, 331, 3999, 3085, 338, 341, 342, 343, 453, 380, 385, 395, 2438, 399, 400, 408, 409, 410, 411, 5044, 5024, 413, 4372, 436, 2613, 437, 438, 3810, 4764, 5555, 443, 3445, 458, 4243, 465, 473, 474, 475, 479, 480, 496, 5562, 3453, 687, 329, 1375, 520, 521, 525, 536, 551, 4076, 3951, 555, 556, 789, 2599, 559, 560, 563, 564, 615, 618, 620, 1391, 624, 1254, 679, 680, 2310, 3520, 685, 689, 524, 3395, 372, 2346, 692, 693, 696, 5231, 5194, 1991, 4711, 3070, 3920, 700, 686, 701, 5592, 5804, 703, 704, 5773, 5232, 5286, 5544, 1859, 729, 5551, 731, 732, 737, 2611, 770, 5264, 3475, 777, 779, 780, 781, 2343, 784, 785, 5789, 788, 4793, 792, 793, 794, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 808, 5225, 4758, 811, 817, 819, 822, 823, 824, 830, 4990, 831, 2607, 4989, 852, 791, 853, 854, 861, 862, 375, 374, 864, 865, 866, 867, 3265, 376, 871, 2334, 873, 877, 878, 1873, 2339, 2412, 881, 883, 884, 889, 891, 5815, 4924, 897, 898, 3617]

from reporter.models import SearchParams
import pandas as pd 

from question_utils import get_all_responses

def get_q08_answer():

    criteria_categories = []

    for idx, cat in enumerate(spending_categories):
        print(f"{idx} out of {len(spending_categories)} Processing category {cat}...")

        search_params = SearchParams(
            years=[2019],
            spending_categories={
                "values": [cat],
                "match_all": "false"
            },
        )

        limit = 500
        include_fields = ["ProjectNum","FiscalYear","AwardAmount","PrincipalInvestigators"]

        # get all responses
        response = get_all_responses(search_params, include_fields, limit)

        # convert responses to a dataframe
        results_2019 = pd.DataFrame(response['results'])

        # explode PIs into separate rows
        results_2019 = results_2019.explode('principal_investigators')

        search_params.years = [2023]
        response = get_all_responses(search_params, include_fields, limit)
        results_2023 = pd.DataFrame(response['results'])
        results_2023 = results_2023.explode('principal_investigators')

        # combine 2019 and 2023 results
        results = pd.concat([results_2019, results_2023], ignore_index=True)

        # group by fiscal year and count unique PIs and sum award amounts
        summary = results.groupby('fiscal_year').agg(
            unique_pis=('principal_investigators', 'nunique'),
            total_funding=('award_amount', 'sum')
        ).reset_index()

        # see if funding decreased by more than 30% but unique PIs increased
        if len(summary) == 2:
            funding_decrease = (summary.loc[summary['fiscal_year'] == 2023, 'total_funding'].values[0] < 
                                summary.loc[summary['fiscal_year'] == 2019, 'total_funding'].values[0] * 0.7)
            pi_increase = (summary.loc[summary['fiscal_year'] == 2023, 'unique_pis'].values[0] > 
                           summary.loc[summary['fiscal_year'] == 2019, 'unique_pis'].values[0])

            if funding_decrease and pi_increase:
                print(f"Category {cat} had a funding decrease of more than 30% but an increase in unique PIs.\n")
                criteria_categories.append(cat)
            else:
                print(f"Category {cat} did not meet the criteria.\n")
                
        print(summary)

    print("Categories that met the criteria:", criteria_categories)

if __name__ == "__main__":
    get_q08_answer()
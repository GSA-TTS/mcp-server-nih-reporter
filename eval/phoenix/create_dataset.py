import pandas as pd
from phoenix.client import Client

def upload_dataset(filepath, name):
    # create dataframe from csv file
    data = pd.read_csv(filepath)

    px_client = Client()
    dataset = px_client.datasets.create_dataset(
        dataframe=data,
        name=name,
        input_keys=["query"],
        output_keys=["responses"],
    )

if __name__ == "__main__":
    upload_dataset("eval/phoenix/datasets/reporter-test-3.csv", "reporter-test-3")
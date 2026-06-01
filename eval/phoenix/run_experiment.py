from dns.resolver import query
from phoenix.client import Client
import agent 
import asyncio

from agent import NIHReporterAgent
from judges import match_expected_response, check_answer_scope

# Initialize client - automatically reads from environment variables:
client = Client()

# Get the dataset
dataset = client.datasets.get_dataset(
    dataset="reporter-eval-scope-1"
    # version_id="RGF0YXNldFZlcnNpb246MQ=="  # or omit for latest version
)

agent = NIHReporterAgent(project_name="nih-reporter-experiments")
asyncio.run(agent.initialize())

# Define your task using the agent
def my_task(example):
    """Run each query through the NIH Reporter agent"""
    query = example.input['query']
    
    # Run the agent synchronously (Phoenix experiments expect sync functions)
    response = asyncio.run(agent.run(query))
    return response

# Store the evaluators for later use
evaluators = [check_answer_scope, match_expected_response]

# Run an experiment
experiment = client.experiments.run_experiment(
    dataset=dataset,
    task=my_task,
    evaluators=evaluators,
)

from phoenix.client import Client
import asyncio

import sys
from pathlib import Path

# Add the phoenix directory to Python path
phoenix_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(phoenix_dir))

# Import agent and judges 
from agent import NIHReporterAgent
from judges import match_expected_response, check_answer_scope

# Initialize client - automatically reads from environment variables:
client = Client()

# Get the dataset
dataset = client.datasets.get_dataset(
    dataset="reporter-test-2"
    # version_id="RGF0YXNldFZlcnNpb246MQ=="  # or omit for latest version
)

system_prompt_version = "v3"

agent = NIHReporterAgent(
    project_name="nih-reporter-experiments",
    phoenix_endpoint="http://localhost:4317",
    prompt_version=system_prompt_version)
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
    experiment_description="Try running experiment from new directory structure.",
    experiment_metadata={"system_prompt_version": system_prompt_version}
)

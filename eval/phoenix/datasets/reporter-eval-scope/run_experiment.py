from phoenix.client import Client
import asyncio
import argparse
import sys
from pathlib import Path

# Add the phoenix directory to Python path
phoenix_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(phoenix_dir))

# Import agent and judges 
from agent import NIHReporterAgent
from judges import match_expected_response, check_answer_scope


def main(
    dataset_name: str = "reporter-eval-scope",
    dataset_version_id: str = None,
    system_prompt_version: str = "v3",
    project_name: str = "nih-reporter-experiments",
    phoenix_endpoint: str = "http://localhost:4317",
    experiment_description: str = None,
    experiment_metadata: dict = None
):
    """
    Run a Phoenix experiment with the NIH Reporter agent.
    
    Args:
        dataset_name: Name of the Phoenix dataset to use
        dataset_version_id: Specific version ID of dataset (None for latest)
        system_prompt_version: Version identifier for the system prompt
        project_name: Name of the Phoenix project
        phoenix_endpoint: URL endpoint for Phoenix OTLP collector
        experiment_description: Human-readable description of the experiment
        experiment_metadata: Additional metadata to attach to the experiment
    
    Returns:
        The experiment result object from Phoenix
    """
    # Initialize client - automatically reads from environment variables
    client = Client()
    
    # Get the dataset
    dataset_kwargs = {"dataset": dataset_name}
    if dataset_version_id:
        dataset_kwargs["version_id"] = dataset_version_id
    
    dataset = client.datasets.get_dataset(**dataset_kwargs)
    
    # Initialize the agent
    agent = NIHReporterAgent(
        project_name=project_name,
        phoenix_endpoint=phoenix_endpoint,
        prompt_version=system_prompt_version
    )
    asyncio.run(agent.initialize())
    
    # Create the task using the agent's method
    my_task = agent.create_experiment_task()
    
    # Store the evaluators
    evaluators = [check_answer_scope, match_expected_response]
    
    # Prepare experiment metadata
    if experiment_metadata is None:
        experiment_metadata = {}
    experiment_metadata["system_prompt_version"] = system_prompt_version
    
    # Set default experiment description if not provided
    if experiment_description is None:
        experiment_description = f"Experiment with system prompt {system_prompt_version}"
    
    # Run an experiment
    experiment = client.experiments.run_experiment(
        dataset=dataset,
        task=my_task,
        evaluators=evaluators,
        experiment_description=experiment_description,
        experiment_metadata=experiment_metadata
    )
    
    return experiment


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Phoenix experiments with NIH Reporter agent",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--dataset-name",
        type=str,
        default="reporter-eval-scope",
        help="Name of the Phoenix dataset to use"
    )
    
    parser.add_argument(
        "--dataset-version-id",
        type=str,
        default=None,
        help="Specific version ID of dataset (omit for latest version)"
    )
    
    parser.add_argument(
        "--system-prompt-version",
        type=str,
        default="v3",
        help="Version identifier for the system prompt"
    )
    
    parser.add_argument(
        "--project-name",
        type=str,
        default="nih-reporter-experiments",
        help="Name of the Phoenix project"
    )
    
    parser.add_argument(
        "--phoenix-endpoint",
        type=str,
        default="http://localhost:4317",
        help="URL endpoint for Phoenix OTLP collector"
    )
    
    parser.add_argument(
        "--experiment-description",
        type=str,
        default=None,
        help="Human-readable description of the experiment"
    )
    
    args = parser.parse_args()
    
    # Run the main function with parsed arguments
    experiment = main(
        dataset_name=args.dataset_name,
        dataset_version_id=args.dataset_version_id,
        system_prompt_version=args.system_prompt_version,
        project_name=args.project_name,
        phoenix_endpoint=args.phoenix_endpoint,
        experiment_description=args.experiment_description
    )
    
    print(f"Experiment completed: {experiment}")
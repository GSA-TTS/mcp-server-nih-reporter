# Phoenix Evaluation Framework

This directory contains a consolidated framework for running Phoenix evaluation experiments with the NIH Reporter agent.

## Overview

The Phoenix evaluation framework has been consolidated to eliminate code duplication and provide a consistent CLI-driven workflow. All experiment scripts and dataset creation operations now use centralized tools.

### Structure

```
eval/phoenix/
├── create_dataset.py          # Unified dataset creation CLI
├── run_experiment.py          # Unified experiment runner CLI
├── datasets.yaml              # Dataset registry and configuration
├── README.md                  # This file
├── agent.py                   # NIHReporterAgent class
├── judges/                    # Evaluation functions
│   ├── correctness_judge.py   # match_expected_response evaluator
│   └── relevance_judge.py     # check_answer_scope evaluator
├── prompts/                   # System prompt versions
│   ├── system_prompt_v1.txt   # Basic analyst prompt
│   ├── system_prompt_v2.txt   # With scope boundaries
│   └── system_prompt_v3.txt   # Mixed questions handling
└── datasets/                  # Test datasets (CSVs only)
    ├── reporter-eval-0/
    ├── reporter-eval-scope/
    ├── reporter-eval-test-3/
    └── reporter-test-2/
```

---

## Quick Start

**Note:** Use the project's virtual environment Python to run these scripts:

```bash
# Set up environment variable for convenience
PYTHON=/Users/marksaronson/Documents/code_projects/nih/mcp-server-nih-reporter/.venv/bin/python

# Or use the full path in each command
```

### 1. List Available Datasets

```bash
$PYTHON create_dataset.py --list
# Or with full path:
# /Users/marksaronson/Documents/code_projects/nih/mcp-server-nih-reporter/.venv/bin/python create_dataset.py --list
```

### 2. Create a Dataset in Phoenix

```bash
$PYTHON create_dataset.py --dataset-name reporter-test-2
```

### 3. Run an Experiment

```bash
$PYTHON run_experiment.py --dataset-name reporter-test-2
```

---

## Available Datasets

| Dataset Name | Size | Description |
|--------------|------|-------------|
| **reporter-eval-0** | 11 questions | Mixed evaluation (basic + scope) |
| **reporter-test-2** | 4 questions | Basic functionality test |
| **reporter-eval-test-3** | 4 questions | Basic + out-of-scope test with ground truth |
| **reporter-eval-scope-1** | 11 questions | Scope boundary evaluation |
| **reporter-eval-scope-0** | 71 questions | Comprehensive dataset with rationales |

---

## Dataset Creation

### Basic Usage

```bash
# Create a dataset from datasets.yaml configuration
python create_dataset.py --dataset-name reporter-eval-0

# Create with a custom name in Phoenix
python create_dataset.py --dataset-name reporter-test-2 --phoenix-name my-test-dataset

# Dry run (validate without uploading)
python create_dataset.py --dataset-name reporter-eval-scope-1 --dry-run
```

### Options

```
--dataset-name NAME     Name from datasets.yaml (required)
--list                  List all available datasets
--phoenix-name NAME     Custom name in Phoenix (default: dataset-name)
--csv-path PATH         Override CSV path from config
--dry-run               Validate without uploading
```

### Adding New Datasets

1. Add your CSV file to `datasets/<dataset-name>/examples/`
2. Update `datasets.yaml`:

```yaml
datasets:
  my-new-dataset:
    csv_path: datasets/my-new-dataset/examples/questions.csv
    input_keys:
      - query
    output_keys:
      - responses
    description: "Description of the dataset"
```

3. Create the dataset:

```bash
python create_dataset.py --dataset-name my-new-dataset
```

---

## Running Experiments

### Basic Usage

```bash
# Run with default settings (prompt v3)
python run_experiment.py --dataset-name reporter-test-2

# Test different prompt versions
python run_experiment.py --dataset-name reporter-eval-0 --system-prompt-version v2

# Add custom experiment description
python run_experiment.py \
    --dataset-name reporter-eval-scope-1 \
    --experiment-description "Testing boundary detection with v3 prompt" \
    --system-prompt-version v3
```

### Options

```
--dataset-name NAME              Dataset name in Phoenix (required)
--system-prompt-version VERSION  Prompt version: v1, v2, or v3 (default: v3)
--experiment-description TEXT    Human-readable description
--project-name NAME              Phoenix project name (default: nih-reporter-experiments)
--phoenix-endpoint URL           Phoenix OTLP endpoint (default: http://localhost:4317)
--dataset-version-id ID          Specific dataset version (default: latest)
--list-datasets                  Show available datasets and exit
--no-validate                    Skip dataset validation
```

### Experiment Workflow

1. **Start Phoenix** (if not already running):
   ```bash
   arize-phoenix run
   ```

2. **Create datasets** (one-time per dataset):
   ```bash
   python create_dataset.py --dataset-name reporter-test-2
   python create_dataset.py --dataset-name reporter-eval-0
   ```

3. **Run experiments**:
   ```bash
   # Test with v3 prompt (recommended)
   python run_experiment.py --dataset-name reporter-test-2 --system-prompt-version v3
   
   # Compare v2 vs v3 on scope dataset
   python run_experiment.py --dataset-name reporter-eval-scope-1 --system-prompt-version v2
   python run_experiment.py --dataset-name reporter-eval-scope-1 --system-prompt-version v3
   ```

4. **View results** in Phoenix UI at http://localhost:6006

---

## System Prompts

### v1: Basic Analyst
- Simple, permissive prompt
- No scope boundaries defined
- Answers any question

### v2: Scope Boundaries
- Defines what the agent should/shouldn't do
- Strict scope enforcement
- Refuses mixed questions entirely

### v3: Mixed Questions Handling (Recommended)
- **"Be helpful first"** principle
- Provides factual data even when question contains subjective elements
- Addresses scope limitations after providing data
- Example: "Is $500K sufficient?" → Provides actual funding data, then notes sufficiency requires judgment

---

## Evaluators

### check_answer_scope
Evaluates whether the agent stays within scope or refuses appropriately:
- **within_scope**: NIH question answered OR non-NIH question refused
- **out_of_scope**: NIH question refused OR non-NIH question answered

### match_expected_response
LLM-as-judge evaluation of correctness:
- **correct**: Response contains key information and answers appropriately
- **incorrect**: Response missing key information or inaccurate

Both evaluators use `claude_4_5_sonnet` as the judge model.

---

## Examples

### Compare Prompt Versions

```bash
# Create dataset once
python create_dataset.py --dataset-name reporter-eval-scope-1

# Run experiments with different prompts
python run_experiment.py --dataset-name reporter-eval-scope-1 --system-prompt-version v1
python run_experiment.py --dataset-name reporter-eval-scope-1 --system-prompt-version v2
python run_experiment.py --dataset-name reporter-eval-scope-1 --system-prompt-version v3

# Compare results in Phoenix UI
```

### Test with Ground Truth Data

```bash
# reporter-eval-test-3 has programmatic ground truth in groundtruth/ directory
python create_dataset.py --dataset-name reporter-eval-test-3
python run_experiment.py --dataset-name reporter-eval-test-3 --system-prompt-version v3
```

### Quick Smoke Test

```bash
# Use smallest dataset for fast iteration
python create_dataset.py --dataset-name reporter-test-2
python run_experiment.py --dataset-name reporter-test-2 --system-prompt-version v3
```

---

## Migration Notes

### What Changed

This consolidation replaced:
- 4 duplicate `create_dataset.py` files (one per dataset directory)
- 5 duplicate `run_experiment.py` files (with inconsistent features)
- ~565 lines of duplicated code

With:
- 1 unified `create_dataset.py` with full CLI support
- 1 unified `run_experiment.py` with enhanced features
- 1 `datasets.yaml` configuration file
- Better error handling and validation

### Old vs New

**Before:**
```bash
cd datasets/reporter-test-2/
# Edit create_dataset.py to change dataset name
python create_dataset.py

# Edit run_experiment.py to change parameters
python run_experiment.py
```

**After:**
```bash
# From eval/phoenix/ directory
python create_dataset.py --dataset-name reporter-test-2
python run_experiment.py --dataset-name reporter-test-2 --system-prompt-version v3
```

### Removed Files

The following duplicate files were removed:
```
datasets/reporter-eval-0/create_dataset.py
datasets/reporter-eval-0/run_experiment.py
datasets/reporter-test-2/create_dataset.py
datasets/reporter-test-2/run_experiment.py
datasets/reporter-eval-test-3/create_dataset.py
datasets/reporter-eval-test-3/run_experiment.py
datasets/reporter-eval-scope/create_dataset.py
datasets/reporter-eval-scope/run_experiment.py
datasets/reporter-eval-scope/examples/run_experiment.py
```

All CSV files and the `groundtruth/` directory remain unchanged.

---

## Troubleshooting

### "Dataset not found in datasets.yaml"
Add your dataset to `datasets.yaml` or use `--no-validate` to skip validation.

### "CSV file not found"
Check that the `csv_path` in `datasets.yaml` is correct relative to the `eval/phoenix/` directory.

### "System prompt file not found"
Ensure the prompt version exists in `prompts/system_prompt_{version}.txt`. Available versions: v1, v2, v3.

### "Error loading dataset from Phoenix"
Make sure you've created the dataset first using `create_dataset.py`.

### Phoenix not running
Start Phoenix with:
```bash
arize-phoenix run
```

Then access the UI at http://localhost:6006

---

## Future Enhancements

Potential improvements for future iterations:

1. **Batch operations**: Run multiple experiments in one command
2. **Grid search**: Test all datasets × all prompt versions
3. **Results comparison**: CLI tool to compare experiment results
4. **Dataset versioning**: Automatic version tracking
5. **Experiment templates**: Predefined configurations for common tests
6. **CI/CD integration**: Automated experiment runs on changes
7. **Custom evaluators**: Easy way to add new judge functions

---

## Questions?

For issues or questions about this framework:
- Check the code in `agent.py`, `judges/`, and the consolidated scripts
- Review experiment results in Phoenix UI at http://localhost:6006
- Consult the Phoenix documentation: https://docs.arize.com/phoenix

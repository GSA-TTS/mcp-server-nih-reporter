#!/usr/bin/env python3
"""Manual NIH RePORTER query helper for Databricks eval dataset work.

Examples:

    .\.venv\Scripts\python.exe eval/databricks_eval/query_reporter_api.py
    .\.venv\Scripts\python.exe eval/databricks_eval/query_reporter_api.py 0
    .\.venv\Scripts\python.exe eval/databricks_eval/query_reporter_api.py 4
"""

from __future__ import annotations

import json
import sys

from api_client import run_query
from query_specs import QUERY_SPECS


def main() -> None:
    query_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    spec = QUERY_SPECS[query_index]

    print(f"Question {query_index}: {spec['question']}")
    print("URL:", spec["url"])
    print("PROCESSOR:", spec["processor"])
    print("PARAMS:")
    print(json.dumps(spec["params"], indent=2))
    print("\nRESPONSE:")

    data = run_query(spec["url"], spec["params"])
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()

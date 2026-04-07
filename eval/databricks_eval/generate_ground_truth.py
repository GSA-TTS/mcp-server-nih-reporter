#!/usr/bin/env python3
"""Generate a two-column CSV of questions and expected answers."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from api_client import fetch_all_pages
from processors import PROCESSORS, serialize_answer
from query_specs import QUERY_SPECS


DEFAULT_OUTPUT = Path("eval/databricks_eval/nih_reporter_ground_truth.csv")


def generate_rows(question_indexes: list[int] | None = None) -> list[dict[str, str]]:
    indexes = question_indexes if question_indexes is not None else list(range(len(QUERY_SPECS)))
    rows: list[dict[str, str]] = []

    for index in indexes:
        spec = QUERY_SPECS[index]
        processor = PROCESSORS[spec["processor"]]
        data = fetch_all_pages(spec["url"], spec["params"])
        answer = processor(data, **spec.get("processor_kwargs", {}))
        rows.append({"question": spec["question"], "expected_answer": serialize_answer(answer)})

    return rows


def write_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["question", "expected_answer"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    indexes = [int(arg) for arg in sys.argv[1:]] if len(sys.argv) > 1 else None
    rows = generate_rows(indexes)
    write_csv(rows, DEFAULT_OUTPUT)
    print(f"Wrote {len(rows)} rows to {DEFAULT_OUTPUT}")


if __name__ == "__main__":
    main()

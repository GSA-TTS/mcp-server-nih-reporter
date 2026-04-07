from __future__ import annotations

from copy import deepcopy
from typing import Any

import requests


def run_query(url: str, params: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        url,
        json=params,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def fetch_all_pages(url: str, params: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(params)
    limit = payload.get("limit", 500)
    offset = payload.get("offset", 0)
    max_results = payload.pop("max_results", None)

    first_page = run_query(url, payload)
    total = first_page.get("meta", {}).get("total", len(first_page.get("results", [])))
    combined_results = list(first_page.get("results", []))

    while offset + limit < total:
        if max_results is not None and len(combined_results) >= max_results:
            break
        offset += limit
        payload["offset"] = offset
        page = run_query(url, payload)
        combined_results.extend(page.get("results", []))

    if max_results is not None:
        combined_results = combined_results[:max_results]

    all_pages = deepcopy(first_page)
    all_pages["results"] = combined_results
    if "meta" in all_pages:
        all_pages["meta"]["offset"] = 0
        all_pages["meta"]["limit"] = len(combined_results)
    return all_pages

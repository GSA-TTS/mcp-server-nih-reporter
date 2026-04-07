from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any


def get_nested(record: dict[str, Any], path: str) -> Any:
    current: Any = record
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def serialize_answer(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def count_results(data: dict[str, Any], **_: Any) -> int:
    return len(data.get("results", []))


def count_active_results(data: dict[str, Any], **_: Any) -> int:
    return sum(1 for row in data.get("results", []) if row.get("is_active") is True)


def extract_first_fields(data: dict[str, Any], fields: list[str], **_: Any) -> dict[str, Any]:
    first = data.get("results", [{}])[0]
    return {field: get_nested(first, field) for field in fields}


def sum_field(data: dict[str, Any], field: str, **_: Any) -> int | float:
    return sum((get_nested(row, field) or 0) for row in data.get("results", []))


def average_field(data: dict[str, Any], field: str, **_: Any) -> float:
    numeric_values = [get_nested(row, field) for row in data.get("results", [])]
    numeric_values = [value for value in numeric_values if isinstance(value, (int, float))]
    if not numeric_values:
        return 0.0
    return sum(numeric_values) / len(numeric_values)


def list_projects_with_fields(
    data: dict[str, Any],
    fields: list[str],
    min_value_field: str | None = None,
    min_value: int | float | None = None,
    **_: Any,
) -> list[dict[str, Any]]:
    rows = []
    for row in data.get("results", []):
        if min_value_field is not None and min_value is not None:
            value = get_nested(row, min_value_field) or 0
            if value < min_value:
                continue
        rows.append({field: get_nested(row, field) for field in fields})
    return rows


def top_groups_by_sum(
    data: dict[str, Any],
    group_field: str,
    value_field: str,
    top_n: int = 5,
    **_: Any,
) -> list[dict[str, Any]]:
    totals: dict[str, float] = defaultdict(float)
    for row in data.get("results", []):
        group = get_nested(row, group_field)
        value = get_nested(row, value_field) or 0
        if group:
            totals[str(group)] += value
    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:top_n]
    return [{"group": group, "total": total} for group, total in ranked]


def top_groups_by_count(
    data: dict[str, Any],
    group_field: str,
    top_n: int = 10,
    **_: Any,
) -> list[dict[str, Any]]:
    counts = Counter()
    for row in data.get("results", []):
        group = get_nested(row, group_field)
        if group:
            counts[str(group)] += 1
    return [{"group": group, "count": count} for group, count in counts.most_common(top_n)]


def group_counts(data: dict[str, Any], group_field: str, **_: Any) -> dict[str, int]:
    counts = Counter()
    for row in data.get("results", []):
        group = get_nested(row, group_field)
        if group:
            counts[str(group)] += 1
    return dict(sorted(counts.items()))


def top_pi_by_total_funding(data: dict[str, Any], **_: Any) -> dict[str, Any]:
    totals: dict[str, float] = defaultdict(float)
    for row in data.get("results", []):
        award_amount = row.get("award_amount") or 0
        for pi in row.get("principal_investigators") or []:
            name = pi.get("full_name")
            if name:
                totals[name] += award_amount
    if not totals:
        return {}
    name, amount = max(totals.items(), key=lambda item: item[1])
    return {"principal_investigator": name, "total_award_amount": amount}


def top_foreign_countries_by_funding(data: dict[str, Any], top_n: int = 5, **_: Any) -> dict[str, Any]:
    country_totals: dict[str, float] = defaultdict(float)
    institutions: list[dict[str, Any]] = []

    for row in data.get("results", []):
        organization = row.get("organization") or {}
        country = organization.get("org_country")
        org_name = organization.get("org_name")
        award_amount = row.get("award_amount") or 0
        if country and country != "UNITED STATES":
            country_totals[country] += award_amount
            institutions.append(
                {
                    "project_num": row.get("project_num"),
                    "organization": org_name,
                    "country": country,
                    "award_amount": award_amount,
                }
            )

    top_countries = sorted(country_totals.items(), key=lambda item: (-item[1], item[0]))[:top_n]
    return {
        "foreign_institutions": institutions,
        "top_countries_by_total_award_amount": [
            {"country": country, "total_award_amount": total} for country, total in top_countries
        ],
    }


def count_active_and_collect_terms(data: dict[str, Any], term_field: str, **_: Any) -> dict[str, Any]:
    active_rows = [row for row in data.get("results", []) if row.get("is_active") is True]
    terms = Counter()
    for row in active_rows:
        for term in row.get(term_field) or []:
            if term:
                terms[str(term)] += 1
    return {"active_count": len(active_rows), "program_terms": dict(terms.most_common(50))}


def publication_count_and_titles(data: dict[str, Any], **_: Any) -> dict[str, Any]:
    publications = []
    for row in data.get("results", []):
        publications.append(
            {
                "pmid": row.get("pmid"),
                "title": row.get("title"),
                "journal": row.get("journal_title"),
                "publication_year": row.get("pub_year"),
            }
        )
    return {"publication_count": len(publications), "publications": publications}


PROCESSORS = {
    "average_field": average_field,
    "count_active_and_collect_terms": count_active_and_collect_terms,
    "count_active_results": count_active_results,
    "count_results": count_results,
    "extract_first_fields": extract_first_fields,
    "group_counts": group_counts,
    "list_projects_with_fields": list_projects_with_fields,
    "publication_count_and_titles": publication_count_and_titles,
    "sum_field": sum_field,
    "top_foreign_countries_by_funding": top_foreign_countries_by_funding,
    "top_groups_by_count": top_groups_by_count,
    "top_groups_by_sum": top_groups_by_sum,
    "top_pi_by_total_funding": top_pi_by_total_funding,
}

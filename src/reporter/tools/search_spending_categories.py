from reporter.models.spending_categories import (
    SPENDING_CATEGORY_MAP_FY2024,
    _normalize_spending_category_name,
)


def register(mcp):
    @mcp.tool()
    async def search_spending_categories(
        query: str,
        limit: int = 10,
    ):
        """
        Search NIH spending categories by name and return matching (id, name) pairs.

        Use this tool BEFORE filtering by `spending_categories` when you only know a
        plain-English topic (e.g., "aging", "breast cancer", "opioid") and need
        valid numeric IDs.

        Args:
            query (str): Plain-English category search text. Partial matches are supported.
            limit (int): Maximum number of matches to return (default 10, max 50).

        Returns:
            list[dict]: Matching categories as [{"id": int, "name": str}] ordered by match quality.
        """
        if not query or not query.strip():
            return []

        limit = max(1, min(limit, 50))
        normalized_query = _normalize_spending_category_name(query)
        query_tokens = set(normalized_query.split())

        scored: list[tuple[int, int, str]] = []  # (-score, id, name)
        for category_id, category_name in SPENDING_CATEGORY_MAP_FY2024.items():
            normalized_name = _normalize_spending_category_name(category_name)

            if normalized_query == normalized_name:
                score = 3  # exact match
            elif normalized_name.startswith(normalized_query):
                score = 2  # prefix match
            elif query_tokens and query_tokens.issubset(set(normalized_name.split())):
                score = 1  # all tokens present
            elif any(token in normalized_name for token in query_tokens):
                score = 0  # partial token match
            else:
                continue

            scored.append((-score, category_id, category_name))

        scored.sort(key=lambda item: (item[0], item[2]))
        return [{"id": category_id, "name": name} for _, category_id, name in scored[:limit]]

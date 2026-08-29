from __future__ import annotations

import os
from typing import Any

from tavily import TavilyClient


def search_sources(
    claim: str,
    max_results: int = 5,
) -> list[dict[str, Any]]:
    """
    Search the web for evidence related to a factual claim.

    Returns normalized search results containing:
    - title
    - url
    - content
    - score
    """

    if not isinstance(claim, str):
        raise TypeError("claim must be a string")

    claim = claim.strip()

    if not claim:
        return []

    if max_results <= 0:
        return []

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is not set."
        )

    client = TavilyClient(api_key=api_key)

    response = client.search(
        query=claim,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
        include_raw_content=False,
    )

    results = []

    for item in response.get("results", []):
        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "score": item.get("score", 0.0),
            }
        )

    return results
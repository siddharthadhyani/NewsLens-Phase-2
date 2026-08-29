from __future__ import annotations

from typing import List, Dict
from urllib.parse import quote
import requests


def search_sources(claim: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the web for sources related to a claim.

    Uses DuckDuckGo's public HTML search endpoint as a simple
    dependency-free first implementation.

    Returns:
        A list of dictionaries containing:
        - title
        - url
        - snippet
    """

    if not isinstance(claim, str):
        raise TypeError("claim must be a string")

    claim = claim.strip()

    if not claim:
        return []

    if max_results <= 0:
        return []

    url = f"https://html.duckduckgo.com/html/?q={quote(claim)}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

    except requests.RequestException:
        return []

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(response.text, "html.parser")

    results: List[Dict[str, str]] = []

    for result in soup.select(".result"):

        title_element = result.select_one(".result__a")
        snippet_element = result.select_one(".result__snippet")

        if title_element is None:
            continue

        title = title_element.get_text(" ", strip=True)
        result_url = title_element.get("href", "").strip()

        snippet = ""

        if snippet_element is not None:
            snippet = snippet_element.get_text(" ", strip=True)

        if not result_url:
            continue

        results.append(
            {
                "title": title,
                "url": result_url,
                "snippet": snippet,
            }
        )

        if len(results) >= max_results:
            break

    return results
from __future__ import annotations

from typing import Any

from core.claims import extract_claims
from services.evidence import classify_evidence
from services.source_search import search_sources


def verify_article(
    article: str,
    max_claims: int = 5,
    sources_per_claim: int = 3,
) -> dict[str, Any]:
    """
    Run the Phase 2 article verification pipeline.

    Article
        -> claim extraction
        -> Tavily source search
        -> evidence classification
        -> article-level score
    """

    if not isinstance(article, str):
        raise TypeError("article must be a string")

    article = article.strip()

    if not article:
        raise ValueError("article cannot be empty")

    if max_claims <= 0:
        raise ValueError("max_claims must be greater than 0")

    if sources_per_claim <= 0:
        raise ValueError("sources_per_claim must be greater than 0")

    claims = extract_claims(article)[:max_claims]

    claim_results = []

    for claim in claims:
        sources = search_sources(
            claim,
            max_results=sources_per_claim,
        )

        result = classify_evidence(
            claim,
            sources,
        )

        claim_results.append(result)

    if claim_results:
        overall_score = round(
            sum(item["confidence"] for item in claim_results)
            / len(claim_results)
        )
    else:
        overall_score = 0

    return {
        "article": article,
        "claim_count": len(claim_results),
        "claims": claim_results,
        "overall_score": overall_score,
    }
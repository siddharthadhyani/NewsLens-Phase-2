from __future__ import annotations

import re
from typing import Any


SUPPORTED = "SUPPORTED"
PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
CONTRADICTED = "CONTRADICTED"
UNVERIFIED = "UNVERIFIED"


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s%.-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _token_overlap(claim: str, evidence: str) -> float:
    claim_tokens = set(_normalize(claim).split())
    evidence_tokens = set(_normalize(evidence).split())

    if not claim_tokens:
        return 0.0

    return len(claim_tokens & evidence_tokens) / len(claim_tokens)


def classify_evidence(
    claim: str,
    search_results: list[dict[str, Any]],
) -> dict[str, Any]:

    if not isinstance(claim, str):
        raise TypeError("claim must be a string")

    claim = claim.strip()

    if not claim:
        raise ValueError("claim cannot be empty")

    if not isinstance(search_results, list):
        raise TypeError("search_results must be a list")

    if not search_results:
        return {
            "claim": claim,
            "verdict": UNVERIFIED,
            "confidence": 0,
            "evidence": [],
        }

    evidence = []

    for result in search_results:
        content = str(result.get("content", "")).strip()

        if not content:
            continue

        overlap = _token_overlap(claim, content)

        evidence.append(
            {
                "title": str(result.get("title", "")),
                "url": str(result.get("url", "")),
                "content": content,
                "search_score": float(result.get("score", 0.0)),
                "overlap": round(overlap, 3),
            }
        )

    if not evidence:
        return {
            "claim": claim,
            "verdict": UNVERIFIED,
            "confidence": 0,
            "evidence": [],
        }

    best = max(
        evidence,
        key=lambda item: (
            item["overlap"],
            item["search_score"],
        ),
    )

    overlap = best["overlap"]
    search_score = best["search_score"]

    combined = (overlap * 0.7) + (search_score * 0.3)

    if overlap >= 0.65 and search_score >= 0.65:
        verdict = SUPPORTED

    elif overlap >= 0.35 and search_score >= 0.45:
        verdict = PARTIALLY_SUPPORTED

    else:
        verdict = UNVERIFIED

    confidence = round(combined * 100)

    return {
        "claim": claim,
        "verdict": verdict,
        "confidence": confidence,
        "evidence": evidence,
    }
from __future__ import annotations

import re
from typing import Any


SUPPORTED = "SUPPORTED"
PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
CONTRADICTED = "CONTRADICTED"
UNVERIFIED = "UNVERIFIED"


# Words that usually indicate opinion, rhetoric, or emotional framing.
SUBJECTIVE_TERMS = {
    "unbelievable",
    "shocking",
    "terrifying",
    "catastrophic",
    "disastrous",
    "amazing",
    "outrageous",
    "horrific",
    "incredible",
    "insane",
    "obviously",
    "clearly",
    "everyone",
    "nobody",
    "always",
    "never",
    "completely",
    "destroy",
    "destroyed",
    "urgent",
    "urgently",
}


NEGATION_TERMS = {
    "not",
    "no",
    "never",
    "cannot",
    "can't",
    "didn't",
    "doesn't",
    "isn't",
    "wasn't",
    "weren't",
    "false",
    "denied",
    "deny",
    "rejected",
}


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9%.\s'-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _tokens(text: str) -> set[str]:
    return set(_normalize(text).split())


def _numbers(text: str) -> set[str]:
    """
    Extract numeric values such as:
    40
    40%
    1.5
    1.5%
    """
    return {
        value.lower()
        for value in re.findall(
            r"\b\d+(?:\.\d+)?%?",
            text.lower(),
        )
    }


def _has_subjective_language(text: str) -> bool:
    tokens = _tokens(text)
    return bool(tokens & SUBJECTIVE_TERMS)


def _contains_negation(text: str) -> bool:
    tokens = _tokens(text)
    return bool(tokens & NEGATION_TERMS)


def _token_overlap(claim: str, evidence: str) -> float:
    claim_tokens = _tokens(claim)
    evidence_tokens = _tokens(evidence)

    if not claim_tokens:
        return 0.0

    return len(claim_tokens & evidence_tokens) / len(claim_tokens)


def _number_match(claim: str, evidence: str) -> bool:
    claim_numbers = _numbers(claim)

    if not claim_numbers:
        return True

    evidence_numbers = _numbers(evidence)

    return bool(claim_numbers & evidence_numbers)


def _number_conflict(claim: str, evidence: str) -> bool:
    claim_numbers = _numbers(claim)
    evidence_numbers = _numbers(evidence)

    if not claim_numbers or not evidence_numbers:
        return False

    # If both contain numeric values but share none, treat this
    # as a possible contradiction only when textual overlap is high.
    return not bool(claim_numbers & evidence_numbers)


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

    evidence_items: list[dict[str, Any]] = []

    claim_is_subjective = _has_subjective_language(claim)

    for result in search_results:

        content = str(result.get("content", "")).strip()

        if not content:
            continue

        search_score = float(result.get("score", 0.0))
        overlap = _token_overlap(claim, content)

        evidence_items.append(
            {
                "title": str(result.get("title", "")),
                "url": str(result.get("url", "")),
                "content": content,
                "search_score": search_score,
                "overlap": round(overlap, 3),
                "number_match": _number_match(claim, content),
            }
        )

    if not evidence_items:
        return {
            "claim": claim,
            "verdict": UNVERIFIED,
            "confidence": 0,
            "evidence": [],
        }

    best = max(
        evidence_items,
        key=lambda item: (
            item["overlap"],
            item["search_score"],
        ),
    )

    overlap = best["overlap"]
    search_score = best["search_score"]
    numbers_match = best["number_match"]

    # --------------------------------------------------------
    # Conservative verification logic
    # --------------------------------------------------------

    if claim_is_subjective:
        verdict = UNVERIFIED
        confidence = round(search_score * 40)

    elif overlap >= 0.70 and search_score >= 0.70:

        if not numbers_match and _number_conflict(
            claim,
            best["content"],
        ):
            verdict = CONTRADICTED
            confidence = round(
                (overlap * 0.6 + search_score * 0.4) * 100
            )

        elif _contains_negation(best["content"]):
            verdict = PARTIALLY_SUPPORTED
            confidence = round(
                (overlap * 0.6 + search_score * 0.4) * 100
            )

        else:
            verdict = SUPPORTED
            confidence = round(
                (overlap * 0.6 + search_score * 0.4) * 100
            )

    elif overlap >= 0.40 and search_score >= 0.45:

        if not numbers_match and _number_conflict(
            claim,
            best["content"],
        ):
            verdict = CONTRADICTED
        else:
            verdict = PARTIALLY_SUPPORTED

        confidence = round(
            (overlap * 0.6 + search_score * 0.4) * 100
        )

    else:
        verdict = UNVERIFIED
        confidence = round(
            (overlap * 0.5 + search_score * 0.5) * 100
        )

    return {
        "claim": claim,
        "verdict": verdict,
        "confidence": min(100, max(0, confidence)),
        "evidence": evidence_items,
    }
"""
NewsLens Phase 2
Claim extraction utilities.

This module identifies factual/checkable statements from
an article so they can be verified against external evidence
in later Phase 2 steps.
"""

from __future__ import annotations

import re
from typing import List


def normalize_text(text: str) -> str:
    """
    Normalize whitespace while preserving sentence boundaries.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> List[str]:
    """
    Split article text into simple sentences.

    This is intentionally lightweight. More advanced NLP-based
    sentence segmentation can be introduced later if needed.
    """
    text = normalize_text(text)

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def is_checkable_claim(sentence: str) -> bool:
    """
    Decide whether a sentence appears to contain a factual claim.

    This is a first-pass heuristic for Phase 2. It is not a
    truth detector. It only identifies statements that may be
    suitable for later verification.
    """
    sentence = sentence.strip()

    if not sentence:
        return False

    # Ignore obvious questions.
    if sentence.endswith("?"):
        return False

    # Ignore very short fragments.
    words = sentence.split()

    if len(words) < 5:
        return False

    # Common linguistic signals for factual claims.
    claim_patterns = [
        r"\b(is|are|was|were)\b",
        r"\b(has|have|had)\b",
        r"\b(will|would)\b",
        r"\b(announced|reported|said|stated)\b",
        r"\b(increased|decreased|rose|fell)\b",
        r"\b(reached|caused|created|resulted)\b",
        r"\b(percent|%|\d+)\b",
    ]

    return any(
        re.search(pattern, sentence, flags=re.IGNORECASE)
        for pattern in claim_patterns
    )


def extract_claims(text: str) -> List[str]:
    """
    Extract potentially checkable claims from article text.

    Returns:
        A list of sentence-level claims.
    """
    sentences = split_sentences(text)

    claims = [
        sentence
        for sentence in sentences
        if is_checkable_claim(sentence)
    ]

    return claims
from core.claims import extract_claims


def test_extracts_factual_claim():
    text = (
        "The government announced a 40% increase in funding. "
        "Will the policy work?"
    )

    claims = extract_claims(text)

    assert "The government announced a 40% increase in funding." in claims


def test_empty_text_returns_empty_list():
    assert extract_claims("") == []
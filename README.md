# 📰 NewsLens

> **Understand the news. Don't just read it.**

NewsLens is an AI-assisted media literacy and evidence-based news analysis tool. It analyzes how a news story is presented and helps users investigate potentially factual claims using live web sources.

---

## 🎯 Problem Statement

News consumers are exposed to large amounts of information every day. Headlines and articles can influence readers through:

- Sensational language
- Emotional framing
- Loaded words
- Strong positive or negative language
- Claims presented without immediate context

NewsLens helps users examine these signals before accepting information at face value.

---

## 💡 Our Solution

NewsLens analyzes a news article in two layers:

### Phase 1 — Presentation Analysis

The system analyzes how the article is written and presented.

1. Tone Analysis
2. Content Type Classification
3. Sensationalism Detection
4. Emotional Framing Analysis
5. Loaded Language Detection
6. Potential Factual Claim Extraction
7. Overall Presentation Score

### Phase 2 — Evidence-Assisted Claim Verification

Potentially checkable claims are investigated using live web search.

1. Extract checkable claims
2. Search live web sources using Tavily
3. Retrieve evidence and source content
4. Compare claims with retrieved evidence
5. Classify claims as:
   - ✅ Supported
   - ⚠️ Partially Supported
   - ❌ Contradicted
   - ❓ Unverified
6. Calculate a claim-verification score
7. Display supporting sources and evidence to the user

---

## 🔎 Phase 2 Verification Pipeline

```text
News Article
     ↓
Claim Extraction
     ↓
Live Web Search
     ↓
Evidence Retrieval
     ↓
Evidence Comparison
     ↓
Claim Verdict
     ↓
Verification Score
     ↓
Sources & Evidence


# 📰 NewsLens

> **Understand the news. Don't just read it..**

## 🚀 Live Demo

👉 **[Launch NewsLens](https://newslens-phase-2-tnx68dxujz7qh8bzxytf9e.streamlit.app/)**

No installation or local setup required..

> **Understand the news. Don't just read it...**

NewsLens is an AI-assisted media literacy and evidence-assisted news analysis platform designed to help users understand both **how a news story is presented** and **whether potentially factual claims are supported by available evidence**..

News articles can influence readers through sensational headlines, emotional language, loaded wording, and claims that are presented without enough context. NewsLens gives users a structured way to examine these signals instead of simply accepting an article at face value.

---

## 🎯 Problem Statement

News consumers are exposed to huge amounts of information every day. A news story can influence perception not only through the facts it presents, but also through the way those facts are written and framed.

Common warning signals include:

- Sensational language.
- Emotional framing.
- Loaded words.
- Strong positive or negative language
- Exaggerated statements
- Potential factual claims without immediate supporting context

NewsLens helps users identify these signals and investigate potentially checkable claims using external web evidence.

---

## 💡 Our Solution

NewsLens uses a two-phase analysis pipeline.

### Phase 1 — News Presentation Analysis

The first layer analyzes the linguistic and presentation characteristics of an article.

It includes:

1. **Tone Analysis**  
   Identifies whether the overall tone is positive, negative, neutral, or unclear.

2. **Content Type Classification**  
   Determines the general type of content being analyzed.

3. **Sensationalism Detection**  
   Identifies language that may exaggerate or dramatize a story.

4. **Emotional Framing Analysis**  
   Detects language that attempts to trigger emotional reactions.

5. **Loaded Language Detection**  
   Identifies strongly biased or emotionally loaded wording.

6. **Potential Factual Claim Extraction**  
   Extracts statements that appear potentially factual or suitable for verification.

7. **Presentation Score**  
   Produces an overall score representing the article's presentation characteristics.

---

## 🔎 Phase 2 — Evidence-Assisted Claim Verification

Phase 2 extends NewsLens beyond presentation analysis by investigating potentially checkable claims using live web search.

The system:

1. Extracts potentially factual claims from the article.
2. Searches the live web for relevant sources using the **Tavily Search API**.
3. Retrieves source titles, URLs, content, and search relevance scores.
4. Compares the extracted claim with the retrieved evidence.
5. Assigns a conservative verification status.
6. Calculates a verification confidence score.
7. Displays the retrieved evidence and source links to the user.

### Verification statuses

- ✅ **SUPPORTED** — the available evidence strongly aligns with the claim.
- ⚠️ **PARTIALLY SUPPORTED** — the available evidence provides only partial support.
- ❌ **CONTRADICTED** — the available evidence conflicts with the claim.
- ❓ **UNVERIFIED** — the available evidence is insufficient to support a reliable conclusion.

---

## 🔬 Phase 2 Architecture

```text
                 News Article
                      │
                      ▼
              Claim Extraction
                      │
                      ▼
              Live Web Search
                (Tavily API)
                      │
                      ▼
             Evidence Retrieval
                      │
                      ▼
             Evidence Comparison
                      │
                      ▼
               Claim Verdict
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Supported   Partially   Unverified
                   Supported
          │
          ▼
        Verification Score
          │
          ▼
      Sources & Evidence

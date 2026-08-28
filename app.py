import re
import streamlit as st


# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="NewsLens",
    page_icon="📰",
    layout="wide"
)


# -----------------------------
# CUSTOM CSS
# -----------------------------

st.markdown("""
<style>

.main {
    background-color: #0b0f17;
}

.block-container {
    max-width: 1100px;
    padding-top: 3rem;
}

.hero {
    padding: 10px 0 25px 0;
}

.badge {
    display: inline-block;
    background: #17243d;
    color: #7db7ff;
    padding: 7px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.hero-title {
    font-size: 48px;
    font-weight: 800;
    margin-top: 15px;
    margin-bottom: 5px;
}

.hero-subtitle {
    color: #a7afbf;
    font-size: 18px;
}

.metric-card {
    background: #151b27;
    border: 1px solid #252d3d;
    border-radius: 14px;
    padding: 20px;
    min-height: 125px;
}

.metric-label {
    color: #8e98aa;
    font-size: 13px;
    font-weight: 600;
}

.metric-value {
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}

.result-box {
    background: #151b27;
    border: 1px solid #252d3d;
    border-radius: 14px;
    padding: 22px;
    margin-top: 15px;
}

.section-title {
    font-size: 23px;
    font-weight: 750;
    margin-top: 25px;
}

.warning {
    background: #2a2115;
    border: 1px solid #59401c;
    border-radius: 12px;
    padding: 15px;
}

.safe {
    background: #14251c;
    border: 1px solid #244d35;
    border-radius: 12px;
    padding: 15px;
}

.claim {
    background: #121925;
    border-left: 4px solid #5c9cff;
    padding: 12px 15px;
    margin: 8px 0;
    border-radius: 6px;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# ANALYSIS DICTIONARIES
# -----------------------------

POSITIVE_WORDS = {
    "success", "successful", "growth", "improve", "improved",
    "benefit", "benefits", "positive", "win", "wins", "victory",
    "progress", "achievement", "opportunity", "hope", "better",
    "increase", "increased", "gain", "gained"
}

NEGATIVE_WORDS = {
    "crisis", "crash", "death", "dead", "disaster", "danger",
    "dangerous", "failure", "failed", "attack", "war", "fear",
    "threat", "threatening", "loss", "lost", "decline", "declined",
    "problem", "protest", "violence", "kill", "killed"
}

SENSATIONAL_WORDS = {
    "shocking", "breaking", "exclusive", "unbelievable",
    "outrageous", "explosive", "massive", "terrifying",
    "horrifying", "stunning", "jaw-dropping", "secret",
    "exposed", "urgent", "disaster", "bombshell", "scandal",
    "you won't believe", "must see", "viral"
}

EMOTIONAL_WORDS = {
    "fear", "afraid", "terrifying", "angry", "anger", "outrage",
    "love", "hate", "shocking", "horrifying", "heartbreaking",
    "tragic", "hope", "proud", "betrayal", "panic"
}

OPINION_MARKERS = {
    "i think", "i believe", "in my opinion", "should",
    "must", "clearly", "obviously", "perhaps", "probably",
    "arguably", "we need", "it seems"
}

FACTUAL_MARKERS = {
    "according to", "reported", "data", "official", "confirmed",
    "announced", "statement", "study", "research", "statistics",
    "percent", "%", "said", "reported by"
}


# -----------------------------
# BASIC TEXT FUNCTIONS
# -----------------------------

def words(text):
    return re.findall(r"\b[\w'-]+\b", text.lower())


def count_matches(text, vocabulary):
    text_lower = text.lower()
    tokens = words(text)

    count = 0

    for item in vocabulary:
        if " " in item:
            if item in text_lower:
                count += 1
        elif item in tokens:
            count += 1

    return count


def sentence_split(text):
    return [
        s.strip()
        for s in re.split(r"[.!?]+", text)
        if s.strip()
    ]


# -----------------------------
# TONE ANALYSIS
# -----------------------------

def analyze_tone(text):
    pos = count_matches(text, POSITIVE_WORDS)
    neg = count_matches(text, NEGATIVE_WORDS)

    if pos > neg:
        tone = "Positive"
    elif neg > pos:
        tone = "Negative"
    else:
        tone = "Neutral"

    total = pos + neg

    if total == 0:
        confidence = 50
    else:
        confidence = min(95, 55 + abs(pos - neg) * 8)

    return tone, confidence, pos, neg


# -----------------------------
# SENSATIONALISM
# -----------------------------

def analyze_sensationalism(text):
    matches = count_matches(text, SENSATIONAL_WORDS)

    exclamation_count = text.count("!")
    question_count = text.count("?")

    uppercase_words = re.findall(r"\b[A-Z]{3,}\b", text)
    uppercase_penalty = min(4, len(uppercase_words))

    score = (
        matches * 12
        + exclamation_count * 7
        + uppercase_penalty * 5
        + min(question_count * 3, 9)
    )

    score = min(100, score)

    if score >= 65:
        label = "High"
    elif score >= 30:
        label = "Moderate"
    else:
        label = "Low"

    return score, label


# -----------------------------
# EMOTIONAL FRAMING
# -----------------------------

def analyze_emotion(text):
    count = count_matches(text, EMOTIONAL_WORDS)

    if count >= 5:
        return "Strong emotional framing", min(95, 55 + count * 6)

    if count >= 2:
        return "Moderate emotional framing", min(90, 45 + count * 7)

    return "Low emotional framing", 25


# -----------------------------
# CONTENT TYPE
# -----------------------------

def analyze_content_type(text):
    opinion = count_matches(text, OPINION_MARKERS)
    factual = count_matches(text, FACTUAL_MARKERS)

    if opinion >= 2 and opinion > factual:
        return "Opinion / Commentary"

    if factual >= 2 and factual >= opinion:
        return "News / Factual reporting"

    return "Mixed / Unclear"


# -----------------------------
# LOADED LANGUAGE
# -----------------------------

def detect_loaded_language(text):
    found = []

    for word in SENSATIONAL_WORDS:
        if word in text.lower():
            found.append(word)

    return found[:10]


# -----------------------------
# CLAIM EXTRACTION
# -----------------------------

def extract_claims(text):
    sentences = sentence_split(text)

    claims = []

    for sentence in sentences:

        lower = sentence.lower()

        has_number = bool(
            re.search(r"\b\d+(?:\.\d+)?%?\b", sentence)
        )

        has_factual_marker = any(
            marker in lower
            for marker in FACTUAL_MARKERS
        )

        has_claim_verb = any(
            verb in lower.split()
            for verb in [
                "is", "are", "was", "were",
                "has", "have", "will",
                "announced", "said", "reported",
                "caused", "increased", "decreased"
            ]
        )

        if has_number or has_factual_marker or has_claim_verb:
            claims.append(sentence)

    return claims[:6]


# -----------------------------
# OVERALL PRESENTATION SCORE
# -----------------------------

def calculate_score(sensationalism, emotion_score, loaded_count, content_type):

    score = 100

    score -= sensationalism * 0.35
    score -= emotion_score * 0.15
    score -= loaded_count * 3

    if content_type == "Mixed / Unclear":
        score -= 5

    return max(0, min(100, round(score)))


# -----------------------------
# EXPLANATION
# -----------------------------

def generate_explanation(
    tone,
    content_type,
    sensational_label,
    emotion_label,
    loaded_words,
    score
):

    explanations = []

    explanations.append(
        f"The story is classified as {content_type.lower()}."
    )

    explanations.append(
        f"The overall tone is {tone.lower()}."
    )

    if sensational_label == "High":
        explanations.append(
            "The text contains several signals associated with sensational presentation."
        )
    elif sensational_label == "Moderate":
        explanations.append(
            "The text contains some attention-grabbing or sensational language."
        )
    else:
        explanations.append(
            "The text shows relatively few sensational language signals."
        )

    if emotion_label == "Strong emotional framing":
        explanations.append(
            "Strong emotional wording may influence how readers perceive the story."
        )
    elif emotion_label == "Moderate emotional framing":
        explanations.append(
            "Some emotional language is present and may influence reader perception."
        )

    if loaded_words:
        explanations.append(
            "Potentially loaded terms detected: "
            + ", ".join(loaded_words[:6])
            + "."
        )

    if score >= 75:
        explanations.append(
            "The presentation appears relatively restrained based on these signals."
        )
    elif score >= 50:
        explanations.append(
            "The presentation contains some signals that deserve reader attention."
        )
    else:
        explanations.append(
            "The presentation contains several signals that deserve careful scrutiny."
        )

    return " ".join(explanations)


# -----------------------------
# HEADER
# -----------------------------

st.markdown("""
<div class="hero">

<div class="badge">
AI-POWERED NEWS INTELLIGENCE
</div>

<div class="hero-title">
📰 NewsLens
</div>

<div class="hero-subtitle">
Understand how information is presented before you believe it.
</div>

</div>
""", unsafe_allow_html=True)


# -----------------------------
# INPUT
# -----------------------------

st.markdown(
    '<div class="section-title">Analyze a news story</div>',
    unsafe_allow_html=True
)

news_text = st.text_area(
    "Paste a headline or article",
    height=220,
    placeholder=(
        "Example:\n\n"
        "Government announces shocking new education policy "
        "that will completely change the future of millions of students..."
    ),
    label_visibility="collapsed"
)

st.caption(
    "NewsLens analyzes tone, content type, sensationalism, "
    "emotional framing, loaded language and potential factual claims."
)


analyze = st.button(
    "🔎  Analyze News",
    use_container_width=True,
    type="primary"
)


# -----------------------------
# ANALYSIS
# -----------------------------

if analyze:

    if not news_text.strip():

        st.warning("Please paste a headline or news article first.")

    elif len(news_text.split()) < 5:

        st.warning(
            "Please provide a little more text for a meaningful analysis."
        )

    else:

        with st.spinner("NewsLens is analyzing the story..."):

            tone, tone_confidence, pos, neg = analyze_tone(news_text)

            sensational_score, sensational_label = (
                analyze_sensationalism(news_text)
            )

            emotion_label, emotion_score = analyze_emotion(news_text)

            content_type = analyze_content_type(news_text)

            loaded_words = detect_loaded_language(news_text)

            claims = extract_claims(news_text)

            overall_score = calculate_score(
                sensational_score,
                emotion_score,
                len(loaded_words),
                content_type
            )

            explanation = generate_explanation(
                tone,
                content_type,
                sensational_label,
                emotion_label,
                loaded_words,
                overall_score
            )


        # -----------------------------
        # RESULTS HEADER
        # -----------------------------

        st.markdown(
            '<div class="section-title">Analysis Results</div>',
            unsafe_allow_html=True
        )

        st.progress(overall_score / 100)

        st.caption(
            f"NewsLens Presentation Score: {overall_score}/100"
        )


        # -----------------------------
        # METRICS
        # -----------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">TONE</div>
                    <div class="metric-value">{tone}</div>
                    <div class="metric-label">
                        {tone_confidence}% confidence
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">CONTENT TYPE</div>
                    <div class="metric-value" style="font-size:20px">
                        {content_type}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">SENSATIONALISM</div>
                    <div class="metric-value">
                        {sensational_label}
                    </div>
                    <div class="metric-label">
                        {sensational_score}/100
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">EMOTIONAL FRAMING</div>
                    <div class="metric-value" style="font-size:19px">
                        {emotion_label}
                    </div>
                    <div class="metric-label">
                        {emotion_score}/100
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # -----------------------------
        # EXPLANATION
        # -----------------------------

        st.markdown(
            '<div class="section-title">🧠 Why did NewsLens flag this?</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="result-box">
                {explanation}
            </div>
            """,
            unsafe_allow_html=True
        )


        # -----------------------------
        # LOADED LANGUAGE
        # -----------------------------

        st.markdown(
            '<div class="section-title">🚨 Language Signals</div>',
            unsafe_allow_html=True
        )

        if loaded_words:

            st.markdown(
                f"""
                <div class="warning">
                <b>Potentially loaded / sensational terms detected</b><br><br>
                {", ".join(loaded_words)}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="safe">
                No major sensational keywords were detected.
                </div>
                """,
                unsafe_allow_html=True
            )


        # -----------------------------
        # CLAIMS
        # -----------------------------

        st.markdown(
            '<div class="section-title">📌 Potential Factual Claims</div>',
            unsafe_allow_html=True
        )

        if claims:

            for claim in claims:

                st.markdown(
                    f"""
                    <div class="claim">
                    {claim}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.caption(
                "These are potential claims extracted for later verification. "
                "NewsLens does not currently determine whether they are true or false."
            )

        else:

            st.info(
                "No obvious factual claims were extracted from this text."
            )


        # -----------------------------
        # BREAKDOWN
        # -----------------------------

        st.markdown(
            '<div class="section-title">📊 Signal Breakdown</div>',
            unsafe_allow_html=True
        )

        breakdown_col1, breakdown_col2 = st.columns(2)

        with breakdown_col1:

            st.write("Positive language")
            st.progress(
                min(pos / 5, 1.0)
            )

            st.write("Negative language")
            st.progress(
                min(neg / 5, 1.0)
            )

        with breakdown_col2:

            st.write("Sensationalism")
            st.progress(
                sensational_score / 100
            )

            st.write("Emotional framing")
            st.progress(
                emotion_score / 100
            )


        # -----------------------------
        # DISCLAIMER
        # -----------------------------

        st.markdown("---")

        st.caption(
            "⚠️ NewsLens Phase 1 analyzes linguistic and presentation signals. "
            "It is not a fact-checking system yet. Source verification, "
            "cross-source comparison and evidence retrieval are planned "
            "for the next phase."
        )


# -----------------------------
# FOOTER
# -----------------------------

st.markdown("---")

st.caption(
    "NewsLens • AI-assisted media literacy and information analysis"
)

import streamlit as st

from utils.ai_engine import (
    generate_ai_insights,
    answer_question
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="MaternaLens AI — AI Insights",
    page_icon="🤖",
    layout="wide"
)


# ==================================================
# HEADER
# ==================================================

st.title("🤖 MaternaLens AI — Intelligence Center")

st.caption(
    "AI-powered maternal-health interpretation and "
    "natural-language analysis"
)


# ==================================================
# CHECK DATA
# ==================================================

if "df" not in st.session_state:

    st.warning(
        "Please load a dataset from the main MaternaLens AI page."
    )

    st.stop()


df = st.session_state["df"]

analysis = st.session_state["analysis"]

validation = st.session_state["validation"]


# ==================================================
# AI ENGINE
# ==================================================

st.markdown("## 🧠 AI Engine")


ai_results = generate_ai_insights(
    df,
    analysis,
    validation
)


engine_name = ai_results.get(
    "engine",
    "MaternaLens AI"
)

engine_status = ai_results.get(
    "status",
    "unknown"
)


e1, e2 = st.columns(2)


e1.metric(
    "AI Engine",
    engine_name
)


if engine_status == "ready":

    e2.success(
        "🟢 AI Engine Ready"
    )

else:

    e2.warning(
        f"AI Engine Status: {engine_status}"
    )


# ==================================================
# AI INSIGHTS
# ==================================================

st.markdown("## 💡 AI-Generated Insights")


insights = ai_results.get(
    "insights",
    []
)


if insights:

    for item in insights:

        category = item.get(
            "category",
            "Insight"
        )

        insight = item.get(
            "insight",
            ""
        )


        with st.container(
            border=True
        ):

            st.markdown(
                f"### {category}"
            )

            st.write(
                insight
            )

else:

    st.info(
        "No AI insights are currently available."
    )


# ==================================================
# MATERNAL HEALTH SNAPSHOT
# ==================================================

st.markdown("## 📌 Maternal Health Snapshot")


mmr = analysis.get(
    "mmr"
)

target = analysis.get(
    "target"
)


if mmr:

    s1, s2, s3 = st.columns(3)


    s1.metric(
        "Latest MMR",
        f"{mmr['latest_value']:.1f}"
    )


    s2.metric(
        "Initial MMR",
        f"{mmr['initial_value']:.1f}"
    )


    s3.metric(
        "MMR Reduction",
        f"{mmr['absolute_reduction']:.1f}"
    )


if target:

    st.markdown(
        "### 🎯 SDG 3.1 Assessment"
    )


    latest = target.get(
        "latest"
    )

    target_value = target.get(
        "target"
    )

    gap = target.get(
        "gap"
    )

    status = target.get(
        "status",
        "Unknown"
    )

    additional = target.get(
        "additional_reduction_required_percent"
    )


    if latest is not None:

        st.write(
            f"**Latest MMR:** {latest:.1f} "
            "per 100,000 live births"
        )


    if target_value is not None:

        st.write(
            f"**SDG 3.1 Target:** {target_value:.1f}"
        )


    if gap is not None:

        st.write(
            f"**Current Gap:** {gap:.1f}"
        )


    if status == "Target achieved":

        st.success(
            "🟢 The SDG 3.1 target has been achieved."
        )

    else:

        st.warning(
            "🟠 The SDG 3.1 target has not yet been achieved."
        )


        if additional is not None:

            st.write(
                f"Approximately **{additional:.2f}%** "
                "additional reduction from the latest "
                "MMR is required to reach the target."
            )


# ==================================================
# NATURAL LANGUAGE Q&A
# ==================================================

st.markdown("## 💬 Ask MaternaLens AI")


st.write(
    "Ask a question about the dataset, maternal mortality, "
    "SDG 3.1, or maternal-health indicators."
)


question = st.text_input(
    "Your question",
    placeholder=(
        "Example: What is the latest maternal mortality ratio?"
    )
)


if question:

    with st.spinner(
        "MaternaLens AI is analyzing the dataset..."
    ):

        response = answer_question(
            question,
            analysis
        )


    st.markdown(
        "### 🤖 AI Response"
    )


    with st.container(
        border=True
    ):

        st.write(
            response
        )


# ==================================================
# QUICK QUESTIONS
# ==================================================

st.markdown("## ⚡ Quick Questions")


q1, q2 = st.columns(2)


with q1:

    if st.button(
        "📉 What is the latest MMR?",
        use_container_width=True
    ):

        response = answer_question(
            "What is the latest MMR?",
            analysis
        )

        st.info(
            response
        )


    if st.button(
        "📊 How much has MMR reduced?",
        use_container_width=True
    ):

        response = answer_question(
            "How much has MMR reduced?",
            analysis
        )

        st.info(
            response
        )


with q2:

    if st.button(
        "🎯 What is the SDG target?",
        use_container_width=True
    ):

        response = answer_question(
            "What is the SDG target?",
            analysis
        )

        st.info(
            response
        )


    if st.button(
        "🧠 Give me an overall summary",
        use_container_width=True
    ):

        response = answer_question(
            "Give me an overall summary.",
            analysis
        )

        st.info(
            response
        )


# ==================================================
# DATASET UNDERSTANDING
# ==================================================

st.markdown("## 🔍 AI Dataset Understanding")


profile = analysis.get(
    "profile",
    {}
)


u1, u2, u3, u4 = st.columns(4)


u1.metric(
    "Records",
    profile.get(
        "rows",
        len(df)
    )
)


u2.metric(
    "Columns",
    profile.get(
        "columns",
        len(df.columns)
    )
)


u3.metric(
    "Indicators",
    profile.get(
        "indicators",
        "N/A"
    )
)


u4.metric(
    "Locations",
    profile.get(
        "areas",
        "N/A"
    )
)


# ==================================================
# AI PIPELINE
# ==================================================

st.markdown("## 🔄 MaternaLens AI Pipeline")


pipeline = [
    ("1️⃣", "Dataset", "Load uploaded or built-in data"),
    ("2️⃣", "Validation", "Check structure and data quality"),
    ("3️⃣", "Analysis", "Identify trends and indicators"),
    ("4️⃣", "AI Reasoning", "Generate interpretable insights"),
    ("5️⃣", "Q&A", "Answer natural-language questions"),
]


for icon, title, description in pipeline:

    with st.container(
        border=True
    ):

        p1, p2 = st.columns([1, 6])

        p1.markdown(
            f"## {icon}"
        )

        p2.markdown(
            f"**{title}**"
        )

        p2.caption(
            description
        )

# ==================================================
# IBM WATSONX.AI INTEGRATION
# ==================================================

st.markdown("## ☁️ IBM watsonx.ai Integration")

ibm_insight = ai_results.get("ibm_insight")

if ibm_insight:
    st.success(
        "🟢 IBM watsonx.ai is connected and actively "
        "providing AI-powered interpretation."
    )

    st.caption(
        "Model: Meta Llama 3.3 70B Instruct • "
        "Platform: IBM watsonx.ai"
    )

else:
    st.info(
        "MaternaLens AI is using its local deterministic "
        "analysis engine. IBM watsonx.ai is available when "
        "valid IBM Cloud credentials are configured."
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "MaternaLens AI • AI Intelligence Center • SDG 3.1"
)
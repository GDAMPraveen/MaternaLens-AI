# ==========================================
# MATERNA LENS AI
# Main Streamlit Application
# ==========================================

import streamlit as st
import pandas as pd

from utils.data_loader import (
    load_dataset,
    load_uploaded_dataset,
    get_dataset_info
)

from utils.data_validator import (
    validate_dataset
)

from utils.analyzer import (
    analyze_dataset
)

from utils.ai_engine import (
    generate_ai_insights,
    answer_question
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MaternaLens AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #6b7280;
        margin-top: 0;
    }

    .section-title {
        font-size: 26px;
        font-weight: 600;
        margin-top: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="main-title">MaternaLens AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered maternal health intelligence for SDG 3.1'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("MaternaLens AI")

st.sidebar.markdown(
    """
    **Maternal Health Intelligence**

    Track maternal mortality, healthcare
    coverage, SDG progress and data-driven
    insights.
    """
)

st.sidebar.divider()

data_source = st.sidebar.radio(
    "Data Source",
    [
        "Built-in Dataset",
        "Upload Dataset"
    ]
)


# ==========================================
# LOAD DATASET
# ==========================================

df = None


if data_source == "Built-in Dataset":

    try:

        df = load_dataset()

        st.sidebar.success(
            "Built-in dataset loaded"
        )

    except Exception as e:

        st.error(
            f"Could not load built-in dataset: {e}"
        )

        st.stop()


else:

    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV Dataset",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:

            df = load_uploaded_dataset(
                uploaded_file
            )

            st.sidebar.success(
                "Dataset uploaded successfully"
            )

        except Exception as e:

            st.error(
                f"Could not read uploaded dataset: {e}"
            )

            st.stop()

    else:

        st.info(
            "Upload a CSV dataset from the sidebar "
            "to begin analysis."
        )

        st.stop()


# ==========================================
# VALIDATE DATASET
# ==========================================

validation = validate_dataset(df)

detected_columns = validation.get(
    "detected_columns",
    {}
)


# ==========================================
# VALIDATION STATUS
# ==========================================

if validation.get("valid"):

    st.sidebar.success(
        "Dataset validation: Passed"
    )

else:

    st.sidebar.warning(
        "Dataset validation: Review required"
    )


# ==========================================
# ANALYZE DATASET
# ==========================================

analysis = analyze_dataset(
    df,
    detected_columns,
    target_value=70
)


# ==========================================
# AI ENGINE
# ==========================================

ai_results = generate_ai_insights(
    df,
    analysis,
    validation
)
# Store data for other pages
st.session_state["df"] = df
st.session_state["validation"] = validation
st.session_state["analysis"] = analysis
st.session_state["ai_results"] = ai_results

# ==========================================
# TOP METRICS
# ==========================================

st.markdown(
    '<div class="section-title">'
    'Maternal Health Overview'
    '</div>',
    unsafe_allow_html=True
)

mmr = analysis.get("mmr")
target = analysis.get("target")
profile = analysis.get("profile", {})


col1, col2, col3, col4 = st.columns(4)


with col1:

    if mmr:

        st.metric(
            "Latest MMR",
            f"{mmr.get('latest_value', 0):.1f}"
        )

    else:

        st.metric(
            "Latest MMR",
            "N/A"
        )


with col2:

    if target:

        st.metric(
            "SDG 3.1 Target",
            f"{target.get('target', 70):.1f}"
        )

    else:

        st.metric(
            "SDG 3.1 Target",
            "70"
        )


with col3:

    if mmr:

        st.metric(
            "MMR Reduction",
            f"{mmr.get('percentage_reduction', 0):.2f}%"
        )

    else:

        st.metric(
            "MMR Reduction",
            "N/A"
        )


with col4:

    st.metric(
        "Records",
        f"{profile.get('rows', len(df)):,}"
    )


# ==========================================
# DATASET INFORMATION
# ==========================================

st.markdown(
    '<div class="section-title">'
    'Dataset Information'
    '</div>',
    unsafe_allow_html=True
)

info_col1, info_col2, info_col3, info_col4 = st.columns(4)


with info_col1:

    st.metric(
        "Rows",
        f"{len(df):,}"
    )


with info_col2:

    st.metric(
        "Columns",
        f"{len(df.columns):,}"
    )


with info_col3:

    st.metric(
        "Indicators",
        f"{profile.get('indicators', 0):,}"
    )


with info_col4:

    st.metric(
        "Locations",
        f"{profile.get('areas', 0):,}"
    )


# ==========================================
# AI INSIGHTS
# ==========================================

st.markdown(
    '<div class="section-title">'
    'AI-Generated Insights'
    '</div>',
    unsafe_allow_html=True
)

for item in ai_results.get(
    "insights",
    []
):

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
            f"**{category}**"
        )

        st.write(
            insight
        )


# ==========================================
# NATURAL LANGUAGE Q&A
# ==========================================

st.markdown(
    '<div class="section-title">'
    'Ask MaternaLens AI'
    '</div>',
    unsafe_allow_html=True
)

question = st.text_input(
    "Ask a question about the dataset",
    placeholder=(
        "Example: What is the latest MMR?"
    )
)


if question:

    answer = answer_question(
        question,
        df,
        analysis
    )

    st.markdown(
        "**MaternaLens AI:**"
    )

    st.info(
        answer
    )


# ==========================================
# RAW DATA PREVIEW
# ==========================================

st.markdown(
    '<div class="section-title">'
    'Data Preview'
    '</div>',
    unsafe_allow_html=True
)

with st.expander(
    "View dataset"
):

    st.dataframe(
        df.head(100),
        use_container_width=True
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "MaternaLens AI • SDG 3.1 Maternal Health "
    "Intelligence • Local AI Engine"
)
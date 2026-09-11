import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.visualizations import (
    create_mmr_trend,
    create_indicator_comparison,
)

st.set_page_config(
    page_title="MaternaLens AI | Dashboard",
    page_icon="🌍",
    layout="wide",
)

# ============================================================
# SESSION STATE
# ============================================================

if "df" not in st.session_state or "analysis" not in st.session_state:
    st.warning("Please load a dataset from the main page first.")
    st.stop()

df = st.session_state["df"]
analysis = st.session_state["analysis"]

validation = st.session_state.get("validation", {})
ai_results = st.session_state.get("ai_results", {})

detected = validation.get("detected_columns", {})

indicator_column = detected.get("indicator")
value_column = detected.get("value")
area_column = detected.get("area")
time_column = detected.get("time")
unit_column = detected.get("unit")


# ============================================================
# HEADER
# ============================================================

st.title("🌍 MaternaLens AI")
st.caption(
    "AI-powered maternal health analytics aligned with "
    "UN Sustainable Development Goal 3.1"
)

st.divider()


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.subheader("📊 Dataset Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Records",
    f"{len(df):,}"
)

c2.metric(
    "Indicators",
    f"{df[indicator_column].nunique():,}"
    if indicator_column and indicator_column in df.columns
    else "N/A"
)

c3.metric(
    "Locations",
    f"{df[area_column].nunique():,}"
    if area_column and area_column in df.columns
    else "N/A"
)

c4.metric(
    "Columns",
    f"{len(df.columns):,}"
)

st.divider()


# ============================================================
# SDG 3.1 SECTION
# ============================================================

st.subheader("🎯 SDG 3.1 Progress")

target = analysis.get("target")

if target:

    latest = target.get("latest")
    initial = target.get("initial")
    target_value = target.get("target")
    gap = target.get("gap")
    status = target.get("status")
    reduction_required = target.get(
        "additional_reduction_required_percent"
    )

    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Latest MMR",
        f"{latest:.1f}"
        if latest is not None
        else "N/A",
        help="Maternal deaths per 100,000 live births",
    )

    c2.metric(
        "SDG Target",
        f"{target_value:.0f}",
        help="SDG 3.1 target for maternal mortality",
    )

    c3.metric(
        "Gap to Target",
        f"{gap:.1f}"
        if gap is not None
        else "N/A",
    )

    if reduction_required is not None:
        c4.metric(
            "Reduction Needed",
            f"{reduction_required:.2f}%",
        )
    else:
        c4.metric(
            "Status",
            status or "Unknown",
        )

    # --------------------------------------------------------
    # PROGRESS BAR
    # --------------------------------------------------------

    st.markdown("### Progress Toward SDG 3.1")

    if latest is not None and target_value is not None:

        # Percentage progress from initial MMR toward target
        if initial is not None and initial != target_value:

            progress = (
                (initial - latest)
                / (initial - target_value)
            ) * 100

            progress = max(0, min(progress, 100))

        else:
            progress = 0

        st.progress(
            int(progress),
            text=f"{progress:.1f}% of the required reduction achieved",
        )

        if latest <= target_value:
            st.success(
                "✅ The latest MMR has reached the SDG 3.1 target."
            )
        else:
            st.warning(
                f"⚠️ The latest MMR is still "
                f"{gap:.1f} deaths per 100,000 live births "
                f"above the target."
            )


# ============================================================
# MMR TREND
# ============================================================

st.divider()

st.subheader("📈 Maternal Mortality Trend")

try:

    fig = create_mmr_trend(
        df,
        detected,
    )

    if fig is not None:
        st.plotly_chart(
            fig,
            use_container_width=True,
        )
    else:
        st.info(
            "Maternal mortality trend could not be generated "
            "from this dataset."
        )

except Exception as e:

    st.info(
        "Maternal mortality trend is not available "
        "for this dataset."
    )


# ============================================================
# MATERNAL HEALTH INDICATORS
# ============================================================

st.divider()

st.subheader("🩺 Maternal Health Indicators")

try:

    fig = create_indicator_comparison(
        df,
        detected,
    )

    if fig is not None:
        st.plotly_chart(
            fig,
            use_container_width=True,
        )
    else:
        st.info(
            "Indicator comparison is not available."
        )

except Exception:

    st.info(
        "Indicator comparison could not be generated."
    )


# ============================================================
# MMR REDUCTION
# ============================================================

mmr = analysis.get("mmr")

if mmr:

    st.divider()

    st.subheader("📉 MMR Reduction")

    initial_value = mmr.get("initial_value")
    latest_value = mmr.get("latest_value")
    absolute_reduction = mmr.get("absolute_reduction")
    percentage_reduction = mmr.get(
        "percentage_reduction"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Initial MMR",
        f"{initial_value:.1f}"
        if initial_value is not None
        else "N/A",
    )

    c2.metric(
        "Latest MMR",
        f"{latest_value:.1f}"
        if latest_value is not None
        else "N/A",
    )

    c3.metric(
        "Total Reduction",
        (
            f"{absolute_reduction:.1f} "
            f"({percentage_reduction:.2f}%)"
        )
        if absolute_reduction is not None
        and percentage_reduction is not None
        else "N/A",
    )


# ============================================================
# COVERAGE GAP
# ============================================================

coverage = analysis.get("coverage_gap")

if coverage:

    st.divider()

    st.subheader("🏥 Maternal Healthcare Coverage")

    # Support multiple possible key names
    skilled = coverage.get(
        "skilled_attendance_1yr",
        coverage.get("skilled_1yr")
    )

    anc = coverage.get(
        "anc_4plus",
        coverage.get("antenatal_4plus")
    )

    gap = coverage.get(
        "gap",
        coverage.get("coverage_gap")
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Skilled Birth Attendance",
        f"{skilled:.1f}%"
        if isinstance(skilled, (int, float))
        else "N/A",
    )

    c2.metric(
        "ANC 4+ Visits",
        f"{anc:.1f}%"
        if isinstance(anc, (int, float))
        else "N/A",
    )

    c3.metric(
        "Coverage Gap",
        f"{gap:.1f} pp"
        if isinstance(gap, (int, float))
        else "N/A",
    )


# ============================================================
# AI INSIGHTS
# ============================================================

if ai_results:

    st.divider()

    st.subheader("🤖 AI-Generated Insights")

    insights = ai_results.get(
        "insights",
        ai_results.get("key_insights", [])
    )

    if insights:

        for item in insights:

            if isinstance(item, dict):

                category = item.get(
                    "category",
                    "Insight"
                )

                insight = item.get(
                    "insight",
                    ""
                )

                st.info(
                    f"**{category}**\n\n{insight}"
                )

            else:

                st.info(str(item))

    else:

        st.info(
            "AI insights will appear here after analysis."
        )


# ============================================================
# DATASET STRUCTURE
# ============================================================

st.divider()

with st.expander("🔍 Detected Dataset Structure"):

    structure = pd.DataFrame(
        {
            "Role": [
                "Area",
                "Time",
                "Indicator",
                "Value",
                "Unit",
            ],
            "Detected Column": [
                area_column,
                time_column,
                indicator_column,
                value_column,
                unit_column,
            ],
        }
    )

    st.dataframe(
        structure,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "MaternaLens AI • Maternal Health Intelligence "
    "for SDG 3.1 • IBM watsonx.ai integration"
)
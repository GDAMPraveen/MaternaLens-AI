import streamlit as st
import pandas as pd


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="MaternaLens AI — Data Explorer",
    page_icon="🔎",
    layout="wide"
)


# ==================================================
# HEADER
# ==================================================

st.title("🔎 MaternaLens AI — Data Explorer")

st.caption(
    "Interactive exploration of maternal-health datasets"
)


# ==================================================
# CHECK DATA
# ==================================================

if "df" not in st.session_state:

    st.warning(
        "Please load a dataset from the main MaternaLens AI page."
    )

    st.stop()


df = st.session_state["df"].copy()

validation = st.session_state.get(
    "validation",
    {}
)


# ==================================================
# DETECTED COLUMNS
# ==================================================

detected = validation.get(
    "detected_columns",
    {}
)


indicator_column = detected.get(
    "indicator"
)

value_column = detected.get(
    "value"
)

time_column = detected.get(
    "time"
)

area_column = detected.get(
    "area"
)

unit_column = detected.get(
    "unit"
)


# ==================================================
# DATASET SUMMARY
# ==================================================

st.markdown("## 📊 Dataset Summary")


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Total Records",
    len(df)
)


c2.metric(
    "Columns",
    len(df.columns)
)


if indicator_column:

    indicator_count = (
        df[indicator_column]
        .dropna()
        .astype(str)
        .nunique()
    )

else:

    indicator_count = 0


c3.metric(
    "Indicators",
    indicator_count
)


if area_column:

    location_count = (
        df[area_column]
        .dropna()
        .astype(str)
        .nunique()
    )

else:

    location_count = 0


c4.metric(
    "Locations",
    location_count
)


# ==================================================
# FILTER SECTION
# ==================================================

st.markdown("## 🎛️ Explore & Filter")


filtered_df = df.copy()


# ==================================================
# INDICATOR FILTER
# ==================================================

if indicator_column:

    indicator_values = sorted(
        df[indicator_column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    selected_indicators = st.multiselect(
        "Select Indicator(s)",
        options=indicator_values,
        default=[],
        help="Leave empty to include all indicators."
    )


    if selected_indicators:

        filtered_df = filtered_df[
            filtered_df[indicator_column]
            .astype(str)
            .isin(selected_indicators)
        ]


# ==================================================
# LOCATION FILTER
# ==================================================

if area_column:

    area_values = sorted(
        df[area_column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    selected_areas = st.multiselect(
        "Select Location(s)",
        options=area_values,
        default=[],
        help="Leave empty to include all locations."
    )


    if selected_areas:

        filtered_df = filtered_df[
            filtered_df[area_column]
            .astype(str)
            .isin(selected_areas)
        ]


# ==================================================
# TIME PERIOD FILTER
# ==================================================

if time_column:

    time_values = sorted(
        df[time_column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    selected_periods = st.multiselect(
        "Select Time Period(s)",
        options=time_values,
        default=[],
        help="Leave empty to include all time periods."
    )


    if selected_periods:

        filtered_df = filtered_df[
            filtered_df[time_column]
            .astype(str)
            .isin(selected_periods)
        ]


# ==================================================
# UNIT FILTER
# ==================================================

if unit_column:

    unit_values = sorted(
        df[unit_column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    selected_units = st.multiselect(
        "Select Unit(s)",
        options=unit_values,
        default=[],
        help="Leave empty to include all units."
    )


    if selected_units:

        filtered_df = filtered_df[
            filtered_df[unit_column]
            .astype(str)
            .isin(selected_units)
        ]


# ==================================================
# SEARCH
# ==================================================

st.markdown("### 🔍 Text Search")


search_text = st.text_input(
    "Search across the filtered dataset",
    placeholder="Example: maternal mortality, India, 2016..."
)


if search_text:

    search_mask = (
        filtered_df
        .astype(str)
        .apply(
            lambda column: column.str.contains(
                search_text,
                case=False,
                na=False,
                regex=False
            )
        )
        .any(axis=1)
    )


    filtered_df = filtered_df[
        search_mask
    ]


# ==================================================
# FILTERED RESULTS SUMMARY
# ==================================================

st.markdown("## 📋 Filtered Results")


r1, r2, r3 = st.columns(3)


r1.metric(
    "Matching Records",
    len(filtered_df)
)


r2.metric(
    "Records Removed",
    len(df) - len(filtered_df)
)


if len(df) > 0:

    percentage = (
        len(filtered_df) / len(df)
    ) * 100

else:

    percentage = 0


r3.metric(
    "Dataset Coverage",
    f"{percentage:.1f}%"
)


# ==================================================
# DATA TABLE
# ==================================================

if filtered_df.empty:

    st.warning(
        "No records match the selected filters."
    )

else:

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# DOWNLOAD
# ==================================================

st.markdown("## 💾 Export Data")


if not filtered_df.empty:

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=csv_data,
        file_name="maternalens_filtered_data.csv",
        mime="text/csv"
    )

else:

    st.info(
        "There are no records available for download."
    )


# ==================================================
# SELECTED INDICATOR DETAILS
# ==================================================

if (
    indicator_column
    and len(selected_indicators) == 1
):

    selected_indicator = selected_indicators[0]


    st.markdown(
        "## 📌 Selected Indicator Details"
    )


    indicator_df = df[
        df[indicator_column]
        .astype(str)
        == selected_indicator
    ].copy()


    d1, d2, d3, d4 = st.columns(4)


    d1.metric(
        "Records",
        len(indicator_df)
    )


    if value_column:

        numeric_indicator_values = pd.to_numeric(
            indicator_df[value_column],
            errors="coerce"
        ).dropna()


        if not numeric_indicator_values.empty:

            d2.metric(
                "Mean",
                f"{numeric_indicator_values.mean():.2f}"
            )


            d3.metric(
                "Minimum",
                f"{numeric_indicator_values.min():.2f}"
            )


            d4.metric(
                "Maximum",
                f"{numeric_indicator_values.max():.2f}"
            )

        else:

            d2.metric("Mean", "N/A")
            d3.metric("Minimum", "N/A")
            d4.metric("Maximum", "N/A")

    else:

        d2.metric("Mean", "N/A")
        d3.metric("Minimum", "N/A")
        d4.metric("Maximum", "N/A")


# ==================================================
# RAW DATA INSPECTION
# ==================================================

st.markdown("## 🧬 Raw Data Inspection")


with st.expander(
    "Show original dataset"
):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# DETECTED STRUCTURE
# ==================================================

st.markdown(
    "## 🧠 Detected Dataset Structure"
)


structure_data = []


for key, value in detected.items():

    structure_data.append({
        "Data Element": key,
        "Detected Column": value
    })


if structure_data:

    structure_df = pd.DataFrame(
        structure_data
    )


    st.dataframe(
        structure_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No automatic column mappings were detected."
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "MaternaLens AI • Interactive Data Exploration Engine"
)
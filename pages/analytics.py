import streamlit as st
import pandas as pd

from utils.visualizations import (
    create_correlation_heatmap,
    create_data_cube,
    create_data_cube_heatmap,
    create_distribution,
    create_area_comparison
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="MaternaLens AI — Analytics",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# HEADER
# ==================================================

st.title("📊 MaternaLens AI — Analytics")

st.caption(
    "Advanced maternal-health data analysis and exploration"
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
# DETECTED COLUMNS
# ==================================================

detected = validation.get(
    "detected_columns",
    {}
)

indicator_column = detected.get("indicator")
value_column = detected.get("value")
time_column = detected.get("time")
area_column = detected.get("area")


# ==================================================
# ANALYTICAL OVERVIEW
# ==================================================

st.markdown("## 🔎 Analytical Overview")

st.write(
    "MaternaLens AI automatically determines which "
    "analytical methods are appropriate for the selected dataset."
)


# ==================================================
# DATASET STATISTICS
# ==================================================

st.markdown("## 📌 Dataset Statistics")

numeric_columns = validation.get(
    "numeric_columns",
    []
)

c1, c2, c3, c4 = st.columns(4)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Records",
    len(df)
)

c2.metric(
    "Total Columns",
    len(df.columns)
)

c3.metric(
    "Numeric Columns",
    len(numeric_columns)
)

c4.metric(
    "Missing Cells",
    int(df.isna().sum().sum())
)


# ==================================================
# INDICATOR STATISTICS
# ==================================================

st.markdown("## 📋 Indicator Statistics")

indicator_summary = analysis.get(
    "indicators"
)


if (
    indicator_summary is not None
    and not indicator_summary.empty
):

    st.dataframe(
        indicator_summary,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Indicator-level statistics are not available "
        "for this dataset."
    )


# ==================================================
# DISTRIBUTION ANALYSIS
# ==================================================

st.markdown("## 📦 Distribution Analysis")


if value_column:

    try:

        numeric_values = pd.to_numeric(
            df[value_column],
            errors="coerce"
        ).dropna()


        if len(numeric_values) >= 2:

            # Create a temporary dataframe
            # using the actual detected value column.

            distribution_df = pd.DataFrame({
                value_column: numeric_values
            })


            # The visualization function expects
            # the dataframe and detected columns.

            try:

                fig = create_distribution(
                    distribution_df,
                    detected
                )

            except TypeError:

                # Compatibility fallback for the
                # existing visualization function.

                fig = create_distribution(
                    distribution_df,
                    value_column
                )


            if fig is not None:

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                st.info(
                    "A distribution visualization "
                    "could not be generated."
                )

        else:

            st.info(
                "Not enough numeric observations "
                "for distribution analysis."
            )

    except Exception as e:

        st.warning(
            f"Unable to generate distribution analysis: {e}"
        )

else:

    st.info(
        "No numeric value column was detected."
    )


# ==================================================
# CORRELATION INTELLIGENCE
# ==================================================

st.markdown("## 🔥 Correlation Intelligence")

st.write(
    "Correlation analysis is generated only when the "
    "dataset contains sufficient comparable numerical data."
)


if (
    indicator_column
    and value_column
):

    try:

        fig = create_correlation_heatmap(
            df,
            detected
        )


        if fig is not None:

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "A meaningful correlation heatmap could "
                "not be generated from this dataset."
            )

    except Exception:

        st.info(
            "Correlation analysis is not applicable "
            "to the current dataset."
        )

else:

    st.info(
        "Correlation analysis requires indicator "
        "and numeric value information."
    )


# ==================================================
# DATA CUBE
# ==================================================

st.markdown("## 🧊 Data Cube Explorer")

st.write(
    "Explore relationships between indicators and "
    "time periods using a pivot-style analytical view."
)


if (
    indicator_column
    and time_column
    and value_column
):

    try:

        cube = create_data_cube(
            df,
            detected
        )


        if cube is not None:

            st.dataframe(
                cube,
                use_container_width=True
            )


            # ------------------------------------------
            # DATA CUBE HEATMAP
            # ------------------------------------------

            st.markdown(
                "### 🗺 Data Cube Heatmap"
            )


            try:

                cube_fig = create_data_cube_heatmap(
                    cube
                )

            except TypeError:

                cube_fig = create_data_cube_heatmap(
                    df
                )


            if cube_fig is not None:

                st.plotly_chart(
                    cube_fig,
                    use_container_width=True
                )

            else:

                st.info(
                    "A data-cube heatmap could not "
                    "be generated."
                )

        else:

            st.info(
                "The current dataset does not contain "
                "enough information for a data cube."
            )

    except Exception as e:

        st.warning(
            f"Unable to generate data cube: {e}"
        )

else:

    st.info(
        "Data cube analysis requires indicator, "
        "time, and numeric value columns."
    )


# ==================================================
# LOCATION COMPARISON
# ==================================================

st.markdown("## 🌍 Location Comparison")


if area_column:

    try:

        unique_areas = (
            df[area_column]
            .dropna()
            .astype(str)
            .nunique()
        )


        if unique_areas >= 2:

            try:

                area_fig = create_area_comparison(
                    df,
                    detected
                )

            except TypeError:

                area_fig = create_area_comparison(
                    df
                )


            if area_fig is not None:

                st.plotly_chart(
                    area_fig,
                    use_container_width=True
                )

            else:

                st.info(
                    "Location comparison could not "
                    "be generated."
                )

        else:

            st.info(
                "The current dataset contains only one "
                "location. Location comparison requires "
                "at least two locations."
            )

    except Exception as e:

        st.warning(
            f"Unable to generate location comparison: {e}"
        )

else:

    st.info(
        "No geographic/location column was detected."
    )


# ==================================================
# ANALYTICAL READINESS
# ==================================================

st.markdown("## 🧠 Analytical Readiness")


r1, r2 = st.columns(2)


# --------------------------------------------------
# TIME ANALYSIS
# --------------------------------------------------

if time_column:

    r1.success(
        "✅ Time-series analysis available"
    )

else:

    r1.warning(
        "⚠️ Time information not detected"
    )


# --------------------------------------------------
# GEOGRAPHIC ANALYSIS
# --------------------------------------------------

if area_column:

    location_count = (
        df[area_column]
        .dropna()
        .astype(str)
        .nunique()
    )


    if location_count >= 2:

        r2.success(
            "✅ Geographic comparison available"
        )

    else:

        r2.info(
            "ℹ️ Only one location detected"
        )

else:

    r2.warning(
        "⚠️ Geographic information not detected"
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "MaternaLens AI • Advanced Analytics Engine"
)
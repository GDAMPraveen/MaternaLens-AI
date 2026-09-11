# ==========================================
# MATERNALENS AI — VISUALIZATION ENGINE
# ==========================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ------------------------------------------
# MMR TREND
# ------------------------------------------

def create_mmr_trend(df, detected_columns):
    """
    Create an MMR trend chart when the dataset
    contains maternal mortality observations.
    """

    indicator_column = detected_columns.get("indicator")
    value_column = detected_columns.get("value")
    time_column = detected_columns.get("time")

    if not all([
        indicator_column,
        value_column,
        time_column
    ]):
        return None

    indicator_text = (
        df[indicator_column]
        .astype(str)
        .str.lower()
    )

    mask = (
        indicator_text.str.contains(
            "maternal mortality",
            na=False
        )
        |
        indicator_text.str.contains(
            r"\bmmr\b",
            regex=True,
            na=False
        )
    )

    mmr = df[mask].copy()

    if mmr.empty:
        return None

    mmr["NumericValue"] = pd.to_numeric(
        mmr[value_column],
        errors="coerce"
    )

    mmr = mmr.dropna(
        subset=["NumericValue"]
    )

    if mmr.empty:
        return None

    fig = px.line(
        mmr,
        x=time_column,
        y="NumericValue",
        markers=True,
        title="Maternal Mortality Ratio Trend",
        labels={
            time_column: "Time Period",
            "NumericValue": "MMR"
        }
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    return fig


# ------------------------------------------
# TARGET PROGRESS
# ------------------------------------------

def create_target_progress(
    latest_value,
    target_value,
    title="Progress Toward Target"
):
    """
    Create a simple target-progress visualization.
    """

    if latest_value is None or target_value is None:
        return None

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=[latest_value],
            y=["Current"],
            orientation="h",
            name="Current"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[target_value],
            y=["Current"],
            mode="markers",
            marker={"size": 14},
            name="Target"
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Value",
        yaxis_title="",
        template="plotly_white"
    )

    return fig


# ------------------------------------------
# INDICATOR COMPARISON
# ------------------------------------------

def create_indicator_comparison(
    df,
    detected_columns
):
    """
    Compare average numeric values across indicators.
    """

    indicator_column = detected_columns.get("indicator")
    value_column = detected_columns.get("value")

    if not indicator_column or not value_column:
        return None

    working = df.copy()

    working["NumericValue"] = pd.to_numeric(
        working[value_column],
        errors="coerce"
    )

    working = working.dropna(
        subset=["NumericValue"]
    )

    if working.empty:
        return None

    comparison = (
        working
        .groupby(indicator_column)["NumericValue"]
        .mean()
        .reset_index()
        .sort_values(
            "NumericValue",
            ascending=False
        )
    )

    if comparison.empty:
        return None

    fig = px.bar(
        comparison,
        x="NumericValue",
        y=indicator_column,
        orientation="h",
        title="Indicator Comparison",
        labels={
            "NumericValue": "Average Value",
            indicator_column: "Indicator"
        }
    )

    fig.update_layout(
        template="plotly_white",
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    return fig


# ------------------------------------------
# CORRELATION HEATMAP
# ------------------------------------------

def create_correlation_heatmap(
    correlation_matrix
):
    """
    Create a correlation heatmap only when
    a valid correlation matrix exists.
    """

    if correlation_matrix is None:
        return None

    if correlation_matrix.empty:
        return None

    if correlation_matrix.shape[0] < 2:
        return None

    fig = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        aspect="auto",
        title="Indicator Correlation Heatmap",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1
    )

    fig.update_layout(
        template="plotly_white"
    )

    return fig


# ------------------------------------------
# DATA CUBE
# ------------------------------------------

def create_data_cube(
    df,
    detected_columns
):
    """
    Create an Indicator × Time data cube.

    Each cell represents the average numeric value
    for an indicator during a time period.
    """

    indicator_column = detected_columns.get("indicator")
    time_column = detected_columns.get("time")
    value_column = detected_columns.get("value")

    if not all([
        indicator_column,
        time_column,
        value_column
    ]):
        return None

    working = df.copy()

    working["NumericValue"] = pd.to_numeric(
        working[value_column],
        errors="coerce"
    )

    working = working.dropna(
        subset=["NumericValue"]
    )

    if working.empty:
        return None

    cube = pd.pivot_table(
        working,
        index=indicator_column,
        columns=time_column,
        values="NumericValue",
        aggfunc="mean"
    )

    if cube.empty:
        return None

    return cube


# ------------------------------------------
# DATA CUBE HEATMAP
# ------------------------------------------

def create_data_cube_heatmap(
    cube
):
    """
    Visualize the data cube as a heatmap.
    """

    if cube is None or cube.empty:
        return None

    fig = px.imshow(
        cube,
        aspect="auto",
        title="Data Cube — Indicator × Time",
        labels={
            "x": "Time Period",
            "y": "Indicator",
            "color": "Value"
        }
    )

    fig.update_layout(
        template="plotly_white"
    )

    return fig


# ------------------------------------------
# VALUE DISTRIBUTION
# ------------------------------------------

def create_distribution(
    df,
    detected_columns
):
    """
    Create a histogram for the detected value column.
    """

    value_column = detected_columns.get("value")

    if not value_column:
        return None

    values = pd.to_numeric(
        df[value_column],
        errors="coerce"
    ).dropna()

    if values.empty:
        return None

    fig = px.histogram(
        values,
        x=values,
        title="Numeric Value Distribution",
        labels={
            "x": "Value"
        }
    )

    fig.update_layout(
        template="plotly_white"
    )

    return fig


# ------------------------------------------
# AREA / COUNTRY COMPARISON
# ------------------------------------------

def create_area_comparison(
    df,
    detected_columns
):
    """
    Compare average numeric values between
    countries, areas, states, or regions.
    """

    area_column = detected_columns.get("area")
    value_column = detected_columns.get("value")

    if not area_column or not value_column:
        return None

    working = df.copy()

    working["NumericValue"] = pd.to_numeric(
        working[value_column],
        errors="coerce"
    )

    working = working.dropna(
        subset=["NumericValue"]
    )

    if working.empty:
        return None

    comparison = (
        working
        .groupby(area_column)["NumericValue"]
        .mean()
        .reset_index()
        .sort_values(
            "NumericValue",
            ascending=False
        )
    )

    if comparison.empty:
        return None

    # Avoid creating an unreadable chart
    # when hundreds of areas exist.
    if len(comparison) > 20:
        comparison = comparison.head(20)

    fig = px.bar(
        comparison,
        x="NumericValue",
        y=area_column,
        orientation="h",
        title="Area / Country Comparison",
        labels={
            "NumericValue": "Average Value",
            area_column: "Area"
        }
    )

    fig.update_layout(
        template="plotly_white",
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    return fig
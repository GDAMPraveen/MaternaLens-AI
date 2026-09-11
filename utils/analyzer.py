# ==========================================
# MATERNALENS AI — ANALYSIS ENGINE
# ==========================================

import pandas as pd
import numpy as np


# ------------------------------------------
# NUMERIC VALUE CONVERSION
# ------------------------------------------

def get_numeric_values(df, value_column):
    """
    Convert a value column to numeric values.

    Non-numeric entries such as 'Yes' or ranges
    are converted to NaN instead of being deleted.
    """

    if value_column is None:
        return pd.Series(dtype="float64")

    return pd.to_numeric(
        df[value_column],
        errors="coerce"
    )


# ------------------------------------------
# BASIC DATASET SUMMARY
# ------------------------------------------

def basic_summary(df):
    """
    Generate basic statistical information.
    """

    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    }

    numeric_df = df.select_dtypes(include=np.number)

    summary["numeric_columns"] = len(numeric_df.columns)

    if len(numeric_df.columns) > 0:
        summary["numeric_summary"] = numeric_df.describe().round(3)
    else:
        summary["numeric_summary"] = pd.DataFrame()

    return summary


# ------------------------------------------
# CATEGORY SUMMARY
# ------------------------------------------

def categorical_summary(df, column):
    """
    Return frequency information for a categorical column.
    """

    if column is None or column not in df.columns:
        return pd.DataFrame()

    return (
        df[column]
        .value_counts(dropna=False)
        .reset_index()
        .rename(
            columns={
                column: "Value",
                "count": "Count"
            }
        )
    )


# ------------------------------------------
# INDICATOR SUMMARY
# ------------------------------------------

def indicator_summary(df, indicator_column, value_column):
    """
    Calculate summary statistics for each indicator.
    """

    if (
        indicator_column is None
        or value_column is None
        or indicator_column not in df.columns
        or value_column not in df.columns
    ):
        return pd.DataFrame()

    working = df.copy()

    working["_numeric_value"] = pd.to_numeric(
        working[value_column],
        errors="coerce"
    )

    result = (
        working
        .groupby(indicator_column)["_numeric_value"]
        .agg(
            Count="count",
            Mean="mean",
            Minimum="min",
            Maximum="max",
            Median="median"
        )
        .reset_index()
    )

    return result.round(3)


# ------------------------------------------
# TIME TREND
# ------------------------------------------

def time_trend(df, time_column, value_column):
    """
    Prepare time-series data when a usable
    time and numeric value column exist.
    """

    if (
        time_column is None
        or value_column is None
        or time_column not in df.columns
        or value_column not in df.columns
    ):
        return pd.DataFrame()

    working = df.copy()

    working["_numeric_value"] = pd.to_numeric(
        working[value_column],
        errors="coerce"
    )

    working = working.dropna(
        subset=["_numeric_value"]
    )

    if working.empty:
        return pd.DataFrame()

    result = (
        working
        .groupby(time_column)["_numeric_value"]
        .mean()
        .reset_index()
        .rename(
            columns={
                "_numeric_value": "Value"
            }
        )
    )

    return result


# ------------------------------------------
# MMR ANALYSIS
# ------------------------------------------

def mmr_analysis(df, indicator_column, value_column):
    """
    Detect and analyze maternal mortality ratio data.

    Looks specifically for indicators containing
    maternal mortality / mortality ratio / MMR.
    """

    if (
        indicator_column is None
        or value_column is None
        or indicator_column not in df.columns
        or value_column not in df.columns
    ):
        return None

    indicator_text = (
        df[indicator_column]
        .astype(str)
        .str.lower()
    )

    mmr_mask = (
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

    mmr_df = df[mmr_mask].copy()

    if mmr_df.empty:
        return None

    mmr_df["_numeric_value"] = pd.to_numeric(
        mmr_df[value_column],
        errors="coerce"
    )

    mmr_df = mmr_df.dropna(
        subset=["_numeric_value"]
    )

    if mmr_df.empty:
        return None

    values = mmr_df["_numeric_value"]

    result = {
        "records": len(mmr_df),
        "initial_value": float(values.iloc[0]),
        "latest_value": float(values.iloc[-1]),
        "minimum": float(values.min()),
        "maximum": float(values.max())
    }

    if len(values) > 1:
        reduction = (
            values.iloc[0] - values.iloc[-1]
        )

        result["absolute_reduction"] = float(
            reduction
        )

        if values.iloc[0] != 0:
            result["percentage_reduction"] = float(
                reduction / values.iloc[0] * 100
            )
        else:
            result["percentage_reduction"] = None

    else:
        result["absolute_reduction"] = None
        result["percentage_reduction"] = None

    return result


# ------------------------------------------
# TARGET ANALYSIS
# ------------------------------------------

def target_analysis(
    df,
    indicator_column,
    value_column,
    target_value=70
):
    """
    Analyze progress toward the SDG 3.1 maternal mortality target.

    Uses the MMR analysis directly from the dataset instead of
    selecting the latest numeric value from the entire dataset.
    """

    # Recalculate MMR specifically
    mmr = mmr_analysis(
        df,
        indicator_column,
        value_column
    )

    if not mmr:
        return None

    latest = mmr.get("latest_value")
    initial = mmr.get("initial_value")

    if latest is None:
        return None

    gap = latest - target_value

    if latest <= target_value:
        status = "Target achieved"
        additional_reduction = 0.0
    else:
        status = "Target not yet achieved"

        if latest != 0:
            additional_reduction = (
                gap / latest
            ) * 100
        else:
            additional_reduction = None

    return {
        "target": float(target_value),

        "latest": float(latest),

        "gap": float(gap),

        "status": status,

        "additional_reduction_required_percent": (
            round(
                additional_reduction,
                2
            )
            if additional_reduction is not None
            else None
        ),

        "initial": (
            float(initial)
            if initial is not None
            else None
        )
    }

# ------------------------------------------
# CORRELATION ANALYSIS
# ------------------------------------------

def correlation_analysis(df, detected_columns):
    """
    Performs correlation analysis only when the dataset contains
    enough comparable numeric observations across indicators.

    Avoids misleading correlations when there is only one location
    or insufficient repeated observations.
    """

    indicator_column = detected_columns.get("indicator")
    value_column = detected_columns.get("value")
    area_column = detected_columns.get("area")
    time_column = detected_columns.get("time")

    if not indicator_column or not value_column:
        return {
            "applicable": False,
            "reason": "Indicator or numeric value column was not detected."
        }

    working = df[[indicator_column, value_column]].copy()

    if area_column:
        working["Area"] = df[area_column]

    if time_column:
        working["Time"] = df[time_column]

    working[value_column] = pd.to_numeric(
        working[value_column],
        errors="coerce"
    )

    working = working.dropna(subset=[indicator_column, value_column])

    # Number of distinct areas
    area_count = (
        working["Area"].nunique()
        if "Area" in working.columns
        else 1
    )

    # Number of distinct indicators
    indicator_count = working[indicator_column].nunique()

    # Correlation needs repeated comparable observations.
    if area_count < 2:
        return {
            "applicable": False,
            "reason": (
                "Correlation analysis is not applicable because "
                "the dataset contains only one location."
            ),
            "areas": int(area_count),
            "indicators": int(indicator_count)
        }

    if indicator_count < 2:
        return {
            "applicable": False,
            "reason": "At least two indicators are required."
        }

    # Create an observation key so that indicators are compared
    # only where they share the same area/time observation.
    index_columns = []

    if "Area" in working.columns:
        index_columns.append("Area")

    if "Time" in working.columns:
        index_columns.append("Time")

    if not index_columns:
        return {
            "applicable": False,
            "reason": "No comparable observation dimensions were detected."
        }

    pivot = working.pivot_table(
        index=index_columns,
        columns=indicator_column,
        values=value_column,
        aggfunc="mean"
    )

    # Keep only indicators with sufficient observations
    valid_columns = [
        col for col in pivot.columns
        if pivot[col].notna().sum() >= 3
    ]

    pivot = pivot[valid_columns]

    if pivot.shape[1] < 2:
        return {
            "applicable": False,
            "reason": (
                "There are not enough repeated observations "
                "to calculate meaningful indicator correlations."
            ),
            "comparable_indicators": int(pivot.shape[1])
        }

    correlation = pivot.corr()

    return {
        "applicable": True,
        "correlation": correlation,
        "observations": int(len(pivot)),
        "indicators": int(pivot.shape[1]),
        "areas": int(area_count)
    }


# ------------------------------------------
# DATASET PROFILE
# ------------------------------------------

def generate_dataset_profile(
    df,
    detected_columns
):
    """
    Generate a compact profile used by the
    dashboard and AI engine.
    """

    indicator_column = detected_columns.get(
        "indicator"
    )

    area_column = detected_columns.get(
        "area"
    )

    time_column = detected_columns.get(
        "time"
    )

    value_column = detected_columns.get(
        "value"
    )

    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "indicators": 0,
        "areas": 0,
        "time_periods": 0,
        "numeric_values": 0
    }

    if indicator_column in df.columns:
        profile["indicators"] = int(
            df[indicator_column]
            .nunique()
        )

    if area_column in df.columns:
        profile["areas"] = int(
            df[area_column]
            .nunique()
        )

    if time_column in df.columns:
        profile["time_periods"] = int(
            df[time_column]
            .nunique()
        )

    if value_column in df.columns:
        numeric_values = pd.to_numeric(
            df[value_column],
            errors="coerce"
        )

        profile["numeric_values"] = int(
            numeric_values.notna().sum()
        )

    return profile
# ------------------------------------------
# MATERNAL HEALTH COVERAGE GAP ANALYSIS
# ------------------------------------------

def coverage_gap_analysis(
    df,
    indicator_column,
    value_column
):
    """
    Analyze maternal-health coverage indicators.

    Detects skilled birth attendance and antenatal care
    indicators from the indicator text and returns their
    latest numeric values.

    The function is dataset-driven and does not hard-code
    specific indicator values.
    """

    if (
        indicator_column is None
        or value_column is None
        or indicator_column not in df.columns
        or value_column not in df.columns
    ):
        return None

    working = df[
        [indicator_column, value_column]
    ].copy()

    working["_numeric_value"] = pd.to_numeric(
        working[value_column],
        errors="coerce"
    )

    working = working.dropna(
        subset=["_numeric_value"]
    )

    if working.empty:
        return None

    indicator_text = (
        working[indicator_column]
        .astype(str)
        .str.lower()
    )

    # ----------------------------------------------------
    # Skilled birth attendance
    # ----------------------------------------------------

    skilled_mask = (
        indicator_text.str.contains(
            "skilled health personnel",
            na=False
        )
        |
        indicator_text.str.contains(
            "skilled birth attendance",
            na=False
        )
        |
        indicator_text.str.contains(
            "skilled birth",
            na=False
        )
    )

    skilled_df = working[skilled_mask].copy()

    skilled_1yr = None
    skilled_5yr = None

    if not skilled_df.empty:

        skilled_text = (
            skilled_df[indicator_column]
            .astype(str)
            .str.lower()
        )

        skilled_1yr_df = skilled_df[
            skilled_text.str.contains(
                "1 year",
                na=False
            )
        ]

        skilled_5yr_df = skilled_df[
            skilled_text.str.contains(
                "5 year",
                na=False
            )
        ]

        if not skilled_1yr_df.empty:
            skilled_1yr = float(
                skilled_1yr_df[
                    "_numeric_value"
                ].iloc[-1]
            )

        if not skilled_5yr_df.empty:
            skilled_5yr = float(
                skilled_5yr_df[
                    "_numeric_value"
                ].iloc[-1]
            )

        # Fallback if period wording differs
        if (
            skilled_1yr is None
            and skilled_5yr is None
            and len(skilled_df) == 1
        ):
            skilled_1yr = float(
                skilled_df[
                    "_numeric_value"
                ].iloc[-1]
            )

    # ----------------------------------------------------
    # Antenatal care — 4+ visits
    # ----------------------------------------------------

    anc_mask = (
        indicator_text.str.contains(
            "antenatal",
            na=False
        )
        |
        indicator_text.str.contains(
            "antenatal care",
            na=False
        )
    )

    anc_df = working[anc_mask].copy()

    anc_4plus = None

    if not anc_df.empty:

        anc_text = (
            anc_df[indicator_column]
            .astype(str)
            .str.lower()
        )

        anc_4plus_df = anc_df[
            anc_text.str.contains(
                r"4\+|4 or more|four or more",
                regex=True,
                na=False
            )
        ]

        if not anc_4plus_df.empty:
            anc_4plus = float(
                anc_4plus_df[
                    "_numeric_value"
                ].iloc[-1]
            )

        # Fallback if the dataset has only one
        # antenatal-care indicator
        elif len(anc_df) == 1:
            anc_4plus = float(
                anc_df[
                    "_numeric_value"
                ].iloc[-1]
            )

    # ----------------------------------------------------
    # Coverage gap
    # ----------------------------------------------------

    coverage_gap = None

    if (
        skilled_1yr is not None
        and anc_4plus is not None
    ):
        coverage_gap = (
            skilled_1yr - anc_4plus
        )

    return {
        "skilled_attendance_1yr": skilled_1yr,
        "skilled_1yr": skilled_1yr,
        "skilled_attendance_5yr": skilled_5yr,
        "skilled_5yr": skilled_5yr,
        "anc_4plus": anc_4plus,
        "antenatal_4plus": anc_4plus,
        "coverage_gap": coverage_gap,
        "coverage_gap_percentage_points": coverage_gap,
        "available": (
            skilled_1yr is not None
            or anc_4plus is not None
        )
    }

# ------------------------------------------
# COMPLETE ANALYSIS PIPELINE
# ------------------------------------------

def analyze_dataset(df, detected_columns, target_value=70):
    """
    Run the complete MaternaLens analysis pipeline.

    The function is designed to work with both:
    1. The built-in SDG 3.1 dataset
    2. User-uploaded maternal health datasets

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset to analyze.

    detected_columns : dict
        Column mapping produced by data_validator.py.

    target_value : float
        SDG 3.1 maternal mortality target.

    Returns
    -------
    dict
        Complete analysis results.
    """

    results = {}

    # ========================================================
    # DETECTED COLUMNS
    # ========================================================

    indicator_column = detected_columns.get("indicator")
    value_column = detected_columns.get("value")
    area_column = detected_columns.get("area")
    time_column = detected_columns.get("time")
    unit_column = detected_columns.get("unit")

    results["detected_columns"] = detected_columns

    # ========================================================
    # BASIC DATASET SUMMARY
    # ========================================================

    results["basic_summary"] = basic_summary(df)

    # ========================================================
    # DATASET PROFILE
    # ========================================================

    try:
        results["profile"] = generate_dataset_profile(
            df,
            detected_columns
        )
    except Exception:
        results["profile"] = {
            "rows": len(df),
            "columns": len(df.columns),
        }

    # ========================================================
    # INDICATOR ANALYSIS
    # ========================================================

    if indicator_column and value_column:

        try:
            results["indicators"] = indicator_summary(
                df,
                indicator_column,
                value_column
            )
        except Exception:
            results["indicators"] = None

    else:
        results["indicators"] = None

    # ========================================================
    # TIME TREND
    # ========================================================

    if indicator_column and value_column:

        try:
            results["trend"] = time_trend(
                df,
                time_column,
                value_column
            )
        except Exception:
            results["trend"] = None

    else:
        results["trend"] = None

    # ========================================================
    # MMR ANALYSIS
    # ========================================================

    if indicator_column and value_column:

        try:
            results["mmr"] = mmr_analysis(
                df,
                indicator_column,
                value_column
            )
        except Exception:
            results["mmr"] = None

    else:
        results["mmr"] = None

    # ========================================================
    # SDG 3.1 TARGET ANALYSIS
    # ========================================================

    if indicator_column and value_column:

        try:
            results["target"] = target_analysis(
                df,
                indicator_column,
                value_column,
                target_value=target_value
            )
        except Exception:
            results["target"] = None

    else:
        results["target"] = None

    # ========================================================
    # CORRELATION / RELATIONSHIP ANALYSIS
    # ========================================================

    if indicator_column and value_column:

        try:
            # IMPORTANT:
            # correlation_analysis() expects the complete
            # detected_columns dictionary.
            results["correlation"] = correlation_analysis(
                df,
                detected_columns
            )

        except Exception as e:

            results["correlation"] = {
                "applicable": False,
                "reason": (
                    "Correlation analysis could not be completed."
                ),
                "error": str(e),
            }

    else:

        results["correlation"] = {
            "applicable": False,
            "reason": (
                "Indicator and numeric value columns "
                "are required."
            ),
        }

    # ========================================================
    # CATEGORICAL ANALYSIS
    # ========================================================

    try:
        results["categorical"] = categorical_summary(
            df,
            indicator_column
        )
    except Exception:
        results["categorical"] = None

    # ========================================================
    # COVERAGE ANALYSIS
    # ========================================================

    coverage = None

    if indicator_column and value_column:

        try:
            coverage = coverage_gap_analysis(
                df,
                indicator_column,
                value_column
            )
        except Exception:
            coverage = None

    results["coverage"] = coverage

    # Keep compatibility with dashboard / AI code
    results["coverage_gap"] = coverage

    # ========================================================
    # DATA CUBE
    # ========================================================

    try:

        if indicator_column and value_column:

            cube = df.copy()

            cube[value_column] = pd.to_numeric(
                cube[value_column],
                errors="coerce"
            )

            cube = cube.dropna(
                subset=[value_column]
            )

            if area_column and time_column:

                data_cube = cube.pivot_table(
                    index=area_column,
                    columns=indicator_column,
                    values=value_column,
                    aggfunc="mean"
                )

            elif time_column:

                data_cube = cube.pivot_table(
                    index=time_column,
                    columns=indicator_column,
                    values=value_column,
                    aggfunc="mean"
                )

            else:

                data_cube = cube.pivot_table(
                    columns=indicator_column,
                    values=value_column,
                    aggfunc="mean"
                )

            results["data_cube"] = data_cube

        else:

            results["data_cube"] = None

    except Exception:

        results["data_cube"] = None

    # ========================================================
    # NUMERIC DISTRIBUTION
    # ========================================================

    if value_column:

        try:

            numeric_values = pd.to_numeric(
                df[value_column],
                errors="coerce"
            ).dropna()

            results["distribution"] = {
                "count": int(len(numeric_values)),
                "mean": float(numeric_values.mean())
                if len(numeric_values)
                else None,
                "median": float(numeric_values.median())
                if len(numeric_values)
                else None,
                "minimum": float(numeric_values.min())
                if len(numeric_values)
                else None,
                "maximum": float(numeric_values.max())
                if len(numeric_values)
                else None,
                "std": float(numeric_values.std())
                if len(numeric_values) > 1
                else 0.0,
            }

        except Exception:

            results["distribution"] = None

    else:

        results["distribution"] = None

    # ========================================================
    # LOCATION SUMMARY
    # ========================================================

    if area_column and area_column in df.columns:

        try:

            results["locations"] = {
                "count": int(
                    df[area_column].nunique()
                ),
                "names": (
                    df[area_column]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                ),
            }

        except Exception:

            results["locations"] = None

    else:

        results["locations"] = None

    # ========================================================
    # TIME SUMMARY
    # ========================================================

    if time_column and time_column in df.columns:

        try:

            time_values = (
                df[time_column]
                .dropna()
                .astype(str)
            )

            results["time_periods"] = {
                "count": int(
                    time_values.nunique()
                ),
                "earliest": (
                    time_values.min()
                    if len(time_values)
                    else None
                ),
                "latest": (
                    time_values.max()
                    if len(time_values)
                    else None
                ),
            }

        except Exception:

            results["time_periods"] = None

    else:

        results["time_periods"] = None

    # ========================================================
    # ANALYSIS STATUS
    # ========================================================

    results["analysis_status"] = {
        "completed": True,
        "rows_analyzed": int(len(df)),
        "columns_analyzed": int(len(df.columns)),
        "mmr_available": results["mmr"] is not None,
        "target_analysis_available": (
            results["target"] is not None
        ),
        "correlation_available": (
            results["correlation"].get("applicable", False)
            if results["correlation"]
            else False
        ),
        "coverage_available": (
            results["coverage_gap"] is not None
        ),
    }

    return results
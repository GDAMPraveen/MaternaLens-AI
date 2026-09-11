# ==========================================
# MATERNALENS AI — DATA VALIDATOR
# ==========================================

import pandas as pd


# ------------------------------------------
# COLUMN ALIASES
# ------------------------------------------

COLUMN_ALIASES = {
    "area": [
        "AreaName",
        "Area",
        "Country",
        "CountryName",
        "Location",
        "Region",
        "State",
        "District"
    ],

    "time": [
        "TimePeriod",
        "Year",
        "Date",
        "Time",
        "Period"
    ],

    "indicator": [
        "Indicator",
        "Metric",
        "Variable",
        "Measure",
        "IndicatorName"
    ],

    "value": [
        "DataValue",
        "Value",
        "ValueNumeric",
        "Measurement",
        "ObservedValue",
        "Result"
    ],

    "unit": [
        "Unit",
        "Units"
    ],

    "target": [
        "Target",
        "SDG Target"
    ],

    "goal": [
        "Goal",
        "SDG Goal"
    ]
}


# ------------------------------------------
# COLUMN DETECTION
# ------------------------------------------

def detect_columns(df):
    """
    Automatically detect important columns
    using known column-name patterns.
    """

    detected = {}

    for category, aliases in COLUMN_ALIASES.items():

        detected[category] = None

        for column in df.columns:

            column_clean = str(column).strip().lower()

            for alias in aliases:

                if column_clean == alias.lower():
                    detected[category] = column
                    break

            if detected[category] is not None:
                break

    return detected


# ------------------------------------------
# NUMERIC COLUMN DETECTION
# ------------------------------------------

def detect_numeric_columns(df):
    """
    Detect columns that predominantly contain numeric data.

    A column is considered numeric-compatible when at least
    80% of its non-missing values can be converted to numbers.
    """
    numeric_columns = []

    for column in df.columns:
        series = df[column].dropna()

        if len(series) == 0:
            continue

        numeric_values = pd.to_numeric(
            series,
            errors="coerce"
        )

        valid_count = numeric_values.notna().sum()
        numeric_ratio = valid_count / len(series)

        if numeric_ratio >= 0.80:
            numeric_columns.append(column)

    return numeric_columns

# ------------------------------------------
# SDG 3.1 DETECTION
# ------------------------------------------

def detect_sdg31(df, detected_columns):
    """
    Determine whether the dataset contains
    SDG 3.1 maternal health information.
    """

    target_column = detected_columns.get("target")
    indicator_column = detected_columns.get("indicator")

    if target_column is None and indicator_column is None:
        return {
            "sdg31_detected": False,
            "sdg31_rows": 0
        }

    mask = pd.Series(False, index=df.index)

    if target_column is not None:

        target_values = (
            df[target_column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        mask = mask | target_values.str.startswith("3.1")

    if indicator_column is not None:

        indicator_values = (
            df[indicator_column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        mask = mask | indicator_values.str.startswith("3.1")

        mask = mask | indicator_values.str.contains(
            "maternal mortality",
            na=False
        )

    return {
        "sdg31_detected": bool(mask.any()),
        "sdg31_rows": int(mask.sum())
    }


# ------------------------------------------
# MAIN VALIDATION FUNCTION
# ------------------------------------------

def validate_dataset(df):
    """
    Validate a dataset and generate a structured
    validation report.
    """

    issues = []
    warnings = []

    # --------------------------------------
    # Basic validation
    # --------------------------------------

    if df is None:

        return {
            "valid": False,
            "usable": False,
            "issues": ["No dataset was provided."],
            "warnings": [],
            "detected_columns": {}
        }

    if not isinstance(df, pd.DataFrame):

        return {
            "valid": False,
            "usable": False,
            "issues": ["Input is not a pandas DataFrame."],
            "warnings": [],
            "detected_columns": {}
        }

    rows = len(df)
    columns = len(df.columns)

    if rows == 0:
        issues.append("Dataset contains no rows.")

    if columns == 0:
        issues.append("Dataset contains no columns.")

    if columns < 2:
        issues.append(
            "Dataset should contain at least two columns."
        )

    # --------------------------------------
    # Detect important columns
    # --------------------------------------

    detected_columns = detect_columns(df)

    numeric_columns = detect_numeric_columns(df)

    # --------------------------------------
    # Value column analysis
    # --------------------------------------

    value_column = detected_columns.get("value")

    numeric_value_count = 0

    if value_column is not None:

        numeric_values = pd.to_numeric(
            df[value_column],
            errors="coerce"
        )

        numeric_value_count = int(
            numeric_values.notna().sum()
        )

        non_numeric_count = rows - numeric_value_count

        if non_numeric_count > 0:

            warnings.append(
                f"{non_numeric_count} values in "
                f"'{value_column}' are non-numeric."
            )

    elif len(numeric_columns) == 0:

        warnings.append(
            "No numeric columns were detected."
        )

    # --------------------------------------
    # Missing values
    # --------------------------------------

    total_missing = int(
        df.isna().sum().sum()
    )

    if total_missing > 0:

        warnings.append(
            f"Dataset contains {total_missing} missing values."
        )

    # --------------------------------------
    # Duplicate rows
    # --------------------------------------

    duplicate_rows = int(
        df.duplicated().sum()
    )

    if duplicate_rows > 0:

        warnings.append(
            f"Dataset contains {duplicate_rows} duplicate rows."
        )

    # --------------------------------------
    # Important column warnings
    # --------------------------------------

    if detected_columns.get("indicator") is None:

        warnings.append(
            "Indicator/metric column was not detected."
        )

    if detected_columns.get("time") is None:

        warnings.append(
            "Time/year column was not detected."
        )

    if detected_columns.get("area") is None:

        warnings.append(
            "Area/country/location column was not detected."
        )

    # --------------------------------------
    # SDG 3.1 detection
    # --------------------------------------

    sdg31_info = detect_sdg31(
        df,
        detected_columns
    )

    # --------------------------------------
    # Determine usability
    # --------------------------------------

    usable = (
        rows > 0
        and columns >= 2
        and (
            value_column is not None
            or len(numeric_columns) > 0
        )
    )

    if not usable and rows > 0:

        issues.append(
            "Dataset does not contain a usable numeric "
            "value column or numeric data."
        )

    # --------------------------------------
    # Final report
    # --------------------------------------

    report = {

        "valid": len(issues) == 0,

        "usable": usable,

        "rows": rows,

        "columns": columns,

        "column_names": list(df.columns),

        "detected_columns": detected_columns,

        "numeric_columns": numeric_columns,

        "numeric_value_count": numeric_value_count,

        "missing_values": total_missing,

        "duplicate_rows": duplicate_rows,

        "sdg31_detected": sdg31_info["sdg31_detected"],

        "sdg31_rows": sdg31_info["sdg31_rows"],

        "issues": issues,

        "warnings": warnings
    }

    return report
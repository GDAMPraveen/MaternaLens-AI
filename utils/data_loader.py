# ==========================================
# MATERNALENS AI — DATA LOADER
# ==========================================

from pathlib import Path
import pandas as pd


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"

# Default dataset
DEFAULT_DATASET = DATA_DIR / "SDG-3-1-DATA-GOV.csv"


def load_dataset(file_path=None):
    """
    Load a CSV dataset.

    Parameters
    ----------
    file_path : str or Path, optional
        Path to a CSV file.
        If None, the built-in SDG dataset is loaded.

    Returns
    -------
    pandas.DataFrame
        Loaded dataset.
    """

    path = Path(file_path) if file_path else DEFAULT_DATASET

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    # Try UTF-8 first
    try:
        df = pd.read_csv(path, encoding="utf-8")

    except UnicodeDecodeError:
        # Fallback for the current Data.gov.in CSV
        df = pd.read_csv(path, encoding="cp1252")

    return df


def load_uploaded_dataset(uploaded_file):
    """
    Load a dataset supplied through Streamlit's
    file uploader.

    Parameters
    ----------
    uploaded_file
        Streamlit UploadedFile object.

    Returns
    -------
    pandas.DataFrame
        Uploaded dataset.
    """

    if uploaded_file is None:
        return None

    try:
        df = pd.read_csv(
            uploaded_file,
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        uploaded_file.seek(0)

        df = pd.read_csv(
            uploaded_file,
            encoding="cp1252"
        )

    return df


def get_dataset_info(df):
    """
    Generate basic dataset metadata.
    """

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }
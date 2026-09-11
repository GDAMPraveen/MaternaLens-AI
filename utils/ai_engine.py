import os
import pandas as pd

from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

load_dotenv()

# ============================================================
# FORMATTING
# ============================================================

def format_number(value, decimals=2):
    """Safely format numeric values."""

    if value is None:
        return "N/A"

    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)
# ============================================================
# IBM CREDENTIALS
# ============================================================

def get_ibm_credentials():
    """Load IBM watsonx.ai credentials from environment variables."""

    url = os.getenv("IBM_WATSONX_URL")
    api_key = os.getenv("IBM_WATSONX_API_KEY")
    project_id = os.getenv("IBM_WATSONX_PROJECT_ID")

    if not url or not api_key or not project_id:
        return None, None

    credentials = Credentials(
        url=url,
        api_key=api_key
    )

    return credentials, project_id
# ============================================================
# IBM WATSONX AI
# ============================================================

def generate_ibm_response(prompt, credentials, project_id):
    """
    Generate an AI response using IBM watsonx.ai Chat API.
    """

    if not credentials or not project_id:
        return None

    try:
        model = ModelInference(
            model_id="meta-llama/llama-3-3-70b-instruct",
            credentials=credentials,
            project_id=project_id
        )

        response = model.chat(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            params={
                "max_tokens": 300,
                "temperature": 0.2
            }
        )

        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return f"IBM AI error: {str(e)}"

def build_maternal_health_prompt(df, analysis_results):
    """
    Build a grounded prompt for IBM AI using only
    values already calculated by the MaternaLens analyzer.
    """

    mmr = analysis_results.get("mmr") or {}
    target = analysis_results.get("target") or {}
    coverage = analysis_results.get(
        "coverage_gap",
        analysis_results.get("coverage")
    ) or {}

    initial_mmr = mmr.get("initial_value")
    latest_mmr = mmr.get("latest_value")
    reduction = mmr.get("absolute_reduction")
    percentage = mmr.get("percentage_reduction")

    target_value = target.get("target")
    gap = target.get("gap")

    skilled = coverage.get(
        "skilled_attendance_1yr",
        coverage.get("skilled_1yr")
    )

    anc = coverage.get(
        "anc_4plus",
        coverage.get("antenatal_4plus")
    )

    prompt = f"""
You are the AI analyst for MaternaLens AI.

MaternaLens analyzes maternal-health data in relation to
Sustainable Development Goal 3.1.

Use ONLY the information provided below.
Do not invent statistics, countries, causes, trends,
or recommendations that are not supported by the data.

DATASET
- Records: {len(df)}
- Columns: {len(df.columns)}

MATERNAL MORTALITY
- Initial MMR: {initial_mmr}
- Latest MMR: {latest_mmr}
- Absolute reduction: {reduction}
- Percentage reduction: {percentage}%

SDG 3.1 TARGET
- Target MMR: {target_value}
- Remaining gap: {gap}

MATERNAL HEALTH COVERAGE
- Skilled birth attendance: {skilled}%
- Antenatal care (4+ visits): {anc}%

TASK

Provide exactly 3 concise bullet points:

1. Interpret the MMR trend.
2. Assess progress toward the SDG 3.1 target.
3. Identify the most important observable healthcare coverage gap.

Keep the interpretation factual, concise, and data-driven.
"""

    return prompt
# ============================================================
# MMR INSIGHT
# ============================================================

def generate_mmr_insight(mmr_analysis):
    """Generate an interpretable maternal mortality insight."""

    if not mmr_analysis:
        return (
            "Maternal mortality analysis is not available "
            "from the current dataset."
        )

    initial = mmr_analysis.get("initial_value")
    latest = mmr_analysis.get("latest_value")
    reduction = mmr_analysis.get("absolute_reduction")
    percentage = mmr_analysis.get("percentage_reduction")

    if latest is None:
        return (
            "A latest maternal mortality value could not "
            "be identified."
        )

    text = (
        f"The latest maternal mortality ratio is "
        f"{format_number(latest)} per 100,000 live births."
    )

    if initial is not None:
        text += (
            f" The initial recorded value was "
            f"{format_number(initial)}."
        )

    if reduction is not None:
        text += (
            f" This represents a reduction of "
            f"{format_number(reduction)}"
        )

        if percentage is not None:
            text += (
                f", equivalent to "
                f"{format_number(percentage)}%"
            )

        text += " over the available observation period."

    return text


# ============================================================
# SDG TARGET INSIGHT
# ============================================================

def generate_target_insight(target_analysis):
    """Interpret progress toward SDG 3.1."""

    if not target_analysis:
        return (
            "SDG 3.1 target analysis could not be "
            "generated from the available data."
        )

    latest = target_analysis.get("latest")
    target = target_analysis.get("target")
    gap = target_analysis.get("gap")
    status = target_analysis.get("status")
    additional_reduction = target_analysis.get(
        "additional_reduction_required_percent"
    )

    if latest is None or target is None:
        return (
            "SDG target analysis could not be generated "
            "from the available data."
        )

    if status == "Target achieved" or latest <= target:
        return (
            f"The latest maternal mortality ratio is "
            f"{format_number(latest)}, which has reached "
            f"the SDG 3.1 target of "
            f"{format_number(target)} per 100,000 "
            f"live births."
        )

    text = (
        f"The latest maternal mortality ratio is "
        f"{format_number(latest)} per 100,000 live births, "
        f"which is {format_number(abs(gap))} above the "
        f"SDG 3.1 target of "
        f"{format_number(target)}."
    )

    if additional_reduction is not None:
        text += (
            f" An additional reduction of approximately "
            f"{format_number(additional_reduction)}% "
            f"from the latest value would be required "
            f"to reach the target."
        )

    return text


# ============================================================
# COVERAGE GAP INSIGHT
# ============================================================

def generate_coverage_gap_insight(coverage):
    """Interpret maternal healthcare coverage."""

    if not coverage:
        return (
            "Comparable maternal healthcare coverage "
            "indicators were not available."
        )

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

    if skilled is None and anc is None:
        return (
            "The available dataset does not contain "
            "enough comparable coverage indicators."
        )

    text = "Maternal healthcare coverage analysis: "

    if skilled is not None:
        text += (
            f"skilled birth attendance is "
            f"{format_number(skilled, 1)}%"
        )

    if anc is not None:
        if skilled is not None:
            text += (
                f", while antenatal care with "
                f"4+ visits is "
                f"{format_number(anc, 1)}%"
            )
        else:
            text += (
                f"antenatal care with 4+ visits is "
                f"{format_number(anc, 1)}%"
            )

    if gap is not None:
        text += (
            f". The observed coverage difference is "
            f"{format_number(abs(gap), 1)} percentage points."
        )

    return text


# ============================================================
# DATASET OVERVIEW
# ============================================================

def generate_dataset_overview(df, analysis_results=None):
    """Create a concise overview of the uploaded dataset."""

    rows = len(df)
    columns = len(df.columns)

    missing = int(
        df.isna().sum().sum()
    )

    duplicates = int(
        df.duplicated().sum()
    )

    overview = (
        f"The dataset contains {rows:,} records across "
        f"{columns:,} columns."
    )

    if missing:
        overview += (
            f" There are {missing:,} missing cell values."
        )
    else:
        overview += (
            " No missing cell values were detected."
        )

    if duplicates:
        overview += (
            f" {duplicates:,} duplicate rows were detected."
        )
    else:
        overview += (
            " No duplicate rows were detected."
        )

    return overview


# ============================================================
# DATA QUALITY INSIGHT
# ============================================================

def generate_data_quality_insight(df, validation=None):
    """Interpret basic dataset quality."""

    rows = len(df)

    missing = int(
        df.isna().sum().sum()
    )

    duplicates = int(
        df.duplicated().sum()
    )

    if missing == 0 and duplicates == 0:
        return (
            f"The dataset contains {rows:,} records with "
            "no missing cells or duplicate rows detected."
        )

    parts = [
        f"The dataset contains {rows:,} records."
    ]

    if missing:
        parts.append(
            f"{missing:,} missing cell values were detected."
        )

    if duplicates:
        parts.append(
            f"{duplicates:,} duplicate rows were detected."
        )

    return " ".join(parts)


# ============================================================
# RELATIONSHIP INSIGHT
# ============================================================

def generate_relationship_insight(correlation):
    """Interpret correlation analysis results."""

    if not correlation:
        return (
            "Relationship analysis is not available."
        )

    if not correlation.get("applicable"):
        reason = correlation.get(
            "reason",
            "There are not enough comparable observations."
        )

        return (
            "Relationship analysis is not applicable: "
            f"{reason}"
        )

    indicators = correlation.get(
        "indicators",
        0
    )

    observations = correlation.get(
        "observations",
        0
    )

    return (
        f"Relationship analysis is available across "
        f"{indicators} comparable indicators using "
        f"{observations} observations."
    )


# ============================================================
# KEY INSIGHTS
# ============================================================

def generate_key_insights(
    df,
    analysis_results,
    validation=None
):
    """
    Generate structured insights from the complete
    analysis pipeline.
    """

    insights = []

    # --------------------------------------------------------
    # DATASET
    # --------------------------------------------------------

    insights.append(
        {
            "category": "Dataset",
            "insight": generate_dataset_overview(
                df,
                analysis_results
            )
        }
    )

    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    insights.append(
        {
            "category": "Data Quality",
            "insight": generate_data_quality_insight(
                df,
                validation
            )
        }
    )

    # --------------------------------------------------------
    # MMR
    # --------------------------------------------------------

    mmr = analysis_results.get("mmr")

    if mmr:
        insights.append(
            {
                "category": "Maternal Mortality",
                "insight": generate_mmr_insight(mmr)
            }
        )

    # --------------------------------------------------------
    # SDG TARGET
    # --------------------------------------------------------

    target = analysis_results.get("target")

    if target:
        insights.append(
            {
                "category": "SDG 3.1",
                "insight": generate_target_insight(target)
            }
        )

    # --------------------------------------------------------
    # COVERAGE
    # --------------------------------------------------------

    coverage = analysis_results.get(
        "coverage_gap",
        analysis_results.get("coverage")
    )

    if coverage:
        insights.append(
            {
                "category": "Healthcare Coverage",
                "insight": generate_coverage_gap_insight(
                    coverage
                )
            }
        )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    correlation = analysis_results.get(
        "correlation"
    )

    if correlation:

        insights.append(
            {
                "category": "Relationships",
                "insight": generate_relationship_insight(
                    correlation
                )
            }
        )

    return insights


# ============================================================
# QUESTION ANSWERING
# ============================================================

def answer_question(
    question,
    df,
    analysis_results
):
    """
    Basic natural-language question answering.

    This local rule-based engine will later be replaced/
    enhanced with IBM watsonx.ai.
    """

    question = str(question).lower().strip()

    mmr = analysis_results.get("mmr")
    target = analysis_results.get("target")

    # --------------------------------------------------------
    # LATEST MMR
    # --------------------------------------------------------

    if (
        "latest mmr" in question
        or "current mmr" in question
        or "latest maternal mortality" in question
    ):

        if mmr and mmr.get("latest_value") is not None:

            return (
                f"The latest recorded maternal mortality "
                f"ratio is "
                f"{format_number(mmr['latest_value'])} "
                f"per 100,000 live births."
            )

        return (
            "A latest maternal mortality ratio could "
            "not be identified."
        )

    # --------------------------------------------------------
    # INITIAL MMR
    # --------------------------------------------------------

    if (
        "initial mmr" in question
        or "starting mmr" in question
    ):

        if mmr and mmr.get("initial_value") is not None:

            return (
                f"The initial recorded maternal mortality "
                f"ratio is "
                f"{format_number(mmr['initial_value'])} "
                f"per 100,000 live births."
            )

        return (
            "An initial maternal mortality value could "
            "not be identified."
        )

    # --------------------------------------------------------
    # REDUCTION
    # --------------------------------------------------------

    if (
        "how much" in question
        and "reduced" in question
    ) or "mmr reduction" in question:

        if mmr:

            reduction = mmr.get(
                "absolute_reduction"
            )

            percentage = mmr.get(
                "percentage_reduction"
            )

            if reduction is not None:

                response = (
                    f"Maternal mortality decreased by "
                    f"{format_number(reduction)} "
                    f"deaths per 100,000 live births."
                )

                if percentage is not None:
                    response += (
                        f" This is a "
                        f"{format_number(percentage)}% "
                        f"reduction."
                    )

                return response

        return (
            "MMR reduction could not be calculated."
        )

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    if (
        "target" in question
        or "sdg 3.1" in question
    ):

        if target:
            return generate_target_insight(
                target
            )

        return (
            "SDG 3.1 target analysis is not available."
        )

    # --------------------------------------------------------
    # DATASET SIZE
    # --------------------------------------------------------

    if (
        "how many records" in question
        or "number of records" in question
        or "rows" in question
    ):

        return (
            f"The dataset contains "
            f"{len(df):,} records."
        )

    # --------------------------------------------------------
    # COLUMNS
    # --------------------------------------------------------

    if (
        "columns" in question
        or "variables" in question
    ):

        return (
            f"The dataset contains "
            f"{len(df.columns):,} columns."
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    if (
        "summary" in question
        or "overall" in question
        or "overview" in question
    ):

        parts = [
            generate_dataset_overview(
                df,
                analysis_results
            )
        ]

        if mmr:
            parts.append(
                generate_mmr_insight(mmr)
            )

        if target:
            parts.append(
                generate_target_insight(target)
            )

        return " ".join(parts)

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return (
        "I can currently answer questions about the "
        "dataset structure, maternal mortality, MMR "
        "reduction, SDG 3.1 target progress, and "
        "available maternal-health indicators. "
        "IBM watsonx.ai provides more flexible "
        "natural-language reasoning."
    )


# ============================================================
# COMPLETE AI PIPELINE
# ============================================================
def generate_ai_insights(
    df,
    analysis_results,
    validation=None
):
    """
    Complete AI interpretation layer.

    Uses the local deterministic engine for reliable
    calculations and IBM watsonx.ai for natural-language
    interpretation when IBM credentials are available.
    """

    # --------------------------------------------------------
    # LOCAL DETERMINISTIC INSIGHTS
    # --------------------------------------------------------

    key_insights = generate_key_insights(
        df,
        analysis_results,
        validation
    )

    mmr = analysis_results.get("mmr")
    target = analysis_results.get("target")

    # --------------------------------------------------------
    # IBM WATSONX AI
    # --------------------------------------------------------

    credentials, project_id = get_ibm_credentials()

    ibm_insight = None

    if credentials and project_id:

        prompt = build_maternal_health_prompt(
            df,
            analysis_results
        )

        ibm_insight = generate_ibm_response(
            prompt,
            credentials,
            project_id
        )

    # --------------------------------------------------------
    # FINAL AI OUTPUT
    # --------------------------------------------------------

    return {
        "engine": (
            "IBM watsonx.ai + MaternaLens AI Local Engine"
            if ibm_insight
            else "MaternaLens AI Local Engine"
        ),

        "status": "ready",

        # IBM-generated interpretation
        "ibm_insight": ibm_insight,

        # Existing deterministic insights
        "insights": key_insights,

        "key_insights": key_insights,

        "mmr_insight": generate_mmr_insight(
            mmr
        ),

        "target_insight": generate_target_insight(
            target
        ),

        "coverage_insight": generate_coverage_gap_insight(
            analysis_results.get(
                "coverage_gap",
                analysis_results.get("coverage")
            )
        ),

        "relationship_insight":
            generate_relationship_insight(
                analysis_results.get("correlation")
            ),

        "dataset_overview":
            generate_dataset_overview(
                df,
                analysis_results
            ),

        "data_quality":
            generate_data_quality_insight(
                df,
                validation
            ),
    }
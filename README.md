# MaternaLens AI

### AI-Powered Maternal Health Analytics for SDG 3.1

MaternaLens AI is an AI-assisted maternal health analytics platform designed to track progress toward **Sustainable Development Goal (SDG) 3.1 — reducing maternal mortality and improving maternal healthcare coverage**.

The platform combines data validation, exploratory analytics, visualization, deterministic analytical insights, and **IBM watsonx.ai-powered natural-language interpretation and Q&A** into a single Streamlit application.

---

## 🎯 Problem Statement

**SDG 3.1** aims to reduce the global maternal mortality ratio to **less than 70 deaths per 100,000 live births by 2030**.

Maternal health datasets often contain multiple indicators, time periods, units, missing values, and mixed data types. MaternaLens AI provides an accessible analytical layer that helps users understand these datasets and identify important trends and gaps.

---

## 💡 Solution

MaternaLens AI follows an end-to-end analytical workflow:

```text
Dataset
   ↓
Data Validation
   ↓
Column & Indicator Detection
   ↓
Data Analysis
   ↓
Visual Analytics
   ↓
AI-Powered Interpretation
   ↓
Natural-Language Q&A
```

The application supports both the built-in SDG 3.1 dataset and user-uploaded datasets.

---

## 📊 Current Dataset

The included dataset is based on India's SDG National Indicator Framework data and contains:

| Attribute                       | Value |
| ------------------------------- | ----: |
| Records                         | 1,295 |
| Columns                         |    15 |
| Indicators                      |   267 |
| Locations                       |     1 |
| Numeric-compatible observations | 1,279 |
| Duplicate rows                  |     0 |

### SDG 3.1 indicators analyzed

* Maternal Mortality Ratio (MMR)
* Skilled health personnel / skilled birth attendance
* Antenatal care — 4 or more visits

---

## 🔎 Key Findings

For the available India SDG 3.1 data:

* Maternal Mortality Ratio decreased from **130** to **113 per 100,000 live births**.
* This represents a **13.08% reduction**.
* The SDG 3.1 target is **70 per 100,000 live births**.
* The latest observed gap from the target is **43 deaths per 100,000 live births**.
* Skilled birth attendance coverage is **84.4%** for the available one-year period.
* Antenatal care coverage for four or more visits is **51.2%**.
* The resulting coverage gap between these two available indicators is **33.2 percentage points**.

These results are presented as analytical findings from the supplied dataset rather than as causal or clinical conclusions.

---

## 🤖 AI Capabilities

MaternaLens AI integrates **IBM watsonx.ai** for AI-powered interpretation.

### AI Insights

The AI engine receives structured information derived from the dataset and generates concise, dataset-grounded observations.

### Natural-Language Q&A

Users can ask questions such as:

```text
What is the latest MMR?
How much has MMR reduced?
What is the SDG 3.1 target?
How many records are in the dataset?
What is the antenatal care coverage?
```

The system combines deterministic analytical results with IBM watsonx.ai interpretation.

### Model

**Meta Llama 3.3 70B Instruct** through IBM watsonx.ai.

---

## 📈 Analytics Features

MaternaLens AI includes:

* Dataset statistics
* Automatic column detection
* Data validation
* Missing-value analysis
* Duplicate detection
* Indicator statistics
* Distribution analysis
* MMR trend analysis
* SDG target progress
* Data cube exploration
* Heatmap visualization
* Location comparison when multiple locations are available
* Correlation analysis when sufficient comparable observations exist
* Analytical readiness assessment
* AI-generated insights
* Natural-language dataset Q&A

The system avoids forcing analyses that are not statistically meaningful for the available data. For example, correlation analysis is not presented when there is only one geographic location.

---

## 🛠️ Technology Stack

### Frontend / Application

* Python
* Streamlit
* Plotly

### Data Analysis

* Pandas
* NumPy
* Scikit-learn

### AI

* IBM watsonx.ai
* IBM watsonx.ai Python SDK
* Meta Llama 3.3 70B Instruct

### Development

* Jupyter Notebook
* Python virtual environment
* Git / GitHub

---

## 📁 Project Structure

```text
MaternaLens-AI/
│
├── app.py
│
├── data/
│   ├── SDG-3-1-DATA-GOV.csv
│   └── maternalens_insights.csv
│
├── notebooks/
│   └── 01_data_analysis.ipynb
│
├── pages/
│   ├── dashboard.py
│   ├── analytics.py
│   ├── data_explorer.py
│   └── ai_insights.py
│
├── utils/
│   ├── data_loader.py
│   ├── data_validator.py
│   ├── analyzer.py
│   ├── visualizations.py
│   └── ai_engine.py
│
├── assets/
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/GDAMPraveen/MaternaLens-AI.git
cd MaternaLens-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows Git Bash:

```bash
source venv/Scripts/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure IBM watsonx.ai

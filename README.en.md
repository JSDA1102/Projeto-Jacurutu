# 🦉 Project Jacurutu

> **Project Status:** 🚧 In Progress 🚧

**The Jacurutu (Great Horned Owl) is the largest nocturnal bird of prey in Brazil. Known for its acute vision and hearing, it carefully monitors its targets before hunting. The concept of this project is the same: to sharply monitor the "forest" of public spending data to spot transactions that deviate from the pattern.**

## 1. Overview

This project utilizes Data Science to analyze expenditure data from the Federal Government Payment Cards (CPGF).

Our goal is not just to *find* strange transactions, but to **prioritize them** intelligently. To achieve this, we built a system that combines the **"Anomaly Level"** (detected by an AI *Ensemble*) with the **Financial Value (Risk)**. The final result is an interactive *dashboard* where an auditor can investigate the most relevant cases efficiently.

## 2. Data Source

The primary database is the detailed extract of corporate cards from the Federal Government, covering the period from 2023 to the present.

* **Source:** Transparency Portal (Portal da Transparência)
* **Download URL:** [Portal da Transparência - CPGF](https://portaldatransparencia.gov.br/download-de-dados/cpgf)
* **Data Dictionary:** [Data Dictionary - CPGF](https://portaldatransparencia.gov.br/dicionario-de-dados/cpgf)

## 3. Main Technologies

* **[Python 3.12.9](https://www.python.org/)**
* **[Pandas](https://pandas.pydata.org/) & [PyArrow](https://arrow.apache.org/):** For high-performance data manipulation and reading Parquet files.
* **[Scikit-learn](https://scikit-learn.org/):** For building anomaly detection models.
    * **Isolation Forest** (Global detection)
    * **Local Outlier Factor (LOF)** (Local density detection)
* **[Streamlit](https://streamlit.io/):** For building the investigation dashboard.
* **[Geopandas](https://geopandas.org/) (Planned):** For geospatial visualization of expenses.

## 4. Project Pipeline: The Hunting Roadmap

Our methodology follows a structured roadmap to transform raw data into actionable insights.

### 4.1. Advanced Ingestion and Cleaning
* **Consolidation:** Merging of all monthly CSV files.
* **Traceability:** Addition of the `SOURCE_FILE` column for source auditing.
* **Confidentiality Handling:** Identification and handling of 92,000+ confidential transactions (missing date/payee), with accounting date imputation to maintain the time series.
* **Geographic Enrichment (NLP):** Since the original database lacks a State (UF) column, we developed a text processing algorithm that extracts the location from the Management Unit name, identifying regional vs. central expenses.

### 4.2. Feature Engineering
To teach the AI what is "strange," we create mathematical contexts:
* **Temporal Context:** Creation of flags for imputed dates.
* **Frequency Encoding:** Transformation of categorical variables (Agency, Payee) into numerical values based on occurrence rarity.
* **Golden Features (Ratios):** Calculation of statistical ratios (e.g., `Transaction Value / Agency Monthly Average`). This allows detecting subtle deviations that escape raw value analysis.

### 4.3. Modeling (The "Committee of Detectives")
We use an unsupervised **Ensemble** strategy.

* **Detective 1 (`Isolation Forest`):** Focuses on isolating global anomalies and extreme values.
* **Detective 2 (`Local Outlier Factor` - LOF):** Analyzes local density.
    * *Technical Highlight:* We implemented **Jittering** (statistical noise) to handle the high density of repeated transactions (common in government spending), ensuring model stability.
* **Detective 3 (`Autoencoder`):** (Planned) Neural network for reconstructing complex patterns.

### 4.4. Prioritization and Investigation
A technical score alone is insufficient for public auditing. We created the **Priority Score**:

$$Priority = (0.7 \times TechnicalScore) + (0.3 \times FinancialRisk)$$

This ensures that a R$ 10.00 anomaly does not receive the same attention as a R$ 100,000.00 one.

## 5. Evaluation Metrics

Since we do not have labels for "confirmed fraud," we evaluate by relevance:
* **Human Validation:** Manual auditing of the **Top 200** suspicious transactions.
* **Key Metric (`Precision@k`):** "Out of the Top 100 anomalies pointed out, how many are worthy of deep investigation?"

## 6. Limitations and Risks

* **Rarity vs. Illegality:** The model points out what is *atypical*. An expense can be rare (e.g., a one-time equipment purchase) and perfectly legal.
* **Seasonality:** The public sector has strong cycles (e.g., the spending "rush" in December).
* **Cold Start:** New suppliers may have initially high anomaly scores until the system learns their pattern.

## 7. Deliverables

### Mandatory (Core)
1.  **Data Pipeline:** Automated cleaning and feature engineering scripts.
2.  **Trained Models:** Ensemble (IF + LOF) generating anomaly scores.
3.  **Interactive Dashboard:** Streamlit tool for data consumption by the auditor.

### Optional
1.  **Geospatial Analysis:** Heatmaps of suspicious expenses.
2.  **Spending Forecast:** Time series models for future budgeting.

## 8. Roadmap (Progress)

* ✅ **Exploratory Analysis (EDA):** Deep understanding of distributions and seasonality.
* ✅ **Data Cleaning (ETL):** Robust pipeline with geographic extraction and confidentiality handling.
* ✅ **Baseline Model (LOF):** Implemented with advanced Feature Engineering and Jittering.
* 🔲 **Baseline Model (Isolation Forest):** In development.
* 🔲 **Ensemble:** Combination of scores.
* 🔲 **Dashboard v1:** Development of the interface in Streamlit.
* 🔲 **Manual Validation:** Audit of final results.

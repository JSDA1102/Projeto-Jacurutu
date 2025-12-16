# 🦉 Project Jacurutu

> **Project Status:** 🚀 MVP Live (v1.0)

**The Jacurutu (Great Horned Owl) is Brazil's largest nocturnal bird of prey. Known for its keen vision and hearing, it monitors its targets before hunting. This project shares the same goal: monitoring the "forest" of public spending data to hunt down transactions that deviate from the norm.**

## 1. Overview

This project uses Data Science to analyze Federal Government Corporate Card (CPGF) expenditures.

Our goal isn't just to *find* strange transactions, but to **prioritize** them intelligently. We built a system that combines the **"anomaly level"** (detected by an AI Ensemble) with **financial risk**. The result is an interactive dashboard where an auditor can efficiently investigate high-impact cases.

## 2. Data Source

The dataset consists of detailed extracts from Federal Government corporate cards, covering 2023 to the present.

* **Source:** Transparency Portal (Portal da Transparência)
* **Download URL:** [CPGF Data](https://portaldatransparencia.gov.br/download-de-dados/cpgf)

## 3. Architecture & Tech Stack

The project uses a **decoupled architecture** to ensure high dashboard performance:

1.  **Backend (Offline ETL):** Heavy scripts that run in batch mode, train models, and generate an optimized `.parquet` file.
2.  **Frontend (Online Dashboard):** A lightweight app that reads processed data instantly.

### Stack
* **Language:** [Python 3.12.9](https://www.python.org/)
* **Processing:** [Pandas](https://pandas.pydata.org/) & [PyArrow](https://arrow.apache.org/) (Parquet format)
* **Machine Learning:** [Scikit-learn](https://scikit-learn.org/) (Isolation Forest, LOF)
* **Dashboard:** [Streamlit](https://streamlit.io/)
* **Viz:** [Plotly](https://plotly.com/) & [Folium](https://python-visualization.github.io/folium/)

## 4. The Pipeline: The Hunt Roadmap

### 4.1. Ingestion & Advanced Cleaning
* **Consolidation:** Merging monthly CSV files.
* **Secrecy Handling:** Identifying and processing classified transactions (missing date/payee).
* **Geo-Enrichment (NLP):** A text processing algorithm extracts location (State) from the Management Unit's name, enabling heatmap visualization.

### 4.2. Feature Engineering
We create mathematical contexts to teach the AI what "normal" looks like:
* **Frequency Encoding:** Transforming categorical variables based on rarity.
* **Golden Features (Ratios):** Statistical ratios (e.g., `Transaction Value / Agency Monthly Mean`) to detect subtle deviations.

### 4.3. Modeling (The "Detective Committee")
We use an **Unsupervised Ensemble** strategy:

* **Detective 1 (`Isolation Forest`):** Isolates global anomalies and extreme values.
* **Detective 2 (`Local Outlier Factor`):** Analyzes local density to find points isolated from their immediate neighbors.
    * *Technical Highlight:* Implemented **Jittering** to handle the high density of duplicate values in government data.

### 4.4. Prioritization
Technical score alone isn't enough. We created the **Priority Score**:

$$Priority = (0.7 \times TechnicalScore) + (0.3 \times FinancialRisk)$$

This ensures a $10.00 statistical anomaly doesn't outrank a $100,000.00 financial risk.

## 5. How to Run

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run ETL (Generate Data):**
    ```bash
    python run_etl.py
    ```
3.  **Launch Dashboard:**
    ```bash
    streamlit run functions/front/app.py
    ```

## 6. Limitations

* **Rarity vs. Illegality:** The model flags what is *atypical*. A transaction can be rare and perfectly legal.
* **Seasonality:** Public sector has strong spending cycles (e.g., December rush).
* **Cold Start:** New suppliers may have high initial scores.

## 7. Roadmap

* ✅ **EDA:** Deep understanding of distributions.
* ✅ **ETL Pipeline:** Robust cleaning and geo-extraction.
* ✅ **Ensemble Modeling:** Isolation Forest + LOF implementation.
* ✅ **Dashboard v1:** Streamlit interface with maps and exports.
* ✅ **Production Architecture:** Decoupling ETL from Frontend.

### 🔮 Future Improvements
* **Autoencoder (Deep Learning):** Neural networks for complex non-linear pattern reconstruction.
* **Budget Forecasting:** Time-series models.

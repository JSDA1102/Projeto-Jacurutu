# 🦉 Project Jacurutu

> **Project Status:** 🚧 In Progress 🚧

**The Jacurutu (Great Horned Owl) is the largest nocturnal bird of prey in Brazil. Known for its acute vision and hearing, it carefully monitors its targets before hunting. The concept of this project is the same: to sharply monitor the "forest" of public spending data to spot transactions that deviate from the pattern.**

## 1. Overview

This project utilizes Data Science to analyze expenditure data from the Federal Government Payment Cards (CPGF).

Our goal is not just to *find* strange transactions, but to **prioritize them** intelligently. To achieve this, we are building a system that combines the **"Anomaly Level"** (detected by AI) with the **Financial Value (Risk)**. The final result is an interactive *dashboard* where an auditor can investigate the most relevant cases.

## 2. Data Source

The primary database is the detailed extract of corporate cards from the Federal Government, covering the period from 2023 to the present.

* **Source:** Transparency Portal (Portal da Transparência)
* **Download URL:** [Portal da Transparência - CPGF](https://portaldatransparencia.gov.br/download-de-dados/cpgf)
* **Data Dictionary:** [Dicionário de Dados - CPGF](https://portaldatransparencia.gov.br/dicionario-de-dados/cpgf)

## 3. Main Technologies [WIP]

* **[Python 3.12.9](https://www.python.org/)**
* **[Pandas](https://pandas.pydata.org/):** For data loading, cleaning, and manipulation.
* **[Scikit-learn](https://scikit-learn.org/):** For anomaly detection models.
    * **[IsolationForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)**
    * **[Local Outlier Factor (LOF)](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html)**
* **[TensorFlow/Keras](https://www.tensorflow.org/):** For the `Autoencoder` detection model.
* **[Streamlit](https://streamlit.io/):** For building the interactive investigation dashboard.
* **[Geopandas](https://geopandas.org/):** (Planned) For geospatial heatmaps of anomalous spending.

## 4. Project Pipeline: The Hunting Roadmap

Our methodology follows a clear roadmap to transform raw data into actionable insights.

### 4.1. Exploratory Data Analysis (EDA)
* Creation of visualizations to understand distributions and relationships between variables.
* Identification of initial patterns and standard spending behaviors.

### 4.2. Ingestion and Data Cleaning
* **Consolidation:** Merging all monthly CSV files into a single database.
* **Traceability:** Adding a `SOURCE_FILE` column to track the origin of each transaction.
* **Type Correction:** Ensuring dates are parsed correctly and values (e.g., `1.500,75`) are converted to floats.

### 4.3. Feature Engineering
To teach the AI what is "strange," we first need to provide the "context" for each expense. We do this by creating new features that answer specific questions:
* **Bearer Context:** Is this spending normal *for this specific cardholder*? Is it 10x higher than their average?
* **Supplier Context:** Is this transaction amount normal *for this supplier*?
* **Temporal Context:** Did the expense occur on a weekend or holiday? Is the cardholder spending at an unusual frequency?
* **Behavioral Context:** Is it a "round number" value (e.g., R$ 2,000.00)? Is this the first time this government body has purchased from this supplier?

### 4.4. Modeling
We do not rely on a single "detective" (AI model). We use an **Ensemble** strategy (combination of models) for robustness. Each model generates a raw score, which is normalized (scaled 0 to 1) before combination.

* **Detective 1 (`Isolation Forest`):** Isolates anomalies based on random cuts in decision trees.
* **Detective 2 (`Local Outlier Factor` - LOF):** Analyzes local density. If a point has a much lower density than its neighbors, it is an anomaly.
* **Detective 3 (`Autoencoder`):** A neural network that learns to "reconstruct" the normal pattern. The score is the "Reconstruction Error" (how badly it failed to reproduce the transaction).

**Calculating the Anomaly Score:**
The final technical anomaly score is the arithmetic mean of the normalized scores from the three models.

### 4.5. Prioritization & Investigation
A technical score alone is insufficient for public auditing. A R$ 5.00 anomaly has low impact. We created the **Priority Score** by combining "Technical Strangeness" with "Financial Risk".

* **Priority Score Formula:**

$$Priority = (0.7 \times AnomalyScore) + (0.3 \times ValueScore)$$

* **Dashboard (Streamlit):** The auditor does not see the code; they interact with a dashboard containing the list of expenses, already sorted by this `Priority`, ready for analysis and drill-down.

## 5. Evaluation Metrics

Since we do not have a labeled "fraud" dataset, our success is measured by the relevance of our findings:

* **Human Validation:** Manual auditing of the **Top 200** transactions flagged by the model as most suspicious.
* **Key Metric: `Precision@k`:** Answering the question: "Out of the Top 100 anomalies flagged by Jacurutu, how many were *actually* suspicious or worth investigating by an auditor?"

## 6. Limitations & Risks

It is crucial to understand what the model is **not**, and where it might get confused. Jacurutu points out *atypical* transactions, which are not necessarily *illegal*.

1.  **Rarity vs. Illegality:** The model might flag a legitimate expense as "strange" simply because that cardholder rarely uses the card, or because the supplier is new to the database.
2.  **Public Seasonality:** The public sector has strong cycles (e.g., the "rush" of spending at the end of the fiscal year in December). The model might interpret this sudden volume increase as an anomaly if not trained with adequate time windows.
3.  **False Positives (Cold Start):** Suppliers appearing for the first time in the database may have higher anomaly scores until the system "gets used" to their billing pattern.

## 7. Project Deliverables

To define success, we separate what is essential (mandatory) from future improvements (optional).

### Mandatory Deliverables (Core)
1.  **Anomaly Detection Model:** The "Committee of Detectives" (IF, LOF, Autoencoder) trained and capable of generating an anomaly score for each transaction.
2.  **Prioritization Script:** The business logic combining the anomaly score with financial value to create the `Priority Score`.
3.  **Interactive Dashboard (Streamlit):** The visual tool for the end-user (auditor) to consume the prioritized list, analyze outliers (with drill-down), and manage the investigation flow.
4.  **Geospatial Analysis (Geopandas):** Implementation of heatmaps to show *where* geographically the anomalous expenses are concentrated.

### Optional Deliverables
1.  **Spending Forecasting Model:** Utilization of Linear Regression or Time Series models to attempt to *predict* future spending volume by agency or category, aiding in budget planning.

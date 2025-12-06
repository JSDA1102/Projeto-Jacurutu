import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from functions.clean_df import load_and_combine_csvs, clean_dataframe
from functions.state_imput import apply_state_estimation
from functions.feature_engineering import feature_engineering
from functions.models import run_lof_normal, run_lof_classified, run_if_normal, run_if_classified

def run_pipeline(raw_data):
    """
    Runs the entire data processing and modeling pipeline.

    Parameters
    raw_data : Path to directory with CSVs.

    Returns
    Dictionary of length 4:
        - Output of run_lof_classified(df_feature_engineering)
        - Output of run_lof_normal(df_feature_engineering)
        - Output of run_if_classified(df_feature_engineering)
        - Output of run_if_normal(df_feature_engineering)
    """
    # Using functions created previously
    df_raw = load_and_combine_csvs(raw_data)
    df_clean = clean_dataframe(df_raw)
    df_state = apply_state_estimation(df_clean)
    df_feature_engineering = feature_engineering(df_state)

    # Returning a dictionary with 4 different dataframes
    return {
    'lof_classified': run_lof_classified(df_feature_engineering),
    'lof_normal': run_lof_normal(df_feature_engineering),
    'if_classified': run_if_classified(df_feature_engineering),
    'if_normal': run_if_normal(df_feature_engineering)
    }

def combine_dataframes(df_lof_classified, df_lof_normal, df_if_classified, df_if_normal):
    """
    Combine the dataframes LOF and IF, creates ID, rearrange columns,
    and merge final adding only specific columns.
    """
    def combine(df1, df2, label_cols):
        df = pd.concat([df1, df2], ignore_index=True).drop_duplicates().reset_index(drop=True)

        df["ID"] = df.index + 1

        cols = ["ID"] + [c for c in df.columns if c != "ID"]
        df = df[cols]

        df_specific = df[["ID"] + label_cols]
        return df, df_specific

    # Processing LOF
    df_lof_full, df_lof_specific = combine(
        df_lof_classified, df_lof_normal,
        label_cols=["LOF_LABEL", "LOF_SCORE"]
    )
    # Processing IF
    df_if_full, df_if_specific = combine(
        df_if_classified, df_if_normal,
        label_cols=["IF_LABEL", "IF_SCORE"]
    )

    # Final merge: LOF (all columns) + IF (specific columns)
    df_final = df_lof_full.merge(df_if_specific, on="ID", how="inner")

    # Normalization step
    # IF_SCORE: Assuming lower score = higher risk. Invert to: Higher score = Higher risk.
    df_final['RISK_IF_SCORE'] = 1 - df_final['IF_SCORE']

    # LOF_SCORE: Already negative, where more negative is higher risk.
    df_final['RISK_LOF_SCORE'] = df_final['LOF_SCORE'].abs()

    # Normalize both risk scores to the range [-1, 1]
    scaler = MinMaxScaler(feature_range=(-1, 1))

    # Reshape scores for MinMaxScaler and fit/transform
    df_final['LOF_SCORE_NORM'] = scaler.fit_transform(df_final[['RISK_LOF_SCORE']])
    df_final['IF_SCORE_NORM'] = scaler.fit_transform(df_final[['RISK_IF_SCORE']])

    # Clean up intermediate columns
    df_final = df_final.drop(columns=['RISK_LOF_SCORE', 'RISK_IF_SCORE'])

    return df_final

def calculate_priority_score(df: pd.DataFrame):
    """
    Calculates the Technical Score, Financial Risk, and the final weighted
    Priority Score for manual review.

    Returns:
        pd.DataFrame: The DataFrame with the final PRIORITY_SCORE, sorted descending.
    """

    # 3.1 Combine Technical Scores (Mean)
    df['TECHNICAL_SCORE'] = df[['LOF_SCORE_NORM', 'IF_SCORE_NORM']].mean(axis=1)

    # 3.2 Calculate Financial Risk and Final Weighted Priority Score

    # Normalize LOG_VALOR to range [0, 1] to use it as a weighting factor
    log_scaler = MinMaxScaler(feature_range=(0, 1))
    df['FINANCIAL_RISK'] = log_scaler.fit_transform(df[['LOG_VALOR']])

    # Final Priority Calculation: (0.7 * Technical) + (0.3 * Financial Risk)
    df['PRIORITY_SCORE'] = (
        (0.7 * df['TECHNICAL_SCORE']) +
        (0.3 * df['FINANCIAL_RISK'])
    )

    # Order by priority score
    df = df.sort_values(by='PRIORITY_SCORE', ascending=False).reset_index(drop=True)

    return df

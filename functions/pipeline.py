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
    df_raw = load_and_combine_csvs(raw_data)
    df_clean = clean_dataframe(df_raw)
    df_state = apply_state_estimation(df_clean)
    df_feature_engineering = feature_engineering(df_state)

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


# 3. Criação do score de prioridade
# 3.1 Juntar os scores do log e if após normalização (mean)
# 3.2 Score de prioridade (0.7 x score técnico (3.1)) + (0.3 x risco financeiro (valor transação))
# Order by score de prioridade e depois, análise manual

# 1. Post-processing step
# 1.1 Concatenate the 4 dataframes generated in the previous stage
# 2. Normalization of if_score and lof_score (minmaxscaler / -1 to 1)
# 3. Creation of the priority score
# 3.1 Combine the log and if scores after normalization (mean)
# 3.2 Priority score (0.7 x technical score (3.1)) + (0.3 x financial risk (transaction value))
# Order by priority score and then manual analysis
#

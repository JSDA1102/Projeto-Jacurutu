import pandas as pd
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
    tuple of length 4:
        - Output of run_lof_classified(X_processed)
        - Output of run_lof_normal(X_processed)
        - Output of run_if_classified(X_processed)
        - Output of run_if_normal(X_processed)
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

def post_processing(raw_data):
    result_dict = run_pipeline(raw_data)
    dfs = [
        result_dict['lof_classified'].reset_index(drop=True),
        result_dict['lof_normal'].reset_index(drop=True),
        result_dict['if_classified'].reset_index(drop=True),
        result_dict['if_normal'].reset_index(drop=True)
    ]
    df_final = pd.concat(dfs, axis=1)
    return df_final

# 1. Etapa de pos processamento
# 1.1 Concat dos 4 df gerados na etapa anterior
# 2. Normalizacao do if_score e lof_score (minmaxscaler/ -1 a 1)
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

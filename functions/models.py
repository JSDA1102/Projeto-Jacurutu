import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
import joblib
import os
import sys
sys.path.append(os.path.abspath('..'))
from functions.preprocessing import get_preprocessor


FEATURES_MODELO = [
    'LOG_VALOR',
    'RATIO_MES',
    'ANO EXTRATO',
    'MÊS EXTRATO',
    'FREQ_NOME ÓRGÃO',
    'FREQ_ESTADO_ESTIMADO',
    'SIGILOSO',
    'FIM_SEMANA'
]

def run_lof(df, contamination=0.01, n_neighbors=20):
    """
    Executa o pipeline do LOF: Preprocessamento -> Jitter -> Treino -> Predição.

    Args:
        df (pd.DataFrame): DataFrame contendo as features.
        contamination (float): Taxa esperada de anomalias (padrão 1%).
        n_neighbors (int): Número de vizinhos para comparação (padrão 20).

    Returns:
        pd.DataFrame: O DataFrame original acrescido das colunas 'LOF_LABEL' e 'LOF_SCORE'.
    """
    df_result = df.copy()
    # Processamento de X
    preprocessor = get_preprocessor()
    X_scaled = preprocessor.fit_transform(df_result)
    ruido = np.random.normal(0, 1e-5, X_scaled.shape)
    X_final = X_scaled + ruido

    # Treinando o LOF
    lof = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
        n_jobs=-1
    )

    # fit_predict: Retorna -1 para outlier e 1 para normal
    labels = lof.fit_predict(X_final)
    scores = lof.negative_outlier_factor_

    # Adicionando resultados ao DataFrame
    df_result['LOF_LABEL'] = labels
    df_result['LOF_SCORE'] = scores

    return df_result

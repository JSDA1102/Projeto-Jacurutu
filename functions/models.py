import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
import os
import sys
sys.path.append(os.path.abspath('..'))
from functions.preprocessing import get_preprocessor


def run_lof_normal(df, contamination=0.01, n_neighbors=20):
    """
    Executa o LOF APENAS para transações NÃO SIGILOSAS.
    Ignora os dados sigilosos na detecção de anomalia.

    Args:
        df (pd.DataFrame): DataFrame completo.
        contamination (float): Taxa de anomalia.
        n_neighbors (int): Vizinhos.

    Returns:
        pd.DataFrame: DataFrame filtrado (só não sigilosos) com scores.
    """
    # Filtro apenas o que NÃO é sigiloso
    df_normal = df[df['SIGILOSO'] == 0].copy()


    # Preprocessamento
    preprocessor = get_preprocessor()
    X_scaled = preprocessor.fit_transform(df_normal)

    # Adicionando ruído
    ruido = np.random.normal(0, 1e-5, X_scaled.shape)
    X_final = X_scaled + ruido

    # Treinando
    lof = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
        n_jobs=-1
    )

    # Predição
    df_normal['LOF_LABEL'] = lof.fit_predict(X_final)
    df_normal['LOF_SCORE'] = lof.negative_outlier_factor_

    n_anomalias = (df_normal['LOF_LABEL'] == -1).sum()

    return df_normal



def run_lof_classified (df, contamination=0.01, n_neighbors=20):
    """
    Executa o LOF APENAS para transações SIGILOSAS (data imputada, sem favorecido).
    Foca em anomalias de valor e órgão dentro do universo de sigilo.

    Args:
        df (pd.DataFrame): DataFrame completo.
        contamination (float): Taxa de anomalia.
        n_neighbors (int): Vizinhos.

    Returns:
        pd.DataFrame: DataFrame filtrado (só sigilosos) com scores.
    """

    # Pega apenas o SIGILOSO
    df_classified = df[df['SIGILOSO'] == 1].copy()

    # Preprocessamento
    preprocessor = get_preprocessor()
    X_scaled = preprocessor.fit_transform(df_classified)

    # Adicionando ruído
    ruido = np.random.normal(0, 1e-5, X_scaled.shape)
    X_final = X_scaled + ruido

    # Treinando
    lof = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
        n_jobs=-1
    )

    # Predição
    df_classified['LOF_LABEL'] = lof.fit_predict(X_final)
    df_classified['LOF_SCORE'] = lof.negative_outlier_factor_

    n_anomalias = (df_classified['LOF_LABEL'] == -1).sum()

    return df_classified

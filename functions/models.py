import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
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

    # Trainando
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

    # Trainando
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
#######################################################################

def run_if_normal(df, contamination=0.01, random_state=42):
    """
    Executa Isolation Forest APENAS para transações NÃO SIGILOSAS (SIGILOSO=0).
    Ignora os dados sigilosos na detecção de anomalia.
    """
    # Filtrar só registros não sigilosos
    df_normal = df[df['SIGILOSO'] == 0].copy()

    # Preprocessamento
    preprocessor = get_preprocessor()
    X_scaled = preprocessor.fit_transform(df_normal)

    # Adicionar pequeno ruído para evitar colinearidade
    ruido = np.random.normal(0, 1e-5, X_scaled.shape)
    X_final = X_scaled + ruido

    # Treinar Isolation Forest
    if_model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=300,
        n_jobs=-1
    )

    df_normal['IF_LABEL'] = if_model.fit_predict(X_final)
    df_normal['IF_SCORE'] = if_model.decision_function(X_final)

    return df_normal



def run_if_classified(df, contamination=0.01, random_state=42):
    """
    Executa Isolation Forest APENAS para transações SIGILOSAS (SIGILOSO=1).
    Usado para achar anomalias dentro do universo sigiloso.
    """
    # Filtrar só registros sigilosos
    df_classified = df[df['SIGILOSO'] == 1].copy()

    # Preprocessamento
    preprocessor = get_preprocessor()
    X_scaled = preprocessor.fit_transform(df_classified)

    # Ruído
    ruido = np.random.normal(0, 1e-5, X_scaled.shape)
    X_final = X_scaled + ruido

    # Treinar Isolation Forest
    if_model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=300,
        n_jobs=-1
    )

    df_classified['IF_LABEL'] = if_model.fit_predict(X_final)
    df_classified['IF_SCORE'] = if_model.decision_function(X_final)

    return df_classified

import pandas as pd
import os
import re

def load_and_combine_csvs(csv_path):
    """
    Load all CSV files from a directory into a single DataFrame.
    Adds a column 'ARQUIVO_ORIGEM' with the file name for traceability.
    Assumes ; as separator and latin-1 encoding.
    """
    dfs = []
    csv_files = [f for f in os.listdir(csv_path) if f.lower().endswith('.csv')]
    for file in csv_files:
        file_path = os.path.join(csv_path, file)
        df_temp = pd.read_csv(file_path, sep=';', encoding='latin-1', low_memory=False)
        df_temp['ARQUIVO_ORIGEM'] = file
        dfs.append(df_temp)
    df = pd.concat(dfs, ignore_index=True)
    ## Opt.: Adicionar fluxo para considerar somente os ultimos X meses para melhorar performance.
    return df

def clean_dataframe(df):
    """
    Cleans key columns:
    - Converts 'DATA TRANSAÇÃO' to datetime (%d/%m/%Y).
    - Converts 'VALOR TRANSAÇÃO' from Brazilian format to float.
    - Drops duplicates.
    Returns a cleaned DataFrame.
    """
    df = df.copy()
    df['DATA TRANSAÇÃO'] = pd.to_datetime(df['DATA TRANSAÇÃO'], format='%d/%m/%Y', errors='coerce')
    df['VALOR TRANSAÇÃO'] = (
        df['VALOR TRANSAÇÃO']
        .astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
    )
    df['VALOR TRANSAÇÃO'] = pd.to_numeric(df['VALOR TRANSAÇÃO'], errors='coerce').fillna(0)
    df_limpo = df.drop_duplicates()
    return df_limpo

def add_confidential_flags(df_limpo):
    """
    Add one columns:
    - 'SIGILOSO': 1 if transaction is confidential, 0 otherwise.
    """
    df_limpo = df_limpo.copy()
    df_limpo['SIGILOSO'] = (df_limpo['TRANSAÇÃO'] == 'Informações protegidas por sigilo').astype(int)
    return df_limpo

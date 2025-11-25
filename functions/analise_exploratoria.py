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
    Adds two columns:
    - 'SIGILOSO': 1 if transaction is confidential, 0 otherwise.
    - 'DATA_IMPUTADA': 1 if date is imputed/missing, 0 if present.
    """
    df_limpo = df_limpo.copy()
    df_limpo['SIGILOSO'] = (df_limpo['TRANSAÇÃO'] == 'Informações protegidas por sigilo').astype(int)
    df_limpo['DATA_IMPUTADA'] = df_limpo['DATA TRANSAÇÃO'].isnull().astype(int)
    return df_limpo

def estimar_estado(row, termos_especificos, estados_map, siglas_confiaveis):
    texto = str(row['NOME ÓRGÃO']) + " " + str(row['NOME UNIDADE GESTORA'])
    texto = texto.upper()

    # Specific terms mapping
    for termo, uf in termos_especificos.items():
        if termo in texto:
            return uf

    # Clean irrelevant terms
    texto = texto.replace(" SEDE ", " ").replace("PARADA", "")
    termos_presidencia = ['GABINETE DE SEGURANCA', 'SECRETARIA DE ADMINISTRACAO/PR', 'PRESIDENCIA DA REPUBLICA']
    for termo in termos_presidencia:
        if termo in texto:
            return 'DF'

    # Regex for prepositions before state code
    padrao_preposicao = r'\b(NO|NA|DO|DA|DE|EM|AO)\s+(' + '|'.join(siglas_confiaveis) + r')\b'
    match = re.search(padrao_preposicao, texto)
    if match:
        return match.group(2)

    # State by sigla or full name
    for uf, termos in estados_map.items():
        for termo in termos:
            if len(termo) > 3 and termo in texto:
                return uf
            elif re.search(r'\b' + re.escape(termo) + r'\b', texto):
                return uf
    return 'UNIÃO'

def apply_estado_estimation(df_limpo, termos_especificos, estados_map):
    siglas_confiaveis = list(estados_map.keys())
    df_limpo = df_limpo.copy()
    df_limpo['ESTADO_ESTIMADO'] = df_limpo.apply(lambda row: estimar_estado(row, termos_especificos, estados_map, siglas_confiaveis), axis=1)
    return df_limpo

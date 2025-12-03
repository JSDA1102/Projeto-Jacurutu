import numpy as np

def feature_engineering(df):

    # Add confidential flag
    df['SIGILOSO'] = (df['TRANSAÇÃO'] == 'Informações protegidas por sigilo').astype(int)

    # ID_portador column
    df["ID_PORTADOR"] = df["CPF PORTADOR"] + df["NOME PORTADOR"]

    # Weekend column (including "SIGILOSO" rule)
    df["FIM_SEMANA"] = np.where(
        df['SIGILOSO'] == 1,
        0,
        df['DATA TRANSAÇÃO'].dt.day_of_year.isin([5, 6]).astype(int)
    )

    # Transform value into log
    df['LOG_VALOR'] = np.log1p(df['VALOR TRANSAÇÃO'])

    # Frequência para cada coluna categórica informada
    coluna_frequencia = ['NOME ÓRGÃO', 'ESTADO_ESTIMADO', 'NOME FAVORECIDO']
    for col in coluna_frequencia:
        freq_map = df[col].value_counts(normalize=True)
        df[f'FREQ_{col}'] = df[col].map(freq_map)

    # Adiciona uma coluna contendo a média do valor da transação por órgão, ano e mês
    df['MEDIA_VALOR_ORGAO_MES'] = df.groupby(['NOME ÓRGÃO', 'ANO EXTRATO',
                                              'MÊS EXTRATO'])['VALOR TRANSAÇÃO'].transform('mean')

    # Adiciona uma coluna para razão entre o valor da transação e o órgão
    df['RATIO_MES'] = df['VALOR TRANSAÇÃO'] / df['MEDIA_VALOR_ORGAO_MES']

    return df

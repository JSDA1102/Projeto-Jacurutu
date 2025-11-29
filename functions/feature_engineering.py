import numpy as np

def feature_engineering(df):
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

    return df

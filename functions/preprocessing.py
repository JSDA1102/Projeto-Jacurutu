import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, RobustScaler

# 1. Define Final Feature Lists

# These lists must match the columns present in our df_final AFTER feature engineering.

# Categorical Columns (Impute + Encode)
cat_columns = [
    'NOME ÓRGÃO SUPERIOR', 'NOME ÓRGÃO', 'NOME UNIDADE GESTORA', 'CPF PORTADOR',
    'NOME PORTADOR', 'NOME FAVORECIDO', 'TRANSAÇÃO', 'ARQUIVO_ORIGEM', 'ESTADO_ESTIMADO',
    'ID_PORTADOR', 'CNPJ OU CPF FAVORECIDO'
]

# Numerical Value Column (Only Scaling, as Log is pre-calculated)
num_value = ['LOG_VALOR']

# Other Numerical Columns (Scaling for codes, frequencies, and ratios)
num_other = [
    'CÓDIGO ÓRGÃO SUPERIOR', 'CÓDIGO ÓRGÃO', 'CÓDIGO UNIDADE GESTORA', 'ANO EXTRATO',
    'MÊS EXTRATO', 'SIGILOSO', 'FIM_SEMANA', 'FREQ_NOME ÓRGÃO',
    'FREQ_ESTADO_ESTIMADO', 'FREQ_NOME FAVORECIDO', 'SEMESTRE_EXTRATO',
    'MEDIA_VALOR_ORGAO_MES', 'MEDIA_VALOR_ORGAO_SEM', 'RATIO_MES', 'RATIO_SEM'
]


# 2. Define Individual Pipelines (Transformers)

# Numerical other pipeline: Robust Scaling for codes and ratios.
num_other_pipeline = RobustScaler()

# Numerical value pipeline: Robust Scaling for the already log-transformed value.
num_value_pipeline = RobustScaler()

# Categorical pipeline: Impute missing categories with 'Desconhecido', then One-Hot Encode.
cat_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='constant', fill_value='Desconhecido')),
    ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])


# 3. Define the ColumnTransformer 

# The final preprocessor object that combines all steps.
preprocessor = ColumnTransformer(
    transformers=[
        ('num_other', num_other_pipeline, num_other),
        ('num_value', num_value_pipeline, num_value),
        ('cat', cat_pipeline, cat_columns),
    ],
    remainder='passthrough'
)

# You can also define a function to load the combined preprocessor object if needed:
def get_preprocessor():
    """Returns the preprocessor ColumnTransformer object."""
    return preprocessor

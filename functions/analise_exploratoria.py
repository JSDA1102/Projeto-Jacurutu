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
    Adds one columns:
    - 'SIGILOSO': 1 if transaction is confidential, 0 otherwise.
    """
    df_limpo = df_limpo.copy()
    df_limpo['SIGILOSO'] = (df_limpo['TRANSAÇÃO'] == 'Informações protegidas por sigilo').astype(int)
    return df_limpo

MAPA_CIDADES = {
    # RJ
    'RIO DE JANEIRO': 'RJ', 'NITEROI': 'RJ', 'SAO GONCALO': 'RJ',
    'DUQUE DE CAXIAS': 'RJ', 'NOVA IGUACU': 'RJ', 'PETROPOLIS': 'RJ',
    'VOLTA REDONDA': 'RJ', 'ANGRA DOS REIS': 'RJ', 'ITATIAIA': 'RJ',
    'RESENDE': 'RJ', 'PARADA DE LUCAS': 'RJ', 'FLUMINENSE': 'RJ',
    'PEDRO II': 'RJ', 'ILHA DAS FLORES': 'RJ', 'AGULHAS NEGRAS': 'RJ',

    # SP
    'SAO PAULO': 'SP', 'GUARULHOS': 'SP', 'CAMPINAS': 'SP',
    'SAO BERNARDO': 'SP', 'SANTO ANDRE': 'SP', 'OSASCO': 'SP',
    'RIBEIRAO PRETO': 'SP', 'SOROCABA': 'SP', 'SANTOS': 'SP',
    'SAO CARLOS': 'SP', 'TAUBATE': 'SP',

    # MG
    'BELO HORIZONTE': 'MG', 'UBERLANDIA': 'MG', 'JUIZ DE FORA': 'MG',
    'OURO PRETO': 'MG', 'LAVRAS': 'MG', 'ITAJUBA': 'MG', 'ALFENAS': 'MG',
    'SAO JOAO DEL REI': 'MG', 'S.J.DEL-REI': 'MG', 'TRIANGULO MINEIRO': 'MG',

    # ES
    'VITORIA': 'ES', 'VILA VELHA': 'ES',

    # RS
    'PORTO ALEGRE': 'RS', 'CAXIAS DO SUL': 'RS', 'PELOTAS': 'RS',
    'CANOAS': 'RS', 'SANTA MARIA': 'RS', 'RIO GRANDE': 'RS',
    'CONCEICAO S/A': 'RS', 'PAMPA': 'RS',

    # PR
    'CURITIBA': 'PR', 'LONDRINA': 'PR', 'MARINGA': 'PR',
    'PONTA GROSSA': 'PR', 'CASCAVEL': 'PR', 'FOZ DO IGUACU': 'PR',

    # SC
    'FLORIANOPOLIS': 'SC', 'JOINVILLE': 'SC', 'BLUMENAU': 'SC',
    'CHAPECO': 'SC', 'ITAJAI': 'SC', 'RIO DO SUL': 'SC',
    'CATARINENSE': 'SC',

    # Capitais e Polos
    'BRASILIA': 'DF', 'MANAUS': 'AM', 'BELEM': 'PA', 'SANTAREM': 'PA',
    'PORTO VELHO': 'RO', 'RIO BRANCO': 'AC', 'BOA VISTA': 'RR', 'MACAPA': 'AP',
    'PALMAS': 'TO', 'SAO LUIS': 'MA', 'TERESINA': 'PI', 'FORTALEZA': 'CE',
    'NATAL': 'RN', 'JOAO PESSOA': 'PB', 'RECIFE': 'PE', 'MACEIO': 'AL',
    'ARACAJU': 'SE', 'SALVADOR': 'BA', 'FEIRA DE SANTANA': 'BA',
    'GONCALO MONIZ': 'BA', 'CUIABA': 'MT', 'CAMPO GRANDE': 'MS',
    'GOIANIA': 'GO', 'RIO VERDE': 'GO',

    # Nacionais (Forçam DF)
    'NACIONAL': 'DF', 'BRASILEIRA': 'DF', 'CENTRAL': 'DF', 'SUPERIOR': 'DF',
    'CODEVASF': 'DF', 'FNDE': 'DF', 'INEP': 'DF', 'EBSERH': 'DF',
    'SIT': 'DF', 'PARNAIBA': 'DF', 'VALES DO S.FRANC': 'DF',
    'COMUNICACAO S.A': 'DF', 'RECURSOS MINERAIS': 'DF', 'DITEC/DPF': 'DF',
    'INTELIGENCIA': 'DF', 'ABIN': 'DF', 'CNPQ': 'DF', 'CAPES': 'DF'
}

# Mapa de Estados (Siglas e Variações)
MAPA_ESTADOS = {
    'AC': ['ACRE', '/AC', '- AC'], 'AL': ['ALAGOAS', '/AL', '- AL'],
    'AP': ['AMAPA', '/AP', '- AP'], 'AM': ['AMAZONAS', '/AM', '- AM'],
    'BA': ['BAHIA', '/BA', '- BA'], 'CE': ['CEARA', '/CE', '- CE'],
    'DF': ['DISTRITO FEDERAL', 'BRASILIA', '/DF', '- DF'],
    'ES': ['ESPIRITO SANTO', '/ES', '- ES'], 'GO': ['GOIAS', '/GO', '- GO'],
    'MA': ['MARANHAO', '/MA', '- MA'], 'MT': ['MATO GROSSO', '/MT', '- MT'],
    'MS': ['MATO GROSSO DO SUL', '/MS', '- MS'], 'MG': ['MINAS GERAIS', '/MG', '- MG'],
    'PB': ['PARAIBA', '/PB', '- PB'], 'PR': ['PARANA', '/PR', '- PR'], 'PA': ['PARA', '/PA', '- PA'],
    'PE': ['PERNAMBUCO', '/PE', '- PE'], 'PI': ['PIAUI', '/PI', '- PI'],
    'RJ': ['RIO DE JANEIRO', '/RJ', '- RJ'],
    'RN': ['RIO GRANDE DO NORTE', '/RN', '- RN'], 'RS': ['RIO GRANDE DO SUL', '/RS', '- RS'],
    'RO': ['RONDONIA', '/RO', '- RO'], 'RR': ['RORAIMA', '/RR', '- RR'],
    'SC': ['SANTA CATARINA', '/SC', '- SC'], 'SP': ['SAO PAULO', '/SP', '- SP'],
    'SE': ['SERGIPE', '/SE', '- SE'], 'TO': ['TOCANTINS', '/TO', '- TO']
}

# Gera a lista de siglas automaticamente a partir das chaves do mapa
SIGLAS_CONFIAVEIS = list(MAPA_ESTADOS.keys())

# Termos que jogam para UNIÃO (Último Recurso)
TERMOS_UNIAO = [
    'FEDERAL', 'NACIONAL', 'BRASILEIRA', 'REGIONAL', 'SUDESTE', 'NORDESTE',
    'BATALHAO', 'COMANDO', 'LOGISTICO', 'INFANTARIA', 'BRIGADA',
    'GRUPAMENTO', 'SUPRIMENTO', 'EXERCITO', 'MARINHA', 'AERONAUTICA'
]

def _estimate_state_row(linha):
    """
    Internal function to process a single row.
    Uses the global constants defined above.
    """
    texto = str(linha['NOME ÓRGÃO']) + " " + str(linha['NOME UNIDADE GESTORA'])
    texto = texto.upper()

    for termo, uf in MAPA_CIDADES.items():
        if termo in texto:
            return uf

    texto = texto.replace(" SEDE ", " ")
    texto = texto.replace("PARADA", "")

    if 'PRESIDENCIA DA REPUBLICA' in texto or 'GABINETE DE SEGURANCA' in texto:
        return 'DF'

    padrao_preposicao = r'\b(NO|NA|DO|DA|DE|EM|AO)\s+(' + '|'.join(SIGLAS_CONFIAVEIS) + r')\b'
    match = re.search(padrao_preposicao, texto)
    if match:
        return match.group(2)

    for uf, termos in MAPA_ESTADOS.items():
        for termo in termos:
            if len(termo) > 3:
                if termo in texto:
                    return uf
            elif re.search(r'\b' + re.escape(termo) + r'\b', texto):
                return uf

    for termo in TERMOS_UNIAO:
        if termo in texto:
            return 'UNIÃO'

    return 'UNIÃO'

def apply_state_estimation(df):
    """
    Applies the state estimation logic to the entire DataFrame.
    """
    df_resultado = df.copy()
    df_resultado['ESTADO_ESTIMADO'] = df_resultado.apply(_estimate_state_row, axis=1)
    return df_resultado

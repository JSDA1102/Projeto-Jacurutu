import re
import pandas as pd

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

# -----------------------------------------------------------------------------
# 2. LÓGICA DE IMPUTAÇÃO
# -----------------------------------------------------------------------------

def _estimate_state_row(linha):
    """
    Função interna para processar uma única linha.
    Tenta inferir o estado com base no texto combinado de Órgão e Unidade Gestora.
    """
    texto_bruto = str(linha['NOME ÓRGÃO']) + " " + str(linha['NOME UNIDADE GESTORA'])
    texto = texto_bruto.upper()

    # 1. Busca por Cidades Específicas
    for termo, uf in MAPA_CIDADES.items():
        if termo in texto:
            return uf

    # 2. Remover "SEDE" para não confundir com Sergipe (SE)
    texto = re.sub(r'\bSEDE\b', ' ', texto)
    texto = texto.replace("- SEDE", " ")

    # 3. Casos Especiais de DF
    if 'PRESIDENCIA DA REPUBLICA' in texto or 'GABINETE DE SEGURANCA' in texto:
        return 'DF'

    # 4. Busca por Padrão de Preposição: "EM SP", "DO RJ", "NO DF"
    padrao_preposicao = r'\b(NO|NA|DO|DA|DE|EM|AO)\s+(' + '|'.join(SIGLAS_CONFIAVEIS) + r')\b'
    match = re.search(padrao_preposicao, texto)
    if match:
        return match.group(2)

    # 5. Busca Geral nos Mapas de Estados
    for uf, termos in MAPA_ESTADOS.items():
        for termo in termos:
            if len(termo) > 2:
                if termo in texto:
                    return uf

        # Verifica a Sigla (UF) isolada
        if re.search(r'\b' + re.escape(uf) + r'\b', texto):
            return uf

    # 6. Termos Genéricos que indicam UNIÃO
    for termo in TERMOS_UNIAO:
        if termo in texto:
            return 'UNIÃO'

    # 7. Fallback
    return 'UNIÃO'

def apply_state_estimation(df):
    """
    Aplica a lógica de estimação de estado para todo o DataFrame.
    """
    df_resultado = df.copy()
    if not df_resultado.empty:
        df_resultado['ESTADO_ESTIMADO'] = df_resultado.apply(_estimate_state_row, axis=1)
    else:
        df_resultado['ESTADO_ESTIMADO'] = [] # Garante coluna vazia se input vazio

    return df_resultado

# 🦉 Projeto Jacurutu

> **Status do Projeto:** 🚧 Em Andamento 🚧

**O Jacurutu (Corujão-orelhudo) é a maior ave de rapina noturna do Brasil. Conhecida por sua visão e audição aguçadas, ela monitora seus alvos antes da caça. A ideia do projeto é a mesma: monitorar a "floresta" de dados de gastos públicos para encontrar as transações que fogem do padrão.**

## 1. Visão Geral

Este projeto utiliza Ciência de Dados para analisar os gastos dos Cartões de Pagamento do Governo Federal (CPGF).

Nosso objetivo não é apenas *encontrar* transações estranhas, mas **priorizá-las** de forma inteligente. Para isso, construímos um sistema que combina o **nível de "estranheza"** (detectado por um *Ensemble* de IA) com o **valor financeiro (risco)**. O resultado final é um *dashboard* interativo onde um auditor pode investigar os casos mais relevantes com eficiência.

## 2. Fonte dos Dados

A base de dados principal é o extrato detalhado dos cartões corporativos do Governo Federal, cobrindo o período de 2023 até o presente.

* **Fonte:** Portal da Transparência
* **URL de Download:** [Portal da Transparência - CPGF](https://portaldatransparencia.gov.br/download-de-dados/cpgf)
* **Dicionário dos Dados:** [Dicionário de Dados - CPGF](https://portaldatransparencia.gov.br/dicionario-de-dados/cpgf)

## 3. Tecnologias Principais

* **[Python 3.12.9](https://www.python.org/)**
* **[Pandas](https://pandas.pydata.org/) & [PyArrow](https://arrow.apache.org/):** Para manipulação de dados de alta performance e leitura de arquivos Parquet.
* **[Scikit-learn](https://scikit-learn.org/):** Para construção dos modelos de detecção de anomalia.
    * **Isolation Forest** (Detecção global)
    * **Local Outlier Factor (LOF)** (Detecção local/densidade)
* **[Streamlit](https://streamlit.io/):** Para construção do painel de investigação (Dashboard).
* **[Geopandas](https://geopandas.org/) (Planejado):** Para visualização geoespacial dos gastos.

## 4. Pipeline do Projeto: O Roteiro da Caça

Nossa metodologia segue um roteiro estruturado para transformar dados brutos em *insights* acionáveis.

### 4.1. Ingestão e Limpeza Avançada
* **Consolidação:** Unificação de todos os arquivos CSV mensais.
* **Rastreabilidade:** Adição da coluna `ARQUIVO ORIGEM` para auditoria da fonte.
* **Tratamento de Sigilo:** Identificação e tratamento de 92.000+ transações sigilosas (sem data/favorecido), com imputação de datas contábeis para manutenção da série temporal.
* **Enriquecimento Geográfico (NLP):** Como a base original não possui coluna de Estado (UF), desenvolvemos um algoritmo de processamento de texto que extrai a localização a partir do nome da Unidade Gestora, identificando gastos regionais vs. centrais.

### 4.2. Engenharia de Features
Para ensinar a IA o que é "estranho", criamos contextos matemáticos:
* **Contexto Temporal:** Criação de flags para datas imputadas.
* **Frequency Encoding:** Transformação de variáveis categóricas (Órgão, Favorecido) em numéricas baseadas na raridade de ocorrência.
* **Golden Features (Ratios):** Cálculo de razões estatísticas (ex: `Valor da Transação / Média do Órgão no Mês`). Isso permite detectar desvios sutis que escapam à análise de valor bruto.

### 4.3. Modelagem (O "Comitê de Detetives")
Utilizamos uma estratégia de **Ensemble** não supervisionado.

* **Detetive 1 (`Isolation Forest`):** Foca em isolar anomalias globais e valores extremos.
* **Detetive 2 (`Local Outlier Factor` - LOF):** Analisa a densidade local.
    * *Destaque Técnico:* Implementamos **Jittering** (ruído estatístico) para lidar com a alta densidade de transações repetidas (comuns em gastos governamentais), garantindo a estabilidade matemática do modelo.
* **Detetive 3 (`Autoencoder`):** (Planejado) Rede neural para reconstrução de padrões complexos.

### 4.4. Priorização e Investigação
O score técnico não é suficiente para auditoria pública. Criamos o **Score de Prioridade**:

$$Prioridade = (0.7 \times ScoreTecnico) + (0.3 \times RiscoFinanceiro)$$

Isso garante que uma anomalia de R$ 10,00 não tenha a mesma atenção que uma de R$ 100.000,00.

## 5. Métricas de Avaliação

Como não temos rótulos de "fraude confirmada", avaliamos pela relevância:
* **Validação Humana:** Auditoria manual das **Top 200** transações suspeitas.
* **Métrica Chave (`Precision@k`):** "Das Top 100 anomalias apontadas, quantas são dignas de investigação profunda?"

## 6. Limitações e Riscos

* **Raridade vs. Ilegalidade:** O modelo aponta o que é *atípico*. Um gasto pode ser raro (ex: compra única de um equipamento) e perfeitamente legal.
* **Sazonalidade:** O setor público possui ciclos fortes (ex: "correria" de gastos em dezembro).
* **Cold Start:** Novos fornecedores podem ter scores de anomalia inicialmente altos até que o sistema aprenda seu padrão.

## 7. Entregáveis

### Obrigatórios (Core)
1.  **Pipeline de Dados:** Scripts de limpeza e engenharia de features automatizados.
2.  **Modelos Treinados:** Ensemble (IF + LOF) gerando scores de anomalia.
3.  **Dashboard Interativo:** Ferramenta em Streamlit para consumo dos dados pelo auditor.

### Opcionais
1.  **Análise Geoespacial:** Mapas de calor de gastos suspeitos.
2.  **Previsão de Gastos:** Modelos de série temporal para orçamento futuro.

## 8. Roadmap (Progresso)

* ✅ **Análise Exploratória (EDA):** Compreensão profunda das distribuições e sazonalidade.
* ✅ **Limpeza de Dados (ETL):** Pipeline robusto com extração geográfica e tratamento de sigilo.
* ✅ **Baseline Model (LOF):** Implementado com Feature Engineering avançada e Jittering.
* 🔲 **Baseline Model (Isolation Forest):** Em desenvolvimento.
* 🔲 **Ensemble:** Combinação dos scores.
* 🔲 **Dashboard v1:** Desenvolvimento da interface em Streamlit.
* 🔲 **Validação Manual:** Auditoria dos resultados.

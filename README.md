# 🦉 Projeto Jacurutu

> **Status do Projeto:** 🚀 MVP Funcional (v1.0)

**O Jacurutu (Corujão-orelhudo) é a maior ave de rapina noturna do Brasil. Conhecida por sua visão e audição aguçadas, ela monitora seus alvos antes da caça. A ideia do projeto é a mesma: monitorar a "floresta" de dados de gastos públicos para encontrar as transações que fogem do padrão.**

## 1. Visão Geral

Este projeto utiliza Ciência de Dados para analisar os gastos dos Cartões de Pagamento do Governo Federal (CPGF).

Nosso objetivo não é apenas *encontrar* transações estranhas, mas **priorizá-las** de forma inteligente. Para isso, construímos um sistema que combina o **nível de "estranheza"** (detectado por um *Ensemble* de IA) com o **valor financeiro (risco)**. O resultado final é um *dashboard* interativo onde um auditor pode investigar os casos mais relevantes com eficiência e rapidez.

## 2. Fonte dos Dados

A base de dados principal é o extrato detalhado dos cartões corporativos do Governo Federal, cobrindo o período de 2023 até o presente.

* **Fonte:** Portal da Transparência
* **URL de Download:** [Portal da Transparência - CPGF](https://portaldatransparencia.gov.br/download-de-dados/cpgf)
* **Dicionário dos Dados:** [Dicionário de Dados - CPGF](https://portaldatransparencia.gov.br/dicionario-de-dados/cpgf)

## 3. Arquitetura e Tecnologias

O projeto adota uma **arquitetura desacoplada** para garantir alta performance no dashboard:

1.  **Backend (ETL Offline):** Scripts pesados que rodam em batch, treinam os modelos e geram um arquivo otimizado (`.parquet`).
2.  **Frontend (Dashboard Online):** Aplicação leve que apenas lê os dados processados, garantindo carregamento instantâneo.

### Stack Tecnológica
* **Linguagem:** [Python 3.12.9](https://www.python.org/)
* **Processamento:** [Pandas](https://pandas.pydata.org/) & [PyArrow](https://arrow.apache.org/) (Formato Parquet)
* **Machine Learning:** [Scikit-learn](https://scikit-learn.org/)
    * **Isolation Forest** (Detecção global)
    * **Local Outlier Factor (LOF)** (Detecção local/densidade)
* **Dashboard:** [Streamlit](https://streamlit.io/)
* **Visualização:** [Plotly](https://plotly.com/) (Gráficos Interativos) & [Folium](https://python-visualization.github.io/folium/) (Mapas de Calor)

## 4. Pipeline do Projeto: O Roteiro da Caça

Nossa metodologia segue um roteiro estruturado para transformar dados brutos em *insights* acionáveis.

### 4.1. Ingestão e Limpeza Avançada
* **Consolidação:** Unificação de arquivos CSV mensais.
* **Rastreabilidade:** Adição da coluna `ARQUIVO ORIGEM` para auditoria da fonte.
* **Tratamento de Sigilo:** Identificação e tratamento de transações sigilosas (sem data/favorecido), com imputação de datas contábeis.
* **Enriquecimento Geográfico (NLP):** Algoritmo de processamento de texto que extrai a localização (Estado/UF) a partir do nome da Unidade Gestora, permitindo a criação de mapas de calor.

### 4.2. Engenharia de Features
Para ensinar a IA o que é "estranho", criamos contextos matemáticos:
* **Contexto Temporal:** Criação de flags para datas imputadas.
* **Frequency Encoding:** Transformação de variáveis categóricas (Órgão, Favorecido) em numéricas baseadas na raridade.
* **Golden Features (Ratios):** Cálculo de razões estatísticas (ex: `Valor da Transação / Média do Órgão no Mês`). Isso permite detectar desvios sutis que escapam à análise de valor bruto.

### 4.3. Modelagem (O "Comitê de Detetives")
Utilizamos uma estratégia de **Ensemble Não Supervisionado**:

* **Detetive 1 (`Isolation Forest`):** Foca em isolar anomalias globais e valores extremos.
* **Detetive 2 (`Local Outlier Factor`):** Analisa a densidade local, identificando pontos isolados em relação aos seus vizinhos imediatos.
    * *Destaque Técnico:* Implementação de **_Jittering_** (ruído estatístico controlado) para lidar com a alta duplicidade de valores exatos em transações governamentais.

### 4.4. Priorização e Investigação
O score técnico sozinho não é suficiente para auditoria pública. Criamos o **_Priority Score_**:

$$Prioridade = (0.7 \times ScoreTecnico) + (0.3 \times RiscoFinanceiro)$$

Isso garante que uma anomalia estatística de R$ 10,00 não tenha a mesma atenção que uma de R$ 100.000,00.

## 5. Como Executar o Projeto

1.  **Instalação das dependências:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Atualização da Base de Dados (Download Automático):**
    Este passo baixa automaticamente os meses faltantes do Portal da Transparência,
    extrai os CSVs para `raw_data/` e reexecuta o ETL para gerar o `.parquet`.
    ```bash
    python download_data.py
    ```
    *Opcional:*
    ```bash
    python download_data.py --dry-run        # mostra o plano, sem baixar
    python download_data.py --start 202501   # baixa a partir de jan/2025
    python download_data.py --end 202606     # baixa até jun/2026
    python download_data.py --no-etl         # só baixa/extrai, sem processar
    ```
3.  **Execução do ETL (Geração dos Dados):**
    Este passo processa os CSVs brutos, treina os modelos e salva o arquivo `.parquet`.
    (Opcional — já é executado automaticamente pelo `download_data.py`.)
    ```bash
    python run_etl.py
    ```
4.  **Execução do Dashboard:**
    ```bash
    streamlit run functions/front/app.py
    ```

## 6. Limitações e Riscos

* **Raridade vs. Ilegalidade:** O modelo aponta o que é *atípico*. Um gasto pode ser raro (ex: compra única de equipamento) e perfeitamente legal.
* **Sazonalidade:** O setor público possui ciclos fortes (ex: encerramento de exercício fiscal em dezembro).
* **Cold Start:** Novos fornecedores podem ter scores de anomalia inicialmente altos até que o sistema aprenda seu padrão.

## 7. Roadmap (Progresso)

* ✅ **Análise Exploratória (EDA):** Compreensão profunda das distribuições e sazonalidade.
* ✅ **Limpeza de Dados (ETL):** Pipeline robusto com extração geográfica e tratamento de sigilo.
* ✅ **Modelagem Ensemble:** Implementação e combinação de Isolation Forest + LOF.
* ✅ **Dashboard v1:** Interface em Streamlit com mapas, filtros e exportação (Excel/CSV).
* ✅ **Arquitetura de Produção:** Separação do ETL (`run_etl.py`) do Frontend.
* ✅ **Atualização Automática de Dados:** Download/extração automatizados dos meses faltantes.

### 🔮 Melhorias Futuras
* **Autoencoder (_Deep Learning_):** Implementar redes neurais para reconstrução de padrões complexos não lineares.
* **Previsão Orçamentária:** Modelos de séries temporais (Prophet/ARIMA) para prever gastos futuros.

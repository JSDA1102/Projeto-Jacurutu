# 🦉 Projeto Jacurutu

> **Status do Projeto:** 🚧 Em Andamento (Fase de Baseline) 🚧

**O Jacurutu (Corujão-orelhudo) é a maior ave de rapina noturna do Brasil. Conhecida por sua visão e audição aguçadas, ela monitora seus alvos antes da caça. A ideia do projeto é a mesma: monitorar a "floresta" de dados de gastos públicos para encontrar as transações que fogem do padrão.**

## 1. Visão Geral

Este projeto usa Ciência de Dados para analisar os gastos dos Cartões de Pagamento do Governo Federal (CPGF).

Nosso objetivo não é apenas *encontrar* transações estranhas, mas **priorizá-las** de forma inteligente. Para isso, vamos construir um sistema que combina o **nível de "estranheza"** (detectado pela IA) com o **valor financeiro (risco)**. O resultado final é um *dashboard* interativo onde um auditor pode investigar os casos mais relevantes.

## 2. Fonte dos Dados

A base de dados principal é o extrato detalhado dos cartões corporativos do Governo Federal, cobrindo o período de 2023 até o presente.

* **Fonte:** Portal da Transparência
* **URL de Download:** `https://portaldatransparencia.gov.br/download-de-dados/cpgf`
* **Dicionário dos Dados:** `https://portaldatransparencia.gov.br/dicionario-de-dados/cpgf`

## 3. Tecnologias Principais

* **[Python 3.12.9](https://www.python.org/)**
* **[Pandas](https://pandas.pydata.org/):** Para carregar, limpar e organizar os dados.
* **[Scikit-learn](https://scikit-learn.org/):** Para os modelos de detecção de anomalia (IF e LOF).
    * **[IsolationForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)**
    * **[Local Outlier Factor (LOF)](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html)**
* **[TensorFlow/Keras](https://www.tensorflow.org/):** Para o modelo de detecção via `Autoencoder`.
* **[Streamlit](https://streamlit.io/):** Para construir o *dashboard* interativo de investigação.
* **[Geopandas](https://geopandas.org/):** (Planejado) Para criar mapas de onde os gastos anômalos ocorrem.

## 4. Pipeline do Projeto: O Roteiro da Caça

Nossa metodologia segue um roteiro claro para transformar dados brutos em *insights* acionáveis.

### 4.1. Ingestão e Limpeza dos dados
* **Consolidação:** Juntamos todos os arquivos CSV mensais em uma única base de dados.
* **Rastreabilidade:** Adicionamos a coluna `ARQUIVO ORIGEM` para saber de onde veio cada transação.
* **Tratamento de Nulos:** Removemos 23.8% das linhas que não tinham dados essenciais (como `CPF PORTADOR` ou `DATA TRANSAÇÃO`), pois elas não podem ser analisadas.
* **Correção de Tipos:** Garantimos que datas sejam lidas como datas e valores (ex: `1.500,75`) sejam lidos como números.

### 4.2. Detecções Rápidas
Antes de usar IA, procuramos por anomalias óbvias com regras simples (SQL):
* **Valores Extremos:** Quais são as 10 maiores transações de toda a base? (Risco de alto impacto).
* **Duplicatas Exatas:** Existem gastos idênticos (mesmo valor, data e fornecedor) lançados mais de uma vez? (Risco de erro ou fraude).

### 4.3. Engenharia de Features
Para a IA saber o que é "estranho", primeiro precisamos ensiná-la a entender o "contexto" de cada gasto. Fazemos isso criando novas colunas que respondem perguntas:
* **Contexto do Portador:** Esse gasto é normal *para este portador*? É 10x maior que a média dele?
* **Contexto do Fornecedor:** Esse gasto é normal *para este fornecedor*?
* **Contexto Temporal:** O gasto ocorreu em um fim de semana ou feriado? O portador está gastando com uma frequência incomum?
* **Contexto Comportamental:** O gasto foi um valor "redondo" (ex: R$ 2.000,00)? É a primeira vez que este órgão compra deste fornecedor?

### 4.4. Modelagem
Não confiamos em um único "detetive" (modelo de IA). Usamos uma estratégia de **Ensemble** (combinação de modelos) para robustez. Cada modelo gera um score bruto, que é normalizado (escala 0 a 1) antes da combinação.

* **Detetive 1 (`Isolation Forest`):** Isola anomalias baseando-se em cortes aleatórios de árvores de decisão.
* **Detetive 2 (`Local Outlier Factor` - LOF):** Analisa a densidade local. Se um ponto tem densidade muito menor que seus vizinhos, é anômalo.
* **Detetive 3 (`Autoencoder`):** Rede neural que aprende a "reconstruir" o padrão normal. O score é o "Erro de Reconstrução" (o quão mal ele conseguiu desenhar a transação).

**Cálculo do Score de Estranheza:**
A pontuação final de anomalia técnica é a média aritmética dos scores normalizados dos três modelos.

### 4.5. Priorização e Investigação
O score técnico não é suficiente para auditoria pública. Uma anomalia de R$ 5,00 tem baixo impacto. Criamos o **Score de Prioridade** combinando "estranheza" e "risco financeiro".
* **Score de Prioridade:** Nós criamos um score final que une a "estranheza" com o "risco financeiro":
    `Prioridade = (0.7 * Score_Estranheza) + (0.3 * Score_Valor)`
* **Dashboard (Streamlit):** O auditor não vê o código, ele vê um painel interativo com a lista de gastos, já ordenada por esta `Prioridade`, pronta para análise e investigação.

## 5. Métricas de Avaliação

Como não temos um gabarito de "fraudes" marcadas, nosso sucesso é medido pela relevância do que encontramos:
* **Validação Humana:** Vamos auditar manualmente as **Top 200** transações que o modelo apontar como mais suspeitas.
* **Métrica Chave: `Precision@k`:** Vamos responder à pergunta: "Das Top 100 anomalias que o Jacurutu apontou, quantas eram *realmente* suspeitas ou interessantes para um auditor investigar?".
* É crucial entender o que o modelo **não** é, e onde ele pode se confundir. O Jacurutu aponta transações *atípicas*, que não são necessariamente *ilegais*.
1.  **Raridade vs. Ilegalidade:** O modelo pode marcar como "estranho" um gasto legítimo apenas porque aquele portador raramente utiliza o cartão, ou porque o fornecedor é novo na base.
2.  **Sazonalidade Pública:** O setor público possui ciclos fortes (ex: "correria" de gastos no fim do exercício fiscal em dezembro). O modelo pode interpretar esse aumento súbito de volume como anomalia se não for treinado com janelas temporais adequadas.
3.  **Falsos Positivos (Cold Start):** Fornecedores que aparecem pela primeira vez na base podem ter scores de anomalia mais altos até que o sistema "se acostume" com o padrão de cobrança deles.

## 6. Entregáveis do Projeto

Para definir o sucesso, separamos o que é essencial (obrigatório) do que são melhorias futuras (opcionais).

### Entregáveis Obrigatórios (Core do Projeto)
1.  **Modelo de Detecção de Anomalias:** O "Comitê de Detetives" (IF, LOF, Autoencoder) treinado e capaz de gerar um score de "estranheza" para cada transação.
2.  **Script de Priorização:** A lógica de negócio que combina o score de "estranheza" com o valor financeiro para criar o `Score de Prioridade`.
3.  **Dashboard Interativo (Streamlit):** A ferramenta visual para o usuário final (auditor) consumir a lista priorizada, analisar os *outliers* (com *drill-down*) e gerenciar o fluxo de investigação.
4.  **Análise Geoespacial (Geopandas):** Implementar o mapa de calor (planejado na seção de tecnologias) para mostrar *onde* geograficamente os gastos anômalos estão concentrados.

### Entregáveis Opcionais
1.  **Modelo de Previsão de Gastos:** Utilizar modelos de Regressão Linear ou Séries Temporais para tentar *prever* o volume de gastos futuros por órgão ou categoria, ajudando no planejamento orçamentário.

## 7. Roadmap (Próximos Passos)

1.  **Queries Rápidas:** Implementar as detecções SQL (duplicatas, top 1%).
2.  **Modelo Baseline:** Rodar o primeiro "detetive" (`Isolation Forest`) e exportar o Top 500 de suspeitos.
3.  **Dashboard v1:** Construir o painel inicial em Streamlit para exibir esta primeira lista.
4.  **Revisão Manual:** Analisar manualmente 50-100 casos para validar o *baseline*.
5.  **Notebook Completo:** Implementar o "Comitê de Detetives" completo (com LOF e Autoencoder).

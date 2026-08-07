import os
import io
import base64
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

# Caminho do logo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# Converte o logo para base64
try:
    with open(LOGO_PATH, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
except FileNotFoundError:
    logo_base64 = ""


# > CONFIGURAÇÃO GERAL

st.set_page_config(page_title="Projeto Jacurutu", page_icon="🦉", layout="wide")

# CSS
st.markdown(
    """
    <style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');

    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #2DD4BF, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        width: fit-content;
    }

    h1 i, h2 i, h3 i, h1 span, h2 span, h3 span {
        -webkit-text-fill-color: #2DD4BF !important;
    }

    [data-testid="stMetricLabel"] {
        color: #E5E7EB !important;
        font-size: 14px !important;
    }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] > div {
        color: #2DD4BF !important;
        font-weight: 700 !important;
    }

    p, li, div {
        color: #E5E7EB;
    }

    .leaflet-container {
        color: #333 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 1. TRADUÇÕES E CONSTANTES
TRANS = {
    "pt": {
        "title": "🦉 Projeto Jacurutu",
        "subtitle": "Monitoramento inteligente de gastos públicos via detecção de anomalias",
        "menu_items": ["Conceito", "Dashboard"],
        "sidebar_filters": '<i class="fa-solid fa-tree" style="margin-right:0.5rem;"></i> Filtros da Floresta',
        "filter_estado": "Estado (UF)",
        "filter_orgsup": "Órgão Superior",
        "filter_org": "Órgão",
        "filter_ug": "Unidade Gestora",
        "filter_sigilo": "Transações Sigilosas",
        "sigilo_sim": "Sim", "sigilo_nao": "Não",
        "filter_date": "Período",
        "warning_nodata": "Sem dados carregados.",
        "warning_filter_empty": "Nenhum registro encontrado com os filtros aplicados.",
        "kpi_trans": "Transações filtradas",
        "kpi_valor": "Valor total filtrado",
        "kpi_anom_valor": "Valor total das anomalias",
        "kpi_estado": "Estado Principal",
        "map_anom": '<i class="fa-solid fa-map" style="margin-right:8px;"></i> Mapa de Calor: Risco & Anomalias',
        "map_spend": '<i class="fa-solid fa-dollar-sign" style="margin-right:8px;"></i> Mapa de Calor: Volume de Gastos',
        "obs_uniao": "🔍 Obs.: \"UNIÃO\" representa órgãos federais/forças sem UF explícita (plotado em Brasília).",
        "chart_time": '<i class="fa-solid fa-chart-line" style="margin-right:8px;"></i> Gastos vs Anomalias (Mensal)',
        "scatter": "Dispersão: Valor × Score de Risco",
        "table": "Top 100 - Maior Risco",
        "performance_tip": "Dica: Filtre por Estado/Órgão para acelerar visualizações.",
        "export_title": "Exportação de Dados",
        "excel_cap": "Ideal para relatórios pontuais com menor volumetria.",
        "excel_btn": "Baixar Top",
        "excel_help": "Devido ao peso do formato Excel, esta opção baixa apenas as {} linhas de maior prioridade.",
        "csv_cap": "Ideal para auditoria completa e importação em outros sistemas.",
        "csv_btn": "Baixar Tudo",
        "csv_help": "Baixa todos os dados filtrados atualmente, sem limite de linhas.",
        "rows_label": "linhas",
        "col_priority": "Prioridade (%)"
    },
    "en": {
        "title": "🦉 Project Jacurutu",
        "subtitle": "Intelligent monitoring of public spending via anomaly detection",
        "menu_items": ["Concept", "Dashboard"],
        "sidebar_filters": '<i class="fa-solid fa-tree" style="margin-right:0.5rem;"></i> Forest Filters',
        "filter_estado": "State (UF)",
        "filter_orgsup": "Superior Agency",
        "filter_org": "Agency",
        "filter_ug": "Management Unit",
        "filter_sigilo": "Classified Transactions",
        "sigilo_sim": "Yes", "sigilo_nao": "No",
        "filter_date": "Period",
        "warning_nodata": "No data loaded.",
        "warning_filter_empty": "No records match the filters.",
        "kpi_trans": "Filtered transactions",
        "kpi_valor": "Total amount",
        "kpi_anom_valor": "Total amount of anomalies",
        "kpi_estado": "Top state",
        "map_anom": '<i class="fa-solid fa-map"></i> Heatmap: Anomalies',
        "map_spend": '<i class="fa-solid fa-dollar-sign"></i> Heatmap: Spending Volume',
        "obs_uniao": '🔍 Note: "UNIÃO" represents federal bodies without explicit state (plotted in Brasilia).',
        "chart_time": '<i class="fa-solid fa-chart-line"></i> Spending vs Anomalies (Monthly)',
        "scatter": "Scatter: Value × Risk Score",
        "table": "Top 100 - Highest Risk",
        "performance_tip": "Tip: Filter by State/Agency to speed up visuals.",
        "export_title": "Data Export",
        "excel_cap": "Best for specific reports and quick viewing.",
        "excel_btn": "Download Top",
        "excel_help": "Due to Excel file size, this option downloads only the top {} highest priority rows.",
        "csv_cap": "Best for full audits and importing into other systems.",
        "csv_btn": "Download All",
        "csv_help": "Downloads all currently filtered data, with no row limit.",
        "rows_label": "rows",
        "col_priority": "Priority (%)"
    }
}

# Coordenadas Centrais (Para o Heatmap)
COORDS_ESTADOS = {
    "AC": [-9.02, -70.81], "AL": [-9.66, -36.65], "AP": [1.41, -51.82],
    "AM": [-3.41, -65.85], "BA": [-12.97, -38.50], "CE": [-3.71, -38.54],
    "DF": [-15.79, -47.86], "ES": [-19.18, -40.30], "GO": [-15.82, -49.83],
    "MA": [-2.53, -44.28], "MG": [-18.51, -44.55], "MS": [-20.77, -54.78],
    "MT": [-12.68, -56.92], "PA": [-3.50, -52.00], "PB": [-7.12, -34.88],
    "PR": [-24.50, -51.00], "PE": [-8.30, -37.00], "PI": [-7.00, -42.00],
    "RJ": [-22.90, -43.17], "RN": [-5.79, -36.50], "RS": [-30.03, -53.00],
    "RO": [-10.80, -62.80], "RR": [2.82, -60.67], "SC": [-27.25, -50.30],
    "SP": [-22.50, -48.00], "SE": [-10.57, -37.45], "TO": [-10.18, -48.33],
    "UNIÃO": [-15.79, -47.86], "UNIAO": [-15.79, -47.86]
}


# 2. CARREGAMENTO DE DADOS
@st.cache_data
def load_data():
    path = "functions/front/dashboard_data.parquet"
    if not os.path.exists(path):
        path = "dashboard_data.parquet"
    if os.path.exists(path):
        df = pd.read_parquet(path)
        if "PRIORITY_SCORE" in df.columns:
            log_s = np.log1p(df["PRIORITY_SCORE"].clip(lower=0))
            min_l, max_l = log_s.min(), log_s.max()
            if max_l > min_l:
                df["PRIORITY_PCT"] = ((log_s - min_l) / (max_l - min_l)) * 99 + 1
            else:
                df["PRIORITY_PCT"] = 50.0
        return df
    return pd.DataFrame()

df = load_data()


# 3. SIDEBAR + FILTROS EM CASCATA
with st.sidebar:
    lang_opt = st.radio("Idioma / Language", ["Português", "English"], horizontal=True)
    lang = "pt" if lang_opt == "Português" else "en"
    T = TRANS[lang]

    st.markdown(f'<h3 style="margin-bottom:0.5rem;">{T["sidebar_filters"]}</h3>', unsafe_allow_html=True)

    if df.empty:
        st.warning(T["warning_nodata"])
        st.stop()

    # 3.1. Estado
    estados = sorted(df["ESTADO_ESTIMADO"].unique().tolist())
    estado_sel = st.multiselect(T["filter_estado"], estados)

    df_tmp = df[df["ESTADO_ESTIMADO"].isin(estado_sel)] if estado_sel else df

    # 3.2. Órgão Superior
    orgsup_opts = sorted(df_tmp["NOME ÓRGÃO SUPERIOR"].unique().tolist())
    orgsup_sel = st.multiselect(T["filter_orgsup"], orgsup_opts)

    if orgsup_sel: df_tmp = df_tmp[df_tmp["NOME ÓRGÃO SUPERIOR"].isin(orgsup_sel)]

    # 3.3. Órgão
    org_opts = sorted(df_tmp["NOME ÓRGÃO"].unique().tolist())
    org_sel = st.multiselect(T["filter_org"], org_opts)

    if org_sel: df_tmp = df_tmp[df_tmp["NOME ÓRGÃO"].isin(org_sel)]

    # 3.4. Unidade Gestora
    ug_opts = sorted(df_tmp["NOME UNIDADE GESTORA"].unique().tolist())
    ug_sel = st.multiselect(T["filter_ug"], ug_opts)

    # 3.5. Sigilo
    sigilo_choice = st.radio(T["filter_sigilo"], [T["sigilo_sim"], T["sigilo_nao"]], index=1)

    # 3.6. Data
    valid_dates = df["DATA TRANSAÇÃO"].dropna()
    if not valid_dates.empty:
        min_d = valid_dates.min().date()
        max_d = valid_dates.max().date()
    else:
        max_d = datetime.now().date()
        min_d = max_d - timedelta(days=90)

    try:
        date_sel = st.date_input(
            T["filter_date"],
            value=[min_d, max_d],
            min_value=min_d,
            max_value=max_d
        )
    except Exception:
        date_sel = [min_d, max_d]

# APLICAÇÃO DOS FILTROS
df_f = df.copy()

mask_sem_data = df_f["DATA TRANSAÇÃO"].isna()
if mask_sem_data.any() and "ANO EXTRATO" in df_f.columns and "MÊS EXTRATO" in df_f.columns:
    # Cria data dia 01 do mês/ano de referência
    datas_imputadas = pd.to_datetime(
        df_f.loc[mask_sem_data, "ANO EXTRATO"].astype(str) + "-" +
        df_f.loc[mask_sem_data, "MÊS EXTRATO"].astype(str) + "-01",
        errors='coerce'
    )
    df_f.loc[mask_sem_data, "DATA TRANSAÇÃO"] = datas_imputadas

# 1. Filtros de Categoria (Cascata)
if 'estado_sel' in locals() and estado_sel:
    df_f = df_f[df_f["ESTADO_ESTIMADO"].isin(estado_sel)]

if 'orgsup_sel' in locals() and orgsup_sel:
    df_f = df_f[df_f["NOME ÓRGÃO SUPERIOR"].isin(orgsup_sel)]

if 'org_sel' in locals() and org_sel:
    df_f = df_f[df_f["NOME ÓRGÃO"].isin(org_sel)]

if 'ug_sel' in locals() and ug_sel:
    df_f = df_f[df_f["NOME UNIDADE GESTORA"].isin(ug_sel)]

# 2. Filtro de Sigilo
df_f["SIGILOSO"] = pd.to_numeric(df_f["SIGILOSO"], errors='coerce').fillna(0).astype(int)

if 'sigilo_choice' in locals():
    if sigilo_choice == T["sigilo_sim"]:
        df_f = df_f[df_f["SIGILOSO"] == 1]
    else:
        df_f = df_f[df_f["SIGILOSO"] == 0]

# 3. Filtro de Período
if 'date_sel' in locals() and isinstance(date_sel, (list, tuple)) and len(date_sel) == 2:
    try:
        start_dt = pd.to_datetime(date_sel[0])
        end_dt = pd.to_datetime(date_sel[1])
        df_f = df_f[(df_f["DATA TRANSAÇÃO"] >= start_dt) & (df_f["DATA TRANSAÇÃO"] <= end_dt)]
    except Exception:
        pass

# 5. Layout Principal
if logo_base64:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:24px;">
            <img src="data:image/png;base64,{logo_base64}" style="width:54px; margin-top:8px;" />
            <div style="margin-top:22px;">
                <h1 style="margin:10; font-size:48px; line-height:1.05;">
                    {T['title'].replace('🦉','')}
                </h1>
            </div>
        </div>
        <p style="font-size:20px; color:#9ca3af; margin-top:6px; max-width:900px;">
            {T['subtitle']}
        </p>
        """,
        unsafe_allow_html=True
    )
else:
    st.title(T['title'])
    st.markdown(f"**{T['subtitle']}**")


# > MENU DE NAVEGAÇÃO

selected = option_menu(
    menu_title=None,
    options=T["menu_items"],
    icons=["file-text", "search"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#1F2937"},
        "icon": {"color": "#2DD4BF", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "--hover-color": "#374151",
            "color": "#E5E7EB"
        },
        "nav-link-selected": {"background-color": "#0D9488", "color": "white"},
    }
)


# > ABA CONCEITO

if selected == T["menu_items"][0]:

    if lang == "pt":
        st.markdown("""
### <i class="fa-solid fa-chart-column" style="margin-right:8px;"></i> 1. O que o sistema faz?
O Jacurutu aplica técnicas de Ciência de Dados para identificar padrões atípicos nos gastos com Cartões de Pagamento do Governo Federal (CPGF), ajudando auditorias a priorizar casos de maior impacto.

O painel permite que auditores e analistas:
- Identifiquem gastos incomuns (“anomalias”).
- Priorizem transações por risco financeiro.
- Visualizem agregações por estado, órgão e período.
- Separem transações sigilosas das demais.

---

### <i class="fa-solid fa-brain" style="margin-right:8px;"></i> 2. Modelos de detecção (Score Técnico)
Usamos um *ensemble* de modelos de anomalia:
- **Isolation Forest** — isola pontos atípicos globalmente.
- **Local Outlier Factor (LOF)** — detecta pontos com baixa densidade local.

A média dos scores desses modelos compõe o **Score Técnico** (indicador de estranheza estatística).

---

### <i class="fa-solid fa-fire" style="margin-right:8px;"></i> 3. Pontuação de Risco (Priority Score)
A **Pontuação de Risco** (denominada *Priority Score* em inglês) combina estranheza técnica com materialidade financeira:

$$
\\text{Pontuação de Risco} =
(0.7 \\times \\text{Score Técnico}) +
(0.3 \\times \\text{Risco Financeiro})
$$

- **Score Técnico:** média dos scores de IF e LOF — mede quão atípica é a transação.
- **Risco Financeiro:** valor monetário da transação — maior valor = maior materialidade.

Essa combinação evita que anomalias de valor ínfimo recebam prioridade acima de casos de maior impacto financeiro.

---

### <i class="fa-solid fa-lock" style="margin-right:8px;"></i> 4. Transações Sigilosas
Algumas linhas da base são marcadas como **SIGILOSO = 1**. Essas transações costumam ter informações omitidas (data precisa, favorecido, descrição) por determinação legal ou judicial.

#### Base Legal
A classificação é regulada pela **Lei nº 12.527/2011 — LAI** (Lei de Acesso à Informação) e decretos complementares. O sigilo pode ser aplicado quando a divulgação puder:
- comprometer defesa ou soberania;
- colocar vidas em risco;
- prejudicar investigações ou atividades de inteligência;
- violar a intimidade ou a privacidade de pessoas.

No painel você escolhe analisar **Somente Sigilosas (Sim)** ou **Sem Sigilosas (Não — padrão)**.

---

### <i class="fa-solid fa-folder-open" style="margin-right:8px;"></i> 5. Fonte de Dados
- **Base:** Extrato detalhado dos Cartões de Pagamento do Governo Federal (CPGF), 2023–presente.
- **Origem / Download:** Portal da Transparência — CPGF.
- **Dicionário:** Dicionário de Dados — CPGF.
- **Mais sobre o Portal:** https://portaldatransparencia.gov.br/controle-social

---

### <i class="fa-solid fa-compass" style="margin-right:8px;"></i> 6. Observação sobre 'UNIÃO'
Quando não é possível inferir UF a partir do nome da unidade gestora, adotamos a categoria **UNIÃO**, que é apresentada como **DF (Brasília)** no mapa. Isso abrange órgãos federais com atuação nacional e forças armadas.

---

### <i class="fa-solid fa-circle-exclamation" style="margin-right:8px;"></i> 7. Aviso Importante
O Jacurutu **não acusa fraude**; ele destaca comportamentos atípicos para orientar auditoria humana. Resultados devem ser interpretados por especialistas.

""", unsafe_allow_html=True)
    else:
        st.markdown("""
### <i class="fa-solid fa-chart-column" style="margin-right:8px;"></i> 1. What the system does
Jacurutu uses Data Science to surface unusual spending patterns in the Federal Government Corporate Card dataset (CPGF), helping auditors prioritize the most impactful cases.

The dashboard helps auditors and analysts:
- Detect unusual spending (“anomalies”).
- Prioritize transactions by financial risk.
- Visualize aggregates by state, agency and time.
- Separate sensitive (classified) transactions.

---

### <i class="fa-solid fa-brain" style="margin-right:8px;"></i> 2. Detection models (Technical Score)
We use an ensemble of anomaly detectors:
- **Isolation Forest** — isolates global outliers.
- **Local Outlier Factor (LOF)** — finds locally low-density points.

The average output of these models forms the **Technical Score** (how statistically unusual a transaction is).

---

### <i class="fa-solid fa-fire" style="margin-right:8px;"></i> 3. Risk Score (Priority Score)
The final prioritization metric combines anomaly strength with financial materiality:

$$
\\text{Risk Score} =
(0.7 \\times \\text{Technical Score}) +
(0.3 \\times \\text{Financial Risk})
$$

- **Technical Score:** average of IF and LOF scores.
- **Financial Risk:** transaction amount.

This prevents low-value anomalies from outranking high-impact transactions.

---

### <i class="fa-solid fa-lock" style="margin-right:8px;"></i> 4. Classified / Sensitive Transactions
Some records are marked **SIGILOSO = 1** (classified). These entries may lack precise date, beneficiary name, or detailed description due to legal restrictions or court orders.

#### Legal Basis
Classification follows **Law 12.527/2011 (LAI)** and complementary decrees. Disclosure may be restricted if it could:
- compromise national defense or international relations;
- endanger lives;
- harm investigations or intelligence work;
- violate privacy.

The dashboard supports filtering: **Only sensitive (Yes)** or **Exclude sensitive (No — default)**.

---

### <i class="fa-solid fa-folder-open" style="margin-right:8px;"></i> 5. Data Sources
- **Dataset:** Federal Corporate Card transactions (CPGF), 2023–present.
- **Source / Download:** CPGF on Portal da Transparência.
- **Data Dictionary:** CPGF Data Dictionary.
- **About the Portal:** https://portaldatransparencia.gov.br/controle-social

---

### <i class="fa-solid fa-compass" style="margin-right:8px;"></i> 6. Note on 'UNIÃO'
When a state's inference is not possible from the unit name, we use **UNIÃO**, plotted as **DF (Brasília)**. This includes federal bodies and military units without explicit state.

---

### <i class="fa-solid fa-circle-exclamation" style="margin-right:8px;"></i> 7. Important Notice
Jacurutu **does not claim fraud**. It flags unusual patterns to guide human audit efforts.

""", unsafe_allow_html=True)


# > ABA DASHBOARD

elif selected == T["menu_items"][1]:

    if df_f.empty:
        st.warning(T["warning_filter_empty"])
        st.stop()

    # --- ANOMALIAS FILTRADAS ---
    if "TECHNICAL_LABEL" in df_f.columns:
        df_anomalias = df_f[df_f["TECHNICAL_LABEL"] == -1]
    else:
        corte_risco = df_f["PRIORITY_SCORE"].quantile(0.90)
        df_anomalias = df_f[df_f["PRIORITY_SCORE"] >= corte_risco]

    # --- KPIs ---
    k1, k2, k3, k4 = st.columns(4)

    # KPI 1: Transações
    k1.metric(T["kpi_trans"], f"{len(df_f):,}")

    # KPI 2: Valor Total
    k2.metric(T["kpi_valor"], f"R$ {df_f['VALOR TRANSAÇÃO'].sum():,.2f}")

    # KPI 3: Valor das Anomalias
    total_anomalo = df_anomalias['VALOR TRANSAÇÃO'].sum()
    k3.metric(T["kpi_anom_valor"], f"R$ {total_anomalo:,.2f}")

    # KPI 4: Estado Principal
    top_state = df_f["ESTADO_ESTIMADO"].mode()[0] if not df_f.empty else "-"
    k4.metric(T["kpi_estado"], top_state)

    st.divider()
    st.info(T["obs_uniao"])

# MAPAS

    # 1. Preparação dos Dados
    with st.spinner("Calculando geolocalização dos gastos..."):
        df_geo = df_f.groupby("ESTADO_ESTIMADO")[["VALOR TRANSAÇÃO", "PRIORITY_SCORE"]].agg(
            VALOR_TOTAL=("VALOR TRANSAÇÃO", "sum"),
            RISCO_MAX=("PRIORITY_SCORE", "max")
        ).reset_index()

        def get_heat_data(df_input, col_peso):
            data = []
            for _, r in df_input.iterrows():
                uf = r["ESTADO_ESTIMADO"]
                w = r[col_peso]
                if uf in COORDS_ESTADOS and w > 0:
                    lat, lon = COORDS_ESTADOS[uf]
                    data.append([lat, lon, np.log1p(w)])
            return data

        heat_anom_data = get_heat_data(df_geo, "RISCO_MAX")
        heat_spend_data = get_heat_data(df_geo, "VALOR_TOTAL")

    # 2. Renderização
    map_id = f"{len(df_f)}_{df_f['VALOR TRANSAÇÃO'].sum()}"

    c1, c2 = st.columns(2)

    # MAPA 1: ANOMALIAS
    with c1:
        st.markdown(
        f"""
        <h3 style="display:flex; align-items:center; gap:6px;">
            {T["map_anom"]}
        </h3>
        """, unsafe_allow_html=True)

        m1 = folium.Map(location=[-15.78, -47.93], zoom_start=3, tiles="CartoDB positron")
        if heat_anom_data:
            HeatMap(heat_anom_data, radius=25, blur=15, gradient={0.4: 'orange', 1: 'red'}).add_to(m1)

        st_folium(m1, height=400, width=None, key=f"mapa_anomalia_{map_id}", returned_objects=[])

    # MAPA 2: GASTOS
    with c2:
        st.markdown(
            f"""
            <h3 style="display:flex; align-items:center; gap:6px;">
                {T["map_spend"]}
            </h3>
            """, unsafe_allow_html=True)

        m2 = folium.Map(location=[-15.78, -47.93], zoom_start=3, tiles="CartoDB positron")
        if heat_spend_data:
            HeatMap(heat_spend_data, radius=25, blur=15, gradient={0.4: 'blue', 1: 'green'}).add_to(m2)

        st_folium(m2, height=400, width=None, key=f"mapa_gastos_{map_id}", returned_objects=[])


    # GRÁFICO TEMPORAL
    st.markdown(f"### {T['chart_time']}", unsafe_allow_html=True)

    df_f["MES"] = df_f["DATA TRANSAÇÃO"].dt.to_period("M").astype(str)

    if "TECHNICAL_LABEL" in df_f.columns:
            df_anom_chart = df_f[df_f["TECHNICAL_LABEL"] == -1]
    else:
            corte_risco = df_f["PRIORITY_SCORE"].quantile(0.90)
            df_anom_chart = df_f[df_f["PRIORITY_SCORE"] >= corte_risco]

    total_by_month = df_f.groupby("MES")["VALOR TRANSAÇÃO"].sum().reset_index().rename(columns={"VALOR TRANSAÇÃO":"TOTAL"})
    anom_by_month = df_anom_chart.groupby("MES")["VALOR TRANSAÇÃO"].sum().reset_index().rename(columns={"VALOR TRANSAÇÃO":"ANOMALIA"})

    time_df = pd.merge(total_by_month, anom_by_month, on="MES", how="left").fillna(0)
    time_df = time_df.sort_values("MES")

    fig_time = px.line(
        time_df,
        x="MES",
        y=["TOTAL", "ANOMALIA"],
        markers=True,
        labels={"value": "R$", "MES": "Mês"},
        color_discrete_map={"TOTAL": "#2DD4BF", "ANOMALIA": "#EF4444"},
        template="plotly_dark"
    )
    fig_time.update_layout(height=400, xaxis_title="Mês", legend_title="", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_time, use_container_width=True)

    #  SCATTER PLOT
    st.subheader(T["scatter"])
    df_scat = df_f.sample(min(2000, len(df_f)))
    fig_sc = px.scatter(
        df_scat, x="VALOR TRANSAÇÃO", y="PRIORITY_PCT",
        color="NOME ÓRGÃO SUPERIOR", size="VALOR TRANSAÇÃO",
        hover_data=["NOME FAVORECIDO", "ESTADO_ESTIMADO", "PRIORITY_SCORE"],
        color_continuous_scale="Tealgrn",
        template="plotly_dark",
        labels={"PRIORITY_PCT": T["col_priority"], "VALOR TRANSAÇÃO": "Valor da Transação" if lang=="pt" else "Transaction Value"}
    )
    fig_sc.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_sc, use_container_width=True)

    # --- TABELA TOP 100 ---
    st.divider()
    st.subheader(T["table"])
    cols_show = ["DATA TRANSAÇÃO", "NOME ÓRGÃO", "NOME FAVORECIDO", "VALOR TRANSAÇÃO", "TRANSAÇÃO", "PRIORITY_PCT", "ESTADO_ESTIMADO"]
    cols_exist = [c for c in cols_show if c in df_f.columns]

    df_top = df_f.sort_values("PRIORITY_SCORE", ascending=False).head(100)[cols_exist].copy()
    df_top = df_top.rename(columns={"PRIORITY_PCT": T["col_priority"]})

    st.dataframe(
        df_top.style.format({
            "VALOR TRANSAÇÃO": "R$ {:,.2f}",
            T["col_priority"]: "{:.1f}%"
        }),
        use_container_width=True
    )

# --- EXPORT ---
    st.divider()
    st.markdown(f"""<h3><i class="fa-solid fa-download" style="margin-right:8px;"></i> {T['export_title']}</h3>""", unsafe_allow_html=True)

    cols_export = [
    "CÓDIGO ÓRGÃO SUPERIOR",
    "NOME ÓRGÃO SUPERIOR",
    "CÓDIGO ÓRGÃO","NOME ÓRGÃO",
    "CÓDIGO UNIDADE GESTORA",
    "NOME UNIDADE GESTORA",
    "ANO EXTRATO",
    "MÊS EXTRATO",
    "CNPJ OU CPF FAVORECIDO",
    "NOME FAVORECIDO",
    "TRANSAÇÃO",
    "DATA TRANSAÇÃO",
    "VALOR TRANSAÇÃO",
    "ESTADO_ESTIMADO",
    "SIGILOSO",
    "PRIORITY_SCORE",
    "PRIORITY_PCT",
    "TECHNICAL_LABEL"
    ]
    cols_final = [c for c in cols_export if c in df_f.columns]

    col_xlsx, col_csv = st.columns(2)

    with col_xlsx:
        st.markdown("""<p><i class="fa-solid fa-file-excel"></i> Excel (.xlsx)</p>""", unsafe_allow_html=True)
        st.caption(T["excel_cap"])

        limit_excel = 5000
        buffer_xlsx = io.BytesIO()

        with pd.ExcelWriter(buffer_xlsx, engine='openpyxl') as writer:
            df_f[cols_final].head(limit_excel).to_excel(writer, index=False)

        st.download_button(
            label=f"{T['excel_btn']} {limit_excel} (Excel)",
            data=buffer_xlsx.getvalue(),
            file_name='jacurutu_top_risco.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            help=T["excel_help"].format(limit_excel)
        )

    with col_csv:
        st.markdown("""<p><i class="fa-solid fa-file-csv"></i> CSV (.csv)</p>""", unsafe_allow_html=True)
        st.caption(T["csv_cap"])

        csv_data = df_f[cols_final].to_csv(index=False).encode('utf-8')

        st.download_button(
            label=f"{T['csv_btn']} ({len(df_f)} {T['rows_label']})",
            data=csv_data,
            file_name="jacurutu_completo.csv",
            mime="text/csv",
            help=T["csv_help"]
        )

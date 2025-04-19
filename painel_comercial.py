
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Painel Comercial", layout="wide")

# Carregamento dos dados
@st.cache_data
def carregar_dados():
    return pd.read_csv("leads.csv")

df = carregar_dados()

# Conversão de datas
df["data_lead"] = pd.to_datetime(df["data_lead"])
df["data_venda"] = pd.to_datetime(df["data_venda"], errors='coerce')

# Filtros principais
data_hoje = datetime.today().date()
df_hoje = df[df["data_lead"].dt.date == data_hoje]

# Cálculos
leads_hoje = len(df_hoje)
total_leads = len(df)

vendas_hoje = len(df[df["data_venda"].dt.date == data_hoje])
total_vendas = df["status"].str.lower().eq("vendido").sum()

vendas_por_cidade = df[df["status"].str.lower() == "vendido"].groupby("cidade")["id"].count()

atendimentos_por_atendente = df_hoje.groupby("atendente")["id"].count()

# Ticket médio
ticket_medio = df[df["status"].str.lower() == "vendido"]["valor"].mean()

# Tempo médio de fechamento
df_vendas = df[df["status"].str.lower() == "vendido"].copy()
df_vendas["tempo_fechamento"] = (df_vendas["data_venda"] - df_vendas["data_lead"]).dt.days
tempo_medio_fechamento = df_vendas["tempo_fechamento"].mean()

# Dashboard
st.title("Painel de Métricas Comerciais")

col1, col2, col3 = st.columns(3)
col1.metric("Leads gerados hoje", leads_hoje)
col2.metric("Total de Leads", total_leads)
col3.metric("Total de Vendas", total_vendas)

col4, col5, col6 = st.columns(3)
col4.metric("Vendas hoje", vendas_hoje)
col5.metric("Ticket Médio", f"R$ {ticket_medio:.2f}")
col6.metric("Tempo médio de fechamento", f"{tempo_medio_fechamento:.1f} dias")

st.subheader("Vendas por cidade")
st.bar_chart(vendas_por_cidade)

st.subheader("Atendimentos do dia por atendente")
st.bar_chart(atendimentos_por_atendente)

st.divider()

# Edição de Lead
st.subheader("Edição de Leads")
lead_selecionado = st.selectbox("Selecionar Lead", df["id"])
lead = df[df["id"] == lead_selecionado].iloc[0]

novo_atendente = st.selectbox("Atribuir novo Atendente", df["atendente"].unique())
if st.button("Atualizar Atendente"):
    df.loc[df["id"] == lead_selecionado, "atendente"] = novo_atendente
    st.success("Atendente atualizado!")

# Qualidade do lead
qualidade = st.radio("Classifique o lead", ["Quente", "Morno", "Frio"])
if st.button("Salvar Qualidade"):
    df.loc[df["id"] == lead_selecionado, "qualidade"] = qualidade
    st.success("Qualidade atualizada!")

# Follow-ups do dia
st.subheader("Follow-ups do dia")
followups_hoje = df[df["followup_data"].fillna("1900-01-01").apply(lambda x: pd.to_datetime(x).date() == data_hoje)]
st.write(f"Quantidade de follow-ups hoje: {len(followups_hoje)}")

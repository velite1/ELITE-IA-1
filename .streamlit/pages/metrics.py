import streamlit as st
import pandas as pd
from utils.auth import usuario_atual
from utils.database import carregar_leads

def pagina_metricas():
    usuario = usuario_atual()
    if not usuario:
        st.warning("Faça login para acessar essa página.")
        return

    st.title("📊 Métricas Comerciais")

    df = carregar_leads()

    if usuario["nivel"] == "atendente":
        df = df[df["Responsável"] == usuario["nome"]]

    total_leads = len(df)
    leads_por_origem = df["Origem"].value_counts()
    leads_por_responsavel = df["Responsável"].value_counts()

    col1, col2 = st.columns(2)
    col1.metric("Total de Leads", total_leads)
    col2.metric("Origens Únicas", df["Origem"].nunique())

    st.subheader("📌 Leads por Origem")
    st.bar_chart(leads_por_origem)

    if usuario["nivel"] == "supervisor":
        st.subheader("👥 Leads por Responsável")
        st.bar_chart(leads_por_responsavel)

pagina_metricas()

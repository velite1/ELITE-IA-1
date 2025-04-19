import pandas as pd
import streamlit as st
from datetime import datetime, date
import os

st.set_page_config(page_title="Painel Comercial Avançado", layout="wide")

# Função para carregar dados
def carregar_dados():
    if os.path.exists("leads.csv"):
        return pd.read_csv("leads.csv")
    else:
        return pd.DataFrame(columns=["id", "nome", "numero", "cidade", "status", "valor", "data_lead", "data_venda", "atendente", "qualidade", "followup_data"])

# Salvar dados
@st.cache_data(experimental_allow_widgets=True)
def salvar_dados(df):
    df.to_csv("leads.csv", index=False)

# Carregando e preparando dados
df = carregar_dados()
df["data_lead"] = pd.to_datetime(df["data_lead"], errors='coerce')
df["data_venda"] = pd.to_datetime(df["data_venda"], errors='coerce')

# Sidebar - Login simples
st.sidebar.title("Login")
usuario = st.sidebar.text_input("Usuário")
senha = st.sidebar.text_input("Senha", type="password")
botao_login = st.sidebar.button("Entrar")

usuarios = {
    "atendente1": {"senha": "123", "tipo": "atendente"},
    "supervisor": {"senha": "admin", "tipo": "supervisor"}
}

if botao_login and usuario in usuarios and senha == usuarios[usuario]["senha"]:
    tipo_usuario = usuarios[usuario]["tipo"]

    aba = st.sidebar.radio("Menu", ["Dashboard", "Novo Lead", "Follow-ups", "Configurações"] if tipo_usuario == "supervisor" else ["Dashboard", "Novo Lead", "Follow-ups"])

    if aba == "Dashboard":
        st.title("Painel de Métricas Comerciais")

        data_hoje = date.today()
        df_hoje = df[df["data_lead"].dt.date == data_hoje]

        leads_hoje = len(df_hoje)
        total_leads = len(df)
        vendas_hoje = len(df[df["data_venda"].dt.date == data_hoje])
        total_vendas = df["status"].str.lower().eq("vendido").sum()
        ticket_medio = df[df["status"].str.lower() == "vendido"]["valor"].mean()

        df_vendas = df[df["status"].str.lower() == "vendido"].copy()
        df_vendas["tempo_fechamento"] = (df_vendas["data_venda"] - df_vendas["data_lead"]).dt.days
        tempo_medio_fechamento = df_vendas["tempo_fechamento"].mean()

        vendas_por_cidade = df_vendas.groupby("cidade")["id"].count()
        atendimentos_por_atendente = df_hoje.groupby("atendente")["id"].count()

        col1, col2, col3 = st.columns(3)
        col1.metric("Leads gerados hoje", leads_hoje)
        col2.metric("Total de Leads", total_leads)
        col3.metric("Total de Vendas", total_vendas)

        col4, col5, col6 = st.columns(3)
        col4.metric("Vendas hoje", vendas_hoje)
        col5.metric("Ticket Médio", f"R$ {ticket_medio:.2f}" if not pd.isna(ticket_medio) else "-")
        col6.metric("Tempo médio de fechamento", f"{tempo_medio_fechamento:.1f} dias" if not pd.isna(tempo_medio_fechamento) else "-")

        st.subheader("Vendas por cidade")
        st.bar_chart(vendas_por_cidade)

        st.subheader("Atendimentos do dia por atendente")
        st.bar_chart(atendimentos_por_atendente)

    elif aba == "Novo Lead":
        st.title("Cadastrar Novo Lead")
        with st.form("form_lead"):
            nome = st.text_input("Nome")
            numero = st.text_input("Telefone")
            cidade = st.text_input("Cidade")
            status = st.selectbox("Status", ["vendido", "em negociação", "perdido"])
            valor = st.number_input("Valor", min_value=0.0, step=10.0)
            atendente = st.selectbox("Atendente", df["atendente"].unique() if not df.empty else [usuario])
            qualidade = st.selectbox("Qualidade", ["Quente", "Morno", "Frio"])
            followup = st.date_input("Data de Follow-up")
            submitted = st.form_submit_button("Salvar Lead")

            if submitted:
                novo_lead = {
                    "id": df["id"].max() + 1 if not df.empty else 1,
                    "nome": nome,
                    "numero": numero,
                    "cidade": cidade,
                    "status": status,
                    "valor": valor,
                    "data_lead": datetime.today().strftime("%Y-%m-%d"),
                    "data_venda": datetime.today().strftime("%Y-%m-%d") if status == "vendido" else "",
                    "atendente": atendente,
                    "qualidade": qualidade,
                    "followup_data": followup.strftime("%Y-%m-%d")
                }
                df = pd.concat([df, pd.DataFrame([novo_lead])], ignore_index=True)
                salvar_dados(df)
                st.success("Lead cadastrado com sucesso!")

    elif aba == "Follow-ups":
        st.title("Follow-ups do dia")
        hoje = date.today()
        followups = df[df["followup_data"].fillna("1900-01-01").apply(lambda x: pd.to_datetime(x).date() == hoje)]
        st.write(f"Quantidade de follow-ups hoje: {len(followups)}")
        st.dataframe(followups)

    elif aba == "Configurações" and tipo_usuario == "supervisor":
        st.title("Configurações de Atendentes")
        novo_nome = st.text_input("Novo Atendente")
        if st.button("Adicionar Atendente") and novo_nome:
            if novo_nome not in df["atendente"].unique():
                df = pd.concat([df, pd.DataFrame([{**{col: "" for col in df.columns}, "atendente": novo_nome}])], ignore_index=True)
                salvar_dados(df)
                st.success("Atendente adicionado!")
            else:
                st.warning("Atendente já existe.")

else:
    st.warning("Por favor, faça login para acessar o sistema.")


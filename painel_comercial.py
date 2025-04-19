import pandas as pd
import streamlit as st
from datetime import datetime, date
import os

# Funções auxiliares
def carregar_arquivo(nome_arquivo, colunas):
    return pd.read_csv(nome_arquivo) if os.path.exists(nome_arquivo) else pd.DataFrame(columns=colunas)

def salvar_arquivo(df, nome_arquivo):
    df.to_csv(nome_arquivo, index=False)

# Carregar dados
df_leads = carregar_arquivo("leads.csv", ["id", "nome", "numero", "cidade", "status", "valor", "data_lead", "data_venda", "atendente", "qualidade", "followup_data"])
df_cidades = carregar_arquivo("cidades.csv", ["cidade"])
df_usuarios = {
    "admin": {"senha": "admin123", "tipo": "supervisor"},
    "atendente1": {"senha": "123", "tipo": "atendente"},
}

# Configuração de tema
tema = st.sidebar.radio("Selecione o Tema", ["Padrão", "Verde", "Dourado", "Branco"])
cores = {
    "Verde": "#28a745", "Dourado": "#ffd700", "Branco": "white"
}
st.markdown(f"<style>.css-1v3fvcr {{ background-color: {cores.get(tema, 'white')} }}</style>", unsafe_allow_html=True)

# Função de login
usuario = st.sidebar.text_input("Usuário")
senha = st.sidebar.text_input("Senha", type="password")
if st.sidebar.button("Entrar"):
    if usuario in df_usuarios and senha == df_usuarios[usuario]["senha"]:
        tipo_usuario = df_usuarios[usuario]["tipo"]
        abas = ["Dashboard", "Novo Lead", "Follow-ups"]
        if tipo_usuario == "supervisor":
            abas.append("Configurações")
        aba = st.sidebar.radio("Menu", abas)

        # Dashboard
        if aba == "Dashboard":
            st.title("Painel Comercial")
            hoje = date.today()
            leads_hoje = len(df_leads[df_leads["data_lead"].dt.date == hoje])
            vendas_hoje = len(df_leads[df_leads["data_venda"].dt.date == hoje])
            st.metric("Leads Hoje", leads_hoje)
            st.metric("Vendas Hoje", vendas_hoje)

        # Novo Lead
        elif aba == "Novo Lead":
            st.title("Cadastrar Novo Lead")
            with st.form("form_lead"):
                nome = st.text_input("Nome")
                numero = st.text_input("Telefone")
                cidade = st.selectbox("Cidade", df_cidades["cidade"].unique())
                status = st.selectbox("Status", ["vendido", "em negociação", "perdido", "pendente", "cancelado", "em análise", "aguardando pagamento", "em processo", "recusado", "não interessado"])
                valor = st.number_input("Valor", min_value=0.0, step=10.0)
                atendente = st.selectbox("Atendente", df_leads["atendente"].unique() if not df_leads.empty else [usuario])
                qualidade = st.selectbox("Qualidade", ["Quente", "Morno", "Frio"])
                followup = st.date_input("Data de Follow-up")
                submitted = st.form_submit_button("Salvar Lead")

                if submitted:
                    novo_lead = {
                        "id": df_leads["id"].max() + 1 if not df_leads.empty else 1,
                        "nome": nome, "numero": numero, "cidade": cidade, "status": status, "valor": valor,
                        "data_lead": datetime.today().strftime("%Y-%m-%d"), "data_venda": "", "atendente": atendente,
                        "qualidade": qualidade, "followup_data": followup.strftime("%Y-%m-%d")
                    }
                    df_leads = pd.concat([df_leads, pd.DataFrame([novo_lead])], ignore_index=True)
                    salvar_arquivo(df_leads, "leads.csv")
                    st.success("Lead cadastrado com sucesso!")

        # Follow-ups
        elif aba == "Follow-ups":
            st.title("Follow-ups do Dia")
            hoje = date.today()
            followups = df_leads[df_leads["followup_data"].fillna("1900-01-01").apply(lambda x: pd.to_datetime(x).date() == hoje)]
            st.write(f"Quantidade de follow-ups hoje: {len(followups)}")
            st.dataframe(followups)

        # Configurações - Supervisor
        elif aba == "Configurações" and tipo_usuario == "supervisor":
            st.title("Configurações")
            st.subheader("Adicionar Cidade")
            nova_cidade = st.text_input("Nova Cidade")
            if st.button("Adicionar Cidade") and nova_cidade:
                if nova_cidade not in df_cidades["cidade"].unique():
                    df_cidades = pd.concat([df_cidades, pd.DataFrame([{"cidade": nova_cidade}])], ignore_index=True)
                    salvar_arquivo(df_cidades, "cidades.csv")
                    st.success("Cidade adicionada com sucesso!")
                else:
                    st.warning("Cidade já existe.")
    else:
        st.warning("Credenciais incorretas.")
else:
    st.warning("Por favor, faça login para acessar o sistema.")

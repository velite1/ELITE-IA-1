import streamlit as st
from utils.auth import usuario_atual
from utils.database import carregar_leads, adicionar_lead

def pagina_leads():
    usuario = usuario_atual()
    if not usuario:
        st.warning("Faça login para acessar essa página.")
        return

    st.title("📋 Gestão de Leads")

    # Formulário para adicionar novo lead
    with st.expander("➕ Adicionar Novo Lead"):
        with st.form("form_lead"):
            nome = st.text_input("Nome do lead")
            telefone = st.text_input("Telefone")
            origem = st.selectbox("Origem do lead", ["Instagram", "Facebook", "Google", "Indicação", "Outro"])
            submitted = st.form_submit_button("Cadastrar")

            if submitted:
                if nome and telefone:
                    adicionar_lead(nome, telefone, origem, usuario["nome"])
                    st.success("Lead cadastrado com sucesso!")
                else:
                    st.error("Preencha todos os campos obrigatórios.")

    # Visualização dos leads
    df = carregar_leads()

    if usuario["nivel"] == "atendente":
        df = df[df["Responsável"] == usuario["nome"]]

    st.subheader("📑 Leads Cadastrados")
    st.dataframe(df, use_container_width=True)

pagina_leads()

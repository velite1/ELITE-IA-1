import streamlit as st

# Usuários e senhas fictícias (você pode ligar isso a um CSV ou banco real depois)
USERS = {
    "supervisor": {"senha": "1234", "nivel": "supervisor"},
    "atendente1": {"senha": "abcd", "nivel": "atendente"},
}

def autenticar_usuario():
    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if st.session_state.usuario:
        return True

    with st.form("login_form"):
        st.subheader("🔐 Login")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if usuario in USERS and USERS[usuario]["senha"] == senha:
                st.session_state.usuario = {
                    "nome": usuario,
                    "nivel": USERS[usuario]["nivel"]
                }
                st.success(f"Bem-vindo, {usuario}!")
                return True
            else:
                st.error("Usuário ou senha incorretos.")
    return False

def usuario_atual():
    return st.session_state.get("usuario")

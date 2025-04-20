"""
Painel Tráfego - 2025
Aplicação para gerenciamento de leads e vendas com interface Streamlit
Adaptado para refletir a estrutura da planilha de acompanhamento
"""

import pandas as pd
import streamlit as st
from datetime import datetime, date
import os

# Configuração da página
st.set_page_config(page_title="Painel Tráfego - 2025", layout="wide")

# Função para carregar dados de leads
def carregar_dados():
    """Carrega dados do arquivo CSV ou cria um DataFrame vazio se não existir"""
    if os.path.exists("leads_trafego.csv"):
        return pd.read_csv("leads_trafego.csv")
    else:
        return pd.DataFrame(columns=["id", "data", "nome", "telefone", "produto", "canal_vendas", "vendedor", "status", "valor", "data_venda", "qualidade", "followup_data"])

# Função para salvar dados de leads
def salvar_dados(df):
    """Salva o DataFrame no arquivo CSV"""
    df.to_csv("leads_trafego.csv", index=False)

# Função para carregar dados de cidades
def carregar_cidades():
    """Carrega dados de cidades do arquivo CSV ou cria um DataFrame vazio se não existir"""
    if os.path.exists("cidades.csv"):
        return pd.read_csv("cidades.csv")
    else:
        return pd.DataFrame(columns=["cidade"])

# Função para salvar cidades
def salvar_cidades(df):
    """Salva o DataFrame de cidades no arquivo CSV"""
    df.to_csv("cidades.csv", index=False)

# Carregando e preparando dados
df = carregar_dados()
df["data"] = pd.to_datetime(df["data"], errors='coerce')
df["data_venda"] = pd.to_datetime(df["data_venda"], errors='coerce')
df_cidades = carregar_cidades()

# Sidebar - Login simples
st.sidebar.title("Login Tráfego")
usuario = st.sidebar.text_input("Usuário")
senha = st.sidebar.text_input("Senha", type="password")
botao_login = st.sidebar.button("Entrar")

# Usuários do sistema
usuarios = {
    "admin": {"senha": "admin123", "tipo": "supervisor"},  # Usuário master
    "victor": {"senha": "victor123", "tipo": "vendedor"},
    "stayce": {"senha": "stayce123", "tipo": "vendedor"},
    "supervisor": {"senha": "admin", "tipo": "supervisor"}
}

# Seleção de tema
tema = st.sidebar.radio("Selecione o Tema", ["Padrão", "Verde", "Azul", "Branco"])

# Aplicação de temas
if tema == "Verde":
    st.markdown(
        """
        <style>
        .css-1v3fvcr {
            background-color: #28a745;
        }
        </style>
        """, unsafe_allow_html=True)
elif tema == "Azul":
    st.markdown(
        """
        <style>
        .css-1v3fvcr {
            background-color: #007bff;
        }
        </style>
        """, unsafe_allow_html=True)
elif tema == "Branco":
    st.markdown(
        """
        <style>
        .css-1v3fvcr {
            background-color: white;
        }
        </style>
        """, unsafe_allow_html=True)

# Verificação de login
if botao_login and usuario in usuarios and senha == usuarios[usuario]["senha"]:
    tipo_usuario = usuarios[usuario]["tipo"]

    # Menu de navegação
    abas_disponiveis = ["Dashboard", "Novo Lead", "Follow-ups", "Relatórios", "Configurações"]
    if tipo_usuario == "supervisor":
        abas_disponiveis.append("Gestão de Usuários")

    aba = st.sidebar.radio("Menu", abas_disponiveis)

    # Dashboard principal
    if aba == "Dashboard":
        st.title("Painel de Métricas Tráfego - 2025")

        # Cálculo de métricas
        data_hoje = date.today()
        df_hoje = df[df["data"].dt.date == data_hoje]

        leads_hoje = len(df_hoje)
        total_leads = len(df)
        vendas_hoje = len(df[df["data_venda"].dt.date == data_hoje])
        total_vendas = df["status"].str.lower().eq("vendido").sum()
        ticket_medio = df[df["status"].str.lower() == "vendido"]["valor"].mean() if "valor" in df.columns else 0

        # Cálculo de tempo médio de fechamento
        df_vendas = df[df["status"].str.lower() == "vendido"].copy()
        if not df_vendas.empty and "data" in df_vendas.columns and "data_venda" in df_vendas.columns:
            df_vendas["tempo_fechamento"] = (df_vendas["data_venda"] - df_vendas["data"]).dt.days
            tempo_medio_fechamento = df_vendas["tempo_fechamento"].mean()
        else:
            tempo_medio_fechamento = 0

        # Agrupamentos para gráficos
        if not df_vendas.empty:
            if "cidade" in df_vendas.columns:
                vendas_por_cidade = df_vendas.groupby("cidade")["id"].count()
            else:
                vendas_por_cidade = pd.Series(dtype=int)
            
            if "vendedor" in df_vendas.columns:
                vendas_por_vendedor = df_vendas.groupby("vendedor")["id"].count()
            else:
                vendas_por_vendedor = pd.Series(dtype=int)
        else:
            vendas_por_cidade = pd.Series(dtype=int)
            vendas_por_vendedor = pd.Series(dtype=int)

        # Exibição de métricas
        col1, col2, col3 = st.columns(3)
        col1.metric("Leads gerados hoje", leads_hoje)
        col2.metric("Total de Leads", total_leads)
        col3.metric("Total de Vendas", total_vendas)

        col4, col5, col6 = st.columns(3)
        col4.metric("Vendas hoje", vendas_hoje)
        col5.metric("Ticket Médio", f"R$ {ticket_medio:.2f}" if not pd.isna(ticket_medio) and ticket_medio > 0 else "-")
        col6.metric("Tempo médio de fechamento", f"{tempo_medio_fechamento:.1f} dias" if not pd.isna(tempo_medio_fechamento) and tempo_medio_fechamento > 0 else "-")

        # Gráficos
        st.subheader("Vendas por cidade")
        if not vendas_por_cidade.empty:
            st.bar_chart(vendas_por_cidade)
        else:
            st.info("Sem dados para exibir")

        st.subheader("Vendas por vendedor")
        if not vendas_por_vendedor.empty:
            st.bar_chart(vendas_por_vendedor)
        else:
            st.info("Sem dados para exibir")

        # Tabela de leads recentes
        st.subheader("Leads recentes")
        if not df.empty:
            st.dataframe(df.sort_values("data", ascending=False).head(10))

    # Cadastro de novos leads
    elif aba == "Novo Lead":
        st.title("Cadastrar Novo Lead")
        with st.form("form_lead"):
            data_atual = date.today().strftime("%d/%m/%Y")
            data = st.date_input("Data", value=date.today())
            nome = st.text_input("Nome")
            telefone = st.text_input("Telefone")
            produto = st.selectbox("Produto", ["NOVA INSTALAÇÃO", "UPGRADE", "RENOVAÇÃO"])
            canal_vendas = st.selectbox("Canal de Vendas", ["TRÁFEGO PAGO", "INDICAÇÃO", "SITE", "REDES SOCIAIS"])
            vendedor = st.selectbox("Vendedor", ["VICTOR", "STAYCE"] if not df.empty and "vendedor" in df.columns else ["VICTOR", "STAYCE"])
            status = st.selectbox("Status", ["VENDIDO", "EM NEGOCIAÇÃO", "PERDIDO", "PENDENTE", "INVIABILIDADE", "EM ANÁLISE"])
            valor = st.number_input("Valor", min_value=0.0, step=10.0)
            qualidade = st.selectbox("Qualidade", ["Quente", "Morno", "Frio"])
            followup = st.date_input("Data de Follow-up")
            submitted = st.form_submit_button("Salvar Lead")

            if submitted:
                novo_lead = {
                    "id": df["id"].max() + 1 if not df.empty and "id" in df.columns else 1,
                    "data": data.strftime("%Y-%m-%d"),
                    "nome": nome,
                    "telefone": telefone,
                    "produto": produto,
                    "canal_vendas": canal_vendas,
                    "vendedor": vendedor,
                    "status": status,
                    "valor": valor,
                    "data_venda": date.today().strftime("%Y-%m-%d") if status == "VENDIDO" else "",
                    "qualidade": qualidade,
                    "followup_data": followup.strftime("%Y-%m-%d")
                }
                df = pd.concat([df, pd.DataFrame([novo_lead])], ignore_index=True)
                salvar_dados(df)
                st.success("Lead cadastrado com sucesso!")

    # Acompanhamento de follow-ups
    elif aba == "Follow-ups":
        st.title("Follow-ups do dia")
        hoje = date.today()
        
        if "followup_data" in df.columns:
            followups = df[df["followup_data"].fillna("1900-01-01").apply(lambda x: pd.to_datetime(x).date() == hoje)]
            st.write(f"Quantidade de follow-ups hoje: {len(followups)}")
            if not followups.empty:
                st.dataframe(followups)
            else:
                st.info("Não há follow-ups agendados para hoje")
        else:
            st.warning("Dados de follow-up não encontrados")

    # Relatórios
    elif aba == "Relatórios":
        st.title("Relatórios de Vendas")
        
        periodo = st.selectbox("Selecione o período", ["Hoje", "Esta semana", "Este mês", "Todo o período"])
        
        if periodo == "Hoje":
            df_filtrado = df[df["data"].dt.date == date.today()]
        elif periodo == "Esta semana":
            hoje = date.today()
            inicio_semana = hoje - pd.Timedelta(days=hoje.weekday())
            df_filtrado = df[df["data"].dt.date >= inicio_semana]
        elif periodo == "Este mês":
            hoje = date.today()
            df_filtrado = df[df["data"].dt.month == hoje.month]
        else:
            df_filtrado = df
            
        if not df_filtrado.empty:
            st.subheader(f"Leads no período: {len(df_filtrado)}")
            vendas_periodo = df_filtrado[df_filtrado["status"].str.lower() == "vendido"]
            st.subheader(f"Vendas no período: {len(vendas_periodo)}")
            
            if "vendedor" in df_filtrado.columns:
                st.subheader("Desempenho por vendedor")
                desempenho = df_filtrado.groupby("vendedor")["status"].apply(lambda x: (x.str.lower() == "vendido").sum()).reset_index()
                desempenho.columns = ["Vendedor", "Vendas"]
                st.dataframe(desempenho)
            
            st.subheader("Dados completos do período")
            st.dataframe(df_filtrado)
        else:
            st.info("Sem dados para o período selecionado")

    # Configurações
    elif aba == "Configurações":
        st.title("Configurações do Sistema")
        
        st.subheader("Adicionar nova cidade")
        nova_cidade = st.text_input("Nova Cidade")
        if st.button("Adicionar Cidade") and nova_cidade:
            if nova_cidade not in df_cidades["cidade"].unique():
                df_cidades = pd.concat([df_cidades, pd.DataFrame([{"cidade": nova_cidade}])], ignore_index=True)
                salvar_cidades(df_cidades)
                st.success("Cidade adicionada com sucesso!")
            else:
                st.warning("Cidade já existe.")
        
        st.subheader("Exportar dados")
        if st.button("Exportar para Excel"):
            if not df.empty:
                df.to_excel("leads_trafego_export.xlsx", index=False)
                st.success("Dados exportados com sucesso!")
                st.download_button(
                    label="Baixar arquivo Excel",
                    data=open("leads_trafego_export.xlsx", "rb").read(),
                    file_name="leads_trafego_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("Não há dados para exportar")
                
    # Gestão de usuários (apenas para supervisores)
    elif aba == "Gestão de Usuários" and tipo_usuario == "supervisor":
        st.title("Gestão de Usuários do Sistema")
        
        st.subheader("Adicionar novo usuário")
        novo_nome = st.text_input("Nome do usuário")
        novo_tipo = st.selectbox("Tipo de usuário", ["vendedor", "supervisor"])
        nova_senha = st.text_input("Senha inicial", type="password")
        foto = st.file_uploader("Foto do usuário", type=["jpg", "png", "jpeg"])
        
        if st.button("Adicionar Usuário") and novo_nome and nova_senha:
            usuarios[novo_nome] = {"senha": nova_senha, "tipo": novo_tipo}
            st.success(f"Usuário {novo_nome} adicionado com sucesso!")
        
        st.subheader("Usuários atuais")
        usuarios_df = pd.DataFrame([
            {"Usuário": user, "Tipo": data["tipo"]} 
            for user, data in usuarios.items()
        ])
        st.dataframe(usuarios_df)

# Mensagem de login
else:
    st.title("Painel Tráfego - 2025")
    st.warning("Por favor, faça login para acessar o sistema.\n\nLogin master:\nUsuário: admin\nSenha: admin123")
    
    # Imagem de boas-vindas
    st.image("https://via.placeholder.com/800x400?text=Bem-vindo+ao+Painel+Trafego+2025", use_column_width=True)


abas_disponiveis = ["Dashboard", "Novo Lead", "Follow-ups", "Configurações"]
if tipo_usuario == "supervisor":
    abas_disponiveis.append("Gestão de Logins")

aba = st.sidebar.radio("Menu", abas_disponiveis)

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
        cidade = st.selectbox("Cidade", df_cidades["cidade"].unique())
        status = st.selectbox("Status", ["vendido", "em negociação", "perdido", "pendente", "cancelado", "em análise", "aguardando pagamento", "em processo", "recusado", "não interessado"])
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

elif aba == "Configurações":
    st.title("Configurações de Atendentes e Cidades")
    st.subheader("Alterar ou adicionar cidade")
    nova_cidade = st.text_input("Nova Cidade")
    if st.button("Adicionar Cidade") and nova_cidade:
        if nova_cidade not in df_cidades["cidade"].unique():
            df_cidades = pd.concat([df_cidades, pd.DataFrame([{"cidade": nova_cidade}])], ignore_index=True)
            salvar_cidades(df_cidades)
            st.success("Cidade adicionada com sucesso!")
        else:
            st.warning("Cidade já existe.")
            
elif aba == "Gestão de Logins" and tipo_usuario == "supervisor":
    st.title("Gestão de Logins de Usuários")
    novo_nome = st.text_input("Novo Usuário")
    novo_email = st.text_input("E-mail do Usuário")
    foto = st.file_uploader("Foto do Atendente", type=["jpg", "png", "jpeg"])
    if st.button("Adicionar Usuário") and novo_nome and novo_email:
        usuarios[novo_nome] = {"senha": "senha123", "tipo": "atendente"}
        st.success("Usuário adicionado com sucesso!")

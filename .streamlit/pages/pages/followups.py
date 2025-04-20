import streamlit as st
import pandas as pd
from datetime import datetime

# Função para carregar dados de follow-ups (pode ser substituída por banco de dados ou API)
def load_followups():
    # Exemplo de dados fictícios
    data = {
        'lead_id': [1, 2, 3, 4],
        'nome': ['João Silva', 'Maria Oliveira', 'Carlos Souza', 'Ana Santos'],
        'data_followup': [
            '2025-04-18 10:00:00', '2025-04-19 14:30:00', '2025-04-18 15:45:00', '2025-04-20 09:00:00'
        ],
        'status': ['pendente', 'concluído', 'pendente', 'pendente'],
        'comentarios': [
            'Aguardando confirmação de interesse.',
            'Cliente fechou a venda.',
            'Cliente pediu mais informações.',
            'Cliente solicitou novo contato.'
        ]
    }
    df = pd.DataFrame(data)
    df['data_followup'] = pd.to_datetime(df['data_followup'])
    return df

# Função para adicionar um novo follow-up
def add_followup(lead_id, nome, data_followup, comentarios, status='pendente'):
    df = load_followups()
    new_followup = pd.DataFrame({
        'lead_id': [lead_id],
        'nome': [nome],
        'data_followup': [data_followup],
        'status': [status],
        'comentarios': [comentarios]
    })
    df = pd.concat([df, new_followup], ignore_index=True)
    df.to_csv('followups.csv', index=False)  # Salvar no CSV (substitua para salvar no banco)
    st.success('Novo follow-up adicionado com sucesso!')

# Título da página
st.title('Acompanhamento de Follow-ups')

# Carregar os follow-ups
followups_df = load_followups()

# Exibir follow-ups pendentes
st.subheader('Follow-ups Pendentes')
pendentes = followups_df[followups_df['status'] == 'pendente']
st.write(pendentes)

# Exibir follow-ups concluídos
st.subheader('Follow-ups Concluídos')
concluidos = followups_df[followups_df['status'] == 'concluído']
st.write(concluidos)

# Formulário para adicionar um novo follow-up
st.subheader('Adicionar Novo Follow-up')
with st.form(key='followup_form'):
    lead_id = st.number_input('ID do Lead', min_value=1, step=1)
    nome = st.text_input('Nome do Lead')
    data_followup = st.date_input('Data do Follow-up', min_value=datetime.today())
    comentarios = st.text_area('Comentários')
    status = st.selectbox('Status', ['pendente', 'concluído'])
    
    submit_button = st.form_submit_button(label='Adicionar Follow-up')
    
    if submit_button:
        add_followup(lead_id, nome, data_followup, comentarios, status)

# Função para atualizar status de follow-up
st.subheader('Atualizar Status de Follow-up')
lead_id_update = st.number_input('ID do Lead para Atualizar Status', min_value=1, step=1)
novo_status = st.selectbox('Novo Status', ['pendente', 'concluído'])

if st.button('Atualizar Status'):
    followups_df.loc[followups_df['lead_id'] == lead_id_update, 'status'] = novo_status
    st.success(f'Status do follow-up para o Lead {lead_id_update} atualizado para {novo_status}.')

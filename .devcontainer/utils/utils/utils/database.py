import pandas as pd
from datetime import datetime

CSV_PATH = "leads.csv"

def carregar_leads():
    try:
        return pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Nome", "Telefone", "Origem", "Status", "Último Contato", "Responsável"])

def salvar_leads(df):
    df.to_csv(CSV_PATH, index=False)

def adicionar_lead(nome, telefone, origem, responsavel):
    df = carregar_leads()
    novo = {
        "Nome": nome,
        "Telefone": telefone,
        "Origem": origem,
        "Status": "Novo",
        "Último Contato": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Responsável": responsavel
    }
    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
    salvar_leads(df)

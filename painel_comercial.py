import pandas as pd
import streamlit as st
from datetime import datetime, date
import os

# Função para carregar dados
def carregar_dados():
    if os.path.exists("leads.csv"):
        return pd.read_csv("leads.csv")
    else:
        return pd.DataFrame(columns=["id", "nome", "numero", "cidade", "status", "valor", "data_lead", "data_venda", "atendente", "qualidade", "followup_data"])

# Função para salvar dados
def salvar_dados(df):
    df.to_csv("leads.csv", index=False)

# Função para carregar dados de cidades
def carregar_cidades():
    if os.path.exists("cidades.csv"):
        return pd.read_csv("cidades.csv")
    else:
        return pd.DataFrame(columns=["cidade"])

# Função para


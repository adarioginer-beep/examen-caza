import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials

def conectar():
    # Acceso directo al diccionario del secret para evitar errores de escape
    info = st.secrets["gcp_service_account"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url("https://docs.google.com/spreadsheets/d/1K4QP2c4XYH6MLIA61VP6RmHfFUPLUVwsKP3oIZmidys/edit?usp=sharing").sheet1

st.title("🏹 Registro Academia de Caza")

try:
    sheet = conectar()
    # Leemos datos para mostrar que funciona
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    with st.form("reg"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("REGISTRAR"):
            if u in df['usuario'].values:
                st.warning("El usuario ya existe")
            else:
                sheet.append_row([u, p, "", ""])
                st.success("¡CONECTADO! Usuario guardado en el Excel.")
                st.rerun()
    
    st.write("### Base de datos actual:")
    st.dataframe(df)

except Exception as e:
    st.error(f"Error crítico: {e}")

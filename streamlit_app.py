import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials

# --- CONEXIÓN DIRECTA ---
def conectar():
    try:
        # Cargamos la llave desde los Secrets
        info = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(info, 
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        # Tu URL de Google Sheets
        return client.open_by_url("https://docs.google.com/spreadsheets/d/1K4QP2c4XYH6MLIA61VP6RmHfFUPLUVwsKP3oIZmidys/edit?usp=sharing").sheet1
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

# --- INTERFAZ ---
st.title("🏹 Registro Academia de Caza")

try:
    sheet = conectar()
    df = pd.DataFrame(sheet.get_all_records())
    
    with st.form("registro"):
        nuevo_u = st.text_input("Usuario")
        nuevo_p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("REGISTRAR AHORA"):
            nueva_fila = [nuevo_u, nuevo_p, "", ""]
            sheet.append_row(nueva_fila)
            st.success("¡USUARIO CREADO! Mira tu Excel ahora.")
            
    st.write("### Usuarios actuales en el Excel:")
    st.dataframe(df)
except Exception as e:
    st.error(f"Hubo un problema al leer los datos: {e}")

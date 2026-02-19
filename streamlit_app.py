import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials

# --- CONEXIÓN SEGURA ---
def conectar():
    try:
        # Buscamos la llave en los Secrets
        info = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(info, 
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        # Tu URL de Google Sheets
        return client.open_by_url("https://docs.google.com/spreadsheets/d/1K4QP2c4XYH6MLIA61VP6RmHfFUPLUVwsKP3oIZmidys/edit?usp=sharing").sheet1
    except Exception as e:
        st.error(f"Fallo de configuración: {e}")
        st.stop()

def leer_datos():
    sheet = conectar()
    return pd.DataFrame(sheet.get_all_records())

def guardar_datos(df):
    sheet = conectar()
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- INICIO APP ---
st.set_page_config(page_title="Academia de Caza", page_icon="🏹")

# Cargar preguntas
try:
    with open('preguntas.json', 'r', encoding='utf-8') as f:
        preguntas = json.load(f)
except:
    st.error("Falta el archivo preguntas.json en GitHub")
    st.stop()

if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    tab1, tab2 = st.tabs(["Login", "Registro"])
    with tab2:
        u_reg = st.text_input("Usuario")
        p_reg = st.text_input("Pass", type="password")
        if st.button("Crear Cuenta"):
            df = leer_datos()
            if u_reg in df['usuario'].values: st.warning("Ya existe")
            else:
                df = pd.concat([df, pd.DataFrame([{"usuario": u_reg, "password": p_reg, "temas_completados": "", "preguntas_fallidas": ""}])], ignore_index=True)
                guardar_datos(df)
                st.success("¡Listo! Ya puedes loguearte.")
    with tab1:
        u = st.text_input("Tu Usuario")
        p = st.text_input("Tu Pass", type="password")
        if st.button("Entrar"):
            df = leer_datos()
            if not df[(df['usuario'] == u) & (df['password'] == str(p))].empty:
                st.session_state.user = u
                st.rerun()
            else: st.error("Datos incorrectos")
    st.stop()

# --- PANEL DE CONTROL ---
st.title(f"🏹 Bienvenido, {st.session_state.user}")
if st.button("Cerrar Sesión"):
    st.session_state.user = None
    st.rerun()

modo = st.selectbox("Elegir:", ["Practicar Temas", "Examen Oficial (36)", "Mis Errores"])
# (Aquí sigue el resto de la lógica de tests...)

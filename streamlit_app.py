import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials

# --- FUNCIÓN DE CONEXIÓN BLINDADA ---
def conectar_gsheet():
    # Usamos el nombre exacto que pondremos en Secrets
    info = json.loads(st.secrets["gcp_service_account"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    client = gspread.authorize(creds)
    # Tu URL exacta de la hoja
    url = "https://docs.google.com/spreadsheets/d/1K4QP2c4XYH6MLIA61VP6RmHfFUPLUVwsKP3oIZmidys/edit?usp=sharing"
    return client.open_by_url(url).sheet1

def leer_datos():
    sheet = conectar_gsheet()
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def guardar_datos(df):
    sheet = conectar_gsheet()
    # Limpia y actualiza con los nuevos datos
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- INICIO DE LA APP ---
st.set_page_config(page_title="Academia de Caza", page_icon="🏹")

# Cargar el banco de preguntas
try:
    with open('preguntas.json', 'r', encoding='utf-8') as f:
        banco = json.load(f)
except:
    st.error("Error: No se encuentra preguntas.json en GitHub")
    st.stop()

if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("🔐 Acceso")
    t1, t2 = st.tabs(["Entrar", "Registrarse"])
    
    with t2:
        u_reg = st.text_input("Nuevo Usuario")
        p_reg = st.text_input("Nueva Contraseña", type="password")
        if st.button("Crear mi cuenta"):
            df = leer_datos()
            if u_reg in df['usuario'].values:
                st.warning("El usuario ya existe")
            else:
                nueva_fila = pd.DataFrame([{"usuario": u_reg, "password": p_reg, "temas_completados": "", "preguntas_fallidas": ""}])
                df = pd.concat([df, nueva_fila], ignore_index=True)
                guardar_datos(df)
                st.success("¡Cuenta creada! Ya puedes entrar.")
                
    with t1:
        u_log = st.text_input("Usuario")
        p_log = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            df = leer_datos()
            # Aseguramos que la contraseña sea tratada como texto
            user_match = df[(df['usuario'] == u_log) & (df['password'].astype(str) == str(p_log))]
            if not user_match.empty:
                st.session_state.user = u_log
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    st.stop()

# --- PANEL TRAS EL LOGIN ---
st.title(f"🏹 Panel de {st.session_state.user}")
if st.button("Cerrar Sesión"):
    st.session_state.user = None
    st.rerun()

df = leer_datos()
user_data = df[df['usuario'] == st.session_state.user].iloc[0]

# Aquí puedes añadir el resto de tu lógica de examen
st.write("Has entrado correctamente. ¡La base de datos está conectada!")

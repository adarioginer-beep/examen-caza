import streamlit as st
import pandas as pd
import json
import random
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN DE SEGURIDAD PROFESIONAL ---
def conectar_google_sheets():
    # Cargamos el JSON desde los Secrets de Streamlit
    info_llave = json.loads(st.secrets["gcp_service_account"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info_llave, scopes=scope)
    client = gspread.authorize(creds)
    # Abrimos la hoja por su URL exacta
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1K4QP2c4XYH6MLIA61VP6RmHfFUPLUVwsKP3oIZmidys/edit?usp=sharing").sheet1
    return sheet

def get_data():
    sheet = conectar_google_sheets()
    return pd.DataFrame(sheet.get_all_records())

def save_user(df_completo):
    sheet = conectar_google_sheets()
    # Borramos lo viejo y escribimos lo nuevo (Método infalible)
    sheet.clear()
    sheet.update([df_completo.columns.values.tolist()] + df_completo.values.tolist())

# --- CARGAR PREGUNTAS ---
with open('preguntas.json', 'r', encoding='utf-8') as f:
    banco_preguntas = json.load(f)

# --- LÓGICA DE USUARIOS ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Acceso Academia de Caza")
    tab1, tab2 = st.tabs(["Entrar", "Registrarse"])
    with tab2:
        nuevo_u = st.text_input("Usuario Nuevo")
        nuevo_p = st.text_input("Pass Nueva", type="password")
        if st.button("Crear Cuenta"):
            df = get_data()
            if nuevo_u in df['usuario'].values:
                st.error("Ya existe")
            else:
                nueva_fila = {"usuario": nuevo_u, "password": nuevo_p, "temas_completados": "", "preguntas_fallidas": ""}
                df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
                save_user(df)
                st.success("¡Hecho! Ya puedes entrar.")
    with tab1:
        u = st.text_input("Usuario")
        p = st.text_input("Pass", type="password")
        if st.button("Entrar"):
            df = get_data()
            if not df[(df['usuario'] == u) & (df['password'] == str(p))].empty:
                st.session_state.user = u
                st.rerun()
            else: st.error("Fallo de login")
    st.stop()

# --- INTERFAZ ---
st.title(f"🏹 Panel de {st.session_state.user}")
df = get_data()
user_row = df[df['usuario'] == st.session_state.user].iloc[0]
temas_ok = str(user_row['temas_completados']).split(",") if user_row['temas_completados'] else []

modo = st.selectbox("Elegir:", ["Test por Tema", "Examen 36", "Mis Fallos"])

if modo == "Test por Tema":
    t = st.number_input("Tema", 1, 12)
    preguntas = [p for p in banco_preguntas if p['tema'] == t]
    with st.form("f"):
        res = {p['id']: st.radio(p['pregunta'], p['opciones'], key=p['id']) for p in preguntas}
        if st.form_submit_button("Corregir"):
            aciertos = sum(1 for p in preguntas if res[p['id']] == p['correcta'])
            fallos = [str(p['id']) for p in preguntas if res[p['id']] != p['correcta']]
            
            if aciertos >= 20:
                st.success(f"Aprobado: {aciertos}")
                if str(t) not in temas_ok: temas_ok.append(str(t))
            else: st.error(f"Suspenso: {aciertos}")
            
            # Guardar todo
            df.loc[df['usuario'] == st.session_state.user, 'temas_completados'] = ",".join(temas_ok)
            viejos_f = str(user_row['preguntas_fallidas']).split(",") if user_row['preguntas_fallidas'] else []
            df.loc[df['usuario'] == st.session_state.user, 'preguntas_fallidas'] = ",".join(list(set(viejos_f + fallos)))
            save_user(df)
            st.rerun()

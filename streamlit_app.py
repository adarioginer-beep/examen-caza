import streamlit as st
import json
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Academia de Caza", page_icon="🏹")

# 1. Base de datos temporal (se borra al cerrar el navegador)
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {"admin": "admin"} # Usuario por defecto

if 'user' not in st.session_state:
    st.session_state.user = None

# 2. Cargar preguntas desde tu archivo local
try:
    with open('preguntas.json', 'r', encoding='utf-8') as f:
        banco = json.load(f)
except:
    st.error("⚠️ No se encuentra 'preguntas.json' en tu GitHub.")
    st.stop()

# --- ACCESO ---
if not st.session_state.user:
    st.title("🏹 Acceso Academia de Caza")
    st.warning("Nota: Los datos son temporales. Si cierras la pestaña, se borran.")
    
    t1, t2 = st.tabs(["Entrar", "Registrarse"])
    with t2:
        u_reg = st.text_input("Elige Usuario")
        p_reg = st.text_input("Elige Contraseña", type="password")
        if st.button("Crear Cuenta"):
            st.session_state.usuarios[u_reg] = p_reg
            st.success("¡Cuenta creada! Ya puedes entrar.")
    with t1:
        u_log = st.text_input("Usuario")
        p_log = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u_log in st.session_state.usuarios and st.session_state.usuarios[u_log] == p_log:
                st.session_state.user = u_log
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    st.stop()

# --- PANEL DE CONTROL ---
st.title(f"🏹 Bienvenido, {st.session_state.user}")
if st.button("Cerrar Sesión"):
    st.session_state.user = None
    st.rerun()

modo = st.selectbox("Elegir modo:", ["Test por Tema", "Examen Oficial (36 preguntas)"])

if modo == "Test por Tema":
    tema = st.number_input("Selecciona Tema (1-12)", 1, 12)
    preguntas_tema = [p for p in banco if p['tema'] == tema]
    
    if preguntas_tema:
        with st.form("examen"):
            res = {}
            for p in preguntas_tema:
                res[p['id']] = st.radio(p['pregunta'], p['opciones'], key=p['id'])
            if st.form_submit_button("Corregir"):
                aciertos = sum(1 for p in preguntas_tema if res[p['id']] == p['correcta'])
                if aciertos >= 20: st.success(f"APROBADO: {aciertos}/25")
                else: st.error(f"SUSPENSO: {aciertos}/25")
    else:
        st.write("No hay preguntas registradas para este tema.")

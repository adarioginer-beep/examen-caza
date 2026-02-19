import streamlit as st
import pandas as pd
import json
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Academia de Caza - Volátil", page_icon="🏹")

# --- INICIALIZACIÓN DE MEMORIA TEMPORAL (Se borra al salir) ---
if 'usuarios_temp' not in st.session_state:
    # Creamos un usuario administrador por defecto para que puedas probar
    st.session_state.usuarios_temp = {
        "admin": {"password": "admin", "temas_ok": [], "fallos": []}
    }

if 'user' not in st.session_state:
    st.session_state.user = None

# --- CARGAR PREGUNTAS (Desde tu archivo local en GitHub) ---
try:
    with open('preguntas.json', 'r', encoding='utf-8') as f:
        banco_preguntas = json.load(f)
except:
    st.error("⚠️ No se encuentra el archivo preguntas.json en GitHub.")
    st.stop()

# --- LÓGICA DE ACCESO ---
if not st.session_state.user:
    st.title("🔐 Acceso Temporal")
    st.info("Nota: Esta app no guarda datos. Si cierras el navegador, los datos se pierden.")
    
    t1, t2 = st.tabs(["Entrar", "Registrarse"])
    
    with t2:
        u_reg = st.text_input("Nuevo Usuario")
        p_reg = st.text_input("Nueva Contraseña", type="password")
        if st.button("Crear Cuenta Temporal"):
            if u_reg in st.session_state.usuarios_temp:
                st.warning("Ese usuario ya existe en esta sesión.")
            else:
                st.session_state.usuarios_temp[u_reg] = {"password": p_reg, "temas_ok": [], "fallos": []}
                st.success("¡Cuenta creada! Ya puedes ir a la pestaña Entrar.")
                
    with t1:
        u_log = st.text_input("Usuario")
        p_log = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            user_data = st.session_state.usuarios_temp.get(u_log)
            if user_data and user_data["password"] == p_log:
                st.session_state.user = u_log
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    st.stop()

# --- PANEL DE CONTROL ---
st.title(f"🏹 Panel de {st.session_state.user}")
if st.sidebar.button("Cerrar Sesión (Borrar Todo)"):
    st.session_state.user = None
    st.rerun()

modo = st.selectbox("Elegir modo:", ["Test por Tema", "Examen 36", "Mis Errores"])

# Ejemplo de lógica de Test (se mantiene mientras no salgas)
if modo == "Test por Tema":
    tema = st.number_input("Selecciona Tema (1-12)", 1, 12)
    preguntas = [p for p in banco_preguntas if p['tema'] == tema]
    
    if preguntas:
        with st.form("test"):
            respuestas = {}
            for p in preguntas:
                respuestas[p['id']] = st.radio(p['pregunta'], p['opciones'], key=p['id'])
            
            if st.form_submit_button("Corregir"):
                aciertos = sum(1 for p in preguntas if respuestas[p['id']] == p['correcta'])
                if aciertos >= 20:
                    st.success(f"¡APROBADO! Aciertos: {aciertos}/25")
                    st.session_state.usuarios_temp[st.session_state.user]["temas_ok"].append(tema)
                else:
                    st.error(f"SUSPENSO. Aciertos: {aciertos}/25")
                    # Guardamos fallos en la sesión actual
                    nuevos_fallos = [p['id'] for p in preguntas if respuestas[p['id']] != p['correcta']]
                    st.session_state.usuarios_temp[st.session_state.user]["fallos"].extend(nuevos_fallos)
    else:
        st.warning("No hay preguntas para este tema.")

st.sidebar.write("---")
st.sidebar.write(f"Temas aprobados hoy: {list(set(st.session_state.usuarios_temp[st.session_state.user]['temas_ok']))}")

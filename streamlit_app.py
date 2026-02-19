import streamlit as st
import json
import random
import pandas as pd

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Academia de Caza", page_icon="🏹", layout="wide")

# MEMORIA VOLÁTIL (Se borra al cerrar o refrescar la pestaña)
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {"admin": "admin"} # Usuario por defecto
if 'user' not in st.session_state:
    st.session_state.user = None

# CARGAR EL BANCO DE PREGUNTAS
@st.cache_data
def cargar_banco():
    try:
        with open('preguntas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar preguntas.json: {e}")
        return []

banco = cargar_banco()

# --- INTERFAZ DE LOGIN ---
if not st.session_state.user:
    st.title("🏹 Academia de Caza - Acceso")
    st.warning("⚠️ Esta sesión es temporal. Al cerrar la pestaña, los datos se borran.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Entrar")
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u] == p:
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    
    with col2:
        st.subheader("Registrarse")
        new_u = st.text_input("Nuevo Usuario")
        new_p = st.text_input("Nueva Contraseña", type="password")
        if st.button("Crear Cuenta Temporal"):
            if new_u:
                st.session_state.usuarios[new_u] = new_p
                st.success("¡Cuenta creada! Ya puedes entrar.")
            else:
                st.error("Escribe un nombre de usuario")
    st.stop()

# --- PANEL PRINCIPAL (Solo si está logueado) ---
st.sidebar.title(f"Bienvenido, {st.session_state.user}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.user = None
    st.rerun()

menu = st.sidebar.radio("Menú", ["Inicio", "Test por Tema", "Examen Oficial (36 preg)"])

if menu == "Inicio":
    st.title("🏹 Preparación Examen de Caza")
    st.write("Selecciona un modo de estudio en el menú de la izquierda.")
    st.metric("Preguntas cargadas", len(banco))

elif menu == "Test por Tema":
    st.title("📝 Test por Temas")
    tema_sel = st.number_input("Selecciona Tema (1-12)", 1, 12)
    preguntas_tema = [p for p in banco if p['tema'] == tema_sel]
    
    if preguntas_tema:
        with st.form("test_tema"):
            respuestas = {}
            for p in preguntas_tema:
                st.write(f"**{p['pregunta']}**")
                respuestas[p['id']] = st.radio("Elige respuesta:", p['opciones'], key=f"t_{p['id']}")
            
            if st.form_submit_button("Corregir"):
                aciertos = sum(1 for p in preguntas_tema if respuestas[p['id']] == p['correcta'])
                st.write(f"### Resultado: {aciertos} / {len(preguntas_tema)}")
                if aciertos >= (len(preguntas_tema) * 0.8):
                    st.success("¡APROBADO!")
                else:
                    st.error("SUSPENSO")
    else:
        st.info("No hay preguntas para este tema en el JSON.")

elif menu == "Examen Oficial (36 preg)":
    st.title("⏱️ Simulacro Examen Oficial")
    if len(banco) < 36:
        st.error("Necesitas al menos 36 preguntas en el JSON para este modo.")
    else:
        if 'examen_aleatorio' not in st.session_state:
            st.session_state.examen_aleatorio = random.sample(banco, 36)
        
        with st.form("examen_oficial"):
            resp_ex = {}
            for i, p in enumerate(st.session_state.examen_aleatorio):
                st.write(f"**{i+1}. {p['pregunta']}**")
                resp_ex[p['id']] = st.radio("Respuesta:", p['opciones'], key=f"ex_{p['id']}")
            
            if st.form_submit_button("Finalizar Examen"):
                aciertos = sum(1 for p in st.session_state.examen_aleatorio if resp_ex[p['id']] == p['correcta'])
                st.write(f"### Aciertos: {aciertos} de 36")
                # El examen de caza suele permitir 6 fallos máximo
                if aciertos >= 30:
                    st.success("¡APTO! Enhorabuena.")
                else:
                    st.error("NO APTO. Sigue estudiando.")
                if st.button("Repetir otro examen"):
                    del st.session_state.examen_aleatorio
                    st.rerun()

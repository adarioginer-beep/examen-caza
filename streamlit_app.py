import streamlit as st
import random
import json
import os

st.set_page_config(page_title="Examen Caza Andalucía", layout="centered")

# --- FUNCIÓN PARA CARGAR EL ARCHIVO ---
def cargar_preguntas():
    try:
        with open('preguntas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# --- INICIO DE APP ---
preguntas_totales = cargar_preguntas()

if not preguntas_totales:
    st.error("⚠️ Error: No se encuentra el archivo 'preguntas.json' en GitHub o está vacío.")
else:
    if 'usuario' not in st.session_state:
        st.title("🔑 Acceso Alumnos")
        u = st.text_input("Tu Nombre")
        if st.button("Entrar"):
            st.session_state.usuario = u
            st.rerun()
    else:
        st.sidebar.write(f"Usuario: {st.session_state.usuario}")
        if st.sidebar.button("Salir"):
            del st.session_state.usuario
            st.rerun()

        st.title("📝 Examen de Simulación")
        
        # Botón para forzar que salgan preguntas nuevas
        if st.button("Generar Examen"):
            st.session_state.examen = random.sample(preguntas_totales, min(len(preguntas_totales), 36))
            st.session_state.respuestas = {}

        if 'examen' in st.session_state:
            with st.form("test"):
                for idx, p in enumerate(st.session_state.examen):
                    st.write(f"**{idx+1}. {p['pregunta']}**")
                    st.session_state.respuestas[idx] = st.radio("Elige:", p['opciones'], key=f"r{idx}")
                
                if st.form_submit_button("Corregir"):
                    aciertos = sum(1 for idx, p in enumerate(st.session_state.examen) if st.session_state.respuestas[idx] == p['correcta'])
                    if aciertos >= 20: st.success(f"✅ APROBADO: {aciertos}")
                    else: st.error(f"❌ SUSPENSO: {aciertos}")
                    
                    for idx, p in enumerate(st.session_state.examen):
                        if st.session_state.respuestas[idx] != p['correcta']:
                            st.info(f"Pregunta {idx+1}: La correcta era {p['correcta']}. {p['explicacion']}")

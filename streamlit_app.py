import streamlit as st
import random
import json
import os

st.set_page_config(page_title="Examen Caza Andalucía", layout="centered")

def cargar_preguntas():
    try:
        with open('preguntas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

preguntas_totales = cargar_preguntas()

if not preguntas_totales:
    st.error("⚠️ Sube el archivo preguntas.json a GitHub para empezar.")
else:
    if 'usuario' not in st.session_state:
        st.title("🔑 Acceso Alumnos")
        u = st.text_input("Tu Nombre")
        if st.button("Entrar"):
            st.session_state.usuario = u
            st.rerun()
    else:
        st.sidebar.title(f"👤 {st.session_state.usuario}")
        # AQUÍ ESTÁ LA MAGIA: Selección de modo
        modo = st.sidebar.selectbox("¿Qué quieres hacer?", ["Examen Oficial (Aleatorio)", "Practicar por Temas"])
        
        if st.sidebar.button("Cerrar Sesión"):
            del st.session_state.usuario
            st.rerun()

        if modo == "Practicar por Temas":
            st.title("📚 Práctica por Temas")
            # El programa mira qué temas existen en tu JSON
            temas_disponibles = sorted(list(set([p['tema'] for p in preguntas_totales])))
            tema_elegido = st.selectbox("Selecciona el tema:", temas_disponibles)
            
            # Filtramos solo las preguntas de ese tema
            preguntas_tema = [p for p in preguntas_totales if p['tema'] == tema_elegido]
            
            if st.button(f"Empezar Tema {tema_elegido}"):
                st.session_state.examen = preguntas_tema
                st.session_state.respuestas = {}

        else:
            st.title("📝 Examen Oficial (36 preg)")
            if st.button("Generar Examen Aleatorio"):
                # Mezcla todas las preguntas y elige 36 (o las que haya disponibles)
                st.session_state.examen = random.sample(preguntas_totales, min(len(preguntas_totales), 36))
                st.session_state.respuestas = {}

        # MOSTRAR LAS PREGUNTAS (Si se ha generado un examen o tema)
        if 'examen' in st.session_state:
            with st.form("quiz"):
                for idx, p in enumerate(st.session_state.examen):
                    st.write(f"**{idx+1}. {p['pregunta']}**")
                    st.session_state.respuestas[idx] = st.radio("Respuesta:", p['opciones'], key=f"r{idx}")
                
                if st.form_submit_button("Corregir"):
                    aciertos = sum(1 for idx, p in enumerate(st.session_state.examen) if st.session_state.respuestas[idx] == p['correcta'])
                    if aciertos >= 20: st.success(f"🏆 APROBADO: {aciertos} aciertos.")
                    else: st.error(f"❌ SUSPENSO: {aciertos} aciertos.")
                    
                    for idx, p in enumerate(st.session_state.examen):
                        if st.session_state.respuestas[idx] != p['correcta']:
                            st.warning(f"Pregunta {idx+1}: La correcta era {p['correcta']}")

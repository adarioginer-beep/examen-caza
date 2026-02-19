import streamlit as st
import random
import time

# Configuración básica
st.set_page_config(page_title="ACADEMIA DE CAZA GINER", page_icon="🏹")

# Estilo visual
st.markdown("<h1 style='text-align: center; color: #2e4a31;'>🏹 ACADEMIA DE CAZA GINER</h1>", unsafe_allow_html=True)

# Banco de preguntas directo en el código (Añade más aquí)
preguntas = [
    {"id": 1, "pregunta": "¿Especie de caza mayor más común en España?", "opciones": ["Corzo", "Jabalí", "Ciervo"], "correcta": "Jabalí"},
    {"id": 2, "pregunta": "¿Es obligatorio el seguro para cazar?", "opciones": ["No", "Sí, siempre", "Solo con perros"], "correcta": "Sí, siempre"}
]

# Sistema de entrada
if 'entrar' not in st.session_state:
    st.session_state.entrar = False

if not st.session_state.entrar:
    user = st.text_input("Usuario")
    if st.button("ACCEDER"):
        st.session_state.entrar = True
        st.rerun()
    st.stop()

# Menú y Examen
st.sidebar.title("Menú")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.entrar = False
    st.rerun()

st.header("⏱️ Simulacro de Examen")
if st.button("EMPEZAR"):
    st.session_state.test = random.sample(preguntas, len(preguntas))
    st.session_state.t_inicio = time.time()

if 'test' in st.session_state:
    t_transcurrido = int(time.time() - st.session_state.t_inicio)
    st.sidebar.metric("⏳ TIEMPO", f"{t_transcurrido//60:02d}:{t_transcurrido%60:02d}")
    
    with st.form("exam"):
        res = {}
        for p in st.session_state.test:
            st.write(p['pregunta'])
            res[p['id']] = st.radio("Elige:", p['opciones'], key=p['id'])
        if st.form_submit_button("CORREGIR"):
            aciertos = sum(1 for p in st.session_state.test if res[p['id']] == p['correcta'])
            st.success(f"Resultado: {aciertos} aciertos.")

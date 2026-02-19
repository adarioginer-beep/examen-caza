import streamlit as st
import random
import time

# Configuración de la web
st.set_page_config(page_title="ACADEMIA DE CAZA GINER", page_icon="🏹")

# Diseño profesional
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f1; }
    .main-title { color: #2e4a31; font-size: 3em; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">🏹 ACADEMIA DE CAZA GINER</p>', unsafe_allow_html=True)

# BANCO DE PREGUNTAS INTERNO (Para no depender de Google Sheets)
# Aquí puedes añadir todas las que quieras siguiendo este formato
banco_preguntas = [
    {
        "id": 1,
        "tema": 1,
        "pregunta": "¿Cuál es la especie de caza mayor más común en España?",
        "opciones": ["Corzo", "Jabalí", "Ciervo", "Gamo"],
        "correcta": "Jabalí"
    },
    {
        "id": 2,
        "tema": 1,
        "pregunta": "¿Qué calibre se considera el mínimo para caza mayor?",
        "opciones": ["22 LR", "243 Win", "12/70", "4.5 mm"],
        "correcta": "243 Win"
    }
]

# Sistema de Login Simple (Temporal)
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.subheader("Acceso Alumnos")
        user = st.text_input("Usuario")
        if st.button("Entrar"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# Menú Principal
menu = st.sidebar.radio("Menú", ["Simulacro de Examen", "Repaso por Temas"])

if menu == "Simulacro de Examen":
    st.header("⏱️ Examen Oficial (Cronometrado)")
    if st.button("Empezar Examen"):
        st.session_state.examen = random.sample(banco_preguntas, min(len(banco_preguntas), 36))
        st.session_state.inicio = time.time()
    
    if 'examen' in st.session_state:
        # Cronómetro lateral
        transcurrido = int(time.time() - st.session_state.inicio)
        st.sidebar.metric("⏳ Tiempo", f"{transcurrido//60:02d}:{transcurrido%60:02d}")
        
        with st.form("test"):
            respuestas = {}
            for i, p in enumerate(st.session_state.examen):
                st.write(f"**{i+1}. {p['pregunta']}**")
                respuestas[p['id']] = st.radio("Elige una:", p['opciones'], key=f"p_{p['id']}", index=None)
            
            if st.form_submit_button("Corregir"):
                aciertos = sum(1 for p in st.session_state.examen if respuestas[p['id']] == p['correcta'])
                st.success(f"Has acertado {aciertos} preguntas.")
                for p in st.session_state.examen:
                    if respuestas[p['id']] == p['correcta']:
                        st.write(f"✅ {p['pregunta']} - CORRECTA")
                    else:
                        st.write(f"❌ {p['pregunta']} - INCORRECTA (Era: {p['correcta']})")

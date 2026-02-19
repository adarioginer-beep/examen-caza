import streamlit as st
import json
import random
import time

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(page_title="ACADEMIA DE CAZA", page_icon="🏹", layout="wide")

# CSS para que parezca una web profesional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e4a31; color: white; }
    .stTitle { color: #2e4a31; font-family: 'Helvetica', sans-serif; font-size: 3em !important; text-align: center; border-bottom: 2px solid #2e4a31; padding-bottom: 10px; }
    .header-box { background-color: #2e4a31; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA DE LA WEB ---
st.markdown('<div class="header-box"><h1>🏹 ACADEMIA DE CAZA</h1><p>Tu plataforma de entrenamiento oficial</p></div>', unsafe_allow_html=True)

# --- MEMORIA VOLÁTIL ---
if 'usuarios' not in st.session_state: st.session_state.usuarios = {"admin": "admin"}
if 'user' not in st.session_state: st.session_state.user = None
if 'temas_aprobados' not in st.session_state: st.session_state.temas_aprobados = set()

# --- CARGAR BANCO ---
@st.cache_data
def cargar_banco():
    try:
        with open('preguntas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return []

banco = cargar_banco()

# --- SISTEMA DE LOGIN ---
if not st.session_state.user:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        tab1, tab2 = st.tabs(["🔑 ENTRAR", "📝 REGISTRARSE"])
        with tab1:
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("ACCEDER"):
                if u in st.session_state.usuarios and st.session_state.usuarios[u] == p:
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Error en credenciales")
        with tab2:
            nu = st.text_input("Nuevo Usuario")
            np = st.text_input("Nueva Pass", type="password")
            if st.button("CREAR CUENTA TEMPORAL"):
                st.session_state.usuarios[nu] = np
                st.success("Cuenta lista. Ya puedes entrar.")
    
    st.markdown("---")
    st.caption("© 2024 Academia de Caza - Plataforma de simulación educativa. No vinculada a organismos oficiales.")
    st.stop()

# --- PANEL DE CONTROL ---
st.sidebar.title(f"👤 {st.session_state.user}")
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Tu Progreso")
for t in range(1, 13):
    check = "✅" if t in st.session_state.temas_aprobados else "⚪"
    st.sidebar.write(f"{check} Tema {t}")

menu = st.sidebar.radio("Navegación", ["📚 Test por Tema", "⏱️ Examen Oficial"])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.user = None
    st.rerun()

# --- LÓGICA DE EXAMEN CON CRONÓMETRO ---
if menu == "⏱️ Examen Oficial":
    st.header("Simulacro de Examen Oficial (36 preguntas)")
    if st.button("🚀 COMENZAR NUEVO EXAMEN"):
        st.session_state.examen_actual = random.sample(banco, 36)
        st.session_state.inicio_time = time.time()
        st.rerun()

    if 'examen_actual' in st.session_state:
        t_transcurrido = int(time.time() - st.session_state.inicio_time)
        st.sidebar.metric("⏳ TIEMPO", f"{t_transcurrido//60:02d}:{t_transcurrido%60:02d}")
        
        with st.form("ex"):
            resp = {}
            for i, p in enumerate(st.session_state.examen_actual):
                st.write(f"**{i+1}. {p['pregunta']}**")
                resp[p['id']] = st.radio("Opciones:", p['opciones'], key=f"e{p['id']}", index=None)
            if st.form_submit_button("FINALIZAR"):
                aciertos = sum(1 for p in st.session_state.examen_actual if resp[p['id']] == p['correcta'])
                st.session_state.resultado = (aciertos, resp, st.session_state.examen_actual)
        
        if 'resultado' in st.session_state:
            ac, res_u, ex_a = st.session_state.resultado
            st.subheader(f"Resultado: {ac} / 36")
            for i, p in enumerate(ex_a):
                if res_u[p['id']] == p['correcta']: st.write(f"✅ {i+1}. Correcto")
                else: st.write(f"❌ {i+1}. Fallo. Era: **{p['correcta']}**")

import streamlit as st
import json
import random

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Academia de Caza", page_icon="🏹", layout="wide")

# MEMORIA VOLÁTIL
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {"admin": "admin"}
if 'user' not in st.session_state:
    st.session_state.user = None

# CARGAR EL BANCO DE PREGUNTAS
@st.cache_data
def cargar_banco():
    try:
        with open('preguntas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

banco = cargar_banco()

# --- INTERFAZ DE LOGIN (Se mantiene igual) ---
if not st.session_state.user:
    st.title("🏹 Academia de Caza")
    t1, t2 = st.tabs(["Entrar", "Registrarse"])
    with t1:
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u] == p:
                st.session_state.user = u
                st.rerun()
    with t2:
        new_u = st.text_input("Nuevo Usuario")
        new_p = st.text_input("Nueva Contraseña", type="password")
        if st.button("Crear Cuenta"):
            st.session_state.usuarios[new_u] = new_p
            st.success("¡Cuenta creada!")
    st.stop()

# --- PANEL PRINCIPAL ---
st.sidebar.title(f"Usuario: {st.session_state.user}")
menu = st.sidebar.radio("Menú", ["Test por Tema", "Examen Oficial (36 preg)"])
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.user = None
    st.rerun()

# --- LÓGICA DE EXAMEN ALEATORIO ---
if menu == "Examen Oficial (36 preg)":
    st.title("⏱️ Simulacro de Examen Oficial")
    
    # Botón para generar un nuevo examen aleatorio
    if st.button("Generar nuevo examen aleatorio"):
        if 'examen_actual' in st.session_state:
            del st.session_state.examen_actual
        st.rerun()

    if len(banco) < 36:
        st.error("No hay suficientes preguntas en el JSON (mínimo 36).")
    else:
        # Si no hay un examen en la sesión, elegimos 36 al azar
        if 'examen_actual' not in st.session_state:
            st.session_state.examen_actual = random.sample(banco, 36)
        
        with st.form("form_examen"):
            respuestas_usuario = {}
            for i, p in enumerate(st.session_state.examen_actual):
                st.write(f"**{i+1}. {p['pregunta']}**")
                respuestas_usuario[p['id']] = st.radio("Selecciona:", p['opciones'], key=f"ex_{p['id']}", index=None)
            
            enviado = st.form_submit_button("Corregir Examen")

        if enviado:
            aciertos = 0
            st.write("---")
            st.subheader("Resultados detallados:")
            
            for p in st.session_state.examen_actual:
                resp = respuestas_usuario[p['id']]
                if resp == p['correcta']:
                    aciertos += 1
                    st.write(f"✅ **Pregunta {p['id']}**: ¡Correcto! ({p['correcta']})")
                else:
                    st.write(f"❌ **Pregunta {p['id']}**: Fallaste.")
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;👉 Tu respuesta: *{resp}*")
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ La correcta era: **{p['correcta']}**")
            
            st.write("---")
            if aciertos >= 30:
                st.balloons()
                st.success(f"¡APTO! Has acertado {aciertos} de 36.")
            else:
                st.error(f"NO APTO. Has acertado {aciertos} de 36. (Necesitas 30)")

# --- LÓGICA DE TEST POR TEMA ---
elif menu == "Test por Tema":
    st.title("📝 Práctica por Temas")
    tema_sel = st.number_input("Tema (1-12)", 1, 12)
    preguntas_tema = [p for p in banco if p['tema'] == tema_sel]
    
    if preguntas_tema:
        with st.form("form_tema"):
            resp_tema = {}
            for p in preguntas_tema:
                st.write(f"**{p['pregunta']}**")
                resp_tema[p['id']] = st.radio("Selecciona:", p['opciones'], key=f"t_{p['id']}", index=None)
            
            corregir_t = st.form_submit_button("Corregir Tema")
            
        if corregir_t:
            aciertos_t = 0
            for p in preguntas_tema:
                if resp_tema[p['id']] == p['correcta']:
                    aciertos_t += 1
                    st.write(f"✅ **Correcta**: {p['correcta']}")
                else:
                    st.write(f"❌ **Fallada**. Era: **{p['correcta']}**")
            st.info(f"Resultado: {aciertos_t} de {len(preguntas_tema)}")

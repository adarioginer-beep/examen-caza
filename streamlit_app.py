import streamlit as st
import json
import random
import time
from datetime import datetime

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Academia de Caza", page_icon="🏹", layout="wide")

# MEMORIA VOLÁTIL
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {"admin": "admin"}
if 'user' not in st.session_state:
    st.session_state.user = None
if 'temas_aprobados' not in st.session_state:
    st.session_state.temas_aprobados = set()

# CARGAR EL BANCO DE PREGUNTAS
@st.cache_data
def cargar_banco():
    try:
        with open('preguntas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

banco = cargar_banco()

# --- LOGIN ---
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

# --- PANEL LATERAL ---
st.sidebar.title(f"Usuario: {st.session_state.user}")
st.sidebar.write("### Progreso de Temas")
for t in range(1, 13):
    check = "✅" if t in st.session_state.temas_aprobados else "⚪"
    st.sidebar.write(f"{check} Tema {t}")

menu = st.sidebar.radio("Menú", ["Test por Tema", "Examen Oficial (36 preg)"])

if st.sidebar.button("Cerrar Sesión"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- MODO TEST POR TEMA (Se mantiene igual) ---
if menu == "Test por Tema":
    st.title("📝 Práctica por Temas")
    tema_sel = st.number_input("Selecciona Tema (1-12)", 1, 12)
    preguntas_tema = [p for p in banco if p['tema'] == tema_sel]
    
    if preguntas_tema:
        with st.form("form_tema"):
            resp_tema = {}
            for i, p in enumerate(preguntas_tema):
                st.write(f"### {i+1}. {p['pregunta']}")
                resp_tema[p['id']] = st.radio("Selecciona:", p['opciones'], key=f"t_{p['id']}", index=None)
            corregir_t = st.form_submit_button("Corregir Tema")
            
        if corregir_t:
            aciertos_t = 0
            st.write("---")
            for i, p in enumerate(preguntas_tema):
                resp = resp_tema[p['id']]
                if resp == p['correcta']:
                    aciertos_t += 1
                    st.write(f"✅ **Pregunta {i+1}:** ¡Correcto!")
                else:
                    st.write(f"❌ **Pregunta {i+1}:** Fallaste. Era: {p['correcta']}")
            if aciertos_t >= 20:
                st.success(f"🎉 ¡APROBADO! ({aciertos_t}/25)")
                st.session_state.temas_aprobados.add(tema_sel)
            else:
                st.error(f"❌ SUSPENSO. ({aciertos_t}/25)")

# --- MODO EXAMEN OFICIAL CON CRONÓMETRO ---
elif menu == "Examen Oficial (36 preg)":
    st.title("⏱️ Simulacro de Examen Oficial")

    # Botón para iniciar/reiniciar examen y cronómetro
    if st.button("Generar nuevo examen y empezar cronómetro"):
        st.session_state.examen_actual = random.sample(banco, 36)
        st.session_state.inicio_time = time.time()
        st.rerun()

    if 'examen_actual' in st.session_state:
        # LÓGICA DEL CRONÓMETRO VISIBLE
        tiempo_transcurrido = int(time.time() - st.session_state.inicio_time)
        minutos = tiempo_transcurrido // 60
        segundos = tiempo_transcurrido % 60
        
        # Mostramos el tiempo en un recuadro destacado
        st.sidebar.metric("⏳ Tiempo en el examen", f"{minutos:02d}:{segundos:02d}")
        
        # Aviso: El cronómetro se actualiza cada vez que marcas una respuesta
        st.caption("*(El cronómetro se actualiza al interactuar con las preguntas)*")

        with st.form("form_examen"):
            resp_ex = {}
            for i, p in enumerate(st.session_state.examen_actual):
                st.write(f"### {i+1}. {p['pregunta']}")
                resp_ex[p['id']] = st.radio("Selecciona:", p['opciones'], key=f"ex_{p['id']}", index=None)
            
            enviado = st.form_submit_button("Finalizar y Detener Cronómetro")

        if enviado:
            tiempo_final = int(time.time() - st.session_state.inicio_time)
            min_f = tiempo_final // 60
            seg_f = tiempo_final % 60
            
            aciertos = 0
            st.write("---")
            st.subheader(f"📋 Resultados (Tiempo total: {min_f:02d}:{seg_f:02d})")
            
            for i, p in enumerate(st.session_state.examen_actual):
                resp = resp_ex[p['id']]
                if resp == p['correcta']:
                    aciertos += 1
                    st.write(f"✅ **{i+1}.** Correcto")
                else:
                    st.write(f"❌ **{i+1}.** Fallada. (Era: {p['correcta']})")
            
            if aciertos >= 20:
                st.balloons()
                st.success(f"🏆 ¡APTO! Acertaste {aciertos} de 36 en {min_f} min.")
            else:
                st.error(f"👎 NO APTO. Acertaste {aciertos}. (Tiempo: {min_f} min)")
    else:
        st.info("Pulsa el botón de arriba para comenzar el examen y el tiempo.")

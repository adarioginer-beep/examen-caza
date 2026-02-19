import streamlit as st
import json
import random

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Academia de Caza", page_icon="🏹", layout="wide")

# MEMORIA VOLÁTIL (Se borra al cerrar la pestaña)
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {"admin": "admin"}
if 'user' not in st.session_state:
    st.session_state.user = None
# Registro de temas aprobados para mostrar los checks
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

# Mostrar checks de temas aprobados en el lateral
st.sidebar.write("### Progreso de Temas")
for t in range(1, 13):
    check = "✅" if t in st.session_state.temas_aprobados else "⚪"
    st.sidebar.write(f"{check} Tema {t}")

menu = st.sidebar.radio("Menú", ["Test por Tema", "Examen Oficial (36 preg)"])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.user = None
    st.session_state.temas_aprobados = set() # Limpiar al salir
    st.rerun()

# --- MODO TEST POR TEMA ---
if menu == "Test por Tema":
    st.title("📝 Práctica por Temas")
    tema_sel = st.number_input("Selecciona Tema (1-12)", 1, 12)
    preguntas_tema = [p for p in banco if p['tema'] == tema_sel]
    
    if preguntas_tema:
        # Si el tema ya está aprobado, mostrar aviso
        if tema_sel in st.session_state.temas_aprobados:
            st.success(f"🌟 ¡Ya has aprobado el Tema {tema_sel} en esta sesión!")

        with st.form("form_tema"):
            resp_tema = {}
            for i, p in enumerate(preguntas_tema):
                st.write(f"### Pregunta {i+1}")
                st.write(f"**{p['pregunta']}**")
                resp_tema[p['id']] = st.radio("Selecciona:", p['opciones'], key=f"t_{p['id']}", index=None)
            
            corregir_t = st.form_submit_button("Corregir Tema")
            
        if corregir_t:
            aciertos_t = 0
            st.write("---")
            for i, p in enumerate(preguntas_tema):
                resp = resp_tema[p['id']]
                if resp == p['correcta']:
                    aciertos_t += 1
                    st.write(f"✅ **{i+1}.** Correcta")
                else:
                    st.write(f"❌ **{i+1}.** Fallada (Era: {p['correcta']})")
            
            # Lógica de aprobado: 20 de 25
            total = len(preguntas_tema)
            st.write(f"### Resultado: {aciertos_t} de {total}")
            
            if aciertos_t >= 20:
                st.balloons()
                st.success("🎉 ¡APROBADO! Check añadido al panel lateral.")
                st.session_state.temas_aprobados.add(tema_sel)
                st.rerun() # Para actualizar el check en el lateral inmediatamente
            else:
                st.error(f"❌ SUSPENSO. Necesitas al menos 20 aciertos (tienes {aciertos_t}).")

# --- MODO EXAMEN OFICIAL ---
elif menu == "Examen Oficial (36 preg)":
    st.title("⏱️ Simulacro de Examen Oficial")
    
    if st.button("Generar nuevo examen aleatorio"):
        if 'examen_actual' in st.session_state: del st.session_state.examen_actual
        st.rerun()

    if len(banco) < 36:
        st.error("No hay suficientes preguntas.")
    else:
        if 'examen_actual' not in st.session_state:
            st.session_state.examen_actual = random.sample(banco, 36)
        
        with st.form("form_examen"):
            respuestas_usuario = {}
            for i, p in enumerate(st.session_state.examen_actual):
                st.write(f"### Pregunta {i+1}")
                st.write(f"**{p['pregunta']}**")
                respuestas_usuario[p['id']] = st.radio("Selecciona:", p['opciones'], key=f"ex_{p['id']}", index=None)
            
            enviado = st.form_submit_button("Finalizar y Corregir")

        if enviado:
            aciertos = 0
            for i, p in enumerate(st.session_state.examen_actual):
                if respuestas_usuario[p['id']] == p['correcta']:
                    aciertos += 1
            
            # Lógica de aprobado: 20 de 36
            st.write(f"### Resultado final: {aciertos} de 36")
            if aciertos >= 20:
                st.balloons()
                st.success("🏆 ¡APTO! Has superado el examen.")
            else:
                st.error(f"👎 NO APTO. Has acertado {aciertos}. Necesitas 20.")

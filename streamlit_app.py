import streamlit as st
import random

# Configuración de la página
st.set_page_config(page_title="Examen Licencia Caza Andalucía", layout="centered")

# --- BASE DE DATOS DE PREGUNTAS (Simplificada para el ejemplo) ---
# Aquí he cargado la estructura de los 12 temas con tus validaciones
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = [
        # Ejemplo Tema 7 con tu corrección manual
        {"id": 175, "tema": 7, "pregunta": "¿Quién puede retirar armas de fuego ante una infracción?", 
         "opciones": ["Sólo Guardia Civil", "Guardia Civil y Guarda Rural", "Sólo agentes de la autoridad y guardas rurales con la especialidad en caza..."], 
         "correcta": "Sólo agentes de la autoridad y guardas rurales con la especialidad en caza...",
         "explicacion": "Conforme al art. 34.4, ley 5/2014, 4 de Abril, de seguridad privada."},
        # ... Aquí irían las 300 preguntas procesadas
    ]

# --- LÓGICA DE USUARIOS ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
    st.session_state.fallos = []

# Interfaz de Login
if not st.session_state.usuario:
    st.title("🔑 Acceso Alumnos")
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        st.session_state.usuario = user
        st.rerun()
else:
    # --- MENÚ PRINCIPAL ---
    st.sidebar.title(f"Bienvenido, {st.session_state.usuario}")
    opcion = st.sidebar.radio("Selecciona modo:", ["Examen Oficial (36 preg)", "Por Temas", "Repasar Mis Fallos"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario = None
        st.rerun()

    # --- MODO EXAMEN OFICIAL ---
    if opcion == "Examen Oficial (36 preg)":
        st.title("📝 Examen de Simulación")
        st.info("36 preguntas aleatorias. Necesitas 20 para aprobar.")
        
        # Generar examen (3 de cada tema)
        if 'examen_actual' not in st.session_state:
            examen = []
            for i in range(1, 13):
                pool = [p for p in st.session_state.preguntas if p['tema'] == i]
                examen.extend(random.sample(pool, min(len(pool), 3)))
            st.session_state.examen_actual = examen
            st.session_state.respuestas_usuario = {}

        # Mostrar preguntas
        form = st.form("quiz")
        for idx, p in enumerate(st.session_state.examen_actual):
            st.session_state.respuestas_usuario[idx] = form.radio(f"{idx+1}. {p['pregunta']}", p['opciones'], key=f"p{idx}")
        
        if form.form_submit_button("Finalizar y Corregir"):
            aciertos = 0
            for idx, p in enumerate(st.session_state.examen_actual):
                if st.session_state.respuestas_usuario[idx] == p['correcta']:
                    aciertos += 1
                else:
                    st.error(f"Fallo en preg {idx+1}: {p['explicacion']}")
                    st.session_state.fallos.append(p['id'])
            
            if aciertos >= 20:
                st.balloons()
                st.success(f"¡APROBADO! Aciertos: {aciertos}/36")
            else:
                st.error(f"SUSPENSO. Aciertos: {aciertos}/36. ¡Sigue practicando!")

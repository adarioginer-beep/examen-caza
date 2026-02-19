import streamlit as st
import pandas as pd
import json
import random
from streamlit_gsheets import GSheetsConnection

# Configuración de página
st.set_page_config(page_title="Examen Caza Profesional", page_icon="🏹")

# Conexión a la base de datos (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl=0)

def save_user(df_nuevo):
    conn.update(data=df_nuevo)

# Cargar preguntas
with open('preguntas.json', 'r', encoding='utf-8') as f:
    banco_preguntas = json.load(f)

# --- LÓGICA DE USUARIOS ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Acceso Academia de Caza")
    tab1, tab2 = st.tabs(["Entrar", "Registrarse"])
    
    with tab2:
        nuevo_usuario = st.text_input("Elige Usuario")
        nueva_pass = st.text_input("Elige Contraseña", type="password")
        if st.button("Crear Cuenta"):
            df = get_data()
            if nuevo_usuario in df['usuario'].values:
                st.error("El usuario ya existe")
            else:
                new_row = pd.DataFrame([{"usuario": nuevo_usuario, "password": nueva_pass, "temas_completados": "", "preguntas_fallidas": ""}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_user(df)
                st.success("¡Cuenta creada! Ya puedes entrar.")
                
    with tab1:
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            df = get_data()
            user_data = df[(df['usuario'] == u) & (df['password'] == p)]
            if not user_data.empty:
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    st.stop()

# --- PANEL PRINCIPAL ---
df = get_data()
user_row = df[df['usuario'] == st.session_state.user].iloc[0]
temas_ok = str(user_row['temas_completados']).split(",") if pd.notna(user_row['temas_completados']) else []

st.sidebar.title(f"Hola, {st.session_state.user} 👋")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.user = None
    st.rerun()

# --- ESTADO DEL PROGRESO ---
st.title("🏹 Preparación Examen de Caza")

# Verificar si está listo para el examen
temas_totales = set([str(i) for i in range(1, 13)])
aprobados_set = set([t for t in temas_ok if t])

if temas_totales.issubset(aprobados_set):
    st.balloons()
    st.success("🏆 ¡ESTÁS PREPARADO PARA EL EXAMEN OFICIAL! Has aprobado todos los temas.")

# --- MENÚ DE EXÁMENES ---
opcion = st.selectbox("¿Qué quieres hacer hoy?", 
                     ["Seleccionar un Tema", "Examen Aleatorio (36 preg)", "Repasar mis errores"])

if opcion == "Seleccionar un Tema":
    tema_sel = st.number_input("Elige Tema (1-12)", 1, 12)
    check = "✅ Aprobado" if str(tema_sel) in temas_ok else "❌ No completado"
    st.write(f"Estado: **{check}**")
    
    preguntas = [p for p in banco_preguntas if p['tema'] == tema_sel]
    
    with st.form("test_tema"):
        respuestas = {}
        for p in preguntas:
            st.write(f"**{p['pregunta']}**")
            respuestas[p['id']] = st.radio(f"Opción para {p['id']}", p['opciones'], key=p['id'], label_visibility="collapsed")
        
        if st.form_submit_button("Finalizar Test"):
            aciertos = 0
            fallos_ids = []
            for p in preguntas:
                if respuestas[p['id']] == p['correcta']:
                    aciertos += 1
                else:
                    fallos_ids.append(str(p['id']))
            
            st.write(f"Resultado: {aciertos} / 25")
            
            # Guardar fallos
            viejos_fallos = str(user_row['preguntas_fallidas']).split(",") if pd.notna(user_row['preguntas_fallidas']) else []
            nuevos_fallos = list(set(viejos_fallos + fallos_ids))
            
            # Guardar aprobado si >= 20
            if aciertos >= 20:
                st.success("¡APROBADO!")
                if str(tema_sel) not in temas_ok:
                    temas_ok.append(str(tema_sel))
            else:
                st.error("SUSPENDIDO (Mínimo 20 aciertos)")
            
            # Actualizar Excel
            df.loc[df['usuario'] == st.session_state.user, 'temas_completados'] = ",".join(temas_ok)
            df.loc[df['usuario'] == st.session_state.user, 'preguntas_fallidas'] = ",".join([f for f in nuevos_fallos if f])
            save_user(df)

elif opcion == "Examen Aleatorio (36 preg)":
    st.subheader("Examen de Simulación (Aprobar con 20)")
    if 'examen' not in st.session_state:
        st.session_state.examen = random.sample(banco_preguntas, 36)
    
    with st.form("examen_real"):
        res_ex = {}
        for p in st.session_state.examen:
            st.write(f"**{p['pregunta']}**")
            res_ex[p['id']] = st.radio(f"Opción {p['id']}", p['opciones'], key=f"ex_{p['id']}", label_visibility="collapsed")
        
        if st.form_submit_button("Corregir Examen"):
            aciertos = sum(1 for p in st.session_state.examen if res_ex[p['id']] == p['correcta'])
            if aciertos >= 20:
                st.success(f"¡EXAMEN APROBADO! {aciertos} aciertos.")
            else:
                st.error(f"EXAMEN SUSPENDIDO. {aciertos} aciertos. Se necesitan 20.")
            del st.session_state.examen

elif opcion == "Repasar mis errores":
    fallos_str = str(user_row['preguntas_fallidas']).split(",") if pd.notna(user_row['preguntas_fallidas']) else []
    fallos_ids = [int(f) for f in fallos_str if f]
    
    if not fallos_ids:
        st.info("¡No tienes fallos guardados! Eres un máquina.")
    else:
        st.subheader(f"Tienes {len(fallos_ids)} preguntas por repasar")
        preguntas_fallo = [p for p in banco_preguntas if p['id'] in fallos_ids]
        
        for p in preguntas_fallo:
            with st.expander(f"Pregunta del Tema {p['tema']}"):
                st.write(p['pregunta'])
                st.write(f"**Correcta:** {p['correcta']}")
                if st.button(f"Ya me la sé (Eliminar {p['id']})"):
                    fallos_ids.remove(p['id'])
                    df.loc[df['usuario'] == st.session_state.user, 'preguntas_fallidas'] = ",".join([str(i) for i in fallos_ids])
                    save_user(df)
                    st.rerun()

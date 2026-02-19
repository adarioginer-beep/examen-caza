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
    # El código dentro de la función DEBE tener esta sangría
    conn.update(worksheet="Sheet1", data=df_nuevo)

# Cargar banco de preguntas
with open('preguntas.json', 'r', encoding='utf-8') as f:
    banco_preguntas = json.load(f)

# --- GESTIÓN DE SESIÓN Y USUARIOS ---
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

# --- PANEL DE CONTROL TRAS LOGIN ---
df = get_data()
user_row = df[df['usuario'] == st.session_state.user].iloc[0]
temas_ok = str(user_row['temas_completados']).split(",") if pd.notna(user_row['temas_completados']) else []

st.sidebar.title(f"Hola, {st.session_state.user} 👋")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.user = None
    st.rerun()

# --- ESTADO Y PROGRESO ---
st.title("🏹 Preparación Examen de Caza")

# Verificar si todos los temas (1-12) están aprobados
temas_totales = set([str(i) for i in range(1, 13)])
aprobados_set = set([t for t in temas_ok if t.strip()])

if temas_totales.issubset(aprobados_set):
    st.balloons()
    st.success("🏆 ¡ESTÁS PREPARADO PARA EL EXAMEN OFICIAL! Has aprobado los 12 temas.")

# --- MENÚ DE ACTIVIDADES ---
opcion = st.selectbox("¿Qué quieres hacer hoy?", 
                     ["Seleccionar un Tema", "Examen Aleatorio (36 preg)", "Repasar mis errores"])

if opcion == "Seleccionar un Tema":
    tema_sel = st.number_input("Elige Tema (1-12)", 1, 12)
    check = "✅ Aprobado" if str(tema_sel) in aprobados_set else "❌ Pendiente"
    st.subheader(f"Tema {tema_sel}: {check}")
    
    preguntas = [p for p in banco_preguntas if p['tema'] == tema_sel]
    
    with st.form(f"test_tema_{tema_sel}"):
        respuestas = {}
        for p in preguntas:
            st.write(f"**{p['pregunta']}**")
            respuestas[p['id']] = st.radio(f"Opciones {p['id']}", p['opciones'], key=f"p_{p['id']}", label_visibility="collapsed")
        
        if st.form_submit_button("Corregir Tema"):
            aciertos = 0
            fallos_ids = []
            for p in preguntas:
                if respuestas[p['id']] == p['correcta']:
                    aciertos += 1
                else:
                    fallos_ids.append(str(p['id']))
            
            st.info(f"Has acertado {aciertos} de {len(preguntas)}")
            
            # Guardar fallos históricos
            viejos_fallos = str(user_row['preguntas_fallidas']).split(",") if pd.notna(user_row['preguntas_fallidas']) else []
            nuevos_fallos = list(set([f for f in viejos_fallos if f] + fallos_ids))
            
            # Lógica de aprobado (20 de 25)
            if aciertos >= 20:
                st.success("🎉 ¡TEMA APROBADO!")
                if str(tema_sel) not in aprobados_set:
                    aprobados_set.add(str(tema_sel))
            else:
                st.error("❌ SUSPENDIDO (Necesitas 20 aciertos)")
            
            # Actualizar base de datos
            df.loc[df['usuario'] == st.session_state.user, 'temas_completados'] = ",".join(sorted(list(aprobados_set)))
            df.loc[df['usuario'] == st.session_state.user, 'preguntas_fallidas'] = ",".join(nuevos_fallos)
            save_user(df)
            st.write("Progreso guardado automáticamente.")

elif opcion == "Examen Aleatorio (36 preg)":
    st.subheader("Simulacro de Examen Oficial")
    if 'examen' not in st.session_state:
        st.session_state.examen = random.sample(banco_preguntas, 36)
    
    with st.form("examen_sim"):
        resp_ex = {}
        for i, p in enumerate(st.session_state.examen):
            st.write(f"{i+1}. **{p['pregunta']}**")
            resp_ex[p['id']] = st.radio(f"Ex {p['id']}", p['opciones'], key=f"ex_{p['id']}", label_visibility="collapsed")
        
        if st.form_submit_button("Finalizar Examen"):
            aciertos = sum(1 for p in st.session_state.examen if resp_ex[p['id']] == p['correcta'])
            # Guardar fallos del examen también
            fallos_ex = [str(p['id']) for p in st.session_state.examen if resp_ex[p['id']] != p['correcta']]
            viejos_fallos = str(user_row['preguntas_fallidas']).split(",") if pd.notna(user_row['preguntas_fallidas']) else []
            total_fallos = list(set([f for f in viejos_fallos if f] + fallos_ex))
            
            df.loc[df['usuario'] == st.session_state.user, 'preguntas_fallidas'] = ",".join(total_fallos)
            save_user(df)
            
            if aciertos >= 20:
                st.success(f"🏆 ¡APROBADO! Aciertos: {aciertos}/36")
            else:
                st.error(f"❌ SUSPENDIDO. Aciertos: {aciertos}/36 (Mínimo 20)")
            del st.session_state.examen

elif opcion == "Repasar mis errores":
    fallos_str = str(user_row['preguntas_fallidas']).split(",") if pd.notna(user_row['preguntas_fallidas']) else []
    fallos_ids = [int(f) for f in fallos_str if f.strip()]
    
    if not fallos_ids:
        st.success("🌟 ¡Increíble! No tienes preguntas fallidas en tu historial.")
    else:
        st.subheader(f"Tienes {len(fallos_ids)} preguntas pendientes")
        preguntas_error = [p for p in banco_preguntas if p['id'] in fallos_ids]
        
        for p in preguntas_error:
            with st.expander(f"Error en Tema {p['tema']}"):
                st.write(f"**{p['pregunta']}**")
                st.write(f"Respuesta correcta: {p['correcta']}")
                if st.button(f"Eliminar de fallos (ID {p['id']})"):
                    fallos_ids.remove(p['id'])
                    df.loc[df['usuario'] == st.session_state.user, 'preguntas_fallidas'] = ",".join([str(x) for x in fallos_ids])
                    save_user(df)
                    st.rerun()

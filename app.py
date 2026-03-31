import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection


# Configuración de la página
st.set_page_config(page_title="Evaluación Interactiva", page_icon="📝")

# Inicializar variables de estado (memoria de la app)
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'intento_actual' not in st.session_state:
    st.session_state.intento_actual = 1
if 'aprobado' not in st.session_state:
    st.session_state.aprobado = False

# Función para guardar en "Excel" (usaremos un CSV para mayor compatibilidad inicial)
# Nueva función para guardar en Google Sheets
def guardar_resultados(nombre, puntaje, intentos):
    # Creamos la conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leemos los datos actuales
    df_existente = conn.read(ttl=0) # ttl=0 para que no use caché y lea siempre lo último
    
    # Creamos el nuevo registro
    nuevo_dato = pd.DataFrame({'Nombre': [nombre], 'Puntaje': [puntaje], 'Intentos': [intentos]})
    
    # Unimos los datos
    df_final = pd.concat([df_existente, nuevo_dato], ignore_index=True)
    
    # Lo subimos de nuevo a la nube
    conn.update(data=df_final)
# --- INTERFAZ DE LA APP ---

st.title("📝 Evaluación de Conocimientos")

# 1. PANTALLA DE INGRESO
if st.session_state.usuario is None:
    st.write("Por favor, ingresa tu nombre para comenzar la evaluación.")
    nombre_input = st.text_input("Nombre y Apellido:")
    
    if st.button("Comenzar Test"):
        if nombre_input:
            st.session_state.usuario = nombre_input
            st.rerun()
        else:
            st.warning("Debes ingresar un nombre para continuar.")

# 2. PANTALLA DE EVALUACIÓN
elif not st.session_state.aprobado:
    st.write(f"👤 Evaluado: **{st.session_state.usuario}** | 🔄 Intento: **{st.session_state.intento_actual}**")
    st.markdown("---")
    
    with st.form("formulario_evaluacion"):
        st.subheader("Responde las siguientes preguntas:")
        
        q1 = st.radio("1. ¿Cuánto es 5 + 5?", ["8", "10", "12"], index=None)
        q2 = st.radio("2. ¿Cuál es la capital de Francia?", ["Madrid", "Roma", "París"], index=None)
        q3 = st.radio("3. ¿El sol es una estrella?", ["Verdadero", "Falso"], index=None)
        
        enviado = st.form_submit_button("Enviar Respuestas")
        
        if enviado:
            # Calcular puntaje
            puntaje = 0
            if q1 == "10": puntaje += 1
            if q2 == "París": puntaje += 1
            if q3 == "Verdadero": puntaje += 1
            
            # Lógica de aprobación (Ejemplo: necesita 3/3 para pasar)
            if puntaje == 3:
                st.success(f"¡Felicidades! Obtuviste {puntaje}/3. Has aprobado.")
                guardar_resultados(st.session_state.usuario, puntaje, st.session_state.intento_actual)
                st.session_state.aprobado = True
                st.rerun()
            else:
                st.error(f"Obtuviste {puntaje}/3. Necesitas puntaje perfecto para avanzar.")
                st.session_state.intento_actual += 1
                st.info("Revisa tus respuestas e inténtalo de nuevo.")

# 3. PANTALLA DE ÉXITO
else:
    st.balloons()
    st.success("¡Evaluación completada con éxito!")
    st.write("Tus resultados han sido guardados correctamente en la base de datos.")
    
    if st.button("Evaluar a otra persona"):
        # Reiniciar todas las variables
        st.session_state.usuario = None
        st.session_state.intento_actual = 1
        st.session_state.aprobado = False
        st.rerun()

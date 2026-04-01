import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 🎨 CONFIGURACIÓN VISUAL Y DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Centro de Capacitación - Evaluación",
    page_icon="🎓",
    layout="centered" # Mantiene el contenido enfocado en el centro
)

# --- ESTILOS CSS PERSONALIZADOS (Pequeños trucos visuales) ---
st.markdown("""
    <style>
    /* Estilo para los títulos de las preguntas */
    .stRadio > label {
        font-weight: bold;
        font-size: 1.1rem;
        color: #31333F;
        padding-bottom: 10px;
    }
    /* Estilo para la caja de info del usuario al inicio */
    .css-1r6slb0 {
        background-color: #f0f2f6;
        padding: 20px;
        border_radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


# ==========================================
# 🧠 LÓGICA DE DATOS Y ESTADO
# ==========================================

# --- Inicializar variables de estado (memoria de la app) ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'intento_actual' not in st.session_state:
    st.session_state.intento_actual = 1
if 'aprobado' not in st.session_state:
    st.session_state.aprobado = False
if 'respuestas_usuario' not in st.session_state:
    st.session_state.respuestas_usuario = {}

# --- Función para guardar en Google Sheets (Usando Secrets seguras) ---
def guardar_resultados_nube(nombre, puntaje, intentos):
    try:
        # Creamos la conexión (lee automáticamente de [connections.gsheets] en Secrets)
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Leemos los datos actuales (ttl=0 para garantizar datos frescos)
        df_existente = conn.read(ttl=0)
        
        # Creamos el nuevo registro
        nuevo_dato = pd.DataFrame({'Nombre': [nombre], 'Puntaje': [puntaje], 'Intentos': [intentos]})
        
        # Unimos los datos
        df_final = pd.concat([df_existente, nuevo_dato], ignore_index=True)
        
        # Lo subimos de nuevo a la nube
        conn.update(data=df_final)
        return True
    except Exception as e:
        st.error(f"⚠️ Error crítico al guardar en la nube. Por favor avisa al administrador. Error: {e}")
        return False


# ==========================================
# 📚 DEFINICIÓN DEL CUESTIONARIO REAL
# ==========================================

# Aquí irán tus preguntas reales. He creado una estructura fácil de editar.
# Simplemente copia y pega bloques para agregar más preguntas.

preguntas_reales = [
    {
        "id": 1,
        "pregunta": "1. ¿Cuál es el procedimiento correcto si detecta una anomalía en el sistema de control?",
        "opciones": ["Ignorarla si es pequeña", "Reportar inmediatamente al supervisor", "Intentar arreglarla sin avisar", "Esperar al cambio de turno"],
        "correcta": "Reportar inmediatamente al supervisor"
    },
    {
        "id": 2,
        "pregunta": "2. ¿Verdadero o Falso: El uso de EPP es opcional en la zona de producción?",
        "opciones": ["Verdadero", "Falso"],
        "correcta": "Falso"
    },
    # --- AGREGA MÁS PREGUNTAS AQUÍ SIGUIENDO EL FORMATO ---
    # {
    #     "id": 3,
    #     "pregunta": "3. ...",
    #     "opciones": ["...", "..."],
    #     "correcta": "..."
    # },
]

# Calculamos el puntaje necesario para aprobar (Ej. 100% o 80%)
# Para Duolingo, suele ser perfecto, cambiémoslo a perfecto por ahora.
TOTAL_PREGUNTAS = len(preguntas_reales)
PUNTAJE_MINIMO = TOTAL_PREGUNTAS 


# ==========================================
# 🖥️ INTERFAZ DE USUARIO (UI)
# ==========================================

# --- Cabecera Principal ---
st.title("🎓 Centro de Evaluación Técnica")
st.markdown("Bienvenido al módulo de validación de conocimientos. Responde conscientemente.")
st.markdown("---")


# --- Fase 1: Identificación ---
if st.session_state.usuario is None:
    # Usamos columnas para centrar el formulario de inicio
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.subheader("👋 ¡Hola! Antes de empezar...")
        nombre_input = st.text_input("Ingresa tu Nombre Completo:", placeholder="Ej. Juan Pérez")
        
        # Botón moderno
        if st.button("Comenzar Evaluación 🚀", use_container_width=True):
            if nombre_input:
                st.session_state.usuario = nombre_input
                st.rerun()
            else:
                st.warning("⚠️ Por favor, ingresa tu nombre para continuar.")

# --- Fase 2: Evaluación Activa ---
elif not st.session_state.aprobado:
    
    # 🌟 MEJORA VISUAL: Cabecera de usuario moderna
    st.markdown("### Datos de la Evaluación")
    c1, c2, c3 = st.columns(3)
    c1.metric("👤 Evaluado", st.session_state.usuario)
    c2.metric("🔄 Intento", st.session_state.intento_actual)
    c3.metric("🎯 Meta", f"{PUNTAJE_MINIMO}/{TOTAL_PREGUNTAS}")
    
    st.markdown("---")

    # 🌟 MEJORA VISUAL: Barra de Progreso (Tipo Duolingo)
    # Calculamos cuántas preguntas ha respondido ya
    respondidas = len(st.session_state.respuestas_usuario)
    progreso = respondidas / TOTAL_PREGUNTAS if TOTAL_PREGUNTAS > 0 else 0
    st.write(f"Tu progreso: {respondidas} de {TOTAL_PREGUNTAS} preguntas.")
    st.progress(progreso)
    st.markdown("<br>", unsafe_allow_html=True) # Espacio en blanco

    # --- Creación dinámica del formulario de preguntas ---
    with st.form("evaluacion_form"):
        st.subheader("📝 Cuestionario")
        
        # Iteramos sobre la lista de preguntas reales
        for p in preguntas_reales:
            # Usamos st.radio para selección única moderna
            # Guardamos la respuesta directamente en st.session_state.respuestas_usuario
            key_pregunta = f"p_{p['id']}"
            st.session_state.respuestas_usuario[key_pregunta] = st.radio(
                p["pregunta"],
                p["opciones"],
                index=None, # Inicia sin selección para obligar a elegir
                key=key_pregunta
            )
            st.markdown("<br>", unsafe_allow_html=True) # Espacio entre preguntas

        st.markdown("---")
        # Botón de envío grande y centrado
        enviar_btn = st.form_submit_button("✅ Finalizar y Enviar Respuestas", use_container_width=True)
        
        if enviar_btn:
            # LÓGICA DE EVALUACIÓN
            # Verificamos si respondieron todas
            if None in st.session_state.respuestas_usuario.values() or len(st.session_state.respuestas_usuario) < TOTAL_PREGUNTAS:
                st.warning("⚠️ Por favor, responde todas las preguntas antes de enviar.")
            else:
                # Calcular puntaje final
                puntaje_final = 0
                for p in preguntas_reales:
                    key_p = f"p_{p['id']}"
                    if st.session_state.respuestas_usuario[key_p] == p["correcta"]:
                        puntaje_final += 1
                
                # LÓGICA DE APROBACIÓN (TIPO DUOLINGO: Retintentos)
                if puntaje_final >= PUNTAJE_MINIMO:
                    # 🥳 ¡APROBADO! Guardamos en la nube
                    with st.spinner("Guardando tus resultados exitosos en la base de datos..."):
                        exito_guardado = guardar_resultados_nube(st.session_state.usuario, puntaje_final, st.session_state.intento_actual)
                    
                    if exito_guardado:
                        st.session_state.aprobado = True
                        st.balloons() # Animación Duolingo style
                        st.rerun()
                else:
                    # 😥 REPROBADO: Forzar reintento
                    st.error(f"❌ Obtuviste {puntaje_final}/{TOTAL_PREGUNTAS}. Necesitas puntaje perfecto ({PUNTAJE_MINIMO}/{TOTAL_PREGUNTAS}) para aprobar.")
                    st.markdown("### 🔄 ¡No te rindas!")
                    st.info("Revisa tus conocimientos e inténtalo de nuevo. Tu progreso se ha reiniciado para este nuevo intento.")
                    
                    # Lógica de Duolingo: Aumentar intento y limpiar respuestas
                    st.session_state.intento_actual += 1
                    st.session_state.respuestas_usuario = {} # Limpiamos para el reintento
                    # Al hacer rerun, el formulario se recargará vacío
                    # st.rerun() # Omitimos el rerun automático para que lean el mensaje de error primero.


# --- Fase 3: Pantalla de Éxito Final ---
else:
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.success("🎉 ¡FELICIDADES! 🎉")
        st.markdown(f"### Estimado(a) **{st.session_state.usuario}**,")
        st.markdown(f"Has completado con éxito la evaluación en tu intento número **{st.session_state.intento_actual}**.")
        st.write("Tus resultados han sido registrados oficialmente en nuestro sistema central (Google Sheets). Ya puedes cerrar esta ventana.")
        st.markdown("---")
        
        # Botón opcional para evaluar a otra persona
        if st.button("Evaluar a otra persona (Reiniciar)", use_container_width=True):
            # Limpiamos todo el estado
            st.session_state.usuario = None
            st.session_state.intento_actual = 1
            st.session_state.aprobado = False
            st.session_state.respuestas_usuario = {}
            st.rerun()

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 🎨 CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Evaluación de Capacitación Técnica",
    page_icon="🎓",
    layout="centered"
)

# Inyectamos un poco de CSS para que las pistas y radios se vean mejor
st.markdown("""
    <style>
    .stRadio > label { font-weight: bold; font-size: 1.05rem; }
    .stAlert { border-radius: 10px; }
    div[data-testid="stExpander"] { border: 1px solid #e6e9ef; border-radius: 8px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🧠 LÓGICA DE ESTADO (SESSION STATE)
# ==========================================
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'intento_actual' not in st.session_state:
    st.session_state.intento_actual = 1
if 'aprobado' not in st.session_state:
    st.session_state.aprobado = False
if 'respuestas_usuario' not in st.session_state:
    st.session_state.respuestas_usuario = {}

# ==========================================
# 📊 CONEXIÓN A GOOGLE SHEETS
# ==========================================
def guardar_en_nube(nombre, puntaje, intentos):
    try:
        # Se conecta usando las credenciales de 'Secrets'
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_existente = conn.read(ttl=0)
        
        nuevo_registro = pd.DataFrame({
            'Nombre': [nombre], 
            'Puntaje': [f"{puntaje}/10"], 
            'Intentos': [intentos]
        })
        
        df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
        conn.update(data=df_final)
        return True
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False

# ==========================================
# 📚 CUESTIONARIO PROFESIONAL (10 PREGUNTAS)
# ==========================================
preguntas_reales = [
    {"id": 1, "pregunta": "1. ¿Qué significa la sigla EPP?", "opciones": ["Equipo de Protección Personal", "Evaluación de Procesos"], "correcta": "Equipo de Protección Personal", "pista": "Elementos como casco y guantes."},
    {"id": 2, "pregunta": "2. Extintor para fuego eléctrico:", "opciones": ["Agua", "CO2 o PQS"], "correcta": "CO2 o PQS", "pista": "El agente no debe ser conductor de electricidad."},
    {"id": 3, "pregunta": "3. Función principal de un PLC:", "opciones": ["Automatizar procesos", "Navegar por internet"], "correcta": "Automatizar procesos", "pista": "Es el cerebro de la máquina."},
    {"id": 4, "pregunta": "4. Color de tuberías contra incendios:", "opciones": ["Azul", "Rojo"], "correcta": "Rojo", "pista": "Color universal de emergencia."},
    {"id": 5, "pregunta": "5. ¿Qué es Lockout/Tagout?", "opciones": ["Limpieza", "Bloqueo y Etiquetado"], "correcta": "Bloqueo y Etiquetado", "pista": "Evita que alguien encienda la máquina mientras trabajas."},
    {"id": 6, "pregunta": "6. Límite de ruido (8h) sin protección:", "opciones": ["85 dB", "120 dB"], "correcta": "85 dB", "pista": "A partir de aquí hay riesgo auditivo."},
    {"id": 7, "pregunta": "7. ¿Qué indica el color AMARILLO?", "opciones": ["Seguridad", "Advertencia"], "correcta": "Advertencia", "pista": "Precaución ante un riesgo."},
    {"id": 8, "pregunta": "8. Herramienta para medir tensión:", "opciones": ["Multímetro", "Manómetro"], "correcta": "Multímetro", "pista": "Mide Voltios."},
    {"id": 9, "pregunta": "9. Acción ante derrame químico desconocido:", "opciones": ["Limpiar", "Evacuar el área"], "correcta": "Evacuar el área", "pista": "La seguridad es primero."},
    {"id": 10, "pregunta": "10. ¿Altura mínima para 'Trabajo en Altura'?", "opciones": ["1.80 metros", "5.00 metros"], "correcta": "1.80 metros", "pista": "Requiere uso de arnés obligatorio."}
]

# ==========================================
# 🖥️ INTERFAZ DE USUARIO
# ==========================================
st.title("🎓 Evaluación Técnica de Capacitación")
st.markdown("Responde correctamente las 10 preguntas para aprobar.")

# --- FASE 1: INGRESO ---
if st.session_state.usuario is None:
    nombre = st.text_input("Ingresa tu Nombre Completo:")
    if st.button("Empezar Evaluación"):
        if nombre:
            st.session_state.usuario = nombre
            st.rerun()
        else: st.warning("Ingresa un nombre.")

# --- FASE 2: EVALUACIÓN ---
elif not st.session_state.aprobado:
    col_a, col_b = st.columns(2)
    col_a.write(f"👤 **Usuario:** {st.session_state.usuario}")
    col_b.write(f"🔄 **Intento:** {st.session_state.intento_actual}")
    
    # Barra de progreso dinámica
    respondidas = len([v for v in st.session_state.respuestas_usuario.values() if v is not None])
    st.progress(respondidas / 10)

    with st.form("test"):
        for p in preguntas_reales:
            st.write(f"### Pregunta {p['id']}")
            # Pista interactiva
            with st.expander("💡 Ver pista"):
                st.info(p['pista'])
            
            st.session_state.respuestas_usuario[f"p{p['id']}"] = st.radio(
                p['pregunta'], p['opciones'], index=None, key=f"r{p['id']}", label_visibility="collapsed"
            )
            st.markdown("---")

        if st.form_submit_button("Enviar Resultados", use_container_width=True):
            puntaje = sum(1 for p in preguntas_reales if st.session_state.respuestas_usuario.get(f"p{p['id']}") == p['correcta'])
            
            if puntaje == 10:
                if guardar_en_nube(st.session_state.usuario, puntaje, st.session_state.intento_actual):
                    st.session_state.aprobado = True
                    st.balloons()
                    st.rerun()
            else:
                st.error(f"Puntaje: {puntaje}/10. ¡Debes obtener 10/10 para aprobar! Inténtalo de nuevo.")
                st.session_state.intento_actual += 1

# --- FASE 3: ÉXITO ---
else:
    st.success(f"¡Excelente, {st.session_state.usuario}! Has aprobado.")
    st.write("Tus datos se guardaron en el Excel de la nube.")
    if st.button("Nueva Evaluación"):
        st.session_state.usuario = None
        st.session_state.aprobado = False
        st.session_state.respuestas_usuario = {}
        st.session_state.intento_actual = 1
        st.rerun()

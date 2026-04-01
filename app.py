import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 🎨 CONFIGURACIÓN VISUAL
# ==========================================
st.set_page_config(page_title="Evaluación Técnica", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .stRadio > label { font-weight: bold; font-size: 1.1rem; color: #1E3A8A; }
    .stAlert { border-radius: 12px; }
    div[data-testid="stExpander"] { border: 1px solid #D1D5DB; border-radius: 10px; background-color: #F9FAFB; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📚 TUS 10 PREGUNTAS (Edita el texto aquí)
# ==========================================
preguntas_estaticas = [
    {"id": 1, "pregunta": "1. ¿Qué significa la sigla EPP?", "opciones": ["Equipo de Protección Personal", "Evaluación de Procesos", "Estándar de Prevención"], "correcta": "Equipo de Protección Personal", "pista": "Elementos como casco y guantes."},
    {"id": 2, "pregunta": "2. ¿Qué extintor usar en fuego eléctrico?", "opciones": ["Agua", "CO2 o PQS", "Espuma"], "correcta": "CO2 o PQS", "pista": "No debe conducir electricidad."},
    {"id": 3, "pregunta": "3. Función principal de un PLC:", "opciones": ["Automatizar procesos", "Navegar por internet", "Diseño gráfico"], "correcta": "Automatizar procesos", "pista": "Es el cerebro industrial."},
    {"id": 4, "pregunta": "4. Color de tuberías contra incendios:", "opciones": ["Azul", "Amarillo", "Rojo"], "correcta": "Rojo", "pista": "Color de emergencia universal."},
    {"id": 5, "pregunta": "5. ¿Qué es Lockout/Tagout?", "opciones": ["Limpieza", "Bloqueo y Etiquetado", "Engrase"], "correcta": "Bloqueo y Etiquetado", "pista": "Seguridad antes del mantenimiento."},
    {"id": 6, "pregunta": "6. Límite de ruido (8h) sin protección:", "opciones": ["70 dB", "85 dB", "100 dB"], "correcta": "85 dB", "pista": "Nivel de riesgo auditivo."},
    {"id": 7, "pregunta": "7. ¿Qué indica el color AMARILLO?", "opciones": ["Seguridad", "Advertencia / Peligro", "Obligación"], "correcta": "Advertencia / Peligro", "pista": "Precaución ante un riesgo."},
    {"id": 8, "pregunta": "8. Herramienta para medir tensión:", "opciones": ["Multímetro", "Manómetro", "Tacómetro"], "correcta": "Multímetro", "pista": "Mide voltios y amperios."},
    {"id": 9, "pregunta": "9. Acción ante derrame químico desconocido:", "opciones": ["Limpiar rápido", "Evacuar el área", "Olerlo"], "correcta": "Evacuar el área", "pista": "La seguridad es prioridad."},
    {"id": 10, "pregunta": "10. Altura mínima de 'Trabajo en Altura':", "opciones": ["1.00 metro", "1.80 metros", "3.00 metros"], "correcta": "1.80 metros", "pista": "Requiere uso de arnés."},
]

# ==========================================
# ⚙️ FUNCIONES
# ==========================================
def guardar_datos(nombre, puntaje, intento):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_existente = conn.read(ttl=0)
        nuevo = pd.DataFrame({
            'Nombre': [nombre], 
            'Puntaje': [f"{puntaje}/10"], 
            'Intento': [intento],
            'Fecha': [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")]
        })
        df_final = pd.concat([df_existente, nuevo], ignore_index=True)
        conn.update(data=df_final)
        return True
    except: return False

# ==========================================
# 🖥️ INTERFAZ DE USUARIO
# ==========================================
if 'user' not in st.session_state: st.session_state.user = None
if 'aprobado' not in st.session_state: st.session_state.aprobado = False
if 'intento' not in st.session_state: st.session_state.intento = 1

st.title("🎓 Evaluación de Capacitación")

if st.session_state.user is None:
    st.subheader("Bienvenido")
    nombre = st.text_input("Ingresa tu Nombre Completo:")
    if st.button("Empezar Evaluación") and nombre:
        st.session_state.user = nombre
        st.rerun()

elif not st.session_state.aprobado:
    st.info(f"👤 **Evaluado:** {st.session_state.user} | 🔄 **Intento:** {st.session_state.intento}")
    
    with st.form("test_estatico"):
        respuestas = {}
        for p in preguntas_estaticas:
            st.markdown(f"### {p['pregunta']}")
            with st.expander("💡 Pista"):
                st.write(p['pista'])
            
            respuestas[p['id']] = st.radio(
                "Selecciona una opción:", p['opciones'], 
                index=None, key=f"q{p['id']}", label_visibility="collapsed"
            )
            st.markdown("---")
        
        if st.form_submit_button("✅ Finalizar y Enviar", use_container_width=True):
            if None in respuestas.values():
                st.warning("⚠️ Responde todas las preguntas.")
            else:
                aciertos = sum(1 for p in preguntas_estaticas if respuestas[p['id']] == p['correcta'])
                if aciertos == 10:
                    if guardar_datos(st.session_state.user, aciertos, st.session_state.intento):
                        st.session_state.aprobado = True
                        st.rerun()
                else:
                    st.error(f"Puntaje: {aciertos}/10. ¡Debes obtener 10/10 para aprobar!")
                    st.session_state.intento += 1

else:
    st.success(f"🎊 ¡Felicidades {st.session_state.user}! Has aprobado.")
    st.balloons()
    if st.button("Evaluar a otra persona"):
        st.session_state.user = None
        st.session_state.aprobado = False
        st.session_state.intento = 1
        st.rerun()

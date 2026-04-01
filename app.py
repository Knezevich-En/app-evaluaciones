import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# ==========================================
# 🎨 CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Evaluación Técnica Pro", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .stRadio > label { font-weight: bold; font-size: 1.1rem; color: #1E3A8A; margin-bottom: 5px; }
    .pista-style { background-color: #E0F2FE; padding: 15px; border-radius: 10px; color: #0369A1; font-weight: 500; border-left: 5px solid #0EA5E9; margin-bottom: 10px; }
    .resultado-box { padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📚 PREGUNTAS
# ==========================================
preguntas_estaticas = [
    {"id": 1, "pregunta": "1. ¿Qué significa la sigla EPP?", "opciones": ["Equipo de Protección Personal", "Evaluación de Procesos", "Estándar de Prevención"], "correcta": "Equipo de Protección Personal", "pista": "Casco, guantes y botas son ejemplos de esto."},
    {"id": 2, "pregunta": "2. ¿Qué extintor usar en fuego eléctrico?", "opciones": ["Agua", "CO2 o PQS", "Espuma"], "correcta": "CO2 o PQS", "pista": "El agente no debe ser conductor de electricidad."},
    {"id": 3, "pregunta": "3. Función principal de un PLC:", "opciones": ["Automatizar procesos", "Navegar por internet", "Diseño gráfico"], "correcta": "Automatizar procesos", "pista": "Es el controlador lógico programable industrial."},
    {"id": 4, "pregunta": "4. Color de tuberías contra incendios:", "opciones": ["Azul", "Amarillo", "Rojo"], "correcta": "Rojo", "pista": "Color estándar de seguridad para emergencias."},
    {"id": 5, "pregunta": "5. ¿Qué es Lockout/Tagout?", "opciones": ["Limpieza", "Bloqueo y Etiquetado", "Engrase"], "correcta": "Bloqueo y Etiquetado", "pista": "Procedimiento para evitar arranques accidentales."},
    {"id": 6, "pregunta": "6. Límite de ruido (8h) sin protección:", "opciones": ["70 dB", "85 dB", "100 dB"], "correcta": "85 dB", "pista": "A partir de este nivel el daño es crónico."},
    {"id": 7, "pregunta": "7. ¿Qué indica el color AMARILLO?", "opciones": ["Seguridad", "Advertencia / Peligro", "Obligación"], "correcta": "Advertencia / Peligro", "pista": "Se usa para precaución ante riesgos físicos."},
    {"id": 8, "pregunta": "8. Herramienta para medir tensión:", "opciones": ["Multímetro", "Manómetro", "Tacómetro"], "correcta": "Multímetro", "pista": "Instrumento versátil para electricistas."},
    {"id": 9, "pregunta": "9. Acción ante derrame químico desconocido:", "opciones": ["Limpiar rápido", "Evacuar el área", "Olerlo"], "correcta": "Evacuar el área", "pista": "Nunca arriesgues tu salud ante lo desconocido."},
    {"id": 10, "pregunta": "10. Altura mínima de 'Trabajo en Altura':", "opciones": ["1.00 metro", "1.80 metros", "3.00 metros"], "correcta": "1.80 metros", "pista": "Norma oficial para el uso obligatorio de arnés."},
]

# ==========================================
# ⚙️ INICIALIZACIÓN DE ESTADO
# ==========================================
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'aprobado' not in st.session_state: st.session_state.aprobado = False
if 'intento' not in st.session_state: st.session_state.intento = 1
if 'respuestas_usuario' not in st.session_state: st.session_state.respuestas_usuario = {}
if 'validar' not in st.session_state: st.session_state.validar = False

# ==========================================
# 💾 FUNCIÓN DE GUARDADO (CON DEBUG)
# ==========================================
def guardar_datos(nombre, email, telefono, puntaje, intento):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_existente = conn.read(ttl=0)
        
        nuevo_registro = pd.DataFrame({
            'Nombre': [nombre],
            'Correo': [email],
            'Teléfono': [telefono],
            'Puntaje': [f"{puntaje}/10"],
            'Intento': [intento],
            'Fecha': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        
        df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
        conn.update(data=df_final)
        return True
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {e}")
        return False

# ==========================================
# 🖥️ INTERFAZ
# ==========================================
st.title("🎓 Evaluación de Capacitación")

# --- 1. REGISTRO ---
if st.session_state.perfil is None:
    with st.form("registro_form"):
        st.subheader("📝 Datos del Participante")
        n = st.text_input("Nombre y Apellido:")
        e = st.text_input("Correo Electrónico:")
        t = st.text_input("Teléfono / WhatsApp:")
        if st.form_submit_button("Empezar Evaluación", use_container_width=True):
            if n and e and t:
                st.session_state.perfil = {"n": n, "e": e, "t": t}
                st.rerun()
            else:
                st.warning("⚠️ Completa todos los campos.")

# --- 2. CUESTIONARIO ---
elif not st.session_state.aprobado:
    st.info(f"👤 **{st.session_state.perfil['n']}** | 🔄 Intento: **{st.session_state.intento}**")
    
    # Renderizar preguntas fuera de un Form para mejor respuesta visual
    for p in preguntas_estaticas:
        st.markdown(f"### {p['pregunta']}")
        
        with st.expander("💡 Ver Pista"):
            st.markdown(f'<div class="pista-style">{p["pista"]}</div>', unsafe_allow_html=True)
        
        # Guardamos la selección en el session_state directamente
        st.session_state.respuestas_usuario[p['id']] = st.radio(
            "Selecciona:", p['opciones'], 
            index=None, 
            key=f"radio_{p['id']}_{st.session_state.intento}",
            label_visibility="collapsed"
        )
        
        # Si el usuario ya intentó enviar y falló, mostramos feedback
        if st.session_state.validar:
            if st.session_state.respuestas_usuario[p['id']] == p['correcta']:
                st.success("✅ ¡Correcto!")
            else:
                st.error(f"❌ Incorrecto. La respuesta es: {p['correcta']}")
        st.write("---")

    # Botón de envío fuera de un st.form para evitar problemas de refresco
    if st.button("🚀 Finalizar y Guardar Resultados", use_container_width=True):
        # Verificar si todas están respondidas
        respuestas = st.session_state.respuestas_usuario
        if len(respuestas) < 10 or None in respuestas.values():
            st.warning("⚠️ Por favor, responde todas las preguntas antes de finalizar.")
        else:
            puntos = sum(1 for p in preguntas_estaticas if respuestas.get(p['id']) == p['correcta'])
            
            if puntos == 10:
                with st.spinner("Guardando en la base de datos..."):
                    exito = guardar_datos(
                        st.session_state.perfil['n'], 
                        st.session_state.perfil['e'], 
                        st.session_state.perfil['t'], 
                        puntos, 
                        st.session_state.intento
                    )
                    if exito:
                        st.session_state.aprobado = True
                        st.rerun()
            else:
                st.session_state.validar = True
                st.error(f"Puntaje: {puntos}/10. Revisa los errores marcados arriba e inténtalo de nuevo.")
                st.session_state.intento += 1
                st.rerun()

# --- 3. ÉXITO ---
else:
    st.success("🎊 ¡Felicidades! Has aprobado con puntaje perfecto.")
    st.balloons()
    if st.button("Reiniciar para nuevo usuario", use_container_width=True):
        st.session_state.perfil = None
        st.session_state.aprobado = False
        st.session_state.intento = 1
        st.session_state.respuestas_usuario = {}
        st.session_state.validar = False
        st.rerun()

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 🎨 CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Evaluación Técnica Pro", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .stRadio > label { font-weight: bold; font-size: 1.1rem; color: #1E3A8A; }
    .stAlert { border-radius: 12px; }
    /* Estilo para que la pista sea visible y clara */
    .pista-style { background-color: #E0F2FE; padding: 10px; border-radius: 8px; color: #0369A1; font-weight: 500; border-left: 5px solid #0EA5E9; }
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
# ⚙️ LÓGICA
# ==========================================
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'aprobado' not in st.session_state: st.session_state.aprobado = False
if 'intento' not in st.session_state: st.session_state.intento = 1
if 'mostrar_resultados' not in st.session_state: st.session_state.mostrar_resultados = False

def guardar_datos(nombre, email, telefono, puntaje, intento):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_existente = conn.read(ttl=0)
        nuevo = pd.DataFrame({
            'Nombre': [nombre], 'Correo': [email], 'Teléfono': [telefono],
            'Puntaje': [f"{puntaje}/10"], 'Intento': [intento],
            'Fecha': [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")]
        })
        df_final = pd.concat([df_existente, nuevo], ignore_index=True)
        conn.update(data=df_final)
        return True
    except: return False

# ==========================================
# 🖥️ INTERFAZ
# ==========================================
st.title("🎓 Evaluación de Capacitación")

# REGISTRO
if st.session_state.perfil is None:
    with st.container(border=True):
        st.subheader("📝 Registro de Datos")
        n = st.text_input("Nombre:")
        e = st.text_input("Correo:")
        t = st.text_input("Teléfono:")
        if st.button("Empezar Test", use_container_width=True):
            if n and e and t:
                st.session_state.perfil = {"n": n, "e": e, "t": t}
                st.rerun()
            else: st.warning("Completa los campos.")

# CUESTIONARIO
elif not st.session_state.aprobado:
    st.info(f"👤 {st.session_state.perfil['n']} | Intento: {st.session_state.intento}")
    
    with st.form("quiz"):
        respuestas = {}
        for p in preguntas_estaticas:
            st.markdown(f"### {p['pregunta']}")
            
            # PISTA CORREGIDA (Visible por defecto en expander)
            with st.expander("💡 Toca aquí para ver la pista"):
                st.markdown(f'<div class="pista-style">{p["pista"]}</div>', unsafe_allow_html=True)
            
            respuestas[p['id']] = st.radio("Elige una:", p['opciones'], index=None, key=f"q{p['id']}", label_visibility="collapsed")
            
            # ANIMACIÓN VERDE / ROJO (Solo se muestra tras enviar si falló)
            if st.session_state.mostrar_resultados:
                if respuestas[p['id']] == p['correcta']:
                    st.success("✅ ¡Correcta!")
                elif respuestas[p['id']] is not None:
                    st.error(f"❌ Incorrecta. La respuesta era: {p['correcta']}")
            st.write("---")

        if st.form_submit_button("Finalizar Evaluación", use_container_width=True):
            if None in respuestas.values():
                st.warning("Responde todas.")
            else:
                puntos = sum(1 for p in preguntas_estaticas if respuestas[p['id']] == p['correcta'])
                if puntos == 10:
                    if guardar_datos(st.session_state.perfil['n'], st.session_state.perfil['e'], st.session_state.perfil['t'], puntos, st.session_state.intento):
                        st.session_state.aprobado = True
                        st.rerun()
                else:
                    st.session_state.mostrar_resultados = True
                    st.error(f"Puntaje: {puntos}/10. Revisa tus errores marcados en rojo arriba.")
                    st.session_state.intento += 1

# ÉXITO
else:
    st.success(f"🎊 ¡Felicidades {st.session_state.perfil['n']}! Aprobaste con 10/10.")
    st.balloons()
    if st.button("Reiniciar Test para nuevo usuario", use_container_width=True):
        st.session_state.perfil = None
        st.session_state.aprobado = False
        st.session_state.intento = 1
        st.session_state.mostrar_resultados = False
        st.rerun()

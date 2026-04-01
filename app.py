import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# ==========================================
# 🎨 CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Capacitación Interactiva", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .avatar-box { background-color: #F0F9FF; padding: 20px; border-radius: 15px; border-left: 5px solid #0EA5E9; margin-bottom: 20px; font-size: 1.2rem; }
    .stRadio > label { font-weight: bold; font-size: 1.2rem; color: #1E3A8A; }
    .footer-info { color: #64748B; font-size: 0.9rem; margin-top: 50px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📚 BANCO DE PREGUNTAS
# ==========================================
if 'lista_preguntas' not in st.session_state:
    st.session_state.lista_preguntas = [
        {"id": 1, "tipo": "radio", "pregunta": "¿Qué significa EPP?", "opciones": ["Protección Personal", "Procesos Primarios"], "correcta": "Protección Personal", "pista": "Casco y guantes."},
        {"id": 2, "tipo": "texto", "pregunta": "Escriba la unidad de la Resistencia:", "correcta": "Ohmios", "pista": "Letra Omega."},
        {"id": 3, "tipo": "radio", "pregunta": "¿Color de tubería contra incendio?", "opciones": ["Verde", "Rojo"], "correcta": "Rojo", "pista": "Emergencia."},
        {"id": 4, "tipo": "texto", "pregunta": "¿Cómo se llama el bloqueo de seguridad?", "correcta": "Lockout", "pista": "Empieza con L."},
        # Agrega las otras 6 aquí siguiendo el formato...
    ]

# ==========================================
# ⚙️ VARIABLES DE CONTROL DE FLUJO
# ==========================================
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'indice_pregunta' not in st.session_state: st.session_state.indice_pregunta = 0
if 'aprobado' not in st.session_state: st.session_state.aprobado = False
if 'feedback_avatar' not in st.session_state: st.session_state.feedback_avatar = "¡Hola! Soy tu tutor. ¡Empecemos con éxito! 🚀"
if 'aciertos_totales' not in st.session_state: st.session_state.aciertos_totales = 0
if 'intentos_totales' not in st.session_state: st.session_state.intentos_totales = 1

# ==========================================
# 💾 FUNCIÓN DE GUARDADO
# ==========================================
def guardar_final(nombre, email, telefono, intento):
    try:
        zona = pytz.timezone('America/Guayaquil')
        hora = datetime.now(zona).strftime("%Y-%m-%d %H:%M:%S")
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_ex = conn.read(ttl=0)
        nuevo = pd.DataFrame({
            'Nombre': [nombre], 'Correo': [email], 'Teléfono': [telefono],
            'Puntaje': ["10/10"], 'Intento': [intento], 'Fecha': [hora]
        })
        df_f = pd.concat([df_ex, nuevo], ignore_index=True)
        conn.update(data=df_f)
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# ==========================================
# 🖥️ INTERFAZ DE USUARIO
# ==========================================

# 1. REGISTRO
if st.session_state.perfil is None:
    st.title("🎓 Registro de Capacitación")
    with st.form("reg"):
        n = st.text_input("Nombre:")
        e = st.text_input("Correo:")
        t = st.text_input("Teléfono:")
        if st.form_submit_button("Entrar al Curso"):
            if n and e and t:
                st.session_state.perfil = {"n": n, "e": e, "t": t}
                st.rerun()
            else: st.warning("Completa tus datos.")

# 2. EVALUACIÓN PASO A PASO
elif not st.session_state.aprobado:
    # Mostramos el AVATAR siempre arriba
    st.markdown(f'<div class="avatar-box"><b>Tutor Virtual:</b><br>{st.session_state.feedback_avatar}</div>', unsafe_allow_html=True)
    
    # Obtenemos la pregunta actual de la lista (que puede cambiar de orden)
    lista = st.session_state.lista_preguntas
    idx = st.session_state.indice_pregunta
    
    if idx < len(lista):
        p = lista[idx]
        st.subheader(f"Pregunta {idx + 1} de {len(lista)}")
        st.progress((idx) / len(lista))
        
        st.write(f"### {p['pregunta']}")
        with st.expander("💡 Ver Pista"): st.info(p['pista'])
        
        # Entrada según tipo
        res_usuario = None
        if p['tipo'] == "radio":
            res_usuario = st.radio("Elige:", p['opciones'], index=None, key=f"r_{p['id']}", label_visibility="collapsed")
        else:
            res_usuario = st.text_input("Escribe:", key=f"t_{p['id']}", placeholder="Escribe aquí...").strip()

        # BOTÓN PARA VALIDAR ESTA PREGUNTA
        if st.button("Comprobar Respuesta 🔍", use_container_width=True):
            if not res_usuario:
                st.warning("Escribe o selecciona algo primero.")
            else:
                es_correcta = str(res_usuario).lower() == str(p['correcta']).lower()
                
                if es_correcta:
                    st.session_state.feedback_avatar = "¡Excelente! Sabía que podías. ¡Vamos a la siguiente! ✨"
                    st.session_state.aciertos_totales += 1
                    st.session_state.indice_pregunta += 1
                    st.success("¡CORRECTO!")
                    st.rerun()
                else:
                    st.session_state.feedback_avatar = "¡Uy! Casi lo tienes, pero fallaste. No te preocupes, la repetiremos al final para que aprendas bien. 🧠"
                    # MOVER AL FINAL: Quitamos de la posición actual y ponemos al final
                    pregunta_fallada = st.session_state.lista_preguntas.pop(idx)
                    st.session_state.lista_preguntas.append(pregunta_fallada)
                    st.error("INCORRECTO. Pasamos a la siguiente, esta volverá al final.")
                    # No sumamos al índice porque al hacer pop, la siguiente pregunta ahora ocupa el lugar de la actual
                    st.rerun()
    else:
        # Si llegamos aquí es porque terminamos la lista
        with st.spinner("¡Has completado todas! Guardando registro..."):
            if guardar_final(st.session_state.perfil['n'], st.session_state.perfil['e'], st.session_state.perfil['t'], st.session_state.intentos_totales):
                st.session_state.aprobado = True
                st.rerun()

# 3. ÉXITO
else:
    st.balloons()
    st.success(f"¡Felicidades {st.session_state.perfil['n']}! Has superado el reto.")
    st.markdown(f'<div class="avatar-box"><b>Tutor Virtual:</b><br>¡Increíble trabajo! Has demostrado que dominas el tema perfectamente. 🏆</div>', unsafe_allow_html=True)
    
    if st.button("Reiniciar Sistema"):
        # Limpieza total
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

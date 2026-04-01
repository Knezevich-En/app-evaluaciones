import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz
import time # Para pausar la animación
import re # Para validar correo y teléfono

# ==========================================
# 🎨 CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Capacitación Interactiva Pro", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .avatar-box { background-color: #F0F9FF; padding: 20px; border-radius: 15px; border-left: 5px solid #0EA5E9; margin-bottom: 20px; font-size: 1.2rem; min-height: 80px; }
    .stRadio > label { font-weight: bold; font-size: 1.2rem; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ FUNCIONES DE VALIDACIÓN
# ==========================================
def es_correo_valido(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

def es_telefono_valido(tel):
    # Valida que sean solo números y tenga entre 7 y 12 dígitos
    return tel.isdigit() and 7 <= len(tel) <= 12

# ==========================================
# 📚 BANCO DE PREGUNTAS (Sigue este formato)
# ==========================================
if 'lista_preguntas' not in st.session_state:
    st.session_state.lista_preguntas = [
        {"id": 1, "tipo": "radio", "pregunta": "¿Qué significa EPP?", "opciones": ["Protección Personal", "Procesos Primarios"], "correcta": "Protección Personal", "pista": "Casco y guantes."},
        {"id": 2, "tipo": "texto", "pregunta": "Escriba la unidad de la Resistencia:", "correcta": "Ohmios", "pista": "Letra Omega."},
        {"id": 3, "tipo": "radio", "pregunta": "¿Color de tubería contra incendio?", "opciones": ["Verde", "Rojo"], "correcta": "Rojo", "pista": "Emergencia."},
        {"id": 4, "tipo": "texto", "pregunta": "¿Cómo se llama el bloqueo de seguridad?", "correcta": "Lockout", "pista": "Empieza con L."},
    ]

# Inicialización de estados
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'indice_pregunta' not in st.session_state: st.session_state.indice_pregunta = 0
if 'aprobado' not in st.session_state: st.session_state.aprobado = False
if 'feedback_avatar' not in st.session_state: st.session_state.feedback_avatar = "¡Hola! Soy tu tutor. Ingresa tus datos para comenzar. 😊"
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
        st.error(f"Error de guardado: {e}")
        return False

# ==========================================
# 🖥️ INTERFAZ DE USUARIO
# ==========================================

# 1. REGISTRO CON VALIDACIÓN
if st.session_state.perfil is None:
    st.title("🎓 Registro de Capacitación")
    with st.form("reg"):
        n = st.text_input("Nombre y Apellido:")
        e = st.text_input("Correo Electrónico (ejemplo@mail.com):")
        t = st.text_input("Teléfono (Solo números):")
        
        if st.form_submit_button("Entrar al Curso"):
            if not n or not e or not t:
                st.warning("⚠️ Todos los campos son obligatorios.")
            elif not es_correo_valido(e):
                st.error("❌ El formato del correo no es válido.")
            elif not es_telefono_valido(t):
                st.error("❌ El teléfono debe contener solo números (7-12 dígitos).")
            else:
                st.session_state.perfil = {"n": n, "e": e, "t": t}
                st.rerun()

# 2. EVALUACIÓN PASO A PASO
elif not st.session_state.aprobado:
    st.markdown(f'<div class="avatar-box"><b>Tutor Virtual:</b><br>{st.session_state.feedback_avatar}</div>', unsafe_allow_html=True)
    
    lista = st.session_state.lista_preguntas
    idx = st.session_state.indice_pregunta
    
    if idx < len(lista):
        p = lista[idx]
        st.subheader(f"Pregunta {idx + 1} de {len(lista)}")
        st.progress((idx) / len(lista))
        
        st.write(f"### {p['pregunta']}")
        with st.expander("💡 Ver Pista"): st.info(p['pista'])
        
        res_usuario = None
        if p['tipo'] == "radio":
            res_usuario = st.radio("Elige:", p['opciones'], index=None, key=f"r_{p['id']}", label_visibility="collapsed")
        else:
            res_usuario = st.text_input("Escribe tu respuesta:", key=f"t_{p['id']}").strip()

        if st.button("Comprobar Respuesta 🔍", use_container_width=True):
            if not res_usuario:
                st.warning("Escribe o selecciona algo primero.")
            else:
                es_correcta = str(res_usuario).lower() == str(p['correcta']).lower()
                
                if es_correcta:
                    st.success("✅ ¡CORRECTO!")
                    st.session_state.feedback_avatar = "¡Excelente! Lo lograste. ✨"
                    # Pausa para que el usuario vea el mensaje
                    time.sleep(1.5) 
                    st.session_state.indice_pregunta += 1
                    st.rerun()
                else:
                    st.error("❌ INCORRECTO")
                    st.session_state.feedback_avatar = "Esa no era... No te preocupes, la repetiremos al final. 🧠"
                    time.sleep(2)
                    # Mover al final
                    pregunta_fallada = st.session_state.lista_preguntas.pop(idx)
                    st.session_state.lista_preguntas.append(pregunta_fallada)
                    st.rerun()
    else:
        with st.spinner("Guardando tus resultados..."):
            if guardar_final(st.session_state.perfil['n'], st.session_state.perfil['e'], st.session_state.perfil['t'], st.session_state.intentos_totales):
                st.session_state.aprobado = True
                st.rerun()

# 3. ÉXITO
else:
    st.balloons()
    st.success(f"¡Felicidades {st.session_state.perfil['n']}! 🏆")
    st.markdown(f'<div class="avatar-box"><b>Tutor Virtual:</b><br>¡Has completado el entrenamiento con éxito! Tus datos están en el sistema.</div>', unsafe_allow_html=True)
    
    if st.button("Finalizar y salir"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

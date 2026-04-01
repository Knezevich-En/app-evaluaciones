import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_lottie import st_lottie # Librería para animaciones
import requests
from datetime import datetime
import pytz
import time
import re

# ==========================================
# 🎨 CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Capacitación Interactiva Pro", page_icon="🎓", layout="centered")

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

# URLs de animaciones profesionales (puedes cambiarlas luego)
lottie_hello = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_V9t630.json") # Robot saludando
lottie_success = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_atlup9v6.json") # Check verde animado
lottie_fail = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_h39fbuas.json") # Robot confundido

st.markdown("""
    <style>
    .avatar-text { background-color: #F8FAFC; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; font-size: 1.1rem; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ FUNCIONES DE VALIDACIÓN
# ==========================================
def es_correo_valido(correo):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo) is not None

def es_telefono_valido(tel):
    return tel.isdigit() and 7 <= len(tel) <= 12

# ==========================================
# 📚 BANCO DE PREGUNTAS
# ==========================================
if 'lista_preguntas' not in st.session_state:
    st.session_state.lista_preguntas = [
        {"id": 1, "tipo": "radio", "pregunta": "¿Qué significa EPP?", "opciones": ["Protección Personal", "Procesos Primarios"], "correcta": "Protección Personal", "pista": "Casco y guantes."},
        {"id": 2, "tipo": "texto", "pregunta": "Escriba la unidad de la Resistencia:", "correcta": "Ohmios", "pista": "Letra Omega."},
        {"id": 3, "tipo": "radio", "pregunta": "¿Color de tubería contra incendio?", "opciones": ["Verde", "Rojo"], "correcta": "Rojo", "pista": "Emergencia."},
        {"id": 4, "tipo": "texto", "pregunta": "¿Cómo se llama el bloqueo de seguridad?", "correcta": "Lockout", "pista": "Empieza con L."},
    ]

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'indice_pregunta' not in st.session_state: st.session_state.indice_pregunta = 0
if 'aprobado' not in st.session_state: st.session_state.aprobado = False
if 'estado_animacion' not in st.session_state: st.session_state.estado_animacion = "hello"
if 'feedback_texto' not in st.session_state: st.session_state.feedback_texto = "¡Hola! Soy tu asistente de capacitación. Completa tus datos para iniciar."

# ==========================================
# 💾 GUARDADO
# ==========================================
def guardar_final(nombre, email, telefono):
    try:
        zona = pytz.timezone('America/Guayaquil')
        hora = datetime.now(zona).strftime("%Y-%m-%d %H:%M:%S")
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_ex = conn.read(ttl=0)
        nuevo = pd.DataFrame({'Nombre':[nombre],'Correo':[email],'Teléfono':[telefono],'Puntaje':["10/10"],'Fecha':[hora]})
        df_f = pd.concat([df_ex, nuevo], ignore_index=True)
        conn.update(data=df_f)
        return True
    except: return False

# ==========================================
# 🖥️ INTERFAZ
# ==========================================

# 1. REGISTRO
if st.session_state.perfil is None:
    st.title("🎓 Registro de Usuario")
    col1, col2 = st.columns([1, 2])
    with col1:
        st_lottie(lottie_hello, height=150, key="hello")
    with col2:
        st.markdown(f'<div class="avatar-text">{st.session_state.feedback_texto}</div>', unsafe_allow_html=True)
    
    with st.form("reg"):
        n = st.text_input("Nombre y Apellido:")
        e = st.text_input("Correo:")
        t = st.text_input("Teléfono:")
        if st.form_submit_button("Empezar"):
            if n and es_correo_valido(e) and es_telefono_valido(t):
                st.session_state.perfil = {"n":n, "e":e, "t":t}
                st.rerun()
            else: st.error("Revisa que los datos estén completos y correctos.")

# 2. TEST
elif not st.session_state.aprobado:
    # Avatar con animación dinámica
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.session_state.estado_animacion == "success":
            st_lottie(lottie_success, height=120, loop=False)
        elif st.session_state.estado_animacion == "fail":
            st_lottie(lottie_fail, height=120, loop=False)
        else:
            st_lottie(lottie_hello, height=120)
            
    with col2:
        st.markdown(f'<div class="avatar-text">{st.session_state.feedback_texto}</div>', unsafe_allow_html=True)

    lista = st.session_state.lista_preguntas
    idx = st.session_state.indice_pregunta
    
    if idx < len(lista):
        p = lista[idx]
        st.subheader(f"Pregunta {idx + 1} de {len(lista)}")
        st.write(f"### {p['pregunta']}")
        
        if p['tipo'] == "radio":
            res = st.radio("Elige:", p['opciones'], index=None, key=f"r_{p['id']}", label_visibility="collapsed")
        else:
            res = st.text_input("Escribe:", key=f"t_{p['id']}").strip()

        if st.button("Comprobar", use_container_width=True):
            if res:
                if str(res).lower() == str(p['correcta']).lower():
                    st.session_state.estado_animacion = "success"
                    st.session_state.feedback_texto = "¡Excelente! Respuesta correcta. 🎯"
                    st.success("¡Muy bien!")
                    time.sleep(2)
                    st.session_state.indice_pregunta += 1
                    st.session_state.estado_animacion = "hello"
                    st.rerun()
                else:
                    st.session_state.estado_animacion = "fail"
                    st.session_state.feedback_texto = "¡Oh no! Esa no era. La repetiremos luego. 🔄"
                    st.error("Incorrecto.")
                    time.sleep(2)
                    fallada = st.session_state.lista_preguntas.pop(idx)
                    st.session_state.lista_preguntas.append(fallada)
                    st.session_state.estado_animacion = "hello"
                    st.rerun()
    else:
        if guardar_final(st.session_state.perfil['n'], st.session_state.perfil['e'], st.session_state.perfil['t']):
            st.session_state.aprobado = True
            st.rerun()

# 3. FIN
else:
    st.balloons()
    st.success("¡Completado!")
    if st.button("Reiniciar"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz
import time

# ==========================================
# 🎨 DISEÑO DE INTERFAZ ESTILO DASHBOARD (REPLICA)
# ==========================================
st.set_page_config(page_title="WAVIN - Mantenimiento Autónomo", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
    /* Fondo principal y fuentes */
    [data-testid="stAppViewContainer"] {
        background-color: #0B1E33;
        color: white;
    }
    
    /* Contenedor tipo Tarjeta (Panel Central) */
    .main-card {
        background-color: #162B46;
        border-radius: 20px;
        padding: 30px;
        border: 1px solid #1E3A5F;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Burbuja del Avatar (Izquierda) */
    .avatar-bubble {
        background-color: #0EA5E9;
        border-radius: 15px;
        padding: 15px;
        color: white;
        font-weight: 500;
        position: relative;
        margin-bottom: 20px;
    }
    
    /* Efecto de Luces en las Opciones */
    .stRadio div[role="radiogroup"] > label {
        background-color: #1F3654;
        border: 1px solid #2D4A77;
        padding: 15px !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        transition: 0.3s;
    }
    .stRadio div[role="radiogroup"] > label:hover {
        border-color: #0EA5E9;
        background-color: #254166;
    }

    /* Botón Siguiente Estilo Neón */
    .stButton > button {
        background: linear_gradient(90deg, #00C2FF, #0075FF);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 10px 40px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Barra de Progreso */
    .stProgress > div > div > div > div {
        background-color: #00C2FF;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📚 PREGUNTAS (Basadas en la imagen LOTO)
# ==========================================
if 'lista_preguntas' not in st.session_state:
    st.session_state.lista_preguntas = [
        {"id": 1, "tipo": "radio", "pregunta": "LOTO: Lock Out / Tag Out", "sub": "3. SEGURIDAD — LOTO", "texto": "Procedimiento obligatorio para aislar energías peligrosas antes de realizar mantenimiento o limpieza.", "opciones": ["Aislar todas las fuentes eléctricas antes de iniciar", "Dejar la llave puesta para el siguiente turno", "Operar sin etiquetas de advertencia"], "correcta": "Aislar todas las fuentes eléctricas antes de iniciar", "pista": "¡EL LOTO es crítico! Antes de limpiar hay que aislar TODAS las fuentes."},
        # Aquí puedes agregar más según el dashboard
    ]

if 'indice' not in st.session_state: st.session_state.indice = 0
if 'intentos' not in st.session_state: st.session_state.intentos = 1
if 'perfil' not in st.session_state: st.session_state.perfil = None

# ==========================================
# 🖥️ LÓGICA DE NAVEGACIÓN
# ==========================================

# 1. REGISTRO (Estilo elegante)
if st.session_state.perfil is None:
    st.title("⚙️ Sistema de Control de Capacitación")
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            n = st.text_input("Nombre y Apellido")
            e = st.text_input("Correo")
        with col2:
            t = st.text_input("Teléfono")
        
        if st.button("INGRESAR AL SISTEMA"):
            if n and e and t:
                st.session_state.perfil = {"n":n, "e":e, "t":t}
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 2. INTERFAZ TIPO DASHBOARD
else:
    lista = st.session_state.lista_preguntas
    idx = st.session_state.indice
    
    if idx < len(lista):
        p = lista[idx]
        
        # HEADER SUPERIOR
        col_logo, col_info, col_prog = st.columns([1, 2, 2])
        with col_logo:
            st.subheader("⚙️ WAVIN")
        with col_info:
            st.write(f"**Mantenimiento Autónomo** \nPaso 1 · Limpieza Inicial")
        with col_prog:
            st.write(f"**{idx + 1}/{len(lista)}**")
            st.progress((idx + 1) / len(lista))

        st.write("---")

        # CUERPO CENTRAL (Dos Columnas como la imagen)
        col_avatar, col_content = st.columns([1, 2])
        
        with col_avatar:
            st.markdown(f'<div class="avatar-bubble">{p["pista"]}</div>', unsafe_allow_html=True)
            # Aquí puedes poner una imagen de tu avatar de Blender o un icono
            st.image("https://cdn-icons-png.flaticon.com/512/1904/1904562.png", width=150)
            
            st.markdown("""
                <div style='font-size: 0.8rem; color: #64748B;'>
                SECCIONES:<br>
                EPP 🧤 | LOTO 🔒 | 5 Sentidos 👀
                </div>
            """, unsafe_allow_html=True)

        with col_content:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.caption(p["sub"])
            st.title(p["pregunta"])
            st.write(p["texto"])
            
            res = st.radio("Seleccione la acción correcta:", p["opciones"], index=None, key=f"q_{p['id']}")
            
            col_btns1, col_btns2 = st.columns([1, 1])
            with col_btns2:
                if st.button("Siguiente ▶️", use_container_width=True):
                    if res == p["correcta"]:
                        st.success("✅ Logrado")
                        time.sleep(1)
                        st.session_state.indice += 1
                        st.rerun()
                    else:
                        st.error("❌ Fallo de Seguridad")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.balloons()
        st.success("Capacitación Completada")
        if st.button("Reiniciar"):
            st.session_state.perfil = None
            st.session_state.indice = 0
            st.rerun()

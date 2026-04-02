import streamlit as st
import pandas as pd
import time

# ==========================================
# 🎨 DISEÑO DE INTERFAZ ESTILO DASHBOARD
# ==========================================
st.set_page_config(page_title="WAVIN - Mantenimiento Autónomo", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
    /* Fondo principal y fuentes */
    [data-testid="stAppViewContainer"] {
        background-color: #0B1E33;
        color: white;
    }
    
    /* Contenedor tipo Tarjeta */
    .main-card {
        background-color: #162B46;
        border-radius: 20px;
        padding: 30px;
        border: 1px solid #1E3A5F;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Burbuja del Avatar / Pista */
    .avatar-bubble {
        background-color: #0EA5E9;
        border-radius: 15px;
        padding: 15px;
        color: white;
        font-weight: 500;
        margin-bottom: 20px;
        border-left: 5px solid #00C2FF;
    }
    
    /* Estilo de los Radio Buttons */
    .stRadio div[role="radiogroup"] > label {
        background-color: #1F3654;
        border: 1px solid #2D4A77;
        padding: 15px !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        transition: 0.3s;
        color: white !important;
    }
    .stRadio div[role="radiogroup"] > label:hover {
        border-color: #0EA5E9;
        background-color: #254166;
    }

    /* Botón Siguiente */
    .stButton > button {
        background: linear-gradient(90deg, #00C2FF, #0075FF);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 10px 40px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton > button:hover {
        box-shadow: 0 0 15px #00C2FF;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📚 BANCO DE PREGUNTAS
# ==========================================
if 'lista_preguntas' not in st.session_state:
    st.session_state.lista_preguntas = [
        {
            "id": 1, 
            "sub": "3. SEGURIDAD — LOTO", 
            "pregunta": "LOTO: Lock Out / Tag Out", 
            "texto": "Procedimiento obligatorio para aislar energías peligrosas antes de realizar mantenimiento.", 
            "opciones": ["Aislar todas las fuentes eléctricas antes de iniciar", "Dejar la llave puesta", "Operar sin etiquetas"], 
            "correcta": "Aislar todas las fuentes eléctricas antes de iniciar", 
            "pista": "¡Seguridad Primero! El LOTO exige el bloqueo TOTAL de energías."
        },
        {
            "id": 2, 
            "sub": "1. LIMPIEZA — EPP", 
            "pregunta": "Equipo de Protección Personal", 
            "texto": "Al realizar limpieza inicial en la extrusora, ¿cuál es el EPP indispensable?", 
            "opciones": ["Guantes de nitrilo y gafas", "Ropa de calle", "Solo casco"], 
            "correcta": "Guantes de nitrilo y gafas", 
            "pista": "Protege tus manos y ojos de residuos industriales."
        }
    ]

# Inicializar estados
if 'indice' not in st.session_state: st.session_state.indice = 0
if 'perfil' not in st.session_state: st.session_state.perfil = None

# ==========================================
# 🖥️ LÓGICA DE NAVEGACIÓN
# ==========================================

# 1. PANTALLA DE REGISTRO
if st.session_state.perfil is None:
    st.title("⚙️ Sistema de Control de Capacitación WAVIN")
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        n = st.text_input("Nombre y Apellido")
        e = st.text_input("Correo Institucional")
    with col2:
        t = st.text_input("Teléfono / Extensión")
        
    if st.button("INGRESAR AL SISTEMA"):
        if n and e and t:
            st.session_state.perfil = {"n":n, "e":e, "t":t}
            st.rerun()
        else:
            st.warning("⚠️ Por favor complete todos los campos.")
    st.markdown('</div>', unsafe_allow_html=True)

# 2. INTERFAZ DE EVALUACIÓN
else:
    lista = st.session_state.lista_preguntas
    idx = st.session_state.indice
    
    if idx < len(lista):
        p = lista[idx]
        
        # BARRA SUPERIOR DE PROGRESO
        col_logo, col_info, col_prog = st.columns([1, 2, 2])
        with col_logo:
            st.subheader("⚙️ WAVIN")
        with col_info:
            st.write(f"**Usuario:** {st.session_state.perfil['n']}")
        with col_prog:
            st.write(f"Progreso: {idx + 1}/{len(lista)}")
            st.progress((idx + 1) / len(lista))

        st.divider()

        # CUERPO CENTRAL
        col_side, col_main = st.columns([1, 2])
        
        with col_side:
            st.markdown(f'<div class="avatar-bubble"><b>Nota del Supervisor:</b><br>{p["pista"]}</div>', unsafe_allow_html=True)
            # Imagen estática del operador industrial (la que generamos)
            st.image("https://i.imgur.com/8pMvYmX.png", caption="Supervisor de Planta", use_container_width=True) 

        with col_main:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.caption(p["sub"])
            st.title(p["pregunta"])
            st.write(f"#### {p['texto']}")
            
            res = st.radio("Seleccione la respuesta correcta:", p["opciones"], index=None, key=f"q_{idx}")
            
            if st.button("Siguiente ▶️"):
                if res == p["correcta"]:
                    st.success("✅ RESPUESTA CORRECTA")
                    time.sleep(1.2)
                    st.session_state.indice += 1
                    st.rerun()
                elif res is None:
                    st.warning("Seleccione una opción antes de continuar.")
                else:
                    st.error("❌ FALLO DE SEGURIDAD. Revisa la pista del supervisor.")
            st.markdown('</div>', unsafe_allow_html=True)

    # 3. FINALIZACIÓN
    else:
        st.balloons()
        st.markdown('<div class="main-card" style="text-align: center;">', unsafe_allow_html=True)
        st.title("¡Capacitación Completada!")
        st.write(f"Felicidades **{st.session_state.perfil['n']}**, has superado el módulo de Mantenimiento Autónomo.")
        if st.button("Finalizar y Salir"):
            st.session_state.perfil = None
            st.session_state.indice = 0
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

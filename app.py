import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PyPDF2 import PdfReader
from pptx import Presentation
import json

# ==========================================
# 🎨 CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Capacitación IA - Arturo", page_icon="🤖", layout="centered")

# Estilos para que se vea profesional
st.markdown("""
    <style>
    .stRadio > label { font-weight: bold; color: #1E3A8A; font-size: 1.1rem; }
    div[data-testid="stExpander"] { border: 1px solid #D1D5DB; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🧠 CONFIGURACIÓN DE IA (SINTAXIS ESTABLE)
# ==========================================
try:
    # Usamos la configuración más simple para evitar el error 404
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"⚠️ Error de API: {e}")

# ==========================================
# ⚙️ FUNCIONES DE APOYO
# ==========================================

def extraer_texto(archivo):
    texto = ""
    if archivo.name.endswith('.pdf'):
        reader = PdfReader(archivo)
        for page in reader.pages:
            texto += page.extract_text() or ""
    elif archivo.name.endswith('.pptx'):
        prs = Presentation(archivo)
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texto += shape.text + " "
    return texto

def generar_preguntas(texto_base):
    # Prompt optimizado para recibir JSON puro
    prompt = f"""
    Genera un examen de 10 preguntas de opción múltiple basado en este texto: {texto_base[:15000]}
    Responde UNICAMENTE en formato JSON plano (lista de objetos). 
    No incluyas markdown, ni la palabra 'json'.
    Formato: [{{"id":1, "pregunta":"...", "opciones":["A","B","C"], "correcta":"A", "pista":"..."}}]
    """
    try:
        response = model.generate_content(prompt)
        # Limpiamos posibles etiquetas de markdown que la IA a veces agrega
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        st.error(f"Error al procesar la respuesta de la IA: {e}")
        return None

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
# 🖥️ INTERFAZ DE USUARIO (UI)
# ==========================================

if 'preguntas' not in st.session_state: st.session_state.preguntas = None
if 'user' not in st.session_state: st.session_state.user = None
if 'win' not in st.session_state: st.session_state.win = False
if 'tries' not in st.session_state: st.session_state.tries = 1

st.title("🎓 Evaluación con IA Generativa")

# BARRA LATERAL PARA EL INSTRUCTOR
with st.sidebar:
    st.header("⚙️ Panel de Control")
    doc = st.file_uploader("Cargar Material (PDF/PPTX)", type=["pdf", "pptx"])
    if doc and st.button("Generar Examen"):
        with st.spinner("La IA está leyendo el documento..."):
            txt = extraer_texto(doc)
            st.session_state.preguntas = generar_preguntas(txt)
            if st.session_state.preguntas:
                st.success("¡Examen de 10 preguntas listo!")
                st.session_state.win = False

# CUERPO PRINCIPAL
if st.session_state.preguntas:
    if st.session_state.user is None:
        name = st.text_input("Ingresa tu Nombre para empezar:")
        if st.button("Iniciar") and name:
            st.session_state.user = name
            st.rerun()

    elif not st.session_state.win:
        st.info(f"👤 Estudiante: {st.session_state.user} | 🔄 Intento: {st.session_state.tries}")
        
        with st.form("examen_ia"):
            user_answers = {}
            for p in st.session_state.preguntas:
                st.write(f"### {p['pregunta']}")
                with st.expander("💡 Pista"):
                    st.write(p['pista'])
                
                user_answers[p['id']] = st.radio(
                    "Selecciona:", p['opciones'], index=None, key=f"q{p['id']}", label_visibility="collapsed"
                )
                st.write("---")
            
            if st.form_submit_button("Enviar Evaluación", use_container_width=True):
                if None in user_answers.values():
                    st.warning("Responde todas las preguntas.")
                else:
                    score = sum(1 for p in st.session_state.preguntas if user_answers[p['id']] == p['correcta'])
                    if score == 10:
                        if guardar_datos(st.session_state.user, score, st.session_state.tries):
                            st.session_state.win = True
                            st.rerun()
                    else:
                        st.error(f"Puntaje: {score}/10. ¡Debes sacar 10 para aprobar!")
                        st.session_state.tries += 1
else:
    st.warning("Esperando que el instructor cargue un archivo en el menú lateral.")

if st.session_state.win:
    st.success(f"🎊 ¡Felicidades {st.session_state.user}! Has aprobado.")
    st.balloons()
    if st.button("Reiniciar"):
        st.session_state.user = None
        st.session_state.win = False
        st.session_state.tries = 1
        st.rerun()

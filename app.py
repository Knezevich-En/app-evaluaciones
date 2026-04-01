import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PyPDF2 import PdfReader
from pptx import Presentation
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Capacitación Arturo", page_icon="🎓")

# --- CONEXIÓN IA (Sintaxis Forzada Estable) ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Forzamos el nombre del modelo sin prefijos extraños
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error de API: {e}")

# --- FUNCIONES ---
def extraer_texto(archivo):
    texto = ""
    try:
        if archivo.name.endswith('.pdf'):
            reader = PdfReader(archivo)
            for page in reader.pages: texto += page.extract_text() or ""
        elif archivo.name.endswith('.pptx'):
            prs = Presentation(archivo)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"): texto += shape.text + " "
    except: st.error("Error al leer el archivo.")
    return texto

def generar_examen(contenido):
    prompt = f"""
    Crea 10 preguntas de opción múltiple basadas en este texto: {contenido[:10000]}
    Devuelve SOLO un JSON (lista de objetos) con: id, pregunta, opciones (lista), correcta, pista.
    No uses etiquetas ```json ni nada extra.
    """
    try:
        # Aquí forzamos la llamada para evitar el error 404
        response = model.generate_content(prompt)
        # Limpieza manual del texto por si la IA agrega basura
        txt = response.text.strip()
        if txt.startswith("```"):
            txt = txt.split("```")[1]
            if txt.startswith("json"): txt = txt[4:]
        return json.loads(txt)
    except Exception as e:
        st.error(f"Error técnico de la IA: {e}")
        return None

def guardar(nombre, puntaje, intento):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        nuevo = pd.DataFrame({'Nombre':[nombre], 'Puntaje':[f"{puntaje}/10"], 'Intento':[intento]})
        df_f = pd.concat([df, nuevo], ignore_index=True)
        conn.update(data=df_f)
        return True
    except: return False

# --- UI ---
if 'preg' not in st.session_state: st.session_state.preg = None
if 'user' not in st.session_state: st.session_state.user = None
if 'aprobado' not in st.session_state: st.session_state.aprobado = False
if 'intento' not in st.session_state: st.session_state.intento = 1

st.title("🎓 Sistema de Capacitación")

with st.sidebar:
    st.header("Admin")
    archivo = st.file_uploader("Subir PDF/PPTX", type=["pdf", "pptx"])
    if archivo and st.button("Generar Examen"):
        with st.spinner("IA procesando..."):
            texto = extraer_texto(archivo)
            st.session_state.preg = generar_examen(texto)
            if st.session_state.preg: st.success("¡Listo!")

if st.session_state.preg:
    if not st.session_state.user:
        n = st.text_input("Tu nombre:")
        if st.button("Empezar") and n:
            st.session_state.user = n
            st.rerun()
    elif not st.session_state.aprobado:
        st.write(f"Estudiante: {st.session_state.user} | Intento: {st.session_state.intento}")
        with st.form("test"):
            resp = {}
            for p in st.session_state.preg:
                st.write(f"**{p['pregunta']}**")
                with st.expander("Pista"): st.info(p['pista'])
                resp[p['id']] = st.radio("Opción:", p['opciones'], key=f"p{p['id']}", index=None)
            if st.form_submit_button("Enviar"):
                nota = sum(1 for p in st.session_state.preg if resp.get(p['id']) == p['correcta'])
                if nota == 10:
                    if guardar(st.session_state.user, nota, st.session_state.intento):
                        st.session_state.aprobado = True
                        st.balloons()
                        st.rerun()
                else:
                    st.error(f"Nota: {nota}/10. ¡Inténtalo de nuevo!")
                    st.session_state.intento += 1

if st.session_state.aprobado:
    st.success("¡Aprobado!")
    if st.button("Reiniciar"):
        st.session_state.user = None
        st.session_state.aprobado = False
        st.rerun()

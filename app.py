import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PyPDF2 import PdfReader
from pptx import Presentation
import json

# ==========================================
# 🎨 CONFIGURACIÓN Y ESTILOS VISUALES
# ==========================================
st.set_page_config(page_title="Capacitación Inteligente", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    .stRadio > label { font-weight: bold; font-size: 1.1rem; color: #1E3A8A; }
    .stAlert { border-radius: 12px; }
    div[data-testid="stExpander"] { border: 1px solid #D1D5DB; border-radius: 10px; background-color: #F9FAFB; }
    </style>
    """, unsafe_allow_html=True)
# ==========================================
# 🧠 CONFIGURACIÓN DE IA (MÁXIMA COMPATIBILIDAD)
# ==========================================
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Forzamos el uso de la versión estable v1 para evitar el error 404
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        generation_config={
            "temperature": 0.7,
            "response_mime_type": "application/json",
        }
    )
    # Este comando extra asegura que usemos la dirección correcta
    model._client_options = {"api_version": "v1"} 
    
except Exception as e:
    st.error(f"⚠️ Error en la configuración: {e}")
    

# ==========================================
# ⚙️ FUNCIONES DE PROCESAMIENTO
# ==========================================

def extraer_texto_archivo(archivo):
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

def generar_preguntas_ia(texto_material):
    prompt = f"""
    Basado en este contenido de capacitación: {texto_material[:15000]}
    Genera 10 preguntas de opción múltiple. 
    Responde ÚNICAMENTE en formato JSON (una lista de objetos).
    Cada objeto debe tener: "id", "pregunta", "opciones" (lista de 3), "correcta" (texto exacto de la opción) y "pista".
    Asegúrate de que las preguntas sean profesionales y desafiantes.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error al generar preguntas: {e}")
        return None

def guardar_resultado_final(nombre, puntaje, intento):
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
    except Exception as e:
        st.error(f"Error al guardar en Google Sheets: {e}")
        return False

# ==========================================
# 🖥️ FLUJO DE LA APLICACIÓN (UI)
# ==========================================

# Variables de Control en la Sesión
if 'preguntas_ia' not in st.session_state: st.session_state.preguntas_ia = None
if 'usuario' not in st.session_state: st.session_state.usuario = None
if 'aprobado' not in st.session_state: st.session_state.aprobado = False
if 'intento' not in st.session_state: st.session_state.intento = 1

st.title("🎓 Centro de Capacitación IA")
st.write("Carga tu material (PDF o PPTX) y deja que la IA genere la evaluación.")

# --- SECCIÓN ADMINISTRADOR ---
with st.sidebar:
    st.header("⚙️ Configuración")
    archivo_subido = st.file_uploader("Subir Material", type=["pdf", "pptx"])
    if archivo_subido and st.button("🚀 Generar / Actualizar Test"):
        with st.spinner("Analizando contenido..."):
            contenido = extraer_texto_archivo(archivo_subido)
            st.session_state.preguntas_ia = generar_preguntas_ia(contenido)
            if st.session_state.preguntas_ia:
                st.success("¡Examen listo con 10 preguntas!")
                st.session_state.aprobado = False # Resetear por si había uno anterior

# --- SECCIÓN ESTUDIANTE ---
if st.session_state.preguntas_ia:
    if st.session_state.usuario is None:
        st.subheader("👋 ¡Bienvenido!")
        nombre_input = st.text_input("Ingresa tu Nombre para comenzar:")
        if st.button("Empezar Evaluación") and nombre_input:
            st.session_state.usuario = nombre_input
            st.rerun()

    elif not st.session_state.aprobado:
        st.info(f"👤 **Evaluado:** {st.session_state.usuario}  |  🔄 **Intento:** {st.session_state.intento}")
        
        # Formulario del Test
        with st.form("evaluacion_ia"):
            respuestas_form = {}
            
            for p in st.session_state.preguntas_ia:
                st.markdown(f"### {p['pregunta']}")
                
                # Pista interactiva (Toque Profesional)
                with st.expander(f"¿Necesitas una pista? 💡"):
                    st.write(p['pista'])
                
                respuestas_form[p['id']] = st.radio(
                    "Selecciona la respuesta correcta:",
                    p['opciones'],
                    index=None,
                    key=f"preg_{p['id']}",
                    label_visibility="collapsed"
                )
                st.write("---")

            enviar = st.form_submit_button("✅ Finalizar Evaluación", use_container_width=True)

            if enviar:
                # Validar que todas estén respondidas
                if None in respuestas_form.values():
                    st.warning("⚠️ Por favor responde todas las preguntas.")
                else:
                    aciertos = sum(1 for p in st.session_state.preguntas_ia if respuestas_form[p['id']] == p['correcta'])
                    
                    if aciertos == 10:
                        with st.spinner("Registrando aprobación..."):
                            if guardar_resultado_final(st.session_state.usuario, aciertos, st.session_state.intento):
                                st.session_state.aprobado = True
                                st.balloons()
                                st.rerun()
                    else:
                        st.error(f"Obtuviste {aciertos}/10. Para aprobar necesitas 10/10. ¡Inténtalo de nuevo!")
                        st.session_state.intento += 1

else:
    st.warning("👈 Por favor, el instructor debe cargar un archivo PDF o PPTX en el menú lateral para generar el test.")

# --- PANTALLA DE ÉXITO ---
if st.session_state.aprobado:
    st.success(f"🎊 ¡Felicidades {st.session_state.usuario}! Has aprobado satisfactoriamente.")
    st.balloons()
    if st.button("Evaluar a otro usuario"):
        st.session_state.usuario = None
        st.session_state.aprobado = False
        st.session_state.intento = 1
        st.rerun()

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PyPDF2 import PdfReader
import json

# ==========================================
# 🎨 CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Capacitación IA", page_icon="🤖")

# Configurar IA de Google
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash-latest')
# ==========================================
# 🧠 LÓGICA DE ESTADO
# ==========================================
if 'preguntas_ia' not in st.session_state:
    st.session_state.preguntas_ia = None
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'aprobado' not in st.session_state:
    st.session_state.aprobado = False
if 'intento' not in st.session_state:
    st.session_state.intento = 1

# ==========================================
# 📂 FUNCIÓN: PROCESAR PDF Y GENERAR PREGUNTAS
# ==========================================
def generar_preguntas_con_ia(texto_pdf):
    prompt = f"""
    Basado en el siguiente texto de capacitación, genera 10 preguntas de opción múltiple para una evaluación profesional. 
    Devuelve la respuesta ÚNICAMENTE en formato JSON plano (una lista de objetos).
    Cada objeto debe tener: "id", "pregunta", "opciones" (lista de 3), "correcta" (el texto exacto) y "pista".
    Texto: {texto_pdf[:10000]} 
    """
    response = model.generate_content(prompt)
    # Limpiar la respuesta de la IA por si trae marcas de markdown
    json_clean = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(json_clean)

def guardar_datos(nombre, puntaje, intento):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_existente = conn.read(ttl=0)
        nuevo = pd.DataFrame({'Nombre': [nombre], 'Puntaje': [f"{puntaje}/10"], 'Intento': [intento]})
        df_final = pd.concat([df_existente, nuevo], ignore_index=True)
        conn.update(data=df_final)
        return True
    except: return False

# ==========================================
# 🖥️ INTERFAZ
# ==========================================
st.title("🎓 Sistema de Evaluación Inteligente")

# SECCIÓN ADMINISTRADOR: CARGAR DOCUMENTO
with st.expander("⚙️ Configuración del Test (Solo Instructor)"):
    archivo = st.file_uploader("Sube el PDF de la capacitación", type="pdf")
    if archivo and st.button("Generar nuevo examen con IA"):
        with st.spinner("La IA está analizando el documento y creando preguntas..."):
            reader = PdfReader(archivo)
            texto = ""
            for page in reader.pages: texto += page.extract_text()
            st.session_state.preguntas_ia = generar_preguntas_con_ia(texto)
            st.success("¡Examen generado exitosamente!")

# SECCIÓN USUARIO: EL TEST
if st.session_state.preguntas_ia:
    if st.session_state.usuario is None:
        nombre = st.text_input("Tu Nombre Completo:")
        if st.button("Empezar"):
            if nombre: 
                st.session_state.usuario = nombre
                st.rerun()
    
    elif not st.session_state.aprobado:
        st.write(f"👤 **{st.session_state.usuario}** | 🔄 Intento: **{st.session_state.intento}**")
        st.progress(st.session_state.intento / 5 if st.session_state.intento < 5 else 0.9)
        
        respuestas = {}
        with st.form("test_ia"):
            for p in st.session_state.preguntas_ia:
                st.markdown(f"#### {p['pregunta']}")
                with st.expander("💡 Ver pista"):
                    st.info(p['pista'])
                
                respuestas[p['id']] = st.radio(
                    "Selecciona una opción:", 
                    p['opciones'], 
                    index=None, 
                    key=f"q_{p['id']}"
                )
                st.write("---")
            
            if st.form_submit_button("Finalizar Evaluación"):
                aciertos = sum(1 for p in st.session_state.preguntas_ia if respuestas.get(p['id']) == p['correcta'])
                
                if aciertos == 10:
                    if guardar_datos(st.session_state.usuario, aciertos, st.session_state.intento):
                        st.session_state.aprobado = True
                        st.balloons()
                        st.rerun()
                else:
                    st.error(f"Puntaje: {aciertos}/10. ¡Necesitas 10 para aprobar!")
                    st.session_state.intento += 1
else:
    st.info("Esperando que el instructor suba el material de capacitación...")

# PANTALLA FINAL
if st.session_state.aprobado:
    st.success(f"¡Felicidades {st.session_state.usuario}! Aprobaste en el intento {st.session_state.intento}.")
    if st.button("Reiniciar"):
        st.session_state.usuario = None
        st.session_state.aprobado = False
        st.session_state.intento = 1
        st.rerun()

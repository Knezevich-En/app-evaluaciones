import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz
import time
import re

# ==========================================
# 🎨 CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Evaluación Técnica Pro", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .pista-box { background-color: #F0F9FF; padding: 15px; border-radius: 10px; border-left: 5px solid #0EA5E9; color: #0369A1; font-weight: 500; margin-bottom: 20px; }
    .stRadio > label { font-weight: bold; font-size: 1.2rem; color: #1E3A8A; }
    .stProgress > div > div > div > div { background-color: #0EA5E9; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ VALIDACIONES
# ==========================================
def es_correo_valido(correo):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo) is not None

def es_telefono_valido(tel):
    return tel.isdigit() and 7 <= len(tel) <= 12

# ==========================================
# 📚 BANCO DE PREGUNTAS (10 PREGUNTAS)
# ==========================================
if 'lista_preguntas' not in st.session_state:
    st.session_state.lista_preguntas = [
        {"id": 1, "tipo": "radio", "pregunta": "1. ¿Qué significa la sigla EPP?", "opciones": ["Equipo de Protección Personal", "Evaluación de Procesos", "Estándar de Prevención"], "correcta": "Equipo de Protección Personal", "pista": "Casco, guantes y botas son ejemplos de esto."},
        {"id": 2, "tipo": "radio", "pregunta": "2. ¿Qué extintor usar en fuego eléctrico?", "opciones": ["Agua", "CO2 o PQS", "Espuma"], "correcta": "CO2 o PQS", "pista": "El agente no debe ser conductor de electricidad."},
        {"id": 3, "tipo": "texto", "pregunta": "3. Escriba la unidad de medida de la Resistencia Eléctrica:", "correcta": "Ohmios", "pista": "Se representa con la letra griega Omega (Ω)."},
        {"id": 4, "tipo": "radio", "pregunta": "4. Color de tuberías contra incendios:", "opciones": ["Azul", "Amarillo", "Rojo"], "correcta": "Rojo", "pista": "Color estándar de seguridad para emergencias."},
        {"id": 5, "tipo": "texto", "pregunta": "5. ¿Cómo se llama el procedimiento de Bloqueo y Etiquetado?", "correcta": "Lockout", "pista": "Empieza con la letra L."},
        {"id": 6, "tipo": "radio", "pregunta": "6. Límite de ruido (8h) sin protección:", "opciones": ["70 dB", "85 dB", "100 dB"], "correcta": "85 dB", "pista": "A partir de este nivel el daño es crónico."},
        {"id": 7, "tipo": "radio", "pregunta": "7. ¿Qué indica el color AMARILLO?", "opciones": ["Seguridad", "Advertencia / Peligro", "Obligación"], "correcta": "Advertencia / Peligro", "pista": "Se usa para precaución ante riesgos físicos."},
        {"id": 8, "tipo": "texto", "pregunta": "8. Herramienta para medir tensión eléctrica:", "correcta": "Multímetro", "pista": "Instrumento versátil para electricistas."},
        {"id": 9, "tipo": "radio", "pregunta": "9. Acción ante derrame químico desconocido:", "opciones": ["Limpiar rápido", "Evacuar el área", "Olerlo"], "correcta": "Evacuar el área", "pista": "La seguridad es prioridad ante lo desconocido."},
        {"id": 10, "tipo": "radio", "pregunta": "10. Altura mínima de 'Trabajo en Altura' (metros):", "opciones": ["1.00 m", "1.80 m", "3.00 m"], "correcta": "1.80 m", "pista": "Norma oficial para el uso obligatorio de arnés."},
    ]

# ESTADOS INICIALES
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'indice' not in st.session_state: st.session_state.indice = 0
if 'aprobado' not in st.session_state: st.session_state.aprobado = False
if 'intentos' not in st.session_state: st.session_state.intentos = 1

# ==========================================
# 💾 GUARDADO EN GOOGLE SHEETS
# ==========================================
def finalizar_y_guardar(n, e, t, i):
    try:
        zona = pytz.timezone('America/Guayaquil')
        fecha = datetime.now(zona).strftime("%Y-%m-%d %H:%M:%S")
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        nuevo = pd.DataFrame({'Nombre':[n], 'Correo':[e], 'Teléfono':[t], 'Puntaje':["10/10"], 'Intento':[i], 'Fecha':[fecha]})
        df_f = pd.concat([df, nuevo], ignore_index=True)
        conn.update(data=df_f)
        return True
    except Exception as err:
        st.error(f"Error al conectar con Excel: {err}")
        return False

# ==========================================
# 🖥️ INTERFAZ DE USUARIO
# ==========================================

# 1. REGISTRO
if st.session_state.perfil is None:
    st.title("📝 Registro de Capacitación")
    with st.form("registro"):
        nombre = st.text_input("Nombre y Apellido:")
        correo = st.text_input("Correo Electrónico:")
        fono = st.text_input("Teléfono (Solo números):")
        if st.form_submit_button("Iniciar Evaluación", use_container_width=True):
            if nombre and es_correo_valido(correo) and es_telefono_valido(fono):
                st.session_state.perfil = {"n": nombre, "e": correo, "t": fono}
                st.rerun()
            else: st.error("Por favor, verifica que los datos estén completos y el formato sea correcto.")

# 2. EVALUACIÓN (PREGUNTA POR PREGUNTA)
elif not st.session_state.aprobado:
    lista = st.session_state.lista_preguntas
    idx = st.session_state.indice
    
    if idx < len(lista):
        p = lista[idx]
        st.subheader(f"Pregunta {idx + 1} de {len(lista)}")
        st.progress((idx) / len(lista))
        st.info(f"👤 Evaluado: {st.session_state.perfil['n']} | 🔄 Intento actual: {st.session_state.intentos}")
        
        st.write(f"### {p['pregunta']}")
        with st.expander("💡 Ver Pista"):
            st.markdown(f'<div class="pista-box">{p["pista"]}</div>', unsafe_allow_html=True)
        
        # Entrada de datos
        respuesta = None
        if p['tipo'] == "radio":
            respuesta = st.radio("Selecciona una opción:", p['opciones'], index=None, key=f"pre_{p['id']}")
        else:
            respuesta = st.text_input("Escribe tu respuesta:", key=f"pre_{p['id']}").strip()

        if st.button("Comprobar Respuesta", use_container_width=True):
            if not respuesta:
                st.warning("Debes seleccionar o escribir una respuesta.")
            else:
                es_correcta = str(respuesta).lower() == str(p['correcta']).lower()
                
                if es_correcta:
                    st.success("✅ ¡CORRECTO!")
                    time.sleep(1.5)
                    st.session_state.indice += 1
                    st.rerun()
                else:
                    st.error("❌ INCORRECTO. Esta pregunta volverá al final del test.")
                    time.sleep(2)
                    # Lógica de mover al final
                    fallada = st.session_state.lista_preguntas.pop(idx)
                    st.session_state.lista_preguntas.append(fallada)
                    st.session_state.intentos += 1
                    st.rerun()
    else:
        # Fin de las preguntas
        with st.spinner("Guardando tus resultados en el sistema..."):
            if finalizar_y_guardar(st.session_state.perfil['n'], st.session_state.perfil['e'], st.session_state.perfil['t'], st.session_state.intentos):
                st.session_state.aprobado = True
                st.rerun()

# 3. PANTALLA FINAL
else:
    st.balloons()
    st.success("🎊 ¡Evaluación Finalizada con Éxito!")
    st.write(f"Gracias **{st.session_state.perfil['n']}**, tus datos han sido registrados correctamente.")
    
    if st.button("Registrar nuevo usuario", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

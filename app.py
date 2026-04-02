import streamlit as st
import pandas as pd
import time
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# ==========================================
# 🎨 DISEÑO DE INTERFAZ ESTILO DASHBOARD
# ==========================================
st.set_page_config(page_title="WAVIN - Evaluación MA", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
    /* Fondo principal y fuentes */
    [data-testid="stAppViewContainer"] {
        background-color: #0B1E33;
        color: white;
    }
    
    /* Contenedor tipo Tarjeta (Pantalla Completa y Centrada) */
    .main-card {
        background-color: #162B46;
        border-radius: 20px;
        padding: 40px;
        border: 1px solid #1E3A5F;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        max-width: 800px;
        margin: 0 auto; 
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

    /* Botón Acción */
    .stButton > button {
        background: linear-gradient(90deg, #00C2FF, #0075FF);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 10px 40px;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        box-shadow: 0 0 15px #00C2FF;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📚 BANCO DE PREGUNTAS (10 Preguntas x 10 Pts = 100 Pts)
# ==========================================
if 'lista_preguntas' not in st.session_state:
    st.session_state.lista_preguntas = [
        {
            "id": 1, "sub": "MÓDULO: CULTURA 5S - SEIRI", 
            "pregunta": "Clasificación en la línea de producción", 
            "texto": "Encuentras 5 herramientas en el tablero de tu máquina, pero para el cambio de formato diario solo usas 2. ¿Qué debes hacer según el primer paso de las 5S?", 
            "opciones": ["Fabricar un tablero más grande para que quepan todas.", "Identificar las 3 herramientas innecesarias, marcarlas con tarjeta roja y retirarlas.", "Limpiarlas todas los días para que se vean bien.", "Escribir un manual para usar las 5 herramientas."], 
            "correcta": "Identificar las 3 herramientas innecesarias, marcarlas con tarjeta roja y retirarlas.", 
            "pista": "El primer paso (Seiri) exige separar lo necesario de lo innecesario."
        },
        {
            "id": 2, "sub": "MÓDULO: PASO 1 - LIMPIEZA INICIAL", 
            "pregunta": "Detección con los 5 Sentidos", 
            "texto": "Al limpiar el panel de control, detectas un olor a cable quemado pero no ves humo. No eres electricista. ¿Qué dicta el Paso 1 de Mantenimiento Autónomo?", 
            "opciones": ["Ignorar el olor si la máquina sigue encendida.", "Abrir el panel eléctrico para intentar arreglarlo tú mismo.", "Colocar una etiqueta de anormalidad y reportarlo al técnico de mantenimiento.", "Traer un ventilador para disipar el olor."], 
            "correcta": "Colocar una etiqueta de anormalidad y reportarlo al técnico de mantenimiento.", 
            "pista": "Si detectas algo anormal que no puedes arreglar, debes evidenciarlo con una tarjeta."
        },
        {
            "id": 3, "sub": "MÓDULO: PASO 2 - CONTRAMEDIDAS", 
            "pregunta": "Fuga de fluidos", 
            "texto": "Una tubería gotea aceite sobre un sensor óptico. Según la jerarquía de contramedidas, ¿cuál es la solución definitiva (Nivel 1)?", 
            "opciones": ["Fabricar una cubierta acrílica para tapar el sensor (Proteger).", "Poner una bandeja para que caiga el aceite (Contener).", "Cambiar el empaque dañado de la tubería para que deje de fugar (Eliminar fuente).", "Limpiar el sensor cada 10 minutos."], 
            "correcta": "Cambiar el empaque dañado de la tubería para que deje de fugar (Eliminar fuente).", 
            "pista": "La mejor forma de lidiar con la contaminación es eliminarla de raíz."
        },
        {
            "id": 4, "sub": "MÓDULO: MANTENIMIENTO AUTÓNOMO", 
            "pregunta": "Cambio de Paradigma", 
            "texto": "¿Cuál de las siguientes frases representa la verdadera filosofía del operador en el Mantenimiento Autónomo?", 
            "opciones": ["Yo opero la máquina, tú la arreglas.", "El mantenimiento es responsabilidad exclusiva de los mecánicos.", "Yo opero y yo cuido mi máquina.", "Producir al máximo sin importar el estado del equipo."], 
            "correcta": "Yo opero y yo cuido mi máquina.", 
            "pista": "El MA busca empoderar al operador para que sea el primer guardián de su equipo."
        },
        {
            "id": 5, "sub": "MÓDULO: CULTURA 5S - SEITON", 
            "pregunta": "Orden y Gestión Visual", 
            "texto": "Pierdes 5 minutos cada turno buscando la llave de purga. ¿Qué acción de la fase Seiton (Ordenar) debes aplicar?", 
            "opciones": ["Comprar más llaves para tener en todos lados.", "Crear un tablero de sombras delimitado para que la llave tenga un lugar específico y visible.", "Esconder la llave en tu casillero para que nadie la tome.", "Multar a los compañeros que no devuelvan la llave."], 
            "correcta": "Crear un tablero de sombras delimitado para que la llave tenga un lugar específico y visible.", 
            "pista": "Un lugar para cada cosa, y cada cosa en su lugar. La gestión visual elimina búsquedas."
        },
        {
            "id": 6, "sub": "MÓDULO: PASO 2 - ZONAS DE DIFÍCIL ACCESO", 
            "pregunta": "Lubricación Segura", 
            "texto": "Para lubricar un rodamiento, tienes que subirte a una escalera y estirar el brazo peligrosamente. ¿Qué contramedida se debe tomar?", 
            "opciones": ["Hacerlo con mucho cuidado y usar arnés siempre.", "Dejar de lubricarlo para evitar accidentes.", "Modificar el equipo instalando una manguera de extensión para lubricar desde el piso.", "Pedirle a un operador más alto que lo haga."], 
            "correcta": "Modificar el equipo instalando una manguera de extensión para lubricar desde el piso.", 
            "pista": "Las zonas de difícil acceso deben ser rediseñadas para facilitar el trabajo seguro."
        },
        {
            "id": 7, "sub": "MÓDULO: SEGURIDAD - LOTO", 
            "pregunta": "Aislamiento de Energías", 
            "texto": "Debes realizar la limpieza interna de la tolva mezcladora. ¿Cuál es el paso OBLIGATORIO antes de ingresar cualquier parte de tu cuerpo?", 
            "opciones": ["Gritarle a los compañeros que no enciendan la máquina.", "Solo presionar el botón de Paro de Emergencia.", "Aplicar procedimiento LOTO: Bajar el breaker eléctrico y colocar tu candado personal.", "Hacerlo muy rápido antes de que alguien llegue."], 
            "correcta": "Aplicar procedimiento LOTO: Bajar el breaker eléctrico y colocar tu candado personal.", 
            "pista": "Los botones de emergencia no aíslan la energía. Solo un candado físico LOTO lo garantiza."
        },
        {
            "id": 8, "sub": "MÓDULO: ANÁLISIS 5W1H", 
            "pregunta": "Definición del Problema", 
            "texto": "Ves un charco de agua en el suelo. Antes de buscar soluciones, aplicas 5W1H. ¿Para qué sirve esta herramienta?", 
            "opciones": ["Para castigar al culpable de derramar el agua.", "Para documentar el hallazgo de forma objetiva (Qué, Dónde, Cuándo, etc.) y no saltar a conclusiones.", "Para limpiar el agua más rápido.", "Para medir el volumen exacto de agua."], 
            "correcta": "Para documentar el hallazgo de forma objetiva (Qué, Dónde, Cuándo, etc.) y no saltar a conclusiones.", 
            "pista": "Para encontrar la causa raíz verdadera, primero debes describir el fenómeno con exactitud."
        },
        {
            "id": 9, "sub": "MÓDULO: PASO 1 - ESTÁNDARES", 
            "pregunta": "Elaboración de Rutinas", 
            "texto": "Una vez que la máquina quedó como nueva tras la limpieza inicial, ¿qué documento debe crearse para evitar que vuelva a ensuciarse?", 
            "opciones": ["Un reporte de horas extras.", "Un Estándar Preliminar de Limpieza que defina Qué, Cómo, Quién y Cuándo limpiar.", "Un memorándum a toda la planta.", "Una gráfica de Pareto."], 
            "correcta": "Un Estándar Preliminar de Limpieza que defina Qué, Cómo, Quién y Cuándo limpiar.", 
            "pista": "De nada sirve limpiar si no se estandariza una rutina para mantener esa condición."
        },
        {
            "id": 10, "sub": "MÓDULO: CULTURA 5S - SHITSUKE", 
            "pregunta": "Disciplina y Hábito", 
            "texto": "Han pasado tres meses desde que se implementaron las 5S, pero el área empieza a verse desordenada de nuevo. ¿Qué falló?", 
            "opciones": ["Faltó el quinto paso (Disciplina/Sostener): No se hicieron auditorías ni se mantuvo el hábito.", "Las herramientas se reprodujeron solas.", "Faltó comprar más estantes.", "El gerente de planta no barrió el área."], 
            "correcta": "Faltó el quinto paso (Disciplina/Sostener): No se hicieron auditorías ni se mantuvo el hábito.", 
            "pista": "Las 5S requieren disciplina constante y auditorías para sostenerse en el tiempo."
        }
    ]

# Inicializar estados de la sesión
if 'indice' not in st.session_state: st.session_state.indice = 0
if 'puntaje' not in st.session_state: st.session_state.puntaje = 0
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'respondido' not in st.session_state: st.session_state.respondido = False
if 'intento_actual' not in st.session_state: st.session_state.intento_actual = 1

# ==========================================
# 🖥️ LÓGICA DE NAVEGACIÓN
# ==========================================

# 1. PANTALLA DE REGISTRO
if st.session_state.perfil is None:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.title("⚙️ Sistema de Evaluación Técnica WAVIN")
    st.write("Bienvenido al módulo de certificación en Mantenimiento Autónomo y 5S.")
    st.divider()
    
    # Los 3 campos exactos que solicitaste
    n = st.text_input("Nombre Completo")
    c = st.text_input("Correo Electrónico")
    t = st.text_input("Teléfono")
        
    st.write("") 
    if st.button("INICIAR EVALUACIÓN (100 Puntos)"):
        if n and c and t:
            st.session_state.perfil = {"n": n, "c": c, "t": t}
            st.rerun()
        else:
            st.warning("⚠️ Por favor complete Nombre, Correo y Teléfono para ingresar.")
    st.markdown('</div>', unsafe_allow_html=True)

# 2. INTERFAZ DE EVALUACIÓN
elif st.session_state.indice < len(st.session_state.lista_preguntas):
    lista = st.session_state.lista_preguntas
    idx = st.session_state.indice
    p = lista[idx]
    
    # BARRA SUPERIOR DE PROGRESO Y PUNTAJE
    col_logo, col_info, col_prog = st.columns([1, 2, 2])
    with col_logo:
        st.subheader("⚙️ WAVIN")
    with col_info:
        st.write(f"**Operador:** {st.session_state.perfil['n']} | **Intento:** {st.session_state.intento_actual}")
        st.write(f"**Puntaje Actual:** {st.session_state.puntaje} / 100")
    with col_prog:
        st.write(f"Pregunta: {idx + 1} de {len(lista)}")
        st.progress((idx) / len(lista))

    st.divider()

    # CUERPO CENTRAL DE LA PREGUNTA
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.caption(p["sub"])
    st.title(p["pregunta"])
    st.write(f"#### {p['texto']}")
    st.write("")
    
    res = st.radio("Seleccione su respuesta:", p["opciones"], index=None, key=f"q_{idx}", disabled=st.session_state.respondido)
    st.write("")
    
    if not st.session_state.respondido:
        if st.button("Confirmar Respuesta"):
            if res is None:
                st.warning("Debe seleccionar una opción.")
            else:
                st.session_state.respondido = True
                if res == p["correcta"]:
                    st.session_state.puntaje += 10
                st.rerun()
    else:
        # Retroalimentación
        if res == p["correcta"]:
            st.success("✅ ¡CORRECTO! +10 Puntos.")
        else:
            st.error("❌ INCORRECTO.")
            st.info(f"**Nota Técnica:** {p['pista']}")
        
        st.write("")
        if st.button("Siguiente Pregunta ▶️"):
            st.session_state.respondido = False
            st.session_state.indice += 1
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# 3. FINALIZACIÓN Y GUARDADO EN GOOGLE SHEETS
else:
    st.markdown('<div class="main-card" style="text-align: center;">', unsafe_allow_html=True)
    st.title("📊 Resultados de la Certificación")
    st.divider()
    st.write(f"### Operador: {st.session_state.perfil['n']}")
    st.write(f"**Intento N°:** {st.session_state.intento_actual}")
    
    score = st.session_state.puntaje
    st.markdown(f"<h1 style='font-size: 80px; color: {'#00C2FF' if score >= 80 else '#FF4B4B'};'>{score} / 100</h1>", unsafe_allow_html=True)
    
    if score >= 80:
        st.success("🏆 ¡EXCELENTE! Has aprobado la certificación.")
    else:
        st.error("❌ REPROBADO. Debes repasar y volver a intentarlo.")

    st.divider()
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        # Botón para GUARDAR en Sheets
        if st.button("💾 Guardar Resultados en Excel"):
            with st.spinner("Guardando en Google Sheets..."):
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    df_existente = conn.read()
                    
                    # Zona horaria de Ecuador
                    tz_ecuador = pytz.timezone('America/Guayaquil')
                    fecha_actual = datetime.now(tz_ecuador).strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Datos exactos a guardar
                    nuevo_registro = pd.DataFrame([{
                        "Nombre": st.session_state.perfil['n'],
                        "Correo": st.session_state.perfil['c'],
                        "Telefono": st.session_state.perfil['t'],
                        "Intento": st.session_state.intento_actual,
                        "Puntaje": score,
                        "Fecha": fecha_actual
                    }])
                    
                    if not df_existente.empty:
                        df_actualizado = pd.concat([df_existente, nuevo_registro], ignore_index=True)
                    else:
                        df_actualizado = nuevo_registro
                        
                    conn.update(data=df_actualizado)
                    st.success("✅ ¡Datos guardados correctamente en Google Sheets!")
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar: {e}")
                    st.info("Revisa tu archivo secrets.toml y los permisos del Google Sheet.")
                    
    with col_btn2:
        # Botón para REINTENTAR o SALIR
        if score >= 80:
            if st.button("Salir del Sistema"):
                st.session_state.perfil = None
                st.session_state.indice = 0
                st.session_state.puntaje = 0
                st.session_state.respondido = False
                st.session_state.intento_actual = 1
                st.rerun()
        else:
            if st.button("🔄 Volver a Intentar"):
                st.session_state.indice = 0
                st.session_state.puntaje = 0
                st.session_state.respondido = False
                st.session_state.intento_actual += 1 # Suma un intento
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)

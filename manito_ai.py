
import streamlit as st  

# Cargar y mostrar el logo
 # Ajusta el tamaño según necesites

# Instala primero: pip install streamlit pandas numpy sentence-transformers
import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util

# 1. Configuración inicial
st.set_page_config(page_title="MANITO AI - Editor de FAQs", layout="wide")

# Cargar modelo de embeddings (para comparar similitud entre preguntas)
@st.cache_resource
def cargar_modelo():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

model = cargar_modelo()

# 2. Base de datos de FAQs (se guarda en la sesión de Streamlit)
if 'faqs' not in st.session_state:
    st.session_state.faqs = pd.DataFrame(columns=["Pregunta", "Respuesta", "Embedding"])

# 3. Editor principal (hoja en blanco)
st.title("📄 MANITO AI - Tu hoja inteligente")
st.markdown("""Pega tus preguntas frecuentes y sus respuestas . 
           La IA detectará automáticamente similitudes y alertará sobre preguntas complejas.""")

# 4. Columnas para organización
col_editor, col_preview = st.columns([0.6, 0.4])

with col_editor:
    # Widget para añadir nuevas FAQs
    with st.expander("➕ Nueva pregunta/respuesta", expanded=True):
        nueva_pregunta = st.text_area("Pregunta del cliente:", height=100)
        nueva_respuesta = st.text_area("Respuesta (usa emojis y tono cálido):", height=150)
        
        if st.button("Guardar FAQ"):
            if nueva_pregunta and nueva_respuesta:
                # Calcular embedding de la pregunta
                embedding = model.encode(nueva_pregunta, convert_to_tensor=True).cpu().numpy()
                
                # Guardar en DataFrame
                nueva_fila = pd.DataFrame([{
                    "Pregunta": nueva_pregunta,
                    "Respuesta": nueva_respuesta,
                    "Embedding": embedding
                }])
                
                st.session_state.faqs = pd.concat([st.session_state.faqs, nueva_fila], ignore_index=True)
                st.success("¡Guardado! La IA ahora usará esta respuesta.")
            else:
                st.error("¡Faltan datos! Completa ambos campos.")

with col_preview:
    # Vista previa de FAQs existentes
    st.subheader("📚 Preguntas guardadas")
    if not st.session_state.faqs.empty:
        for idx, row in st.session_state.faqs.iterrows():
            with st.container(border=True):
                st.markdown(f"**Pregunta {idx+1}:** {row['Pregunta']}")
                st.markdown(f"**Respuesta:** {row['Respuesta']}")
                if st.button(f"🗑️ Borrar", key=f"del_{idx}"):
                    st.session_state.faqs = st.session_state.faqs.drop(index=idx).reset_index(drop=True)
                    st.rerun()
    else:
        st.info("Aún no hay preguntas guardadas. ¡Empieza a agregar algunas!")

# 5. Panel de control (alertas y botones)
st.sidebar.header("⚙️ Panel de control")

# Botones de pausa/reanudar
if 'ia_activa' not in st.session_state:
    st.session_state.ia_activa = True

if st.session_state.ia_activa:
    if st.sidebar.button("⏸ Pausar IA", help="Detiene temporalmente las respuestas automáticas"):
        st.session_state.ia_activa = False
else:
    if st.sidebar.button("▶ Reanudar IA", help="Reinicia el procesamiento automático"):
        st.session_state.ia_activa = True

# Sección de alertas
st.sidebar.subheader("🚨 Alertas")
preguntas_complejas = ["Ejemplo: '¿Cómo devuelvo un producto defectuoso?'"]  # Aquí iría la lógica real
if preguntas_complejas:
    st.sidebar.error(f"{len(preguntas_complejas)} preguntas necesitan revisión humana")
    for pregunta in preguntas_complejas:
        st.sidebar.write(f"- {pregunta}")
else:
    st.sidebar.success("¡Todo bajo control!")

# 6. Simulación de procesamiento (esto se conectaría a Mistral)
if st.session_state.ia_activa and not st.session_state.faqs.empty:
    st.sidebar.info("Estado: IA ACTIVA - Analizando mensajes entrantes...")
else:
    st.sidebar.warning("Estado: IA PAUSADA - Solo modo manual")

# Para ejecutar: streamlit run nombre_archivo.py
import streamlit as st
import sqlite3
import streamlit as st

# Conectar a la base de datos (se crea si no existe)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Crear una tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS preguntas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pregunta TEXT
    )
""")
conn.commit()
# Interfaz en Streamlit
st.title("Manito AI - Base de Datos")

# Campo para escribir una pregunta
pregunta = st.text_input("Escribe tu pregunta:")

# Guardar en la base de datos si se presiona el botón
if st.button("Guardar pregunta"):
    cursor.execute("INSERT INTO preguntas (pregunta) VALUES (?)", (pregunta,))
    conn.commit()
    st.success("Pregunta guardada con éxito.")

# Mostrar preguntas guardadas
st.subheader("Historial de preguntas:")
cursor.execute("SELECT * FROM preguntas")
preguntas = cursor.fetchall()

for id, texto in preguntas:
    st.write(f"**{id}**: {texto}")

# Cerrar conexión (opcional, pero en Streamlit se recomienda dejarla abierta)
# conn.close()
#para ejecutar manito_ai usar: streamlit run "tipos de datos\manito_ai.py" --server.port 8501 
#link:http://localhost:8501/ 
#correccion de base de datos manito_ai:
import sqlite3
import streamlit as st

# Conectar a la base de datos
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pregunta TEXT,
        respuesta TEXT
    )
""")
conn.commit()

# Interfaz de Streamlit
st.title("📌 Manito AI - Preguntas y Respuestas")

# Formulario de pregunta y respuesta
st.subheader("➕ Nueva pregunta/respuesta")
pregunta = st.text_area("Pregunta del cliente:")
respuesta = st.text_area("Respuesta (usa emojis y tono cálido):")

# Guardar en la base de datos
if st.button("Guardar FAQ"):
    if pregunta.strip() and respuesta.strip():
        cursor.execute("INSERT INTO faq (pregunta, respuesta) VALUES (?, ?)", (pregunta, respuesta))
        conn.commit()
        st.success("Pregunta y respuesta guardadas correctamente.")
    else:
        st.warning("❗ Por favor, ingresa tanto la pregunta como la respuesta.")

# Mostrar preguntas guardadas
st.subheader("📚 Preguntas guardadas")

cursor.execute("SELECT * FROM faq")
faqs = cursor.fetchall()

if faqs:
    for id, pregunta, respuesta in faqs:
        with st.expander(f"**{pregunta}**"):
            st.write(respuesta)
else:
    st.info("Aún no hay preguntas guardadas. ¡Empieza a agregar algunas!")

# No cerramos la conexión para evitar errores en Streamlit
# importacion de api de openai

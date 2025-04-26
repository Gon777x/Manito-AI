import streamlit as st
import sqlite3

# --- Configuración inicial ---
st.set_page_config(page_title="MANITO AI", layout="wide")

# --- Conexión a la base de datos ---
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pregunta TEXT,
        respuesta TEXT
    )
""")
conn.commit()

# --- Estado de IA (pausada o activa) ---
if 'ia_activa' not in st.session_state:
    st.session_state.ia_activa = True

# --- Sidebar: Panel de control ---
st.sidebar.header("⚙️ Panel de control")

if st.session_state.ia_activa:
    if st.sidebar.button("⏸ Pausar IA"):
        st.session_state.ia_activa = False
else:
    if st.sidebar.button("▶ Reanudar IA"):
        st.session_state.ia_activa = True

# Mostrar estado
if st.session_state.ia_activa:
    st.sidebar.success("Estado: IA ACTIVA ✅")
else:
    st.sidebar.warning("Estado: IA PAUSADA ⏸️")

# --- Título principal ---
st.title("📌 Manito AI - Preguntas y Respuestas")

# --- Formulario para agregar nueva FAQ ---
st.subheader("➕ Nueva pregunta/respuesta")
pregunta = st.text_area("Pregunta del cliente:")
respuesta = st.text_area("Respuesta (usa emojis y tono cálido):")

if st.button("Guardar FAQ"):
    if pregunta.strip() and respuesta.strip():
        cursor.execute("INSERT INTO faq (pregunta, respuesta) VALUES (?, ?)", (pregunta, respuesta))
        conn.commit()
        st.success("Pregunta y respuesta guardadas correctamente.")
        st.experimental_rerun()
    else:
        st.warning("❗ Por favor, ingresa tanto la pregunta como la respuesta.")

# --- Mostrar todas las FAQs guardadas ---
st.subheader("📚 Preguntas guardadas")
cursor.execute("SELECT * FROM faq")
faqs = cursor.fetchall()

if faqs:
    for id, pregunta, respuesta in faqs:
        with st.expander(f"**{pregunta}**"):
            st.write(respuesta)
else:
    st.info("Aún no hay preguntas guardadas. ¡Empieza a agregar algunas!")

# Nota: no cerramos conn para evitar errores en Streamlit
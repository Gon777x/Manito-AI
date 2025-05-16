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
            
            # --- Botón de edición para cada FAQ ---
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("✏ Editar", key=f"editar_{id}"):
                    # Mostrar formulario de edición
                    new_pregunta = st.text_input("Pregunta del cliente", pregunta)
                    new_respuesta = st.text_area("Respuesta", respuesta)
                    
                    if st.button("Guardar cambios", key=f"guardar_{id}"):
                        cursor.execute("UPDATE faq SET pregunta = ?, respuesta = ? WHERE id = ?", (new_pregunta, new_respuesta, id))
                        conn.commit()
                        st.success("FAQ actualizada correctamente.")
                        st.experimental_rerun()

else:
    st.info("Aún no hay preguntas guardadas. ¡Empieza a agregar algunas!")

# --- Función de respuesta humanizada si no se encuentra la pregunta ---
def buscar_respuesta_similar(pregunta_usuario):
    cursor.execute("SELECT pregunta, respuesta FROM faq")
    faqs = cursor.fetchall()
    
    if not faqs:
        return "Hola 👋. Todavía no tengo respuestas cargadas."

    preguntas = [faq[0] for faq in faqs]
    respuestas = [faq[1] for faq in faqs]

    # Si no hay coincidencias exactas, respuesta cálida
    if pregunta_usuario not in preguntas:
        return f"Lo siento, no tengo la respuesta a esa pregunta. 😅 Pero voy a preguntar y te aviso pronto."

    idx_mas_similar = preguntas.index(pregunta_usuario)
    return respuestas[idx_mas_similar]

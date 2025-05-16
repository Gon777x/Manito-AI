import streamlit as st
import sqlite3
import pandas as pd
import docx
import re

# --- Configuración inicial ---
st.set_page_config(page_title="MANITO AI", layout="wide")

# --- Conexión a la base de datos ---
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pregunta TEXT UNIQUE,
        respuesta TEXT
    )
""")
# Tabla para feedback de patrones
cursor.execute("""
    CREATE TABLE IF NOT EXISTS patrones_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        patron TEXT
    )
""")
conn.commit()

# --- Estado de IA ---
if 'ia_activa' not in st.session_state:
    st.session_state.ia_activa = True

if 'confirmar_eliminacion' not in st.session_state:
    st.session_state.confirmar_eliminacion = False

# --- Sidebar ---
st.sidebar.image("MANITO AI LOGO 5.0.png", width=150)
st.sidebar.header("⚙️ Panel de control")
if st.session_state.ia_activa:
    if st.sidebar.button("⏸ Pausar IA"):
        st.session_state.ia_activa = False
else:
    if st.sidebar.button("▶ Reanudar IA"):
        st.session_state.ia_activa = True

st.sidebar.success("Estado: IA ACTIVA ✅" if st.session_state.ia_activa else "Estado: IA PAUSADA ⏸️")

# --- Botón de eliminación masiva ---
st.sidebar.markdown("---")
if not st.session_state.confirmar_eliminacion:
    if st.sidebar.button("🗑 Eliminar TODAS las preguntas"):
        st.session_state.confirmar_eliminacion = True
else:
    st.sidebar.warning("⚠️ Esta acción borrará TODAS las preguntas guardadas.")
    confirmar = st.sidebar.button("❗ Confirmar eliminación total")
    cancelar = st.sidebar.button("Cancelar")

    if confirmar:
        cursor.execute("DELETE FROM faq")
        conn.commit()
        st.sidebar.success("✅ Todas las preguntas han sido eliminadas.")
        st.session_state.confirmar_eliminacion = False
        st.rerun()
    elif cancelar:
        st.session_state.confirmar_eliminacion = False

# --- Título principal ---
st.title("📌 Manito AI - Preguntas y Respuestas")

# --- Buscador ---
busqueda = st.text_input("🔍 Buscar pregunta:")

# --- Agregar FAQ manualmente ---
st.subheader("➕ Nueva pregunta/respuesta")
pregunta = st.text_area("Pregunta del cliente:")
respuesta = st.text_area("Respuesta (usa emojis y tono cálido):")

if st.button("Guardar FAQ"):
    if pregunta.strip() and respuesta.strip():
        cursor.execute("SELECT COUNT(*) FROM faq WHERE pregunta = ?", (pregunta,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO faq (pregunta, respuesta) VALUES (?, ?)", (pregunta, respuesta))
            conn.commit()
            st.success("✅ Pregunta y respuesta guardadas.")
            st.rerun()
        else:
            st.warning("⚠️ Esta pregunta ya existe.")
    else:
        st.warning("❗ Completa los campos antes de guardar.")

# --- Importar FAQs desde archivo con versión Mixta Inteligente ---
st.subheader("📤 Importar FAQs con Detección Inteligente")
archivo = st.file_uploader("Sube un archivo Word (.docx):", type=["docx"])

if archivo:
    doc = docx.Document(archivo)
    parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    detectadas = []

    # Reglas de detección
    patrones_pregunta = ["quiero", "puedo", "cómo", "cuando", "donde", "inscripción", "necesito", "debo"]
    patron_pregunta = re.compile(r'(' + '|'.join(patrones_pregunta) + r')', re.IGNORECASE)

    patron_respuesta = re.compile(r'^(hola|buen día|hola cómo estás)', re.IGNORECASE)

    i = 0
    while i < len(parrafos):
        p = parrafos[i]

        if patron_pregunta.search(p):
            detectadas.append(('pregunta', p))
            i += 1
            continue

        if patron_respuesta.match(p) and len(p) > 20:
            detectadas.append(('respuesta', p))
            i += 1
            continue

        i += 1

    # --- Previsualización con Corrección Visual ---
    st.subheader("🖍️ Detección de FAQs (Versión Mixta Inteligente)")

    confirmados = []
    for idx, (tipo, texto) in enumerate(detectadas):
        color = 'red' if tipo == 'pregunta' else 'orange'
        st.markdown(f"<div style='background-color:{color};padding:10px;border-radius:5px'>{texto}</div>", unsafe_allow_html=True)

        nuevo_tipo = st.radio(f"Corregir este bloque:", ["pregunta", "respuesta"], index=0 if tipo=="pregunta" else 1, key=f"corregir_{idx}")
        confirmados.append((nuevo_tipo, texto))

    if st.button("Guardar FAQs y Feedback"):
        guardados = 0
        for i in range(0, len(confirmados)-1):
            if confirmados[i][0] == "pregunta" and confirmados[i+1][0] == "respuesta":
                cursor.execute("SELECT COUNT(*) FROM faq WHERE pregunta = ?", (confirmados[i][1],))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO faq (pregunta, respuesta) VALUES (?, ?)", (confirmados[i][1], confirmados[i+1][1]))
                    guardados += 1

        # Guardar feedback de patrones corregidos
        for tipo_original, texto in detectadas:
            tipo_corregido = [t for t, tx in confirmados if tx == texto][0]
            if tipo_original != tipo_corregido:
                cursor.execute("INSERT INTO patrones_feedback (tipo, patron) VALUES (?, ?)", (tipo_corregido, texto))

        conn.commit()
        st.success(f"✅ FAQs guardadas: {guardados}")
        st.rerun()

# --- Mostrar y editar FAQs ---
st.subheader("📚 Preguntas guardadas")
cursor.execute("SELECT * FROM faq ORDER BY id DESC")
faqs = cursor.fetchall()

if busqueda:
    faqs = [f for f in faqs if busqueda.lower() in f[1].lower()]

if faqs:
    for id, pregunta, respuesta in faqs:
        with st.expander(f"❓ {pregunta}"):
            st.text_area("Editar pregunta", key=f"edit_pregunta_{id}", value=pregunta, height=70)
            st.text_area("Editar respuesta", key=f"edit_respuesta_{id}", value=respuesta, height=100)

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"💾 Guardar cambios {id}"):
                    nueva_pregunta = st.session_state[f"edit_pregunta_{id}"]
                    nueva_respuesta = st.session_state[f"edit_respuesta_{id}"]

                    try:
                        cursor.execute("UPDATE faq SET pregunta = ?, respuesta = ? WHERE id = ?", 
                                       (nueva_pregunta, nueva_respuesta, id))
                        conn.commit()
                        st.success("✅ Cambios guardados correctamente.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❗ No se pudo guardar. La pregunta ya existe.")

            with col2:
                if st.button(f"🗑 Eliminar pregunta {id}"):
                    cursor.execute("DELETE FROM faq WHERE id = ?", (id,))
                    conn.commit()
                    st.warning("❗ Pregunta eliminada.")
                    st.rerun()
else:
    st.info("Todavía no hay preguntas guardadas.")

# --- Chat ---
st.subheader("💬 Chat con Manito AI")
pregunta_cliente = st.text_input("Escribe tu pregunta aquí:")

if pregunta_cliente and st.session_state.ia_activa:
    cursor.execute("SELECT respuesta FROM faq WHERE pregunta LIKE ?", ('%' + pregunta_cliente + '%',))
    resultado = cursor.fetchone()

    if resultado:
        st.success(f"🤖 Manito responde:\n\n{resultado[0]}")
    else:
        st.info("🤖 Manito responde:\n\n¡Gracias por tu pregunta! 😊 Vamos a revisarla y te responderemos pronto. Mientras tanto, podés consultar nuestras preguntas frecuentes. 🙌")
elif pregunta_cliente and not st.session_state.ia_activa:
    st.warning("⚠️ La IA está pausada. Reanúdala desde el panel lateral para responder preguntas.")
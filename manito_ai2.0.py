# Instala primero: pip install streamlit pandas numpy sentence-transformers
import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util

# 1. Configuración inicial
st.set_page_config(page_title="MANUS AI - Editor de FAQs", layout="wide")

# Cargar modelo de embeddings (para comparar similitud entre preguntas)
@st.cache_resource
def cargar_modelo():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

model = cargar_modelo()

# 2. Base de datos de FAQs (se guarda en la sesión de Streamlit)
if 'faqs' not in st.session_state:
    st.session_state.faqs = pd.DataFrame(columns=["Pregunta", "Respuesta", "Embedding"])

# 3. Editor principal (hoja en blanco)
st.title("📄 MANUS AI - Tu hoja inteligente")
st.markdown("""Pega tus preguntas frecuentes y sus respuestas humanizadas. 
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

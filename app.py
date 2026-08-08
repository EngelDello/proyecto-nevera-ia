import streamlit as st
from PIL import Image
from nevera import identificar_ingredientes, generar_receta_con_filtros

st.set_page_config(page_title="Asistente de Nevera IA", page_icon="🍳", layout="wide")

st.title("🍳 Asistente de Cocina IA (Multimodal)")

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("⚙️ Preferencias y Filtros")

dieta = st.sidebar.selectbox(
    "Tipo de Dieta:",
    ["Sin restricciones", "Vegetariana", "Vegana", "Keto / Bajas calorías", "Sin Glutén"]
)

tiempo = st.sidebar.select_slider(
    "Tiempo para cocinar:",
    options=["Rápido (15 min)", "Normal (30 min)", "Elaborado (Chef)"]
)

despensa = st.sidebar.text_area(
    "Ingredientes básicos de despensa:",
    value="Aceite de oliva, sal, pimienta, ajo, cebolla, arroz"
)

st.sidebar.markdown("---")

# Botón para Reiniciar la App siempre visible en el menú lateral
if st.sidebar.button("🔄 Reiniciar / Nueva Receta", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- ZONA PRINCIPAL ---
st.write("Sube las fotos de tu nevera para comenzar la detección.")

archivos_subidos = st.file_uploader(
    "Selecciona imágenes...",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if archivos_subidos:
    imagenes_pil = [Image.open(f) for f in archivos_subidos]
    
    # Miniaturas de las fotos
    cols = st.columns(len(imagenes_pil))
    for idx, img in enumerate(imagenes_pil):
        cols[idx].image(img, use_container_width=True)

    # PASO 1: ESCANEAR
    if st.button("🔍 1. Escanear e Identificar Ingredientes"):
        with st.spinner("Analizando imágenes de la nevera..."):
            ingredientes_detectados = identificar_ingredientes(imagenes_pil)
            st.session_state['ingredientes'] = ingredientes_detectados

    # PASO 2: EDITAR Y CONFIRMAR
    if 'ingredientes' in st.session_state:
        st.subheader("📝 Paso 2: Revisa y Corrige los Ingredientes Detectados")
        st.info("💡 Si la IA se ha equivocado con algo, edítalo directamente en el cuadro de abajo antes de generar la receta.")
        
        ingredientes_editados = st.text_area(
            "Lista de ingredientes (editable):",
            value=st.session_state['ingredientes'],
            height=250
        )
        
        # PASO 3: GENERAR RECETA
        if st.button("🍳 2. Generar Menú con Lista Confirmada"):
            with st.spinner("El chef robot está diseñando tu menú personalizado..."):
                menu_final = generar_receta_con_filtros(ingredientes_editados, despensa, dieta, tiempo)
                st.session_state['menu'] = menu_final

    # MOSTRAR MENÚ Y DESCARGA
    if 'menu' in st.session_state:
        st.markdown("---")
        st.markdown("### 📜 Tu Menú Sugerido Personalizado:")
        st.markdown(st.session_state['menu'])
        
        st.download_button(
            label="📥 Descargar Menú (Markdown)",
            data=st.session_state['menu'],
            file_name="menu_nevera.md",
            mime="text/markdown"
        )
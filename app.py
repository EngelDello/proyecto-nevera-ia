import streamlit as st
from PIL import Image
from nevera import identificar_ingredientes, generar_receta_con_filtros, MenuCompleto

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
        st.info("💡 Edita los ingredientes en el cuadro de abajo si la IA comete algún error de visión.")
        
        ingredientes_editados = st.text_area(
            "Lista de ingredientes (editable):",
            value=st.session_state['ingredientes'],
            height=250
        )
        
        # PASO 3: GENERAR RECETA EN JSON
        if st.button("🍳 2. Generar Menú con Lista Confirmada"):
            with st.spinner("El chef robot está estructurando tu menú personalizado..."):
                menu_objeto = generar_receta_con_filtros(ingredientes_editados, despensa, dieta, tiempo)
                if menu_objeto:
                    st.session_state['menu_objeto'] = menu_objeto
                else:
                    st.error("No se pudo generar el menú estructurado. Inténtalo de nuevo.")

    # MOSTRAR MENÚ Y DESCARGA (DESDE OBJETO ESTRUCTURADO)
    if 'menu_objeto' in st.session_state:
        menu: MenuCompleto = st.session_state['menu_objeto']
        
        st.markdown("---")
        st.markdown("### 📜 Tu Menú Sugerido Personalizado:")
        
        if menu.observaciones_chef:
            st.info(f"🤖 **Diagnóstico del Chef:** {menu.observaciones_chef}")

        # Renderizado en tarjetas estructuradas
        for plato in menu.platos:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"{plato.tipo_comida}: {plato.nombre}")
                with col2:
                    st.caption(f"⏱️ **{plato.tiempo_preparacion_minutos} min** | 🎯 Dificultad: **{plato.dificultad}**")
                
                # st.write("**Ingredientes usados:**", ", ".join(plato.ingredientes_usados))
                st.write("**Ingredientes usados:** " + " ".join(f"`{ing}`" for ing in plato.ingredientes_usados))
                st.write("**Instrucciones de preparación:**")
                for i, paso in enumerate(plato.pasos, 1):
                    st.write(f"{i}. {paso}")

        # Preparación de datos para la descarga (JSON o Markdown)
        st.markdown("---")
        col_dl1, col_dl2 = st.columns(2)
        
        # Opción 1: Descargar JSON crudo
        json_data = menu.model_dump_json(indent=2)
        col_dl1.download_button(
            label="📥 Descargar Menú (JSON)",
            data=json_data,
            file_name="menu_nevera.json",
            mime="application/json",
            use_container_width=True
        )

        # Opción 2: Descargar formato Markdown generado a partir del objeto
        md_text = f"# Menú Sugerido por Chef Robot\n\n**Observaciones:** {menu.observaciones_chef}\n\n"
        for p in menu.platos:
            md_text += f"## {p.tipo_comida}: {p.nombre}\n"
            md_text += f"- **Tiempo:** {p.tiempo_preparacion_minutos} min\n"
            md_text += f"- **Dificultad:** {p.dificultad}\n"
            md_text += f"- **Ingredientes:** {', '.join(p.ingredientes_usados)}\n\n"
            md_text += "### Pasos:\n"
            for i, paso in enumerate(p.pasos, 1):
                md_text += f"{i}. {paso}\n"
            md_text += "\n---\n"

        col_dl2.download_button(
            label="📄 Descargar Menú (Markdown)",
            data=md_text,
            file_name="menu_nevera.md",
            mime="text/markdown",
            use_container_width=True
        )
import streamlit as st
from urllib.parse import quote_plus
from PIL import Image
from nevera import (
    MenuCompleto,
    Plato,
    IngredienteReceta,
    identificar_ingredientes,
    generar_receta_con_filtros,
    modificar_plato,
    generar_pdf_menu,
    generar_imagen_plato
)

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
st.write("Añade fotos de tu nevera para comenzar la detección.")

tab_archivos, tab_camara = st.tabs(["📁 Subir archivos", "📸 Usar cámara"])

imagenes_pil = []

with tab_archivos:
    archivos_subidos = st.file_uploader(
        "Selecciona una o varias imágenes...",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="uploader_archivos"
    )
    if archivos_subidos:
        imagenes_pil.extend([Image.open(f) for f in archivos_subidos])

with tab_camara:
    foto_camara = st.camera_input("Haz una foto a la nevera o despensa", key="camara_input")
    if foto_camara:
        imagenes_pil.append(Image.open(foto_camara))

if imagenes_pil:
    cols = st.columns(min(len(imagenes_pil), 4))
    for idx, img in enumerate(imagenes_pil):
        cols[idx % 4].image(img, use_container_width=True)
    
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
            with st.spinner("El chef robot está calculando ingredientes y porciones estructuradas..."):
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
        for idx, plato in enumerate(menu.platos):
            with st.container(border=True):
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.subheader(f"{plato.tipo_comida}: {plato.nombre}")
                with col2:
                    st.caption(f"⏱️ **{plato.tiempo_preparacion_minutos} min** | 🎯 Dificultad: **{plato.dificultad}** | 👥 **{plato.raciones} pers.**")
                
                # Lista de ingredientes con cantidades orientativas
                st.write("**Ingredientes usados (cantidades orientativas):**")
                cols_ing = st.columns(2)
                for i, ing in enumerate(plato.ingredientes_usados):
                    col_target = cols_ing[i % 2]
                    col_target.markdown(f"• **{ing.cantidad}** — {ing.nombre}")

                st.write("")
                st.write("**Instrucciones de preparación:**")
                for i, paso in enumerate(plato.pasos, 1):
                    st.write(f"{i}. {paso}")
                
                # Botón de YouTube
                query = quote_plus(f"receta {plato.nombre}")
                url_youtube = f"https://www.youtube.com/results?search_query={query}"
                st.link_button("🎥 Ver recetas similares en YouTube", url_youtube)

                # Generación de imagen con IA
                if "imagenes_platos" not in st.session_state:
                    st.session_state.imagenes_platos = {}

                if plato.nombre in st.session_state.imagenes_platos:
                    st.image(
                        st.session_state.imagenes_platos[plato.nombre],
                        caption=f"Presentación sugerida: {plato.nombre}",
                        use_container_width=True
                    )
                else:
                    if st.button("📸 Generar foto del plato con IA", key=f"btn_img_{idx}"):
                        with st.spinner("Generando fotografía del plato con Imagen 3..."):
                            img_generada = generar_imagen_plato(plato.nombre)
                            if img_generada:
                                st.session_state.imagenes_platos[plato.nombre] = img_generada
                                st.rerun()
                            else:
                                st.error("No se pudo generar la imagen. Revisa la facturación de tu API Key.")

                # Editor dinámico por plato (Ingredientes + Raciones)
                with st.expander("✏️ Solicitar un cambio o ajustar comensales"):
                    col_edit_txt, col_edit_rac = st.columns([3, 1])
                    with col_edit_txt:
                        cambio_texto = st.text_input(
                            "¿Qué quieres cambiar?",
                            placeholder="Ej: Cambia ingredientes, hazlo sin horno...",
                            key=f"input_cambio_{idx}"
                        )
                    with col_edit_rac:
                        nuevas_raciones = st.selectbox(
                            "Raciones:",
                            options=[1, 2, 3, 4, 5, 6],
                            index=[1, 2, 3, 4, 5, 6].index(plato.raciones) if plato.raciones in [1, 2, 3, 4, 5, 6] else 1,
                            key=f"select_rac_{idx}"
                        )

                    if st.button("Aplicar ajuste a este plato", key=f"btn_cambio_{idx}"):
                        instruccion = cambio_texto.strip()
                        ha_cambiado_raciones = (nuevas_raciones != plato.raciones)

                        if instruccion or ha_cambiado_raciones:
                            with st.spinner("Ajustando cantidades y receta con el chef robot..."):
                                plato_modificado = modificar_plato(
                                    plato_actual=plato,
                                    instruccion_cambio=instruccion if instruccion else f"Recalcula los ingredientes para {nuevas_raciones} personas.",
                                    ingredientes_disponibles=st.session_state.get('ingredientes', ''),
                                    despensa=despensa,
                                    raciones_objetivo=nuevas_raciones if ha_cambiado_raciones else None
                                )
                                if plato_modificado:
                                    st.session_state['menu_objeto'].platos[idx] = plato_modificado
                                    st.rerun()
                                else:
                                    st.error("No se pudo aplicar el cambio. Inténtalo de nuevo.")
                        else:
                            st.warning("Escribe una instrucción o selecciona un número diferente de raciones.")

        # Preparación de descargas (JSON, Markdown, PDF)
        st.markdown("---")
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        
        # 1. JSON
        json_data = menu.model_dump_json(indent=2)
        col_dl1.download_button(
            label="📥 Descargar (JSON)",
            data=json_data,
            file_name="menu_nevera.json",
            mime="application/json",
            use_container_width=True
        )

        # 2. Markdown
        md_text = f"# Menú Sugerido por Chef Robot\n\n**Observaciones:** {menu.observaciones_chef}\n\n"
        for p in menu.platos:
            md_text += f"## {p.tipo_comida}: {p.nombre}\n"
            md_text += f"- **Tiempo:** {p.tiempo_preparacion_minutos} min\n"
            md_text += f"- **Dificultad:** {p.dificultad}\n"
            md_text += f"- **Raciones:** {p.raciones} pers.\n"
            md_text += "- **Ingredientes:**\n"
            for ing in p.ingredientes_usados:
                md_text += f"  - {ing.cantidad} de {ing.nombre}\n"
            md_text += "\n### Pasos:\n"
            for i, paso in enumerate(p.pasos, 1):
                md_text += f"{i}. {paso}\n"
            md_text += "\n---\n"

        col_dl2.download_button(
            label="📄 Descargar (Markdown)",
            data=md_text,
            file_name="menu_nevera.md",
            mime="text/markdown",
            use_container_width=True
        )

        # 3. PDF
        pdf_bytes = generar_pdf_menu(menu)
        col_dl3.download_button(
            label="📕 Descargar (PDF)",
            data=pdf_bytes,
            file_name="menu_nevera.pdf",
            mime="application/pdf",
            use_container_width=True
        )
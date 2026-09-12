# Proyecto Nevera IA

Asistente de cocina inteligente desarrollado en Python. Analiza los ingredientes que tienes en casa a partir de fotos y propone un menú personalizado, con corrección manual de la lista detectada, filtros de dieta/tiempo/despensa, modificación dinámica de platos individuales, escalado real de raciones con cantidades estructuradas, enlaces a recetas en vídeo y exportación del menú en PDF, JSON o Markdown. El proyecto evoluciona de forma incremental desde un modelo local hasta una arquitectura en la nube con visión artificial, salida estructurada en JSON e interfaz web interactiva.

---

## Evolución del proyecto

| Versión | Descripción | Tecnología |
|---------|-------------|------------|
| v1 | Entrada manual de ingredientes por consola y propuesta de receta básica. | Ollama + `qwen2.5-coder:1.5b` |
| v2 | Interfaz de chat continuo en bucle `while True`, simulando una conversación interactiva sin reinicios. | Ollama |
| v3 | Control de alucinaciones mediante *System Prompt* estricto para evitar ingredientes fantasma. | Ollama + System Prompt |
| v4 | Migración a Google Gemini mediante API para consultas de texto en la nube. | Google Gemini 2.5 Flash API |
| v5 | Análisis multimodal de varias fotos reales de la nevera con salida estructurada en Markdown. | Google Gemini 2.5 Flash API + Pillow |
| v6 | Interfaz web con Streamlit: flujo en dos fases (detección editable + generación de menú), filtros en barra lateral y reintento ante saturación (503). | Streamlit + Gemini 2.5 Flash API |
| v7 | Salida estructurada estricta (JSON) mediante esquemas **Pydantic**, renderizado dinámico en tarjetas con badges y descarga dual (JSON/MD). | Pydantic + Gemini 2.5 Flash (`Structured Outputs`) |
| v8 | Interacción dinámica por plato (sustitución de ingredientes y cambios específicos sin regenerar todo el menú) y enlaces directos a vídeos de YouTube. | Pydantic + Gemini 2.5 Flash (`modificar_plato`) + Streamlit Expander |
| v9 | Exportación del menú completo a PDF maquetado con `fpdf2`, sanitización de caracteres y descarga directa. | fpdf2 + Streamlit Download Button |
| v10 | Cantidades estructuradas (`IngredienteReceta`), escalado dinámico de raciones/comensales por plato y exportación adaptada. | Pydantic (Nested Models) + Gemini 2.5 Flash + Streamlit |

---

## Cómo funciona (v10)

1. **Subida multimodal:** Subes una o varias fotos de tu nevera y despensa desde el navegador.
2. **Fase 1 — Escaneo:** Gemini analiza las imágenes y devuelve una lista categorizada de todos los ingredientes detectados.
3. **Corrección manual:** Puedes editar libremente esa lista antes de continuar para corregir posibles fallos de visión.
4. **Fase 2 — Menú estructurado con cantidades:** Con la lista confirmada y los filtros seleccionados (dieta, tiempo y despensa básica), Gemini genera un objeto validado por Pydantic con diagnóstico del chef, tiempos de cocción, dificultad y una lista de ingredientes con cantidades orientativas estructuradas (`nombre` y `cantidad`).
5. **Visualización y búsqueda multimedia:** Cada receta se dibuja en una tarjeta independiente que muestra comensales calculados (`👥 X pers.`), lista detallada de ingredientes por columnas con sus respectivas cantidades/unidades y un botón directo a YouTube con búsqueda optimizada.
6. **Fase 3 — Modificación granular y escalado de comensales:** Cada tarjeta incluye un panel desplegable para solicitar ajustes libres (sustituir ingredientes, variar métodos) y/o seleccionar un nuevo número de raciones (1 a 6 personas). La app consulta a Gemini pasando el JSON del plato y recalcula matemáticamente los ingredientes, tiempos e instrucciones sin alterar las demás recetas.
7. **Descarga triple sincronizada:** Exporta el menú completo con las cantidades y raciones actualizadas en tres formatos:
   - **PDF:** Documento maquetado y limpio con `fpdf2`, apto para impresión.
   - **JSON:** Estructura tipada con el esquema completo anidado.
   - **Markdown:** Texto estructurado con viñetas de ingredientes y raciones.

---

## Tecnologías

- Python 3
- [Streamlit](https://streamlit.io/) — interfaz web interactiva
- [Pydantic](https://docs.pydantic.dev/) — validación de esquemas y marcado de salidas estructuradas en JSON
- [Google Generative AI SDK](https://ai.google.dev/) — integración multimodal con Gemini 2.5 Flash (`response_schema`)
- [fpdf2](https://py-pdf.github.io/fpdf2/) — generación y maquetación de documentos PDF
- Pillow — procesamiento de imágenes
- python-dotenv — gestión de variables de entorno
- Git & GitHub

---

## Instalación y uso

```bash
# 1. Clona el repositorio
git clone [https://github.com/EngelDello/proyecto-nevera-ia.git](https://github.com/EngelDello/proyecto-nevera-ia.git)
cd proyecto-nevera-ia

# 2. Instala las dependencias
pip install -r requirements.txt

# 3. Crea el archivo .env con tu clave de API
echo "GEMINI_API_KEY=tu_clave_aqui" > .env

# 4. Ejecuta la app web
streamlit run app.py

Esto abrirá la aplicación en tu navegador en `http://localhost:8501`.

> **Nota:** El archivo `.env` nunca se sube al repositorio. Consulta `.gitignore`.

---

## Próximas versiones

- [x] Respuesta estructurada en JSON (ingredientes detectados, receta, tiempo, dificultad)
- [x] Reintento automático ante errores temporales de la API (503 / alta demanda)
- [x] Interacción real: sustitución de ingredientes, ajuste de raciones
- [x] Búsqueda de vídeos de YouTube relacionados con la receta
- [x] Descarga del menú también en PDF
- [x] Ajuste dinámico de raciones con cantidades estructuradas (gramos/unidades)
- [ ] Generación de imagen del plato final
- [ ] Despliegue en la nube (Streamlit Community Cloud o similar)

---

## Estructura del repositorio

```text
proyecto-nevera-ia/
├── app.py            # Interfaz web (Streamlit): tarjetas visuales, badges, flujo 2 fases, descargas
├── nevera.py         # Backend: esquemas Pydantic (Plato, MenuCompleto), identificar_ingredientes(), generar_receta_con_filtros() y modificar_plato()
├── images/           # Imágenes de ejemplo de la nevera
├── requirements.txt  # Lista de dependencias (google-genai, streamlit, pydantic, pillow, python-dotenv)
├── README.md
├── .gitignore
└── .env              # Claves de API (no incluido en el repo)
```

---

## Objetivo

Proyecto de aprendizaje progresivo para explorar el ecosistema de IA generativa con Python: modelos locales, APIs multimodales, prompt engineering, esquemas Pydantic anidados para structured outputs, re-prompting granular, escalado dinámico de datos, generación documental (PDF), interfaces web y arquitectura limpia.

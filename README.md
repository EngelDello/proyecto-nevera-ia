# Proyecto Nevera IA

Asistente de cocina inteligente desarrollado en Python. Analiza los ingredientes que tienes en casa a partir de fotos y propone un menú personalizado, con corrección manual de la lista detectada y filtros de dieta, tiempo y despensa. El proyecto evoluciona de forma incremental desde un modelo local hasta una arquitectura en la nube con visión artificial, salida estructurada en JSON e interfaz web interactiva.

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

---

## Cómo funciona (v8)

1. **Subida multimodal:** Subes una o varias fotos de tu nevera y despensa desde el navegador.
2. **Fase 1 — Escaneo:** Gemini analiza las imágenes y devuelve una lista categorizada de todos los ingredientes detectados.
3. **Corrección manual:** Puedes editar libremente esa lista antes de continuar para corregir posibles fallos de visión.
4. **Fase 2 — Menú estructurado en JSON:** Con la lista confirmada y los filtros seleccionados (dieta, tiempo y despensa básica), Gemini genera un objeto validado por Pydantic con diagnóstico del chef, tiempos de cocción, dificultad, ingredientes e instrucciones detalladas.
5. **Visualización y búsqueda multimedia:** Cada receta se dibuja en una tarjeta independiente con etiquetas (*badges*) para los ingredientes y un botón directo con búsqueda optimizada en YouTube.
6. **Fase 3 — Modificación interactiva (Re-prompting granular):** Cada tarjeta incluye un desplegable para solicitar ajustes específicos (sustituir ingredientes, adaptar tiempos o técnicas). La app consulta a Gemini enviando únicamente el JSON de ese plato y actualiza la tarjeta al instante sin alterar las demás.
7. **Descarga dual:** Permite exportar el menú completo en formato estructurado (`.json`) o en texto maquetado (`.md`).

---

## Tecnologías

- Python 3
- [Streamlit](https://streamlit.io/) — interfaz web interactiva
- [Pydantic](https://docs.pydantic.dev/) — validación de esquemas y marcado de salidas estructuradas en JSON
- [Google Generative AI SDK](https://ai.google.dev/) — integración con Gemini 2.5 Flash (`response_schema`)
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
- [ ] Ajuste dinámico de raciones con cantidades estructuradas (gramos/unidades)
- [ ] Descarga del menú también en PDF
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

Proyecto de aprendizaje progresivo para explorar el ecosistema de IA generativa con Python: modelos locales, APIs multimodales, prompt engineering, esquemas Pydantic para structured outputs, interfaces web y arquitectura limpia.

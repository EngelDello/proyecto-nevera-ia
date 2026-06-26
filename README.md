# Proyecto Nevera IA

Asistente de cocina inteligente desarrollado en Python. Analiza los ingredientes que tienes en casa y propone recetas detalladas. El proyecto evoluciona de forma incremental desde un modelo local hasta una arquitectura en la nube con visión artificial.

---

## Evolución del proyecto

| Versión | Descripción | Tecnología |
|---------|-------------|------------|
| v1 | Entrada manual de ingredientes por consola y propuesta de receta básica. | Ollama + `qwen2.5-coder:1.5b` |
| v2 | Interfaz de chat continuo en bucle `while True`, simulando una conversación interactiva sin reinicios. | Ollama |
| v3 | Control de alucinaciones mediante *System Prompt* estricto para evitar ingredientes fantasma. | Ollama + System Prompt |
| v4 | Migración a Google Gemini mediante API para consultas de texto en la nube. | Google Gemini 2.5 Flash API |
| v5 | Análisis multimodal de varias fotos reales de la nevera con salida estructurada en Markdown. | Google Gemini 2.5 Flash API + Pillow |

---

## Tecnologías

- Python 3
- [Ollama](https://ollama.com/) — inferencia local en las primeras versiones
- [Google Generative AI SDK](https://ai.google.dev/) — integración con Gemini por API en las versiones en la nube
- Pillow — carga de imágenes locales
- Git & GitHub

---

## Instalación y uso

```bash
# 1. Clona el repositorio
git clone https://github.com/EngelDello/proyecto-nevera-ia.git
cd proyecto-nevera-ia

# 2. Instala las dependencias
pip install -r requirements.txt

# 3. Crea el archivo .env con tu clave de API
echo "GOOGLE_API_KEY=tu_clave_aqui" > .env

# 4. Ejecuta el asistente
python nevera.py
```

> **Nota:** El archivo `.env` nunca se sube al repositorio. Consulta `.gitignore`.

---

## Próximas versiones

- [ ] Respuesta estructurada en JSON (ingredientes detectados, receta, tiempo, dificultad)
- [ ] Contexto y memoria entre conversaciones
- [ ] Interacción real: sustitución de ingredientes, ajuste de raciones
- [ ] Interfaz web mínima
- [ ] Búsqueda de vídeos de YouTube relacionados con la receta
- [ ] Generación de imagen del plato final

---

## Estructura del repositorio

```text
proyecto-nevera-ia/
├── nevera.py         # Script principal
├── images/           # Imágenes de la nevera usadas en la versión multimodal
├── requirements.txt  # Lista de dependencias
├── README.md
├── .gitignore
└── .env              # Claves de API (no incluido en el repo)
```

---

## Objetivo

Proyecto de aprendizaje progresivo para explorar el ecosistema de IA generativa con Python: modelos locales, APIs multimodales, prompt engineering y orquestación de servicios externos.

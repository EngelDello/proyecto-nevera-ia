import os
import time  # 👈 Importante añadir esto arribaceta
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key) if api_key else None

# FASE 1: Identificar ingredientes desde las imágenes
def identificar_ingredientes(imagenes):
    if not client:
        return "Error: No se encontró la API Key en el archivo .env"
    
    prompt = """Analiza minuciosamente las imágenes de la nevera/despensa. 
    Genera una lista clara y estructurada por categorías (Proteínas, Verduras, Frutas, Lácteos, etc.) 
    de TODOS los ingredientes que ves. Sé preciso y breve en los nombres."""
    
    try:
        respuesta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=imagenes + [prompt]
        )
        return respuesta.text
    except Exception as e:
        return f"Error al conectar con Gemini: {e}"

# FASE 2: Generar la receta con los ingredientes corregidos + Filtros
def generar_receta_con_filtros(ingredientes_texto, despensa, dieta, tiempo_cocina, intentos=3):
    if not client:
        return "Error: No se encontró la API Key en el archivo .env"
    
    reglas_chef = f"""Actúas como un chef robot ultra-estricto y eficiente.
    
    Tus restricciones actuales son:
    - Dieta: {dieta}
    - Tiempo disponible: {tiempo_cocina}
    - Ingredientes básicos de despensa disponibles: {despensa}
    
    Debes diseñar un menú óptimo (Desayuno, Almuerzo, Cena) usando ÚNICAMENTE los ingredientes confirmados 
    y respetando estrictamente las restricciones del usuario."""
    
    prompt = f"Aquí tienes la lista confirmada de ingredientes disponibles:\n\n{ingredientes_texto}\n\nPor favor, genera el plan de menú."
    
    for intento in range(intentos):
        try:
            respuesta = client.models.generate_content(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(system_instruction=reglas_chef),
                contents=[prompt]
            )
            return respuesta.text
        except Exception as e:
            # Si es un error de servidor saturado (503) y nos quedan reintentos
            if "503" in str(e) and intento < intentos - 1:
                time.sleep(2)  # Espera 2 segundos antes de volver a probar
                continue
            return f"Error al conectar con Gemini tras varios intentos: {e}"
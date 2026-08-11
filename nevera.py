import os
import time
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key) if api_key else None

# --- ESQUEMA DE SALIDA ESTRUCTURADA (JSON) ---
class Plato(BaseModel):
    nombre: str = Field(description="Nombre descriptivo del plato")
    tipo_comida: str = Field(description="Desayuno, Almuerzo o Cena")
    tiempo_preparacion_minutos: int = Field(description="Tiempo estimado de preparación en minutos")
    dificultad: str = Field(description="Baja, Media o Alta")
    ingredientes_usados: List[str] = Field(description="Ingredientes de la lista confirmada o despensa usados")
    pasos: List[str] = Field(description="Pasos cronológicos de preparación")

class MenuCompleto(BaseModel):
    observaciones_chef: str = Field(description="Diagnóstico breve del chef robot sobre el inventario y recomendaciones")
    platos: List[Plato]

# FASE 1: Identificar ingredientes
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

# FASE 2: Generar menú con formato JSON estricto
def generar_receta_con_filtros(ingredientes_texto, despensa, dieta, tiempo_cocina, intentos=3):
    if not client:
        return None
    
    reglas_chef = f"""Actúas como un chef robot ultra-estricto y eficiente.
    
    Tus restricciones actuales son:
    - Dieta: {dieta}
    - Tiempo disponible: {tiempo_cocina}
    - Ingredientes básicos de despensa disponibles: {despensa}
    
    Debes diseñar un menú óptimo (Desayuno, Almuerzo, Cena) usando ÚNICAMENTE los ingredientes confirmados 
    y respetando estrictamente las restricciones del usuario."""
    
    prompt = f"Aquí tienes la lista confirmada de ingredientes disponibles:\n\n{ingredientes_texto}\n\nGenera el menú completo."
    
    for intento in range(intentos):
        try:
            respuesta = client.models.generate_content(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(
                    system_instruction=reglas_chef,
                    response_mime_type="application/json",
                    response_schema=MenuCompleto,
                ),
                contents=[prompt]
            )
            # Convertimos la respuesta JSON a un objeto Python tipado
            return MenuCompleto.model_validate_json(respuesta.text)
        except Exception as e:
            if "503" in str(e) and intento < intentos - 1:
                time.sleep(2)
                continue
            return None
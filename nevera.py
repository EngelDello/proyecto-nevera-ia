import os
import time
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types
import unicodedata
from fpdf import FPDF

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key) if api_key else None

# --- ESQUEMA DE SALIDA ESTRUCTURADA (JSON) ---
class Plato(BaseModel):
    nombre: str = Field(description="Nombre descriptivo del plato")
    tipo_comida: str = Field(description="Desayuno, Almuerzo o Cena")
    tiempo_preparacion_minutos: int = Field(description="Tiempo estimado de preparación en minutos")
    dificultad: str = Field(description="Baja, Media o Alta")
    #raciones: int = Field(default=2, description="Número de personas para las que está calculada la receta")
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

# FASE 3: Modificar un plato individual manteniendo el esquema
def modificar_plato(plato_actual: Plato, instruccion_cambio: str, ingredientes_disponibles: str, despensa: str, intentos=3):
    if not client:
        return None

    reglas_chef = f"""Actúas como un chef robot.
    Tu tarea es MODIFICAR un único plato existente siguiendo la petición del usuario.
    
    Reglas estrictas:
    - Mantén la coherencia con los ingredientes disponibles confirmados: {ingredientes_disponibles}
    - Ingredientes básicos de despensa: {despensa}
    - Aplica la instrucción solicitada por el usuario de forma precisa."""

    prompt = f"""Plato actual (formato JSON):
    {plato_actual.model_dump_json(indent=2)}

    Instrucción de cambio del usuario:
    "{instruccion_cambio}"

    Devuelve el plato modificado en el mismo formato estructurado."""

    for intento in range(intentos):
        try:
            respuesta = client.models.generate_content(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(
                    system_instruction=reglas_chef,
                    response_mime_type="application/json",
                    response_schema=Plato,  # Forzamos a devolver un único objeto Plato
                ),
                contents=[prompt]
            )
            return Plato.model_validate_json(respuesta.text)
        except Exception as e:
            if "503" in str(e) and intento < intentos - 1:
                time.sleep(2)
                continue
            return None

def limpiar_texto_pdf(texto: str) -> str:
    """Sanea el texto eliminando caracteres tipográficos incompatibles con Latin-1."""
    if not texto:
        return ""
    reemplazos = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '…': '...', '•': '*'
    }
    for orig, nuevo in reemplazos.items():
        texto = texto.replace(orig, nuevo)
    # Conserva caracteres españoles estándar (tildes, ñ) y descarta caracteres no soportados
    return texto.encode('latin-1', 'replace').decode('latin-1')

class PDFMenu(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'Menú Sugerido - Nevera IA', border=False, align='C')
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def generar_pdf_menu(menu: MenuCompleto) -> bytes:
    pdf = PDFMenu()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.ln(4)  # Separa el contenido del encabezado
    
    # Ancho efectivo de la página (evita cualquier error de espacio horizontal)
    ancho_util = pdf.epw
    
    # Diagnóstico del chef
    if menu.observaciones_chef:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(ancho_util, 7, 'Diagnostico del Chef:', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(ancho_util, 5, limpiar_texto_pdf(menu.observaciones_chef))
        pdf.ln(4)

    # Platos
    for plato in menu.platos:
        # Título del plato
        pdf.set_font('Helvetica', 'B', 13)
        pdf.cell(ancho_util, 8, limpiar_texto_pdf(f"{plato.tipo_comida}: {plato.nombre}"), new_x="LMARGIN", new_y="NEXT")
        
        # Metadatos
        pdf.set_font('Helvetica', 'I', 9)
        pdf.cell(ancho_util, 5, limpiar_texto_pdf(f"Tiempo: {plato.tiempo_preparacion_minutos} min  |  Dificultad: {plato.dificultad}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        
        # Ingredientes
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(ancho_util, 6, "Ingredientes:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 9)
        pdf.multi_cell(ancho_util, 5, limpiar_texto_pdf(", ".join(plato.ingredientes_usados)))
        pdf.ln(2)
        
        # Pasos
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(ancho_util, 6, "Instrucciones de preparacion:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 9)
        for i, paso in enumerate(plato.pasos, 1):
            pdf.multi_cell(ancho_util, 5, limpiar_texto_pdf(f"{i}. {paso}"))
            pdf.ln(1)
        
        pdf.ln(4)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(4)

    return bytes(pdf.output())
import os
from dotenv import load_dotenv # para cargar .env
from google import genai # librerias de google
from google.genai import types

# 1. carga las variables del .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

2. # iniciar con verificacion
try:
    if not api_key:
        raise ValueError("No se encontro la api de google en el fichero .env")
    
    client = genai.Client(api_key=api_key)
    # Verificación simple: Intentar listar modelos o una llamada mínima
    # Esto asegura que la comunicación con Google es posible
    client.models.get(model='gemini-2.5-flash')
    print("✅ Cliente de Google GenAI conectado correctamente.\n")
except Exception as e:
    print(f"❌ Error al iniciar el cliente: {e}")
    client = None

# 3. Realizar la consulta si el cliente está listo
if client:
    print("🧠 === BIENVENIDO AL ASISTENTE DE COCINA IA CON GEMINI ===")
    print("Escribe tus ingredientes o 'salir' para terminar el programa.")

    # 1. Definimos las reglas fijas del juego (El System Prompt)
    reglas_chef = (
        "Actúas como un chef robot ultra-estricto. "
        "Tu misión es dar una receta usando ÚNICAMENTE los ingredientes que te pase el usuario. "
        "Está totalmente prohibido añadir ingredientes extra (ni sal, ni aceite, ni especias, ni embutidos). "
        "Si no se puede hacer nada comestible con lo que te dan, di textualmente: 'No se puede cocinar nada seguro'."
    )

    while True:
        print("\n" + "=" * 30)
        user_input = input("Qué ingredientes tienes hoy?")
        if user_input.lower() == "salir":
            print("\n Hasta luego! Gracias por usar el chef IA.")
            break   

        print("\n⏳ El chef estricto está calculando...")

        try:
            # 2. Ahora enviamos una LISTA de mensajes organizada por roles
            respuesta = client.models.generate_content(
                model='gemini-2.5-flash',
                # Aquí pasas el "system content"
                config=types.GenerateContentConfig(
                    system_instruction=reglas_chef
                ),
                contents=f"Mis ingredientes son {user_input}."
            )
            print("\n👨‍🍳 MENÚ PROPUESTO:")
            print(respuesta.text)
        except Exception as e:
            print(f"Error al conectar con Gemini. Error: {e}") 
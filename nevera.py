import ollama

print("🧠 === BIENVENIDO AL ASISTENTE DE COCINA IA ===")
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
        respuesta = ollama.chat(
            model='qwen2.5-coder:1.5b',
            messages=[
                # primero le fijamos la personalidad y las prohibiciones
                {'role': 'system', 'content': reglas_chef},
                # Luego le pasamos tus ingredientes actuales
                {'role': 'user', 'content': f"Mis ingredientes son {user_input}."}
            ]
        )
        print("\n👨‍🍳 MENÚ PROPUESTO:")
        print(respuesta['message']['content'])
    except Exception as e:
        print(f"Error al conectar con Ollama. Error: {e}") 
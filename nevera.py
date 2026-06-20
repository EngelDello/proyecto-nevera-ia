import ollama

print("🧠 === BIENVENIDO AL ASISTENTE DE COCINA IA ===")
print("Escribe los ingredientes que tienes en la nevera separados por comas.")
print("Ejemplo: huevos, tomate, queso, pollo\n")

# 1. Aquí el programa se para y espera a que tú escribas.
# Lo que escribas se guardará dentro de la variable 'mis_ingredientes'

mis_ingredientes = input("Qué tienes en la nevera hoy?")

# 2. Creamos las instrucciones uniendo tu texto con la petición para el chef
instrucciones = f"Actúa como un chef. Dame una receta rápida usando estrictamente estos ingredientes: {mis_ingredientes}"

print("\n⏳ El chef de Ollama (Qwen) está pensando... (tardará unos 30 segundos)")

# 3. Llamamos a tu modelo ganador de ayer
respuesta = ollama.chat(
    model='qwen2.5-coder:1.5b', # Tu modelo ganador
    messages=[
        {'role': 'user', 'content': instrucciones} # Tu pregunta
    ]
)

# 4. Mostramos el resultado limpio
print("\n👨‍🍳 MENÚ PROPUESTO:")
print(respuesta['message']['content'])
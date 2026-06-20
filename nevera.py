import ollama

print("🧠 === BIENVENIDO AL ASISTENTE DE COCINA IA ===")
print("Escribe tus ingredientes o 'salir' para terminar el programa.")
# exit_bool = False
while True:
    print("\n" + "=" * 30)

    # 1. Aquí el programa se para y espera a que tú escribas.
    # Lo que escribas se guardará dentro de la variable 'mis_ingredientes'
    user_input = input("Qué tienes en la nevera hoy?")
    # comprobacion si ha puesto salir
    if user_input.lower() == "salir":
        print("\n Hasta luego! Gracias por usar el chef IA.")
        break # el comando break rompe el bucle y sale del programa
    # 2. Creamos las instrucciones uniendo tu texto con la petición para el chef")
    instrucciones = f"Actúa como un chef. Dame una receta rápida usando estrictamente estos ingredientes: {user_input}"

    print("\n⏳ El chef de Ollama (Qwen) está pensando... (tardará unos 30 segundos)")

    # 3. Llamamos a tu modelo ganador de ayer
    try:      
        respuesta = ollama.chat(
            model='qwen2.5-coder:1.5b', # Tu modelo ganador
            messages=[
                {'role': 'user', 'content': instrucciones} # Tu pregunta}
            ]
        )
        # 4. Mostramos el resultado limpio
        print("\n👨‍🍳 MENÚ PROPUESTO:")
        print(respuesta['message']['content'])
    except Exception as e:
        # por si falla la ejecucion
        print(f"Error al conectar con Ollama. Error: {e}")

    #aqui vuelve al principio o si has puesto salir sale

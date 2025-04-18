import openai

# Si usás openai>=1.0.0, hay que usar Client
client = openai.OpenAI(api_key="sk-XXXXXXXXXXXXXXXXXXXX")

def responder_con_manito(prompt_usuario):
    try:
        respuesta = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": (
                    "Actuás como el representante oficial de Manito AI. "
                    "Tu tono es amigable, claro, profesional y empático. "
                    "No mencionás que sos una IA, hablás como si fueras parte del equipo. "
                    "Tu objetivo es ayudar al usuario con respuestas útiles y naturales."
                )},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

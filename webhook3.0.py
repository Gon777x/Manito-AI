from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# --- Conexión a la misma base que usa Manito AI ---
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# --- Ruta para verificación de Meta ---
@app.route('/webhook', methods=['GET'])
def verify():
    verify_token = "manito_token_seguro"
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == verify_token:
        return request.args.get("hub.challenge")
    return "Error de verificación", 403

# --- Ruta para recibir mensajes ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Datos recibidos:", data)

    try:
        mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        numero = data['entry'][0]['changes'][0]['value']['messages'][0]['from']

        # Buscar respuesta en la base
        cursor.execute("SELECT respuesta FROM faq WHERE pregunta LIKE ?", ('%' + mensaje + '%',))
        resultado = cursor.fetchone()

        if resultado:
            respuesta = resultado[0]
        else:
            respuesta = "🤖 ¡Gracias por tu mensaje! Pronto te responderemos."

        # --- Aquí es donde responderías usando la API de WhatsApp (omito el código real de envío por seguridad) ---
        print(f"Responder a {numero}: {respuesta}")

    except Exception as e:
        print("Error al procesar:", e)

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(port=5000)
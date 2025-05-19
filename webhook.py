from flask import Flask, request
import sqlite3
import requests

app = Flask(__name__)

VERIFY_TOKEN = 'MANITO_AI_301'  # Usá el mismo en Meta Developers
PAGE_ACCESS_TOKEN = 'TU_TOKEN_PAGINA_DE_META'  # Cambialo por tu token real

@app.route('/', methods=['GET'])
def verificar_webhook():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == VERIFY_TOKEN:
        return challenge
    return 'Token inválido', 403

@app.route('/', methods=['POST'])
def recibir_mensajes():
    data = request.get_json()
    if data and 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                if 'message' in messaging_event:
                    remitente = messaging_event['sender']['id']
                    texto = messaging_event['message'].get('text', '')

                    # Buscar respuesta en SQLite
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT respuesta FROM faq WHERE pregunta LIKE ?", ('%' + texto + '%',))
                    resultado = cursor.fetchone()
                    conn.close()

                    respuesta = resultado[0] if resultado else "¡Hola! 😊 No tengo esa respuesta aún, pero te responderé pronto."

                    # Enviar respuesta a Meta Messenger
                    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
                    payload = {
                        'recipient': {'id': remitente},
                        'message': {'text': respuesta}
                    }
                    requests.post(url, json=payload)
    return 'EVENT_RECEIVED', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
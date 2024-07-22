# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

messages = []

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    recipient = data['recipient']
    message = data['message']
    messages.append({'recipient': recipient, 'message': message, 'sender': 'Anonymous'})
    return jsonify({'status': 'Message sent'}), 200

@app.route('/get-messages', methods=['GET'])
def get_messages():
    recipient = request.args.get('recipient')
    recipient_messages = [msg for msg in messages if msg['recipient'] == recipient]
    return jsonify({'messages': recipient_messages}), 200

if __name__ == '__main__':
    app.run(debug=True)

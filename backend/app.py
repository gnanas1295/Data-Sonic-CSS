from flask import Flask, request, jsonify

app = Flask(__name__)

messages = []

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    messages.append(data['message'])
    return jsonify({'status': 'Message received'}), 200

@app.route('/get-messages', methods=['GET'])
def get_messages():
    return jsonify({'messages': messages}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
